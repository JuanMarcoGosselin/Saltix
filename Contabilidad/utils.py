from django.utils import timezone
from Asistencias.models import Asistencia
from Profesores.models import Profesor
from Contabilidad.models import Periodo, Nomina
from decimal import Decimal

UNIDADES = (
    "cero", "uno", "dos", "tres", "cuatro", "cinco", "seis", "siete", "ocho",
    "nueve", "diez", "once", "doce", "trece", "catorce", "quince", "dieciseis",
    "diecisiete", "dieciocho", "diecinueve", "veinte", "veintiuno", "veintidos",
    "veintitres", "veinticuatro", "veinticinco", "veintiseis", "veintisiete",
    "veintiocho", "veintinueve",
)
DIEZ_DIEZ = ("", "", "", "treinta", "cuarenta", "cincuenta", "sesenta", "setenta", "ochenta", "noventa")
CIENTOS = ("", "ciento", "doscientos", "trescientos", "cuatrocientos", "quinientos", "seiscientos", "setecientos", "ochocientos", "novecientos")

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

def get_nomina_for_profesor(profesor_id):
    # Solo se puede generar una nomina por periodo y profesor. Si ya existe una nomina para el periodo y profesor, se devuelve esa nomina sin generar una nueva.
    periodo_actual = get_active_periodo()
    if periodo_actual is None:
        raise Exception("No hay un periodo activo para generar la nómina.")
    existing_nomina = Nomina.objects.filter(profesor_id=profesor_id, periodo=periodo_actual).first()
    if existing_nomina:
        return existing_nomina
    
    nomina = Nomina.objects.create(
        profesor_id=profesor_id,
        periodo=periodo_actual,
        total_bruto=calculate_base_payment(profesor_id),
        total_percepciones=Decimal("0.00"),  # Aquí se podrían agregar percepciones adicionales
        total_impuestos=Decimal("0.00"),  # Aquí se podrían calcular impuestos basados en las percepciones
        total_deducciones=Decimal("0.00"),  # Aquí se podrían agregar deducciones adicionales
        total_neto=Decimal("0.00"),  # Este campo se actualizará después de calcular el neto
        fecha_de_generacion=timezone.now(),
        estado="procesando",
    )
    return nomina

def get_total_faltas(profesor_id):
    asistencias = get_all_asistencia(profesor_id)
    if asistencias is None:
        return 0

    total_faltas = sum(1 for a in asistencias if a.estado == "FALTA")
    total_retardos = get_retardos(profesor_id)
    total_faltas += total_retardos // 3

    return total_faltas

def mark_nomina_as_paid(nomina_id):
    nomina = Nomina.objects.get(id=nomina_id)
    nomina.estado = "pagada"
    nomina.save()
    return nomina

def number_to_spanish_words(number):
    number = int(number)
    if number < 30:
        return UNIDADES[number]
    if number < 100:
        ten, unit = divmod(number, 10)
        return DIEZ_DIEZ[ten] if unit == 0 else f"{DIEZ_DIEZ[ten]} y {UNIDADES[unit]}"
    if number == 100:
        return "cien"
    if number < 1000:
        hundred, rest = divmod(number, 100)
        return CIENTOS[hundred] if rest == 0 else f"{CIENTOS[hundred]} {number_to_spanish_words(rest)}"
    if number < 1000000:
        thousand, rest = divmod(number, 1000)
        prefix = "mil" if thousand == 1 else f"{number_to_spanish_words(thousand)} mil"
        return prefix if rest == 0 else f"{prefix} {number_to_spanish_words(rest)}"
    million, rest = divmod(number, 1000000)
    prefix = "un millon" if million == 1 else f"{number_to_spanish_words(million)} millones"
    return prefix if rest == 0 else f"{prefix} {number_to_spanish_words(rest)}"

def money_to_spanish_text(amount):
    amount = Decimal(amount or 0).quantize(Decimal("0.01"))
    pesos = int(amount)
    cents = int((amount - Decimal(pesos)) * 100)
    peso_label = "peso" if pesos == 1 else "pesos"
    return f"{number_to_spanish_words(pesos)} {peso_label} {cents:02d}/100 M.N.".upper()
