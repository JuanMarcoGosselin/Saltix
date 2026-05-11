from datetime import timedelta
from decimal import Decimal

from django.utils import timezone

from Contabilidad.models import DetalleNomina, Nomina
from Contabilidad.utils import calcular_pago_base, get_horas_trabajadas, get_periodo_activo
from Profesores.utils import (
    get_attendance_stats,
    get_faltas,
    get_horario_display,
    get_incidencias,
    get_profesor_context,
    get_recibo_detalle,
)


def build_week_navigation(periodo, request):
    week_offset = int(request.GET.get("week_offset", 0))

    if not periodo:
        hoy = timezone.localdate()
        return {
            "week_offset": 0,
            "max_week_offset": 0,
            "min_week_offset": 0,
            "week_offset_prev": 0,
            "week_offset_next": 0,
            "semana_inicio": hoy,
            "semana_fin": hoy + timedelta(days=5),
        }

    base_week_start = periodo.fecha_inicio - timedelta(days=periodo.fecha_inicio.weekday())
    last_week_start = periodo.fecha_fin - timedelta(days=periodo.fecha_fin.weekday())
    max_week_offset = (last_week_start - base_week_start).days // 7
    min_week_offset = -1

    week_offset = max(min_week_offset, min(max_week_offset, week_offset))
    inicio_semana = base_week_start + timedelta(weeks=week_offset)

    return {
        "week_offset": week_offset,
        "max_week_offset": max_week_offset,
        "min_week_offset": min_week_offset,
        "week_offset_prev": max(min_week_offset, week_offset - 1),
        "week_offset_next": min(max_week_offset, week_offset + 1),
        "semana_inicio": inicio_semana,
        "semana_fin": inicio_semana + timedelta(days=5),
    }


def build_horario_colors(profesor, inicio_semana, fin_semana):
    return get_horario_display(
        profesor.id,
        inicio_semana=inicio_semana,
        fin_semana=fin_semana,
    )


def calculate_salary_kpis(profesor, periodo):
    ultima_nomina = (
        Nomina.objects
        .filter(profesor=profesor, estado="pagada")
        .order_by("-fecha_de_generacion")
        .first()
    )
    detalle_nomina = DetalleNomina.objects.filter(nomina=ultima_nomina) if ultima_nomina else []

    horas_trabajadas = Decimal(str(get_horas_trabajadas(profesor.id)))
    salario_bruto = calcular_pago_base(profesor.id)
    salario_neto = horas_trabajadas * profesor.costo_por_hora

    return {
        "salario_bruto": salario_bruto,
        "pagoxhora": f"${profesor.costo_por_hora:.2f}",
        "salario_neto": salario_neto,
        "proximo_pago_fecha": (
            (periodo.fecha_fin + timedelta(days=1)).strftime("%d/%m/%Y")
            if periodo else "N/A"
        ),
        "recibo_detalle": get_recibo_detalle(ultima_nomina, detalle_nomina),
    }


def calculate_hours_kpis(profesor):
    horas_trabajadas = get_horas_trabajadas(profesor.id)
    salario_bruto = calcular_pago_base(profesor.id)

    return {
        "horas_trabajadas": (
            f"{int(horas_trabajadas)} horas"
            if profesor.costo_por_hora > 0 else "N/A"
        ),
        "horas_esperadas": (
            f"{salario_bruto // profesor.costo_por_hora} horas"
            if profesor.costo_por_hora > 0 else "N/A"
        ),
    }


def calculate_period_stats(profesor):
    return get_attendance_stats(profesor.id)


def get_dashboard_context(profesor, request):
    hoy = timezone.localdate()
    periodo = get_periodo_activo()
    semana = build_week_navigation(periodo, request)
    attendance_stats = calculate_period_stats(profesor)

    context = {
        "fecha_actual": hoy,
        "nombrep": profesor.usuario.get_full_name(),
        "periodo_actual": periodo.display_label() if periodo else "Sin periodo activo",
        "attendance_stats": attendance_stats,
        "horario_display": build_horario_colors(
            profesor,
            semana["semana_inicio"],
            semana["semana_fin"],
        ),
        "faltas": get_faltas(
            profesor.id,
            inicio_semana=semana["semana_inicio"],
            fin_semana=semana["semana_fin"],
        ),
        "incidencias": get_incidencias(profesor.id),
        "perfil": get_profesor_context(profesor.id),
    }

    context.update(semana)
    context.update(calculate_salary_kpis(profesor, periodo))
    context.update(calculate_hours_kpis(profesor))
    return context
