from datetime import datetime as dt
from datetime import timedelta
import json

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render
from django.template.loader import render_to_string
from django.utils import timezone
from django.views.decorators.http import require_POST

from Asistencias.models import Asistencia, Incidencia
from Contabilidad.models import DetalleNomina, Nomina
from Contabilidad.utils import *
from core.decorators import requiere_rol

from .models import Horario, Profesor
from .utils import *


@login_required
def dashboard(request):
    usuario = request.user

    profesor = (
        Profesor.objects
        .select_related("usuario")
        .get(usuario_id=usuario.id)
    )

    ultima_nomina = (
        Nomina.objects
        .filter(profesor=profesor, estado='pagada')
        .order_by('-fecha_de_generacion')
        .first()
    )

    detalle_nomina = (
        DetalleNomina.objects.filter(nomina=ultima_nomina)
        if ultima_nomina else []
    )

    recibo_detalle = get_recibo_detalle(ultima_nomina, detalle_nomina)

    hoy = timezone.localdate()
    periodo = get_periodo_activo()

    salario_bruto = calcular_pago_base(profesor.id)

    horas_trabajadas = get_horas_trabajadas(profesor.id)
    salario_neto = Decimal(str(horas_trabajadas)) * profesor.costo_por_hora

    week_offset = int(request.GET.get("week_offset", 0))
    base_week_start = (
        periodo.fecha_inicio
        - timedelta(days=periodo.fecha_inicio.weekday())
    )

    last_week_start = (
        periodo.fecha_fin
        - timedelta(days=periodo.fecha_fin.weekday())
    )

    max_week_offset = (
        (last_week_start - base_week_start).days // 7
    )

    min_week_offset = -1

    week_offset = max(
        min_week_offset,
        min(max_week_offset, week_offset)
    )

    inicio_semana = (
        base_week_start
        + timedelta(weeks=week_offset)
    )
    fin_semana = inicio_semana + timedelta(days=5)

    attendance_stats = get_attendance_stats(profesor.id)

    horario_display = get_horario_display(
        profesor.id,
        inicio_semana=inicio_semana,
        fin_semana=fin_semana,
    )

    perfil_contexto = get_profesor_context(profesor.id)

    context = {
        "fecha_actual": hoy,
        "nombrep": profesor.usuario.get_full_name(),

        # Periodo
        "periodo_actual": (
            periodo.display_label()
            if periodo else "Sin periodo activo"
        ),

        # Nómina
        "salario_bruto": salario_bruto,
        "pagoxhora": f"${profesor.costo_por_hora:.2f}",
        "salario_neto": salario_neto,

        "horas_trabajadas": (
            f"{int(horas_trabajadas)} horas"
            if profesor.costo_por_hora > 0 else "N/A"
        ),

        "horas_esperadas": (
            f"{salario_bruto // profesor.costo_por_hora} horas"
            if profesor.costo_por_hora > 0 else "N/A"
        ),

        "proximo_pago_fecha": (
            (periodo.fecha_fin + timedelta(days=1)).strftime("%d/%m/%Y")
            if periodo else "N/A"
        ),

        # Semana actual
        "week_offset": week_offset,
        "max_week_offset": max_week_offset,
        "min_week_offset": min_week_offset,

        "week_offset_prev": max(
            min_week_offset,
            week_offset - 1
        ),

        "week_offset_next": min(
            max_week_offset,
            week_offset + 1
        ),

        "semana_inicio": inicio_semana,
        "semana_fin": fin_semana,

        # Asistencias
        "attendance_stats": attendance_stats,

        "horario_display": horario_display,

        "faltas": get_faltas(
            profesor.id,
            inicio_semana=inicio_semana,
            fin_semana=fin_semana,
        ),

        "incidencias": get_incidencias(profesor.id),

        # Perfil
        "perfil": perfil_contexto,

        # Recibo
        "recibo_detalle": recibo_detalle,
    }

    if request.GET.get("partial") == "faltas":

        rows_html = render_to_string(
            "Profesores/partials/faltas_rows.html",
            context,
            request=request,
        )

        horario_html = render_to_string(
            "Profesores/partials/horario_semana.html",
            context,
            request=request,
        )

        return JsonResponse({
            "rows_html": rows_html,
            "horario_html": horario_html,

            "stats": {
                "asistencias": attendance_stats["total_asistencias"],
                "retardos": attendance_stats["total_retardos"],
                "faltas": attendance_stats["total_faltas"],
                "justificadas": attendance_stats["total_justificadas"],
            },

            "week_offset": week_offset,
            "week_offset_prev": max(min_week_offset, week_offset - 1),

            "week_offset_next": min(max_week_offset, week_offset + 1),
            "max_week_offset": max_week_offset,

            "semana_inicio": inicio_semana.strftime("%d/%m/%Y"),
            "semana_fin": fin_semana.strftime("%d/%m/%Y"),

            "periodo_inicio": periodo.fecha_inicio.strftime("%d/%m/%Y"),
            "periodo_fin": periodo.fecha_fin.strftime("%d/%m/%Y"),
        })

    return render(request, "Profesores/dashboard.html", context)

