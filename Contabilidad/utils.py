from django.utils import timezone
from Asistencias.models import Asistencia
from Profesores.models import Profesor
from Contabilidad.models import Periodo, Nomina

def get_all_periodos():
    return Periodo.objects.all().order_by("-fecha_inicio")

def create_periodo(fecha_inicio, fecha_fin):
    if get_active_periodo() is not None:
        raise Exception("Ya existe un periodo abierto. Ciérralo antes de crear uno nuevo.")

    periodo = Periodo(fecha_inicio=fecha_inicio, fecha_fin=fecha_fin)
    periodo.save()
    return periodo

def deactivate_periodo():
    periodo = get_active_periodo()
    if periodo is None:
        raise Exception("No hay un periodo abierto para desactivar.")
    

    # Checar que no falte generar nominas para el periodo antes de desactivarlo
    profesores = get_all_active_profesores()
    nominas = Nomina.objects.filter(profesor__in=profesores, periodo=periodo)

    if nominas.count() < profesores.count():
        raise Exception(
            "No se han generado todas las nóminas para este periodo. "
            "Genera las nóminas restantes antes de desactivar el periodo."
        )

    periodo.estado = "CERRADO"
    periodo.fecha_fin = timezone.now().date()
    periodo.save()

    return periodo


def get_active_periodo():
    try:
        return Periodo.objects.get(estado="ABIERTO")
    except Periodo.DoesNotExist:
        return None

def get_all_active_profesores():
    return Profesor.objects.filter(estado_laboral="ACTIVO")

def get_all_asistencia(profesor_id):
    periodo_actual = get_active_periodo()
    if periodo_actual is None:
        return None
    
    try:
        profesor = Profesor.objects.get(id=profesor_id)
        return Asistencia.objects.filter(
            profesor=profesor, 
            fecha__range=(periodo_actual.fecha_inicio, periodo_actual.fecha_fin)
        )
    
    except Profesor.DoesNotExist:
        return None

