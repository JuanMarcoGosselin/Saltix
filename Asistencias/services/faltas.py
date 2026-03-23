from __future__ import annotations

from dataclasses import dataclass
from datetime import date, timedelta

from django.db.models import Exists, OuterRef, QuerySet
from django.utils import timezone

from Asistencias.models import Asistencia, Incidencia


SIMULATED_PAYROLL_WEEKS = 5


@dataclass(frozen=True)
class DateRange:
    inicio: date
    fin: date


def simulated_payroll_period(hoy: date | None = None) -> DateRange:
    hoy = hoy or timezone.localdate()
    return DateRange(inicio=hoy - timedelta(weeks=SIMULATED_PAYROLL_WEEKS), fin=hoy)


def start_of_week(d: date) -> date:
    return d - timedelta(days=d.weekday())


def weeks_between(week_start_a: date, week_start_b: date) -> int:
    """
    NÃºmero de semanas enteras entre dos inicios de semana (Lunes).
    Retorna un entero >= 0 si a estÃ¡ despuÃ©s o igual a b.
    """
    delta_days = (week_start_a - week_start_b).days
    return max(0, delta_days // 7)


def current_payroll_period(hoy: date | None = None) -> DateRange:
    """
    Periodo vigente (Contabilidad.Periodo con estado ABIERTO).
    Se ignora el plantel y se toma el periodo ABIERTO mÃ¡s reciente.
    Si no existe, se usa un periodo simulado (fallback).
    """
    hoy = hoy or timezone.localdate()
    try:
        from Contabilidad.models import Periodo  # import local para evitar acoplamiento duro
    except Exception:
        return simulated_payroll_period(hoy=hoy)

    periodo = (
        Periodo.objects.filter(estado="ABIERTO")
        .order_by("-fecha_inicio", "-id")
        .first()
    )
    if not periodo:
        return simulated_payroll_period(hoy=hoy)
    return DateRange(inicio=periodo.fecha_inicio, fin=periodo.fecha_fin)


def previous_payroll_period(*, current_inicio: date) -> DateRange | None:
    """
    Periodo anterior (cerrado) mÃ¡s reciente antes del periodo actual.
    Se ignora el plantel.
    """
    try:
        from Contabilidad.models import Periodo
    except Exception:
        return None

    prev = (
        Periodo.objects.filter(estado="CERRADO", fecha_fin__lt=current_inicio)
        .order_by("-fecha_fin", "-id")
        .first()
    )
    if not prev:
        return None
    return DateRange(inicio=prev.fecha_inicio, fin=prev.fecha_fin)


def week_range(hoy: date | None = None, week_offset: int = 0) -> DateRange:
    hoy = hoy or timezone.localdate()
    week_offset = max(0, int(week_offset))
    inicio_semana = hoy - timedelta(days=hoy.weekday()) - timedelta(weeks=week_offset)
    fin_semana = inicio_semana + timedelta(days=5)  # Lun-Sab (inclusive)
    return DateRange(inicio=inicio_semana, fin=fin_semana)


def intersect_ranges(a: DateRange, b: DateRange) -> DateRange | None:
    inicio = max(a.inicio, b.inicio)
    fin = min(a.fin, b.fin)
    if inicio > fin:
        return None
    return DateRange(inicio=inicio, fin=fin)


def unjustified_absences_queryset(
    *,
    profesor=None,
    hoy: date | None = None,
    week_offset: int = 0,
) -> tuple[QuerySet[Asistencia], DateRange, DateRange, DateRange | None]:
    hoy = hoy or timezone.localdate()
    nav = unjustified_absences_navigation(hoy=hoy)
    current_period: DateRange = nav["current_period"]
    prev_period: DateRange | None = nav["previous_period"]
    anchor: date = nav["anchor"]
    max_week_offset: int = nav["max_week_offset"]
    max_offset_actual: int = nav["max_offset_actual"]
    prev_offset: int | None = nav["prev_offset"]

    week_offset = max(0, min(int(week_offset or 0), max_week_offset))
    if prev_offset is not None and week_offset > max_offset_actual and week_offset != prev_offset:
        week_offset = prev_offset
    rango_semana = week_range(hoy=anchor, week_offset=week_offset)

    # Si se selecciona el offset especial del periodo anterior, usamos ese periodo.
    if prev_period is not None and prev_offset is not None and week_offset == prev_offset:
        rango_periodo = prev_period
    else:
        rango_periodo = current_period

    rango_efectivo = intersect_ranges(rango_semana, rango_periodo)

    qs = Asistencia.objects.filter(
        estado="FALTA",
        justificada=False,
        cancelada_institucional=False,
    )
    if profesor is not None:
        qs = qs.filter(profesor=profesor)

    if rango_efectivo is None:
        qs = qs.none()
    else:
        qs = qs.filter(fecha__range=(rango_efectivo.inicio, rango_efectivo.fin))

    pendiente_qs = Incidencia.objects.filter(asistencia_id=OuterRef("pk"), estado="PENDIENTE")
    qs = qs.annotate(tiene_incidencia_pendiente=Exists(pendiente_qs))

    qs = qs.select_related("profesor", "horario", "profesor__usuario").order_by("-fecha", "-id")
    return qs, rango_semana, rango_periodo, rango_efectivo


def unjustified_absences_max_week_offset(*, hoy: date | None = None) -> int:
    """
    MÃ¡ximo week_offset permitido para el dashboard del profesor:
    - semanas dentro del periodo vigente
    - + la Ãºltima semana del periodo anterior (si existe)
    """
    hoy = hoy or timezone.localdate()
    rango_periodo = current_payroll_period(hoy=hoy)
    prev_periodo = previous_payroll_period(current_inicio=rango_periodo.inicio)

    anchor = min(hoy, rango_periodo.fin)
    anchor_week = start_of_week(anchor)
    max_offset_actual = weeks_between(anchor_week, start_of_week(rango_periodo.inicio))
    max_offset = max_offset_actual
    if prev_periodo is not None:
        max_offset = max(max_offset, weeks_between(anchor_week, start_of_week(prev_periodo.fin)))
    return max_offset


def unjustified_absences_navigation(*, hoy: date | None = None) -> dict:
    """
    Datos de navegaciÃ³n de semanas para el mÃ³dulo de justificaciones:
    - semanas del periodo vigente
    - + salto a la Ãºltima semana del periodo anterior (si existe)
    """
    hoy = hoy or timezone.localdate()
    current = current_payroll_period(hoy=hoy)
    prev = previous_payroll_period(current_inicio=current.inicio)

    anchor = min(hoy, current.fin)
    anchor_week = start_of_week(anchor)

    max_offset_actual = weeks_between(anchor_week, start_of_week(current.inicio))
    prev_offset = None
    if prev is not None:
        prev_offset = weeks_between(anchor_week, start_of_week(prev.fin))

    max_week_offset = max_offset_actual if prev_offset is None else max(max_offset_actual, prev_offset)
    return {
        "max_week_offset": max_week_offset,
        "max_offset_actual": max_offset_actual,
        "prev_offset": prev_offset,
        "anchor": anchor,
        "current_period": current,
        "previous_period": prev,
    }


def period_stats(*, profesor, hoy: date | None = None) -> dict:
    hoy = hoy or timezone.localdate()
    periodo = current_payroll_period(hoy=hoy)

    qs = Asistencia.objects.filter(
        profesor=profesor,
        fecha__range=(periodo.inicio, periodo.fin),
        cancelada_institucional=False,
    )

    return {
        "asistencias": qs.filter(estado="ASISTENCIA").count(),
        "retardos": qs.filter(estado="RETARDO").count(),
        "faltas": qs.filter(estado="FALTA", justificada=False).count(),
        "justificadas": qs.filter(justificada=True).count(),
    }


def all_absences_queryset(
    *,
    profesor=None,
    fecha_inicio: date | None = None,
    fecha_fin: date | None = None,
) -> QuerySet[Asistencia]:
    qs = Asistencia.objects.filter(
        estado__in=("FALTA", "JUSTIFICADA"),
        cancelada_institucional=False,
    )
    if profesor is not None:
        qs = qs.filter(profesor=profesor)
    if fecha_inicio:
        qs = qs.filter(fecha__gte=fecha_inicio)
    if fecha_fin:
        qs = qs.filter(fecha__lte=fecha_fin)

    return qs.select_related("profesor", "horario", "profesor__usuario").order_by("-fecha", "-id")
