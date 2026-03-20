from .models import Profesor, Horario
from datetime import datetime, timedelta
from Asistencias.models import Asistencia
from django.utils import timezone

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
