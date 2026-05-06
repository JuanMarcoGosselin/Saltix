from django.utils import timezone
from Asistencias.models import Asistencia
from Profesores.models import Profesor
from Contabilidad.models import Periodo, Nomina
from decimal import Decimal

def get_all_periodos():
    return Periodo.objects.all().order_by("-fecha_inicio")

def get_last_periodo():
    return Periodo.objects.all().order_by("-fecha_inicio").first()

def create_periodo(fecha_inicio, fecha_fin):
    if get_active_periodo() is not None:
        raise Exception("Ya existe un periodo abierto. Ciérralo antes de crear uno nuevo.")

    periodo = Periodo(fecha_inicio=fecha_inicio, fecha_fin=fecha_fin)
    periodo.save()
    return periodo

def deactivate_periodo(id):
    try:
        periodo = Periodo.objects.get(id=id, estado="ABIERTO")
    except Periodo.DoesNotExist:
        raise Exception("No se encontro un periodo abierto para cerrar.")
    
    if periodo.fecha_fin > timezone.now().date():
        raise Exception("No se puede cerrar un periodo antes de su fecha de fin.")
    
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

def calculate_class_hours(clase):
    # Calcula la duración en horas de una clase dada su hora de inicio y fin.
    hora_inicio = clase.hora_entrada
    hora_fin = clase.hora_salida

    duracion = (hora_fin.hour) - (hora_inicio.hour)
    return max(duracion, 0)  # Asegura que no se devuelvan horas negativas

def calculate_valid_hours(profesor_id):
    asistencias = get_all_asistencia(profesor_id)
    if asistencias is None:
        return 0

    total_hours = sum(calculate_class_hours(a) for a in asistencias if a.estado == "ASISTENCIA" or (a.estado == "JUSTIFICADA" and a.justificada) or (a.estado == "RETARDO" )) * 1.0
    return total_hours

def get_retardos(profesor_id):
    asistencias = get_all_asistencia(profesor_id)
    if asistencias is None:
        return 0

    total_retardos = sum(1 for a in asistencias if a.estado == "RETARDO")
    return total_retardos

def calculate_base_payment(profesor_id):
    profesor = Profesor.objects.get(id=profesor_id)
    valid_hours = calculate_valid_hours(profesor_id)
    late = get_retardos(profesor_id)

    valid_hours -= late % 3  # Cada 3 retardos se descuenta 1 hora de pago

    return Decimal(str(valid_hours)) * profesor.costo_por_hora

def get_nominas_from_period():
    periodo_actual = get_active_periodo()
    if periodo_actual is None:
        return []

    return Nomina.objects.filter(periodo=periodo_actual)

def get_pending_nomina():
    nominas = get_nominas_from_period()
    profesores = get_all_active_profesores()
    profesores_con_nomina = set(nomina.profesor.id for nomina in nominas)

    return [profesor for profesor in profesores if profesor.id not in profesores_con_nomina]    

def generate_nomina_for_profesor(profesor_id):
    # Generamos la nomina del profesor
    pass