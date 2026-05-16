import calendar
import io
from datetime import date, datetime, timedelta
from decimal import Decimal, InvalidOperation

from django.db import transaction
from django.utils import timezone

from Asistencias.models import Asistencia, Incidencia
from Contabilidad.models import CatalogoConcepto, DetalleNomina, Nomina, Periodo
from Profesores.models import Horario, Profesor


RETARDOS_POR_FALTA = 3
DIAS = {0: "LUN", 1: "MAR", 2: "MIE", 3: "JUE", 4: "VIE", 5: "SAB", 6: "DOM"}
ESTADOS_NOMINA_CERRADOS = {"cerrada", "pagada"}


UNIDADES = (
    "cero", "uno", "dos", "tres", "cuatro", "cinco", "seis", "siete", "ocho",
    "nueve", "diez", "once", "doce", "trece", "catorce", "quince", "dieciseis",
    "diecisiete", "dieciocho", "diecinueve", "veinte", "veintiuno", "veintidos",
    "veintitres", "veinticuatro", "veinticinco", "veintiseis", "veintisiete",
    "veintiocho", "veintinueve",
)
DECENAS = ("", "", "", "treinta", "cuarenta", "cincuenta", "sesenta", "setenta", "ochenta", "noventa")
CIENTOS = ("", "ciento", "doscientos", "trescientos", "cuatrocientos", "quinientos", "seiscientos", "setecientos", "ochocientos", "novecientos")


def money(value):
    try:
        return Decimal(value or 0).quantize(Decimal("0.0001"))
    except (InvalidOperation, TypeError, ValueError):
        return Decimal("0.0000")


def get_periodo_activo():
    return Periodo.objects.filter(estado="ABIERTO").order_by("-fecha_inicio", "-id").first()


def get_todos_los_periodos():
    return Periodo.objects.all().order_by("-fecha_inicio", "-id")


def get_ultimo_periodo():
    return Periodo.objects.order_by("-fecha_inicio", "-id").first()


def get_ultimo_periodo_cerrado():
    return Periodo.objects.filter(estado="CERRADO").order_by("-fecha_fin", "-id").first()


def rango_quincenal(fecha=None):
    fecha = fecha or timezone.localdate()
    if fecha.day <= 15:
        return fecha.replace(day=1), fecha.replace(day=15)
    ultimo_dia = calendar.monthrange(fecha.year, fecha.month)[1]
    return fecha.replace(day=16), fecha.replace(day=ultimo_dia)


def crear_periodo(fecha_inicio, fecha_fin, tipo="QUINCENAL"):
    if get_periodo_activo() is not None:
        raise Exception("Ya existe un periodo abierto. Cierralo antes de crear uno nuevo.")
    existente = Periodo.objects.filter(
        fecha_inicio=fecha_inicio,
        fecha_fin=fecha_fin,
        tipo=tipo,
    ).first()
    if existente:
        if existente.estado == "CERRADO":
            raise Exception("Ese periodo ya existe y esta cerrado.")
        return existente
    return Periodo.objects.create(fecha_inicio=fecha_inicio, fecha_fin=fecha_fin, tipo=tipo)


def crear_periodo_actual():
    inicio, fin = rango_quincenal()
    return crear_periodo(inicio, fin)


def cerrar_periodo(periodo_id):
    try:
        periodo = Periodo.objects.get(id=periodo_id, estado="ABIERTO")
    except Periodo.DoesNotExist:
        raise Exception("No se encontro un periodo abierto con ese ID.")

    profesores = get_profesores_activos()
    generadas = Nomina.objects.filter(profesor__in=profesores, periodo=periodo).count()
    if generadas < profesores.count():
        raise Exception("Faltan nominas por generar. Genera todas las nominas antes de cerrar el periodo.")

    nominas_abiertas = Nomina.objects.filter(
        profesor__in=profesores,
        periodo=periodo,
    ).exclude(estado__in=ESTADOS_NOMINA_CERRADOS).count()
    if nominas_abiertas:
        raise Exception("No se puede cerrar el periodo. Todas las nominas deben estar cerradas o pagadas.")

    periodo.estado = "CERRADO"
    periodo.fecha_cierre = timezone.now()
    periodo.save(update_fields=["estado", "fecha_cierre"])
    return periodo