@login_required
@requiere_rol("Profesor")
def registro_asistencia(request):
    profesor = Profesor.objects.select_related("usuario").get(
        usuario_id=request.user.id
    )

    hoy = timezone.localdate()

    horarios_hoy = obtener_horario_hoy(profesor).order_by("hora_inicio")

    asistencias_hoy = {
        a.horario_id: a
        for a in Asistencia.objects.filter(
            profesor=profesor,
            fecha=hoy,
            horario__in=horarios_hoy,
        )
    }

    for horario in horarios_hoy:
        asistencia = asistencias_hoy.get(horario.id)

        horario.ya_registrada = asistencia is not None
        horario.salida = asistencia.hora_salida if asistencia else None
        horario.asistencia_id = asistencia.id if asistencia else None

    context = {
        "profesor_nombre": (
            f"{profesor.usuario.nombre} "
            f"{profesor.usuario.apellido}"
        ).strip(),

        "profesor_iniciales": (
            f"{(profesor.usuario.nombre or 'U')[:1]}"
            f"{(profesor.usuario.apellido or '')[:1]}"
        ).upper(),

        "profesor_rol": "Profesor",
        "horarios_hoy": horarios_hoy,
        "fecha_hoy": hoy,
    }

    return render(
        request,
        "Profesores/registro_asistencia.html",
        context,
    )


@require_POST
@requiere_rol("Profesor")
def asistencia_accion(request):
    try:
        body = json.loads(request.body)

        horario_id = body.get("horario_id")

        if not horario_id:
            return JsonResponse({
                'error': 'Horario no proporcionado'
            }, status=400)

        profesor = Profesor.objects.get(usuario_id=request.user.id)

        hoy = timezone.localdate()

        asistencia = Asistencia.objects.filter(
            profesor=profesor,
            horario_id=horario_id,
            fecha=hoy,
        ).first()

        if not asistencia:

            if not verificar_entrada(horario_id):
                return JsonResponse({
                    'error': 'Fuera del horario permitido para registrar entrada'
                }, status=400)

            ahora = timezone.now()

            horario = Horario.objects.get(id=horario_id)

            tz = timezone.get_current_timezone()

            inicio = timezone.make_aware(
                dt.combine(hoy, horario.hora_inicio),
                tz,
            )

            if ahora > inicio:
                estado = "RETARDO"

                tolerancia_minutos = int(
                    (ahora - inicio).total_seconds() // 60
                )
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
                'message': 'Salida registrada correctamente',
            })

        return JsonResponse({
            'error': 'Ya registraste entrada y salida para este horario'
        }, status=400)

    except Exception as e:
        return JsonResponse({
            'error': str(e)
        }, status=500)