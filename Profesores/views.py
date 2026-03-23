import json
from datetime import datetime as dt
from datetime import timedelta

from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Prefetch
from django.http import JsonResponse
from django.shortcuts import render
from django.template.loader import render_to_string
from django.utils import timezone
from django.views.decorators.http import require_POST

from Asistencias.models import Asistencia
from Asistencias.services import (
    current_payroll_period,
    obtener_color_estado,
    obtener_estado_clase,
    period_stats,
    unjustified_absences_navigation,
    unjustified_absences_queryset,
)
from core.decorators import requiere_rol

from .models import Horario, Profesor
from .utils import (
    dashboard_kpis,
    format_hours,
    format_money,
    obtener_horario_hoy,
    profesor_profile_context,
    verificar_entrada,
    verificar_salida,
)

@login_required
def dashboard(request):
    usuario = request.user
    profesor = Profesor.objects.select_related("usuario").get(usuario_id=usuario.id)
    diasp = ["LUN", "MAR", "MIE", "JUE", "VIE", "SAB"]

    hoy = timezone.localdate()

    try:
        week_offset = int(request.GET.get("week_offset", 0) or 0)
    except (TypeError, ValueError):
        week_offset = 0

    nav = unjustified_absences_navigation(hoy=hoy)
    max_week_offset = int(nav["max_week_offset"] or 0)
    max_offset_actual = int(nav["max_offset_actual"] or 0)
    prev_offset = nav.get("prev_offset", None)
    prev_offset = int(prev_offset) if prev_offset is not None else None

    week_offset = max(0, min(week_offset, max_week_offset))
    if prev_offset is not None and week_offset > max_offset_actual and week_offset != prev_offset:
        week_offset = prev_offset

    def week_prev(off: int) -> int:
        if prev_offset is not None and off == max_offset_actual:
            return prev_offset
        return min(max_week_offset, off + 1)

    def week_next(off: int) -> int:
        if prev_offset is not None and off == prev_offset:
            return max_offset_actual
        return max(0, off - 1)

    week_offset_prev = week_prev(week_offset)
    week_offset_next = week_next(week_offset)

    periodo_actual = current_payroll_period(hoy=hoy)

    faltas_qs, faltas_rango_semana, faltas_rango_periodo, faltas_rango_efectivo = unjustified_absences_queryset(
        profesor=profesor,
        hoy=hoy,
        week_offset=week_offset,
    )

    inicio_semana = faltas_rango_semana.inicio
    fin_semana = faltas_rango_semana.fin

    asistenciap = Asistencia.objects.filter(profesor=profesor, fecha__range=(inicio_semana, fin_semana))

    clasep = (
        Horario.objects.filter(profesor_id=profesor.id, activo=True).order_by("dia_semana", "hora_inicio")
        .prefetch_related(Prefetch("asistencia_set", queryset=asistenciap, to_attr="_asistencias_semana"))
    )

    horario_color = {}
    horario_estado = {}

    dias_map = {"LUN": 0, "MAR": 1, "MIE": 2, "JUE": 3, "VIE": 4, "SAB": 5}
    for clase in clasep:
        dia_clase = dias_map.get(clase.dia_semana)
        if dia_clase is None:
            continue
        fecha_clase = inicio_semana + timedelta(days=dia_clase)
        estado = obtener_estado_clase(profesor, clase, fecha_clase)
        horario_color[clase.id] = obtener_color_estado(estado)
        horario_estado[clase.id] = estado

    stats = period_stats(profesor=profesor, hoy=hoy)
    kpis = dashboard_kpis(profesor=profesor, hoy=hoy, rango_periodo=periodo_actual)
    horarios_clase = kpis["horarios_clase"]
    minutos_trabajados_periodo = kpis["minutos_trabajados_periodo"]
    minutos_esperados_periodo = kpis["minutos_esperados_periodo"]
    mes_inicio = kpis["mes_inicio"]
    mes_fin = kpis["mes_fin"]
    salario_bruto_real_periodo = kpis["salario_bruto_real_periodo"]

    faltas_paginator = Paginator(faltas_qs, 12)
    faltas_page = faltas_paginator.get_page(request.GET.get("page"))

    if request.GET.get("partial") == "faltas":
        is_current_week = inicio_semana <= hoy <= fin_semana and hoy.weekday() < 6
        partial_ctx = {
            "faltas_page": faltas_page,
            "horaclasep": range(5, 24),
            "diasp": diasp,
            "diaactualp": diasp[hoy.weekday()] if hoy.weekday() < 6 else "",
            "horaactualp": timezone.localtime(timezone.now()),
            "is_current_week": is_current_week,
            "clasep": clasep,
            "horario_color": horario_color,
            "horario_estado": horario_estado,
        }
        rows_html = render_to_string("Profesores/partials/faltas_rows.html", partial_ctx, request=request)
        horario_html = render_to_string("Profesores/partials/horario_semana.html", partial_ctx, request=request)
        return JsonResponse(
            {
                "rows_html": rows_html,
                "horario_html": horario_html,
                "stats": stats,
                "count_total": faltas_page.paginator.count,
                "page_number": faltas_page.number,
                "num_pages": faltas_page.paginator.num_pages,
                "has_previous": faltas_page.has_previous(),
                "has_next": faltas_page.has_next(),
                "week_offset": week_offset,
                "week_offset_prev": week_offset_prev,
                "week_offset_next": week_offset_next,
                "max_week_offset": max_week_offset,
                "semana_inicio": faltas_rango_semana.inicio.strftime("%d/%m/%Y"),
                "semana_fin": faltas_rango_semana.fin.strftime("%d/%m/%Y"),
                "periodo_inicio": faltas_rango_periodo.inicio.strftime("%d/%m/%Y"),
                "periodo_fin": faltas_rango_periodo.fin.strftime("%d/%m/%Y"),
            }
        )

    context = {
        "fecha_actual": hoy.strftime("%d/%m/%Y"),
        "nombrep": profesor.usuario.nombre,
        "apellidop": profesor.usuario.apellido,
        "salariop": format_money(salario_bruto_real_periodo),
        "salariomensualp": format_money(salario_bruto_real_periodo),
        "salarionetop": f"${format_money(salario_bruto_real_periodo)}",
        "salario_trend_label": f"${format_money(profesor.costo_por_hora)}/h",
        "horasesperadasp": format_hours(minutos_esperados_periodo),
        "horasp": format_hours(minutos_trabajados_periodo),
        "horas_trend_label": f"Periodo {periodo_actual.inicio.strftime('%d/%m')}–{periodo_actual.fin.strftime('%d/%m')}",
        "proximo_pago_fecha": periodo_actual.fin.strftime("%d/%m/%Y"),
        "resumen_mes_label": f"Periodo: {periodo_actual.inicio.strftime('%d/%m/%Y')} – {periodo_actual.fin.strftime('%d/%m/%Y')}",
        "recibo_periodo_label": f"{mes_inicio.strftime('%d/%m/%Y')} – {mes_fin.strftime('%d/%m/%Y')}",
        "recibo_detalle": [],
        "recibos": [],
        "horaclasep": range(5, 24),
        "horaactualp": timezone.localtime(timezone.now()),
        "diasp": diasp,
        "diaactualp": diasp[hoy.weekday()] if hoy.weekday() < 6 else "",
        "is_current_week": inicio_semana <= hoy <= fin_semana and hoy.weekday() < 6,
        "clasep": clasep,
        "asistenciap": asistenciap,
        "horario_color": horario_color,
        "horario_estado": horario_estado,
        "week_offset": week_offset,
        "max_week_offset": max_week_offset,
        "week_offset_prev": week_offset_prev,
        "week_offset_next": week_offset_next,
        "faltas_page": faltas_page,
        "faltas_semana_inicio": faltas_rango_semana.inicio,
        "faltas_semana_fin": faltas_rango_semana.fin,
        "faltas_periodo_inicio": faltas_rango_periodo.inicio,
        "faltas_periodo_fin": faltas_rango_periodo.fin,
        "faltas_rango_efectivo": faltas_rango_efectivo,
        "stat_asistencias": stats.get("asistencias", 0),
        "stat_retardos": stats.get("retardos", 0),
        "stat_faltas": stats.get("faltas", 0),
        "stat_justificadas": stats.get("justificadas", 0),
        **profesor_profile_context(profesor=profesor, hoy=hoy, horarios_clase=horarios_clase),
    }

    return render(request, "Profesores/dashboard.html", context)