def periodo_editable(periodo):
    return periodo and periodo.estado == "ABIERTO"


def nomina_editable(nomina):
    return nomina.periodo.estado == "ABIERTO" and nomina.estado not in ESTADOS_NOMINA_CERRADOS


def validar_nomina_editable(nomina):
    if not nomina_editable(nomina):
        raise Exception("No se puede modificar una nomina cerrada o de un periodo cerrado.")


def get_profesores_activos():
    return Profesor.objects.select_related("usuario").filter(estado_laboral="ACTIVO")


def horas_de_clase(horario):
    inicio = datetime.combine(date.today(), horario.hora_inicio)
    fin = datetime.combine(date.today(), horario.hora_fin)
    return Decimal(str(max((fin - inicio).total_seconds() / 3600, 0)))


def horas_de_asistencia(asistencia):
    if not asistencia.hora_salida:
        return Decimal("0")
    inicio = datetime.combine(date.today(), asistencia.hora_entrada)
    fin = datetime.combine(date.today(), asistencia.hora_salida)
    return Decimal(str(max((fin - inicio).total_seconds() / 3600, 0)))


def total_horas_periodo(profesor_id, periodo=None):
    periodo = periodo or get_periodo_activo()
    if periodo is None:
        return Decimal("0")

    horarios = Horario.objects.filter(profesor_id=profesor_id, activo=True)
    total = Decimal("0")
    fecha = periodo.fecha_inicio
    while fecha <= periodo.fecha_fin:
        dia = DIAS[fecha.weekday()]
        for horario in horarios.filter(dia_semana=dia):
            total += horas_de_clase(horario)
        fecha += timedelta(days=1)
    return total.quantize(Decimal("0.01"))


def get_asistencias_periodo(profesor_id, periodo=None):
    periodo = periodo or get_periodo_activo()
    if periodo is None:
        return Asistencia.objects.none()
    return Asistencia.objects.filter(
        profesor_id=profesor_id,
        fecha__range=(periodo.fecha_inicio, periodo.fecha_fin),
    ).exclude(tipo_registro="COMPENSATORIA")


def get_compensatorias_periodo(profesor_id, periodo=None):
    periodo = periodo or get_periodo_activo()
    if periodo is None:
        return Asistencia.objects.none()
    return Asistencia.objects.filter(
        profesor_id=profesor_id,
        fecha__range=(periodo.fecha_inicio, periodo.fecha_fin),
        tipo_registro="COMPENSATORIA",
    )


def get_incidencias_aprobadas_ids(asistencias):
    return set(
        Incidencia.objects.filter(asistencia__in=asistencias, estado="APROBADA")
        .values_list("asistencia_id", flat=True)
    )


def asistencia_justificada(asistencia, aprobadas_ids):
    return asistencia.justificada or asistencia.estado == "JUSTIFICADA" or asistencia.id in aprobadas_ids


def contar_incidencias_periodo(profesor_id, periodo=None):
    asistencias = list(get_asistencias_periodo(profesor_id, periodo).select_related("horario"))
    aprobadas_ids = get_incidencias_aprobadas_ids(asistencias)
    faltas = [a for a in asistencias if a.estado == "FALTA" and not asistencia_justificada(a, aprobadas_ids)]
    retardos = [a for a in asistencias if a.estado == "RETARDO" and not asistencia_justificada(a, aprobadas_ids)]
    return {
        "asistencias": asistencias,
        "faltas": faltas,
        "retardos": retardos,
        "faltas_count": len(faltas),
        "retardos_count": len(retardos),
        "faltas_equivalentes": len(retardos) // RETARDOS_POR_FALTA,
    }


def calcular_horas_profesor(profesor_id, periodo=None):
    periodo = periodo or get_periodo_activo()
    if periodo is None:
        return Decimal("0")
    asistencias = get_asistencias_periodo(profesor_id, periodo).filter(
        estado__in=["ASISTENCIA", "RETARDO"],
        fecha__lte=timezone.localdate(),
    )
    aprobadas_ids = get_incidencias_aprobadas_ids(asistencias)
    horas = Decimal("0")
    for asistencia in asistencias.select_related("horario"):
        if asistencia_justificada(asistencia, aprobadas_ids):
            continue
        horas += horas_de_asistencia(asistencia)
    for compensatoria in get_compensatorias_periodo(profesor_id, periodo):
        horas += horas_de_asistencia(compensatoria)
    return horas.quantize(Decimal("0.01"))


