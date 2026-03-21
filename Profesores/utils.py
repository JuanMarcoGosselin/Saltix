import calendar
from datetime import datetime, timedelta
from decimal import Decimal, ROUND_HALF_UP

from django.utils import timezone

from Asistencias.models import Asistencia

from .models import Horario, Profesor

def obtener_horario_hoy(profesor):
    dias = {
        0: "LUN",
        1: "MAR",
        2: "MIE",
        3: "JUE",
        4: "VIE",
        5: "SAB",
    }

    hoy = timezone.localdate()
    dia = dias.get(hoy.weekday())
    if not dia:
        return Horario.objects.none()
    return Horario.objects.filter(profesor=profesor, dia_semana=dia)


def obtener_horario(profesor):
    dias = {
        0: "LUN",
        1: "MAR",
        2: "MIE",
        3: "JUE",
        4: "VIE",
        5: "SAB",
    }
    horario = {}
    horas_totales = 0
    for dia in dias:
        horario[dia] = Horario.objects.filter(profesor=profesor, dia_semana=dias[dia])
        for clase in horario[dia]:
            horas_totales += clase.hora_fin.hour - clase.hora_inicio.hour
    return (horario, horas_totales)


def verificar_entrada(horario_id):
    ahora = timezone.now()
    hoy = ahora.date()

    horario = Horario.objects.get(id=horario_id)
    tz = timezone.get_current_timezone()
    inicio = timezone.make_aware(datetime.combine(hoy, horario.hora_inicio), tz)

    return inicio - timedelta(minutes=15) <= ahora <= inicio + timedelta(minutes=30)


def verificar_salida(horario_id):
    ahora = timezone.now()
    hoy = ahora.date()

    horario = Horario.objects.get(id=horario_id)
    tz = timezone.get_current_timezone()
    fin = timezone.make_aware(datetime.combine(hoy, horario.hora_fin), tz)

    return fin - timedelta(minutes=10) <= ahora <= fin + timedelta(minutes=30)


def minutes_between_times(start, end) -> int:
    if start is None or end is None:
        return 0
    base = datetime(2000, 1, 1)
    start_dt = datetime.combine(base.date(), start)
    end_dt = datetime.combine(base.date(), end)
    if end_dt < start_dt:
        end_dt += timedelta(days=1)
    return int((end_dt - start_dt).total_seconds() // 60)


def format_hours(minutes: int) -> str:
    hours = (Decimal(minutes) / Decimal(60)).quantize(Decimal("0.1"), rounding=ROUND_HALF_UP)
    if hours == hours.to_integral():
        return str(hours.quantize(Decimal("0"), rounding=ROUND_HALF_UP))
    return str(hours)


def format_money(amount: Decimal) -> str:
    amount = (amount or Decimal(0)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    return f"{amount:,.2f}"


def expected_minutes_for_range(horarios, inicio, fin) -> int:
    if not inicio or not fin or fin < inicio:
        return 0

    minutos_por_dia = {}
    for h in horarios:
        minutos_por_dia.setdefault(h.dia_semana, 0)
        minutos_por_dia[h.dia_semana] += minutes_between_times(h.hora_inicio, h.hora_fin)

    total = 0
    d = inicio
    while d <= fin:
        dia = ("LUN", "MAR", "MIE", "JUE", "VIE", "SAB", "DOM")[d.weekday()]
        total += minutos_por_dia.get(dia, 0)
        d += timedelta(days=1)
    return total


def month_bounds(hoy):
    month_end_day = calendar.monthrange(hoy.year, hoy.month)[1]
    return hoy.replace(day=1), hoy.replace(day=month_end_day)


def dashboard_kpis(*, profesor: Profesor, hoy, rango_periodo):
    asistencias_periodo = (
        Asistencia.objects.filter(
            profesor=profesor,
            fecha__range=(rango_periodo.inicio, rango_periodo.fin),
            cancelada_institucional=False,
            estado__in=("ASISTENCIA", "RETARDO"),
        )
        .select_related("horario")
    )
    minutos_trabajados_periodo = sum(
        minutes_between_times(a.horario.hora_inicio, a.horario.hora_fin) for a in asistencias_periodo if a.horario_id
    )

    horarios_clase = list(Horario.objects.filter(profesor=profesor, es_hora_clase=True))
    minutos_esperados_periodo = expected_minutes_for_range(
        horarios_clase, rango_periodo.inicio, rango_periodo.fin
    )

    mes_inicio, mes_fin = month_bounds(hoy)
    minutos_esperados_mes = expected_minutes_for_range(horarios_clase, mes_inicio, mes_fin)
    horas_esperadas_mes = (Decimal(minutos_esperados_mes) / Decimal(60))
    salario_bruto_estimado_mes = horas_esperadas_mes * (profesor.costo_por_hora or Decimal(0))

    return {
        "horarios_clase": horarios_clase,
        "minutos_trabajados_periodo": minutos_trabajados_periodo,
        "minutos_esperados_periodo": minutos_esperados_periodo,
        "mes_inicio": mes_inicio,
        "mes_fin": mes_fin,
        "salario_bruto_estimado_mes": salario_bruto_estimado_mes,
    }


def profesor_profile_context(*, profesor: Profesor, hoy, horarios_clase):
    return {
        "perfil_iniciales": f"{(profesor.usuario.nombre or 'U')[:1]}{(profesor.usuario.apellido or '')[:1]}".upper(),
        "perfil_nombre": f"{profesor.usuario.nombre} {profesor.usuario.apellido}".strip(),
        "perfil_puesto": "Profesor",
        "perfil_estado": (profesor.estado_laboral or "").replace("_", " ").title() or "â€”",
        "perfil_anios_institucion": str(max(0, (hoy - profesor.fecha_ingreso).days // 365)) if profesor.fecha_ingreso else "â€”",
        "perfil_jornada_semanal": format_hours(sum(minutes_between_times(h.hora_inicio, h.hora_fin) for h in horarios_clase)),
        "perfil_grupos": str(len(horarios_clase)),
        "perfil_anios_experiencia": str(max(0, (hoy - profesor.fecha_ingreso).days // 365)) if profesor.fecha_ingreso else "â€”",
        "perfil_datos": [
            {"label": "Email", "value": profesor.usuario.email},
            {"label": "TelÃ©fono", "value": profesor.telefono},
            {"label": "RFC", "value": profesor.rfc},
            {"label": "CURP", "value": profesor.curp},
            {"label": "Dirección", "value": profesor.direccion},
            {"label": "Fecha de ingreso", "value": profesor.fecha_ingreso.strftime("%d/%m/%Y") if profesor.fecha_ingreso else "â€”"},
            {"label": "Tipo de contrato", "value": profesor.tipo_contrato},
            {"label": "Costo por hora", "value": f"${format_money(profesor.costo_por_hora or Decimal(0))}"},
            {"label": "Departamentos", "value": ", ".join(profesor.departamentos.values_list("nombre", flat=True)) or "â€”"},
            {"label": "Planteles", "value": ", ".join(profesor.planteles.values_list("nombre", flat=True)) or "â€”"},
        ],
    }
