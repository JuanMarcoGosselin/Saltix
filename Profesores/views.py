from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.utils import timezone
from datetime import datetime, timedelta

from Asistencias.models import Asistencia
from .models import Horario, Profesor 
from .utils import obtener_horario_hoy

from django.http import JsonResponse
from django.views.decorators.http import require_POST
import json
from core.decorators import requiere_rol, requiere_permiso


def dashboard(request):
    usuario = request.user
    profesor = Profesor.objects.get(usuario=usuario.id)
    clasep = Horario.objects.filter(profesor=profesor.id)
    context = {
        "nombrep": profesor.usuario.nombre,
        "apellidop": profesor.usuario.apellido,
        "salariop": profesor.costo_por_hora,
        "salariomensualp": profesor.costo_por_hora,
        "salarionetop": profesor.costo_por_hora,
        "horasesperadasp": 1,
        "horasp": 2,
        "horaclasep": range(5, 24), # 5:00 a 23:00
        "diasp": ['LUN', 'MAR', 'MIE', 'JUE', 'VIE', 'SAB'],
        "clasep": clasep,
        "asistenciap": Asistencia.objects.filter(profesor=profesor.id)
    }

    return render(request, "Profesores/dashboard.html", context)

@login_required
def registro_asistencia(request):
    profesor = Profesor.objects.select_related("usuario").get(usuario=request.user.id)
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

        profesor = Profesor.objects.get(usuario=request.user.id)
        hoy = timezone.localdate()

        asistencia = Asistencia.objects.filter(
            profesor=profesor,
            horario_id=horario_id,
            fecha=hoy
        ).first()

        if not asistencia:
            asistencia = Asistencia.objects.create(
                profesor=profesor,
                horario_id=horario_id,
                fecha=hoy,
                hora_entrada=timezone.now().time(),
                estado="ASISTENCIA",
                creado_por=request.user
            )

            return JsonResponse({
                'tipo': 'entrada',
                'message': 'Asistencia registrada correctamente',
                'asistencia_id': asistencia.id
            })

        if asistencia and not asistencia.hora_salida:
            asistencia.hora_salida = timezone.now().time()
            asistencia.save()

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