def calcular_descuentos_asistencia(profesor_id, periodo=None):
    data = contar_incidencias_periodo(profesor_id, periodo)
    # Como el bruto se calcula desde horas trabajadas reales, las faltas no se
    # descuentan aqui: simplemente no generan pago. Solo penalizamos bloques de
    # retardos acumulados.
    horas_retardos = Decimal(data["faltas_equivalentes"])
    profesor = Profesor.objects.get(id=profesor_id)
    horas_descuento = horas_retardos
    return {
        "horas_descuento": horas_descuento.quantize(Decimal("0.01")),
        "monto": (horas_descuento * profesor.costo_por_hora).quantize(Decimal("0.0001")),
        **data,
    }


def get_total_retardos(profesor_id):
    return contar_incidencias_periodo(profesor_id)["retardos_count"]


def get_faltas_descontables(profesor_id):
    return calcular_descuentos_asistencia(profesor_id)["horas_descuento"]


def get_horas_trabajadas(profesor_id):
    return calcular_horas_profesor(profesor_id)


def get_horas_compensatorias(profesor_id):
    return sum((horas_de_asistencia(a) for a in get_compensatorias_periodo(profesor_id)), Decimal("0"))


def calcular_pago_base(profesor_id, periodo=None):
    profesor = Profesor.objects.get(id=profesor_id)
    return (calcular_horas_profesor(profesor_id, periodo) * profesor.costo_por_hora).quantize(Decimal("0.0001"))


def calcular_deducciones(profesor_id):
    return calcular_descuentos_asistencia(profesor_id)["monto"]


def calcular_percepcion_compensatorias(profesor_id):
    profesor = Profesor.objects.get(id=profesor_id)
    return (get_horas_compensatorias(profesor_id) * profesor.costo_por_hora).quantize(Decimal("0.0001"))


def calcular_isr(base_gravable):
    """
    ISR academico simplificado para Sprint 4.
    No sustituye tablas fiscales oficiales; los rangos son faciles de actualizar.
    """
    base = money(base_gravable)
    if base <= Decimal("5000"):
        return Decimal("0.0000")
    if base <= Decimal("10000"):
        return ((base - Decimal("5000")) * Decimal("0.10")).quantize(Decimal("0.0001"))
    if base <= Decimal("20000"):
        return (Decimal("500") + ((base - Decimal("10000")) * Decimal("0.15"))).quantize(Decimal("0.0001"))
    return (Decimal("2000") + ((base - Decimal("20000")) * Decimal("0.20"))).quantize(Decimal("0.0001"))


def get_nominas_periodo_activo():
    periodo = get_periodo_activo()
    if periodo is None:
        return Nomina.objects.none()
    return Nomina.objects.filter(periodo=periodo).select_related("profesor", "profesor__usuario", "periodo")


def get_profesores_sin_nomina():
    periodo = get_periodo_activo()
    if periodo is None:
        return []
    con_nomina = set(Nomina.objects.filter(periodo=periodo).values_list("profesor_id", flat=True))
    return [p for p in get_profesores_activos() if p.id not in con_nomina]


def get_profesores_sin_nomina_periodo(periodo):
    if periodo is None:
        return []
    con_nomina = set(Nomina.objects.filter(periodo=periodo).values_list("profesor_id", flat=True))
    return [p for p in get_profesores_activos() if p.id not in con_nomina]


def resumen_nomina(profesor_id, periodo):
    descuentos = calcular_descuentos_asistencia(profesor_id, periodo)
    return {
        "horas_trabajadas": calcular_horas_profesor(profesor_id, periodo),
        "faltas": descuentos["faltas_count"],
        "retardos": descuentos["retardos_count"],
        "faltas_equivalentes": descuentos["faltas_equivalentes"],
        "total_bruto": calcular_pago_base(profesor_id, periodo),
        "horas_descuento": descuentos["horas_descuento"],
        "descuento_asistencia": descuentos["monto"],
    }


