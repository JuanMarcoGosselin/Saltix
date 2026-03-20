import json
from datetime import timedelta

from django.contrib.auth.decorators import login_required
from django.db.models import Prefetch
from django.http import JsonResponse
from django.shortcuts import render
from django.utils import timezone
from django.views.decorators.http import require_POST

from Asistencias.models import Asistencia
from Asistencias.services import obtener_color_estado, obtener_estado_clase
from core.decorators import requiere_rol

from .models import Horario, Profesor
from .utils import obtener_horario_hoy, verificar_entrada

def dashboard(request):
    usuario = request.user
    profesor = Profesor.objects.select_related("usuario").get(usuario=usuario.id)
    diasp = ['LUN', 'MAR', 'MIE', 'JUE', 'VIE', 'SAB']

    # Calcular inicio y fin de la semana actual (Lun - Sab)
    hoy = timezone.localdate()
    inicio_semana = hoy - timedelta(days=hoy.weekday())      # Lunes
    fin_semana = inicio_semana + timedelta(days=5)            # Sábado

    asistenciap = Asistencia.objects.filter(profesor=profesor, fecha__range=(inicio_semana, fin_semana))

    clasep = (
        Horario.objects.filter(profesor=profesor)
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

    context = {
        "nombrep": profesor.usuario.nombre,
        "apellidop": profesor.usuario.apellido,
        "salariop": profesor.costo_por_hora,
        "salariomensualp": profesor.costo_por_hora,
        "salarionetop": profesor.costo_por_hora,
        "horasesperadasp": 1,
        "horasp": 2,
        "horaclasep": range(5, 24),
        "horaactualp": timezone.localtime(timezone.now()),
        "diasp": diasp,
        "diaactualp": diasp[hoy.weekday()],
        "clasep": clasep,
        "asistenciap": asistenciap,
        "horario_color": horario_color,
        "horario_estado": horario_estado,
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
        
        if not verificar_entrada(horario_id): 
             return JsonResponse({
            'error': 'Hora de entrada/salida invalido'
        }, status=400)

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
