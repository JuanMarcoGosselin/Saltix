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
from django.http import JsonResponse
from datetime import datetime

from django.utils import timezone
from datetime import datetime, timedelta

def dashboard(request):
    usuario = request.user
    profesor = Profesor.objects.get(usuario=usuario.id)
    clasep = Horario.objects.filter(profesor=profesor.id)
    diasp = ['LUN', 'MAR', 'MIE', 'JUE', 'VIE', 'SAB']

    # Calcular inicio y fin de la semana actual (Lun - Sab)
    hoy = timezone.localtime(timezone.now()).date()
    inicio_semana = hoy - timedelta(days=hoy.weekday())      # Lunes
    fin_semana = inicio_semana + timedelta(days=5)            # Sábado

    asistenciap = Asistencia.objects.filter(
        profesor=profesor.id,
        fecha__gte=inicio_semana,
        fecha__lte=fin_semana,
    )

    horario_color = {}

    # Default pendiente para todas las clases
    for clase in clasep:
        horario_color[clase.id] = "pendiente"

    hoy = timezone.localtime(timezone.now())

    for clase in clasep:
        # Calcular la fecha real de esa clase en la semana actual
        dias_map = {'LUN': 0, 'MAR': 1, 'MIE': 2, 'JUE': 3, 'VIE': 4, 'SAB': 5}
        dia_clase = dias_map.get(clase.dia_semana, -1)
        if dia_clase == -1:
            continue

        fecha_clase = inicio_semana + timedelta(days=dia_clase)

        # Si la clase aún no ha sucedido, se queda pendiente
        if fecha_clase > hoy.date():
            horario_color[clase.id] = "pendiente"
            continue

        # Si ya pasó pero no tiene registro, es falta
        if fecha_clase < hoy.date():
            registro = asistenciap.filter(horario=clase, fecha=fecha_clase).first()
            horario_color[clase.id] = registro.color_clase if registro else "falta"
            continue

        # Si es hoy, verificar si ya pasó la hora
        if fecha_clase == hoy.date():
            if clase.hora_inicio <= hoy.time():
                registro = asistenciap.filter(horario=clase, fecha=fecha_clase).first()
                horario_color[clase.id] = registro.color_clase if registro else "falta"
            else:
                horario_color[clase.id] = "pendiente"

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
        "diaactualp": diasp[datetime.today().weekday()],
        "clasep": clasep,
        "asistenciap": asistenciap,
        "horario_color": horario_color,
    }

    return render(request, "Profesores/dashboard.html", context)

@login_required
def registro_asistencia(request):
    profesor = Profesor.objects.select_related("usuario").get(usuario=request.user.id)
    hoy = timezone.localdate()

    horarios_hoy = obtener_horario_hoy(profesor).order_by("hora_inicio")
    asistencias_hoy_ids = set(
        Asistencia.objects.filter(profesor=profesor, fecha=hoy, horario__in=horarios_hoy).values_list(
            "horario_id", flat=True
        )
    )

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
        "profesor_id": profesor.id,
        "profesor_nombre": f"{profesor.usuario.nombre} {profesor.usuario.apellido}".strip(),
        "profesor_iniciales": f"{(profesor.usuario.nombre or 'U')[:1]}{(profesor.usuario.apellido or '')[:1]}".upper(),
        "profesor_rol": "Profesor",
        "horarios_hoy": horarios_hoy,
        "fecha_hoy": hoy,
    }
    return render(request, "Profesores/registro_asistencia.html", context)


@requiere_rol("Profesor")
def registrar_asistencia(request):
    try:
        profesor_id = request.POST.get("profesor_id")
        horario_id = request.POST.get("horario_id")
        if not horario_id:
            return JsonResponse({'error': 'ID de horario no proporcionado'}, status=400)
        
        asistencia = Asistencia.objects.create(
            profesor_id=profesor_id,
            horario_id=horario_id,
            fecha=timezone.localdate(),
            hora_entrada=timezone.now().time(),
            estado="ASISTENCIA",
            creado_por=request.user
        )

        return JsonResponse({
            'success': f'Asistencia registrada para horario {horario_id}',
            'asistencia_id': asistencia.id
        })
    except json.JSONDecodeError:
        return JsonResponse({'error': 'JSON inválido'}, status=400)

@requiere_rol("Profesor") 
def registrar_salida(request):
    try:
        asistencia_id = request.POST.get("asistencia_id")
        asistencia = Asistencia.objects.get(id=asistencia_id, profesor__usuario=request.user)
        asistencia.hora_salida = timezone.now().time()
        asistencia.save()
        
        return JsonResponse({'success': f'Salida registrada para horario {asistencia_id}'})
    except json.JSONDecodeError:
        return JsonResponse({'error': 'JSON inválido'}, status=400)