def recalcular_totales_nomina(nomina):
    validar_nomina_editable(nomina)
    base = resumen_nomina(nomina.profesor_id, nomina.periodo)
    detalles = DetalleNomina.objects.filter(nomina=nomina).select_related("concepto")

    percepciones_extra = Decimal("0")
    deducciones_extra = Decimal("0")
    percepciones_gravables = Decimal("0")

    for detalle in detalles:
        if detalle.concepto.tipo == "PERCEPCION":
            percepciones_extra += detalle.monto
            if detalle.concepto.clasificacion_fiscal in {"GRAVADA", "MIXTA"}:
                percepciones_gravables += detalle.monto
        else:
            deducciones_extra += detalle.monto

    total_percepciones = base["total_bruto"] + percepciones_extra
    isr = calcular_isr(base["total_bruto"] + percepciones_gravables)
    deducciones_calculadas = base["descuento_asistencia"] + deducciones_extra
    deducciones_disponibles = max(total_percepciones - isr, Decimal("0"))
    total_deducciones = min(deducciones_calculadas, deducciones_disponibles)
    total_neto = total_percepciones - total_deducciones - isr

    nomina.horas_trabajadas = base["horas_trabajadas"]
    nomina.faltas = base["faltas"]
    nomina.retardos = base["retardos"]
    nomina.faltas_equivalentes = base["faltas_equivalentes"]
    nomina.total_bruto = base["total_bruto"]
    nomina.total_percepciones = total_percepciones.quantize(Decimal("0.0001"))
    nomina.total_impuestos = isr
    nomina.total_deducciones = total_deducciones.quantize(Decimal("0.0001"))
    nomina.total_neto = max(total_neto, Decimal("0")).quantize(Decimal("0.0001"))
    nomina.estado = "procesando" if nomina.estado == "pendiente" else nomina.estado
    nomina.save()
    return nomina


@transaction.atomic
def generar_nomina_profesor(profesor_id, periodo=None, regenerar=False):
    periodo = periodo or get_periodo_activo()
    if periodo is None:
        raise Exception("No hay periodo activo para generar la nomina.")
    if periodo.estado != "ABIERTO":
        raise Exception("No se puede generar o regenerar nomina de un periodo cerrado.")

    profesor = Profesor.objects.get(id=profesor_id)
    existente = Nomina.objects.filter(profesor=profesor, periodo=periodo).first()
    if existente and existente.estado in ESTADOS_NOMINA_CERRADOS:
        raise Exception("La nomina esta cerrada y no puede regenerarse.")
    if existente and not regenerar:
        return existente

    base = resumen_nomina(profesor.id, periodo)
    nomina, _ = Nomina.objects.update_or_create(
        profesor=profesor,
        periodo=periodo,
        defaults={
            "horas_trabajadas": base["horas_trabajadas"],
            "faltas": base["faltas"],
            "retardos": base["retardos"],
            "faltas_equivalentes": base["faltas_equivalentes"],
            "total_bruto": base["total_bruto"],
            "total_percepciones": base["total_bruto"],
            "total_impuestos": Decimal("0.0000"),
            "total_deducciones": base["descuento_asistencia"],
            "total_neto": base["total_bruto"] - base["descuento_asistencia"],
            "estado": "procesando",
        },
    )
    return recalcular_totales_nomina(nomina)


def generar_nomina(profesor_id):
    return generar_nomina_profesor(profesor_id)


def regenerar_nomina_profesor(profesor_id, periodo=None):
    return generar_nomina_profesor(profesor_id, periodo, regenerar=True)


def generar_nominas_periodo(periodo=None, regenerar=False):
    periodo = periodo or get_periodo_activo()
    if periodo is None:
        raise Exception("No hay periodo activo.")
    nominas = []
    for profesor in get_profesores_activos():
        nominas.append(generar_nomina_profesor(profesor.id, periodo, regenerar=regenerar))
    return nominas


def regenerar_nominas_periodo(periodo=None):
    return generar_nominas_periodo(periodo, regenerar=True)


def crear_concepto(nombre, tipo):
    tipo = (tipo or "").upper()
    if tipo not in {"PERCEPCION", "DEDUCCION"}:
        raise Exception("Tipo de concepto invalido.")
    nombre = (nombre or "").strip()
    if not nombre:
        raise Exception("El nombre del concepto es obligatorio.")
    clasificacion = "GRAVADA" if tipo == "PERCEPCION" else "EXENTA"
    concepto, _ = CatalogoConcepto.objects.get_or_create(
        nombre=nombre,
        tipo=tipo,
        defaults={"clasificacion_fiscal": clasificacion, "activo": True},
    )
    return concepto


