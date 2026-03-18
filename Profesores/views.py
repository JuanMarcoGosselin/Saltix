from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.utils import timezone
from datetime import datetime, timedelta

from Asistencias.models import Asistencia
from .models import Horario, Profesor 
from .utils import obtener_horario_hoy

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
        "horaclasep": range(5, 24),  # 5:00 a 23:00
        "diasp": ['LUN', 'MAR', 'MIE', 'JUE', 'VIE', 'SAB'],
        "clasep": clasep,       
        "asistenciap": Asistencia.objects.filter(profesor=profesor.id)
    , 
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
    for horario in horarios_hoy:
        horario.ya_registrada = horario.id in asistencias_hoy_ids

    context = {
        "profesor_nombre": f"{profesor.usuario.nombre} {profesor.usuario.apellido}".strip(),
        "profesor_iniciales": f"{(profesor.usuario.nombre or 'U')[:1]}{(profesor.usuario.apellido or '')[:1]}".upper(),
        "profesor_rol": "Profesor",
        "horarios_hoy": horarios_hoy,
        "fecha_hoy": hoy,
    }
    return render(request, "Profesores/registro_asistencia.html", context)

