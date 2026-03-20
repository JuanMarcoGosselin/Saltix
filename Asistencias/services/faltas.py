from __future__ import annotations

from dataclasses import dataclass
from datetime import date, timedelta

from django.db.models import QuerySet
from django.utils import timezone

from Asistencias.models import Asistencia


MAX_WEEK_OFFSET = 8  # ~2 meses
SIMULATED_PAYROLL_WEEKS = 5


@dataclass(frozen=True)
class DateRange:
    inicio: date
    fin: date


def simulated_payroll_period(hoy: date | None = None) -> DateRange:
    hoy = hoy or timezone.localdate()
    return DateRange(inicio=hoy - timedelta(weeks=SIMULATED_PAYROLL_WEEKS), fin=hoy)


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
    week_offset = max(0, min(int(week_offset), MAX_WEEK_OFFSET))

    rango_semana = week_range(hoy=hoy, week_offset=week_offset)
    rango_periodo = simulated_payroll_period(hoy=hoy)
    rango_efectivo = intersect_ranges(rango_semana, rango_periodo)

    qs = Asistencia.objects.filter(
        estado__in=("FALTA", "RETARDO"),
        justificada=False,
        cancelada_institucional=False,
    )
    if profesor is not None:
        qs = qs.filter(profesor=profesor)

    if rango_efectivo is None:
        qs = qs.none()
    else:
        qs = qs.filter(fecha__range=(rango_efectivo.inicio, rango_efectivo.fin))

    qs = qs.select_related("profesor", "horario", "profesor__usuario").order_by("-fecha", "-id")
    return qs, rango_semana, rango_periodo, rango_efectivo


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