def agregar_concepto_nomina(nomina_id, tipo, nombre, monto, descripcion=""):
    nomina = Nomina.objects.select_related("periodo").get(id=nomina_id)
    validar_nomina_editable(nomina)
    monto = money(monto)
    if monto <= 0:
        raise Exception("El monto debe ser mayor a cero.")
    concepto = crear_concepto(nombre, tipo)
    DetalleNomina.objects.create(
        nomina=nomina,
        concepto=concepto,
        monto=monto,
        descripcion=(descripcion or "").strip(),
    )
    return recalcular_totales_nomina(nomina)


def eliminar_concepto_nomina(detalle_id):
    detalle = DetalleNomina.objects.select_related("nomina", "nomina__periodo").get(id=detalle_id)
    nomina = detalle.nomina
    validar_nomina_editable(nomina)
    detalle.delete()
    return recalcular_totales_nomina(nomina)


def cerrar_nomina(nomina_id):
    nomina = Nomina.objects.select_related("periodo").get(id=nomina_id)
    validar_nomina_editable(nomina)
    nomina.estado = "cerrada"
    nomina.save(update_fields=["estado", "fecha_actualizacion"])
    return nomina


def marcar_nomina_pagada(nomina_id):
    nomina = Nomina.objects.select_related("periodo").get(id=nomina_id)
    if nomina.estado == "pagada":
        return nomina
    if nomina.estado == "cerrada":
        nomina.estado = "pagada"
        nomina.save(update_fields=["estado", "fecha_actualizacion"])
        return nomina
    raise Exception("Solo se puede marcar como pagada una nomina cerrada.")


def formato_moneda(monto):
    return f"$ {Decimal(monto or 0).quantize(Decimal('0.01')):,.2f}"


def obtener_nominas_periodo(periodo, profesor_id="", estado=""):
    nominas = Nomina.objects.select_related(
        "profesor",
        "profesor__usuario",
        "profesor__departamento",
        "periodo",
    ).filter(periodo=periodo)
    if profesor_id:
        nominas = nominas.filter(profesor_id=profesor_id)
    if estado:
        nominas = nominas.filter(estado=estado)
    return nominas.order_by("profesor__usuario__apellido", "profesor__usuario__nombre")


def obtener_totales_periodo(periodo, nominas=None):
    nominas = list(nominas if nominas is not None else obtener_nominas_periodo(periodo))
    totales = {
        "total_profesores": len(nominas),
        "total_bruto": Decimal("0.0000"),
        "total_percepciones": Decimal("0.0000"),
        "total_deducciones": Decimal("0.0000"),
        "total_isr": Decimal("0.0000"),
        "total_neto": Decimal("0.0000"),
    }
    for nomina in nominas:
        totales["total_bruto"] += money(nomina.total_bruto)
        totales["total_percepciones"] += money(nomina.total_percepciones)
        totales["total_deducciones"] += money(nomina.total_deducciones)
        totales["total_isr"] += money(nomina.total_impuestos)
        totales["total_neto"] += money(nomina.total_neto)
    return totales


def detectar_inconsistencias_periodo(periodo):
    inconsistencias = []
    profesores = list(get_profesores_activos())
    nominas = Nomina.objects.filter(periodo=periodo).select_related("profesor", "profesor__usuario")
    nominas_por_profesor = {nomina.profesor_id: nomina for nomina in nominas}

    if not nominas_por_profesor:
        inconsistencias.append("Periodo sin nominas generadas.")

    for profesor in profesores:
        nombre = profesor.usuario.get_full_name()
        if not profesor.rfc:
            inconsistencias.append(f"{nombre}: profesor sin RFC.")
        if not profesor.costo_por_hora or profesor.costo_por_hora <= 0:
            inconsistencias.append(f"{nombre}: profesor sin costo por hora valido.")
        if not Horario.objects.filter(profesor=profesor, activo=True).exists():
            inconsistencias.append(f"{nombre}: profesor sin horario activo.")

        nomina = nominas_por_profesor.get(profesor.id)
        if not nomina:
            inconsistencias.append(f"{nombre}: profesor activo sin nomina.")
            continue
        if nomina.total_neto < 0:
            inconsistencias.append(f"{nombre}: sueldo neto negativo.")
        if nomina.total_percepciones is None or nomina.total_neto is None:
            inconsistencias.append(f"{nombre}: nomina incompleta.")
        if nomina.estado not in {"procesando", "cerrada", "pagada"}:
            inconsistencias.append(f"{nombre}: estado de nomina no reconocido.")
        if DetalleNomina.objects.filter(nomina=nomina).exists():
            inconsistencias.append(f"{nombre}: nomina con ajustes manuales.")

    return inconsistencias


