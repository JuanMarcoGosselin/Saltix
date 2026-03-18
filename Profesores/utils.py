from .models import Profesor, Horario
from datetime import datetime, timedelta
from Asistencias.models import Asistencia
from django.utils import timezone

"""
Obtener el Horario del profesor
el horario de el día de hoy
Verificar que la asistencia corresponde al dia y hora actual
Logica de Tolerancia (30min antes de inicio, 10min despues de incio, 10min antes de acabar, 30min despues de acabar)
Verificar que no exista una asistencia ya registrada para esa clase
Calcular 
"""
def obtener_horario_hoy(profesor):
    dias = {
        0 : "LUN",
        1 : "MAR", 
        2 : "MIE",
        3 : "JUE", 
        4 : "VIE", 
        5 : "SAB"
    }

    hoy = timezone.localdate()
    dia = dias.get(hoy.weekday())
    if not dia:
        return Horario.objects.none()
    return Horario.objects.filter(profesor=profesor, dia_semana=dia)


def obtener_horario(profesor): 
    dias = {
        0 : "LUN",
        1 : "MAR", 
        2 : "MIE",
        3 : "JUE", 
        4 : "VIE", 
        5 : "SAB"
    }
    horario = {}
    horas_totales = 0
    for dia in dias:
        horario[dia] = Horario.objects.filter(profesor=profesor, dia_semana=dias[dia])
        for clase in horario[dia]: 
           horas_totales += (clase.hora_fin.hour - clase.hora_inicio.hour)
    return (horario, horas_totales)


def verificar_asistencia(profesor):
    horario_hoy = obtener_horario_hoy(profesor)
    ahora = datetime.now().time()

    for clase in horario_hoy: 
        if clase.hora_inicio - timedelta(minutes=15) <= ahora <= clase.hora_fin + timedelta(minutes=30): 
            asistencia = Asistencia.objects.filter(profesor=profesor, fecha=datetime.now().date(), horario=clase)
            if asistencia.exists(): 
                return "Ya has registrado tu asistencia para esta clase."
            else: 
                return "Puedes registrar tu asistencia para esta clase."
