from time import timezone

from Asistencias.models import Asistencia
from Profesores.models import Profesor
from Contabilidad.models import Periodo, Nomina

def get_all_periodos():
    return Periodo.objects.all().order_by("-fecha_inicio")

def create_periodo(fecha_inicio, fecha_fin):
    if Periodo.objects.filter(activo=True).exists():
        raise Exception("Ya existe un periodo activo. Desactívalo antes de crear uno nuevo.")
    
    periodo = Periodo(fecha_inicio=fecha_inicio, fecha_fin=fecha_fin, activo=True)
    periodo.save()
    return periodo

def deactivate_periodo():
    periodo_id = get_active_periodo().id

    # Checar que no falte generar nominas para el periodo antes de desactivarlo
    profesores = get_all_active_profesores()
    nominas = Nomina.objects.filter(profesor__in=profesores, periodo_id=periodo_id)

    if nominas.count() < profesores.count():
        raise Exception("No se han generado todas las nóminas para este periodo. " \
        "Genera las nóminas restantes antes de desactivar el periodo.")

    try:
        periodo = Periodo.objects.get(id=periodo_id)
        periodo.activo = False
        periodo.fecha_fin = timezone.now()
        periodo.save()
    except Periodo.DoesNotExist:
        raise Exception("El periodo no existe.")

def get_active_periodo():
    try:
        return Periodo.objects.get(activo=True)
    except Periodo.DoesNotExist:
        return None

def get_all_active_profesores():
    return Profesor.objects.filter(activo=True)

def get_all_asistencia(profesor_id):
    try:
        periodo_actual = get_active_periodo()
        profesor = Profesor.objects.get(id=profesor_id)
        asistencia = Asistencia.objects.filter(
            profesor=profesor, 
            fecha__range=(periodo_actual.fecha_inicio, periodo_actual.fecha_fin)
        )
        return asistencia
    except Profesor.DoesNotExist:
        return None