def obtener_resumen_periodo(periodo):
    nominas = list(obtener_nominas_periodo(periodo))
    pendientes = get_profesores_sin_nomina_periodo(periodo)
    return {
        "periodo": periodo,
        "estado_periodo": periodo.estado,
        "total_profesores_incluidos": get_profesores_activos().count(),
        "total_nominas_generadas": len(nominas),
        "total_nominas_pendientes": len(pendientes),
        "total_nominas_cerradas": sum(1 for nomina in nominas if nomina.estado == "cerrada"),
        "total_nominas_pagadas": sum(1 for nomina in nominas if nomina.estado == "pagada"),
        "total_nominas_en_proceso": sum(1 for nomina in nominas if nomina.estado == "procesando"),
        "totales": obtener_totales_periodo(periodo, nominas),
        "inconsistencias": detectar_inconsistencias_periodo(periodo),
        "nominas": nominas,
        "pendientes": pendientes,
    }


def puede_generar_recibo(nomina):
    return nomina.estado in ESTADOS_NOMINA_CERRADOS


def generar_contexto_recibo(nomina):
    detalles = DetalleNomina.objects.filter(nomina=nomina).select_related("concepto").order_by("concepto__tipo", "id")
    return {
        "nomina": nomina,
        "profesor": nomina.profesor,
        "periodo": nomina.periodo,
        "detalles": detalles,
        "percepciones": [detalle for detalle in detalles if detalle.concepto.tipo == "PERCEPCION"],
        "deducciones": [detalle for detalle in detalles if detalle.concepto.tipo == "DEDUCCION"],
        "fecha_emision": timezone.localtime(timezone.now()),
        "leyenda": "Documento administrativo academico generado por Saltix. No sustituye comprobantes fiscales oficiales.",
    }


def _pdf_escape(text):
    return str(text).replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")[:115]


def simple_pdf(text):
    lines = text.splitlines()
    stream = ["BT", "/F1 10 Tf", "42 790 Td"]
    first = True
    for line in lines[:95]:
        clean = _pdf_escape(line)
        if first:
            stream.append(f"({clean}) Tj")
            first = False
        else:
            stream.append(f"0 -13 Td ({clean}) Tj")
    stream.append("ET")
    stream_data = "\n".join(stream).encode("latin-1", errors="replace")
    objects = [
        b"1 0 obj << /Type /Catalog /Pages 2 0 R >> endobj\n",
        b"2 0 obj << /Type /Pages /Kids [3 0 R] /Count 1 >> endobj\n",
        b"3 0 obj << /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Resources << /Font << /F1 4 0 R >> >> /Contents 5 0 R >> endobj\n",
        b"4 0 obj << /Type /Font /Subtype /Type1 /BaseFont /Helvetica >> endobj\n",
        b"5 0 obj << /Length " + str(len(stream_data)).encode() + b" >> stream\n" + stream_data + b"\nendstream endobj\n",
    ]
    output = io.BytesIO()
    output.write(b"%PDF-1.4\n")
    offsets = [0]
    for obj in objects:
        offsets.append(output.tell())
        output.write(obj)
    xref = output.tell()
    output.write(f"xref\n0 {len(objects) + 1}\n0000000000 65535 f \n".encode())
    for offset in offsets[1:]:
        output.write(f"{offset:010d} 00000 n \n".encode())
    output.write(f"trailer << /Size {len(objects) + 1} /Root 1 0 R >>\nstartxref\n{xref}\n%%EOF".encode())
    return output.getvalue()