@login_required
@requiere_rol("Profesor")
def registro_asistencia(request):
    profesor = Profesor.objects.select_related("usuario").get(usuario_id=request.user.id)
    hoy = timezone.localdate()

    horarios_hoy = obtener_horario_hoy(profesor).order_by("hora_inicio")

    asistencias_hoy = {
        a.horario_id: a
        for a in Asistencia.objects.filter(profesor=profesor, fecha=hoy, horario__in=horarios_hoy)
    }

    for horario in horarios_hoy:
        asistencia = asistencias_hoy.get(horario.id)
        horario.ya_registrada = asistencia is not None
        horario.salida = asistencia.hora_salida if asistencia else None
        horario.asistencia_id = asistencia.id if asistencia else None

    context = {
        "profesor_nombre": f"{profesor.usuario.nombre} {profesor.usuario.apellido}".strip(),
        "profesor_iniciales": f"{(profesor.usuario.nombre or 'U')[:1]}{(profesor.usuario.apellido or '')[:1]}".upper(),
        "profesor_rol": "Profesor",
        "horarios_hoy": horarios_hoy,
        "fecha_hoy": hoy,
    }
    return render(request, "Profesores/registro_asistencia.html", context)


@require_POST
@requiere_rol("Profesor")
def asistencia_accion(request):
    try:
        body = json.loads(request.body)
        horario_id = body.get("horario_id")

        if not horario_id:
            return JsonResponse({'error': 'Horario no proporcionado'}, status=400)

        profesor = Profesor.objects.get(usuario_id=request.user.id)
        hoy = timezone.localdate()

        asistencia = Asistencia.objects.filter(
            profesor=profesor,
            horario_id=horario_id,
            fecha=hoy
        ).first()

        if not asistencia:
            if not verificar_entrada(horario_id):
                return JsonResponse({
                    'error': 'Fuera del horario permitido para registrar entrada'
                }, status=400)

            ahora = timezone.now()
            horario = Horario.objects.get(id=horario_id)
            tz = timezone.get_current_timezone()

            inicio = timezone.make_aware(dt.combine(hoy, horario.hora_inicio), tz)
            if ahora > inicio:
                estado = "RETARDO"
                tolerancia_minutos = int((ahora - inicio).total_seconds() // 60)
            else:
                estado = "ASISTENCIA"
                tolerancia_minutos = 0

            asistencia = Asistencia.objects.create(
                profesor=profesor,
                horario_id=horario_id,
                fecha=hoy,
                hora_entrada=ahora.time(),
                estado=estado,
                tolerancia_minutos=tolerancia_minutos,
                creado_por=request.user,
            )

            return JsonResponse({
                'tipo': 'entrada',
                'estado': estado,
                'message': 'Asistencia registrada correctamente',
                'asistencia_id': asistencia.id,
            })

        if not asistencia.hora_salida:
            if not verificar_salida(horario_id):
                return JsonResponse({
                    'error': 'Fuera del horario permitido para registrar salida'
                }, status=400)

            asistencia.hora_salida = timezone.now().time()
            asistencia.save(update_fields=["hora_salida"])

            return JsonResponse({
                'tipo': 'salida',
                'message': 'Salida registrada correctamente'
            })

        return JsonResponse({
            'error': 'Ya registraste entrada y salida para este horario'
        }, status=400)

    except Exception as e:
        return JsonResponse({
            'error': str(e)
        }, status=500)
