from decimal import Decimal
from datetime import datetime, timedelta

from django.utils import timezone

from Asistencias.models import Asistencia, Incidencia
from Profesores.models import Profesor, Horario
from Contabilidad.models import Periodo, Nomina


# Cuántos retardos equivalen a una falta para efectos de nómina
RETARDOS_POR_FALTA = 3

DIAS = {0: "LUN", 1: "MAR", 2: "MIE", 3: "JUE", 4: "VIE", 5: "SAB", 6: "DOM"}

UNIDADES = (
    "cero", "uno", "dos", "tres", "cuatro", "cinco", "seis", "siete", "ocho",
    "nueve", "diez", "once", "doce", "trece", "catorce", "quince", "dieciséis",
    "diecisiete", "dieciocho", "diecinueve", "veinte", "veintiuno", "veintidós",
    "veintitrés", "veinticuatro", "veinticinco", "veintiséis", "veintisiete",
    "veintiocho", "veintinueve",
)
DECENAS = ("", "", "", "treinta", "cuarenta", "cincuenta", "sesenta", "setenta", "ochenta", "noventa")
CIENTOS = ("", "ciento", "doscientos", "trescientos", "cuatrocientos", "quinientos",
           "seiscientos", "setecientos", "ochocientos", "novecientos")


# ── Periodos ───────────────────────────────────────────────────────────────────

def get_periodo_activo():
    return Periodo.objects.filter(estado="ABIERTO").order_by("-fecha_inicio", "-id").first()


def get_todos_los_periodos():
    return Periodo.objects.all().order_by("-fecha_inicio")


def get_ultimo_periodo():
    return Periodo.objects.order_by("-fecha_inicio").first()


def get_ultimo_periodo_cerrado():
    return Periodo.objects.filter(estado="CERRADO").order_by("-fecha_fin").first()


def crear_periodo(fecha_inicio, fecha_fin):
    if get_periodo_activo() is not None:
        raise Exception("Ya existe un periodo abierto. Ciérralo antes de crear uno nuevo.")
    periodo = Periodo(fecha_inicio=fecha_inicio, fecha_fin=fecha_fin)
    periodo.save()
    return periodo


def cerrar_periodo(periodo_id):
    try:
        periodo = Periodo.objects.get(id=periodo_id, estado="ABIERTO")
    except Periodo.DoesNotExist:
        raise Exception("No se encontró un periodo abierto con ese ID.")

    if periodo.fecha_fin > timezone.now().date():
        raise Exception("No se puede cerrar un periodo antes de su fecha de fin.")

    profesores = get_profesores_activos()
    nominas_generadas = Nomina.objects.filter(profesor__in=profesores, periodo=periodo).count()
    if nominas_generadas < profesores.count():
        raise Exception(
            "Faltan nóminas por generar. Genera todas las nóminas antes de cerrar el periodo."
        )

    periodo.estado = "CERRADO"
    # No modificamos fecha_fin — conservamos la fecha original del periodo
    periodo.save(update_fields=["estado"])
    return periodo


# ── Profesores ─────────────────────────────────────────────────────────────────

def get_profesores_activos():
    return Profesor.objects.filter(estado_laboral="ACTIVO")


# ── Horas de clase ─────────────────────────────────────────────────────────────

def horas_de_clase(horario):
    inicio = datetime.combine(datetime.today(), horario.hora_inicio)
    fin = datetime.combine(datetime.today(), horario.hora_fin)
    return (fin - inicio).total_seconds() / 3600


def horas_de_asistencia(asistencia):
    if not asistencia.hora_salida:
        return 0
    inicio = datetime.combine(datetime.today(), asistencia.hora_entrada)
    fin = datetime.combine(datetime.today(), asistencia.hora_salida)
    return max((fin - inicio).total_seconds() / 3600, 0)


def total_horas_periodo(profesor_id):
    periodo = get_periodo_activo()
    if periodo is None:
        return 0

    horarios = Horario.objects.filter(profesor_id=profesor_id, activo=True)

    total = 0
    fecha = periodo.fecha_inicio
    while fecha <= periodo.fecha_fin:
        dia = DIAS[fecha.weekday()]
        for h in horarios.filter(dia_semana=dia):
            total += horas_de_clase(h)
        fecha += timedelta(days=1)

    return round(total, 2)


# ── Asistencias ────────────────────────────────────────────────────────────────

def get_asistencias_periodo(profesor_id):
    periodo = get_periodo_activo()
    if periodo is None:
        return None

    try:
        profesor = Profesor.objects.get(id=profesor_id)
    except Profesor.DoesNotExist:
        return None

    return Asistencia.objects.filter(
        profesor=profesor,
        fecha__range=(periodo.fecha_inicio, periodo.fecha_fin),
    ).exclude(tipo_registro="COMPENSATORIA")


def get_compensatorias_periodo(profesor_id):
    periodo = get_periodo_activo()
    if periodo is None:
        return Asistencia.objects.none()

    return Asistencia.objects.filter(
        profesor_id=profesor_id,
        fecha__range=(periodo.fecha_inicio, periodo.fecha_fin),
        tipo_registro="COMPENSATORIA",
    )


def get_total_retardos(profesor_id):
    asistencias = get_asistencias_periodo(profesor_id)
    if asistencias is None:
        return 0
    justificadas = Incidencia.objects.filter(
        asistencia__in=asistencias,
        estado="APROBADA",
    ).values_list("asistencia_id", flat=True)
    return asistencias.filter(estado="RETARDO").exclude(id__in=justificadas).count()