def generar_texto_recibo(nomina):
    contexto = generar_contexto_recibo(nomina)
    profesor = contexto["profesor"]
    periodo = contexto["periodo"]
    lines = [
        "SALTIX - RECIBO INDIVIDUAL DE NOMINA",
        "",
        f"Profesor: {profesor.usuario.get_full_name()}",
        f"RFC: {profesor.rfc or 'Sin RFC'}",
        f"Periodo: {periodo.fecha_inicio} - {periodo.fecha_fin}",
        f"Fecha de emision: {contexto['fecha_emision']:%d/%m/%Y %H:%M}",
        f"Estado de nomina: {nomina.estado}",
        "",
        f"Horas trabajadas: {nomina.horas_trabajadas}",
        f"Faltas: {nomina.faltas}",
        f"Retardos: {nomina.retardos}",
        f"Sueldo bruto: {formato_moneda(nomina.total_bruto)}",
        f"Total percepciones: {formato_moneda(nomina.total_percepciones)}",
        f"Total deducciones: {formato_moneda(nomina.total_deducciones)}",
        f"ISR: {formato_moneda(nomina.total_impuestos)}",
        f"Sueldo neto: {formato_moneda(nomina.total_neto)}",
        "",
        "Conceptos:",
    ]
    for detalle in contexto["detalles"]:
        lines.append(f"- {detalle.concepto.tipo}: {detalle.concepto.nombre} {formato_moneda(detalle.monto)}")
    if not contexto["detalles"]:
        lines.append("- Sin conceptos adicionales.")
    lines.extend(["", contexto["leyenda"]])
    return "\n".join(lines)


def generar_texto_reporte_periodo(periodo, usuario=None):
    resumen = obtener_resumen_periodo(periodo)
    tipo_reporte = "Vista previa" if periodo.estado == "ABIERTO" else "Reporte oficial"
    usuario_label = usuario.get_full_name() if usuario and hasattr(usuario, "get_full_name") else "Sistema"
    lines = [
        f"SALTIX - {tipo_reporte.upper()} DE NOMINA",
        "",
        f"Periodo: {periodo.fecha_inicio} - {periodo.fecha_fin}",
        f"Estado del periodo: {periodo.estado}",
        f"Fecha de generacion: {timezone.localtime(timezone.now()):%d/%m/%Y %H:%M}",
        f"Generado por: {usuario_label}",
        "",
        "Profesor | Departamento | Horas | Bruto | Percepciones | Deducciones | ISR | Neto | Estado",
    ]
    for nomina in resumen["nominas"]:
        departamento = getattr(nomina.profesor.departamento, "nombre", "Sin departamento")
        lines.append(
            " | ".join([
                nomina.profesor.usuario.get_full_name(),
                departamento,
                str(nomina.horas_trabajadas),
                formato_moneda(nomina.total_bruto),
                formato_moneda(nomina.total_percepciones),
                formato_moneda(nomina.total_deducciones),
                formato_moneda(nomina.total_impuestos),
                formato_moneda(nomina.total_neto),
                nomina.estado,
            ])
        )
    totales = resumen["totales"]
    lines.extend([
        "",
        f"Total profesores con nomina: {totales['total_profesores']}",
        f"Total bruto: {formato_moneda(totales['total_bruto'])}",
        f"Total percepciones: {formato_moneda(totales['total_percepciones'])}",
        f"Total deducciones: {formato_moneda(totales['total_deducciones'])}",
        f"Total ISR: {formato_moneda(totales['total_isr'])}",
        f"Total neto pagado: {formato_moneda(totales['total_neto'])}",
        "",
        "Inconsistencias:",
    ])
    if resumen["inconsistencias"]:
        lines.extend(f"- {item}" for item in resumen["inconsistencias"][:30])
    else:
        lines.append("- Sin inconsistencias detectadas.")
    return "\n".join(lines)


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
    prefijo = "un millon" if millones == 1 else f"{numero_a_palabras(millones)} millones"
    return prefijo if resto == 0 else f"{prefijo} {numero_a_palabras(resto)}"


def dinero_a_texto(monto):
    monto = Decimal(monto or 0).quantize(Decimal("0.01"))
    pesos = int(monto)
    centavos = int((monto - Decimal(pesos)) * 100)
    etiqueta = "peso" if pesos == 1 else "pesos"
    return f"{numero_a_palabras(pesos)} {etiqueta} {centavos:02d}/100 M.N.".upper()
