from datetime import datetime as dt
import json

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render
from django.template.loader import render_to_string
from django.utils import timezone
from django.views.decorators.http import require_POST

from Asistencias.models import Asistencia
from core.decorators import requiere_rol
from Notifications.utils import notify_user
from Profesores.services.dashboard import get_dashboard_context

from .models import Profesor
from .utils import *


@login_required
@requiere_rol("Profesor")
def dashboard(request):
    profesor = (
        Profesor.objects
        .select_related("usuario")
        .get(usuario_id=request.user.id)
    )

    context = get_dashboard_context(
        profesor=profesor,
        request=request,
    )

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

        stats = context["attendance_stats"]

        return JsonResponse({
            "rows_html": rows_html,
            "horario_html": horario_html,
            "stats": {
                "asistencias": stats["total_asistencias"],
                "retardos": stats["total_retardos"],
                "faltas": stats["total_faltas"],
                "justificadas": stats["total_justificadas"],
            },
            "week_offset": context["week_offset"],
            "week_offset_prev": context["week_offset_prev"],
            "week_offset_next": context["week_offset_next"],
            "max_week_offset": context["max_week_offset"],
            "semana_inicio": context["semana_inicio"].strftime("%d/%m/%Y"),
            "semana_fin": context["semana_fin"].strftime("%d/%m/%Y"),
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
@login_required
@requiere_rol("Profesor")
def asistencia_accion(request):
    try:
        body = json.loads(request.body)
        horario_id = body.get("horario_id")

        if not horario_id:
            return JsonResponse({
                "error": "Horario no proporcionado"
            }, status=400)

        profesor = Profesor.objects.get(usuario_id=request.user.id)
        hoy = timezone.localdate()
        horario = obtener_horario_hoy(profesor).filter(id=horario_id).first()
        if not horario:
            return JsonResponse({
                "error": "Horario no disponible para este profesor"
            }, status=403)

        asistencia = Asistencia.objects.filter(
            profesor=profesor,
            horario_id=horario_id,
            fecha=hoy,
        ).first()

        if not asistencia:
            if not verificar_entrada(horario_id):
                return JsonResponse({
                    "error": "Fuera del horario permitido para registrar entrada"
                }, status=400)

            ahora = timezone.now()
            tz = timezone.get_current_timezone()
            inicio = timezone.make_aware(
                dt.combine(hoy, horario.hora_inicio),
                tz,
            )

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
            notify_user(
                request.user,
                "Asistencia registrada",
                f"Se registro tu entrada como {estado.lower()} para el {hoy:%d/%m/%Y}.",
                "warning" if estado == "RETARDO" else "success",
                "/profesores/?page=asistencias",
            )

            return JsonResponse({
                "tipo": "entrada",
                "estado": estado,
                "message": "Asistencia registrada correctamente",
                "asistencia_id": asistencia.id,
            })

        if not asistencia.hora_salida:
            if not verificar_salida(horario_id):
                return JsonResponse({
                    "error": "Fuera del horario permitido para registrar salida"
                }, status=400)

            asistencia.hora_salida = timezone.now().time()
            asistencia.save(update_fields=["hora_salida"])

            return JsonResponse({
                "tipo": "salida",
                "message": "Salida registrada correctamente",
            })

        return JsonResponse({
            "error": "Ya registraste entrada y salida para este horario"
        }, status=400)

    except Exception as e:
        return JsonResponse({
            "error": str(e)
        }, status=500)