def get_faltas_descontables(profesor_id):
    profesor = Profesor.objects.get(id=profesor_id)
    asistencias = get_asistencias_periodo(profesor_id)
    if asistencias is None:
        return 0

    justificadas = Incidencia.objects.filter(
        asistencia__in=asistencias,
        estado="APROBADA",
    ).values_list("asistencia_id", flat=True)
    faltas = asistencias.filter(estado="FALTA", justificada=False).exclude(id__in=justificadas)
    retardos = asistencias.filter(estado="RETARDO").exclude(id__in=justificadas).count()
    faltas_por_retardos = retardos // RETARDOS_POR_FALTA

    horas_faltadas = 0
    for falta in faltas.select_related("horario"):
        if falta.hora_salida:
            horas_faltadas += horas_de_asistencia(falta)
        else:
            horas_faltadas += horas_de_clase(falta.horario)
    descuento = horas_faltadas + faltas_por_retardos

    return descuento

def get_horas_trabajadas(profesor_id):
    # horas trabajadas = las clases a las que asistió (asistencias con estado ASISTENCIA o RETARDO)
    # sin considerar las clases justificadas ni las que no han ocurrido aún (fecha futura).
    asistencias = get_asistencias_periodo(profesor_id)
    if asistencias is None:
        return 0
    justificadas = Incidencia.objects.filter(
        asistencia__in=asistencias,
        estado="APROBADA",
    ).values_list("asistencia_id", flat=True)
    asistencias_validas = asistencias.filter(
        estado__in=["ASISTENCIA", "RETARDO"],
        justificada=False,
        fecha__lte=timezone.localdate(),
    ).exclude(id__in=justificadas)
    return sum(horas_de_asistencia(a) for a in asistencias_validas)

def get_horas_compensatorias(profesor_id):
    compensatorias = get_compensatorias_periodo(profesor_id)
    return sum(horas_de_asistencia(a) for a in compensatorias)


# ── Nóminas ────────────────────────────────────────────────────────────────────

def calcular_pago_base(profesor_id):
    horas = total_horas_periodo(profesor_id)
    profesor = Profesor.objects.get(id=profesor_id)
    return Decimal(str(horas)) * profesor.costo_por_hora


def calcular_deducciones(profesor_id):
    horas_falta = get_faltas_descontables(profesor_id)
    profesor = Profesor.objects.get(id=profesor_id)
    return Decimal(str(horas_falta)) * profesor.costo_por_hora


def calcular_percepcion_compensatorias(profesor_id):
    """
    Percepción extra por clases compensatorias registradas en este periodo.
    Puede incluir compensatorias de faltas de periodos anteriores.
    """
    horas = get_horas_compensatorias(profesor_id)
    profesor = Profesor.objects.get(id=profesor_id)
    return Decimal(str(horas)) * profesor.costo_por_hora


def get_nominas_periodo_activo():
    periodo = get_periodo_activo()
    if periodo is None:
        return Nomina.objects.none()
    return Nomina.objects.filter(periodo=periodo)


def get_profesores_sin_nomina():
    """Profesores activos que todavía no tienen nómina en el periodo actual."""
    nominas = get_nominas_periodo_activo()
    con_nomina = set(n.profesor_id for n in nominas)
    return [p for p in get_profesores_activos() if p.id not in con_nomina]


def generar_nomina(profesor_id):
    periodo = get_periodo_activo()
    if periodo is None:
        raise Exception("No hay periodo activo para generar la nómina.")

    existente = Nomina.objects.filter(profesor_id=profesor_id, periodo=periodo).first()
    if existente:
        return existente

    bruto = calcular_pago_base(profesor_id)
    compensatorias = calcular_percepcion_compensatorias(profesor_id)
    deducciones = calcular_deducciones(profesor_id)
    total_percepciones = bruto + compensatorias

    return Nomina.objects.create(
        profesor_id=profesor_id,
        periodo=periodo,
        total_bruto=bruto,
        total_percepciones=total_percepciones,
        total_impuestos=Decimal("0.00"),
        total_deducciones=deducciones,
        total_neto=total_percepciones - deducciones,
        fecha_de_generacion=timezone.now(),
        estado="procesando",
    )


def marcar_nomina_pagada(nomina_id):
    nomina = Nomina.objects.get(id=nomina_id)
    nomina.estado = "pagada"
    nomina.save(update_fields=["estado"])
    return nomina


# ── Utilidades de texto ────────────────────────────────────────────────────────

def numero_a_palabras(numero):
    numero = int(numero)
    if numero < 30:
        return UNIDADES[numero]
    if numero < 100:
        decena, unidad = divmod(numero, 10)
        return DECENAS[decena] if unidad == 0 else f"{DECENAS[decena]} y {UNIDADES[unidad]}"
    if numero == 100:
        return "cien"
    if numero < 1000:
        centena, resto = divmod(numero, 100)
        return CIENTOS[centena] if resto == 0 else f"{CIENTOS[centena]} {numero_a_palabras(resto)}"
    if numero < 1_000_000:
        miles, resto = divmod(numero, 1000)
        prefijo = "mil" if miles == 1 else f"{numero_a_palabras(miles)} mil"
        return prefijo if resto == 0 else f"{prefijo} {numero_a_palabras(resto)}"
    millones, resto = divmod(numero, 1_000_000)
    prefijo = "un millón" if millones == 1 else f"{numero_a_palabras(millones)} millones"
    return prefijo if resto == 0 else f"{prefijo} {numero_a_palabras(resto)}"


def dinero_a_texto(monto):
    monto = Decimal(monto or 0).quantize(Decimal("0.01"))
    pesos = int(monto)
    centavos = int((monto - Decimal(pesos)) * 100)
    etiqueta = "peso" if pesos == 1 else "pesos"
    return f"{numero_a_palabras(pesos)} {etiqueta} {centavos:02d}/100 M.N.".upper()
