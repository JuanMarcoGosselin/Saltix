import calendar
from datetime import datetime, timedelta
from decimal import Decimal, ROUND_HALF_UP

from django.db.models import Q
from django.utils import timezone

from Asistencias.models import *
from .models import Horario, Profesor
from Contabilidad.utils import get_periodo_activo, total_horas_periodo

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
    return Horario.objects.filter(profesor=profesor, dia_semana=dia, activo=True)

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
    horarios = list(
        Horario.objects.filter(profesor=profesor, activo=True).order_by("dia_semana", "hora_inicio")
    )
    horarios_por_dia = {codigo: [] for codigo in dias.values()}
    for clase in horarios:
        horarios_por_dia.setdefault(clase.dia_semana, []).append(clase)
        horas_totales += clase.hora_fin.hour - clase.hora_inicio.hour

    for dia in dias:
        horario[dia] = horarios_por_dia.get(dias[dia], [])
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

def format_hours(minutes: int) -> str:
    hours = (Decimal(minutes) / Decimal(60)).quantize(Decimal("0.1"), rounding=ROUND_HALF_UP)
    if hours == hours.to_integral():
        return str(hours.quantize(Decimal("0"), rounding=ROUND_HALF_UP))
    return str(hours)

def format_money(amount: Decimal) -> str:
    amount = (amount or Decimal(0)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    return f"{amount:,.2f}"

def month_bounds(hoy):
    month_end_day = calendar.monthrange(hoy.year, hoy.month)[1]
    return hoy.replace(day=1), hoy.replace(day=month_end_day)

def get_attendance_stats(profesor_id):
    periodo = get_periodo_activo()
    asistencias = Asistencia.objects.filter(profesor_id=profesor_id, fecha__range=(periodo.fecha_inicio - timedelta(weeks=1), periodo.fecha_fin))
    stats = {
        "total_asistencias": asistencias.filter(estado="ASISTENCIA").count(),
        "total_retardos": asistencias.filter(estado="RETARDO").count(),
        "total_faltas": asistencias.filter(estado="FALTA", justificada=False).count(),
        "total_justificadas": asistencias.filter(justificada=True).count(),
    }
    return stats

def get_horario_display(profesor_id, inicio_semana, fin_semana):
    dias_map = {
        "LUN": 0,
        "MAR": 1,
        "MIE": 2,
        "JUE": 3,
        "VIE": 4,
        "SAB": 5,
    }

    horario = Horario.objects.filter(profesor_id=profesor_id, activo=True).order_by("dia_semana", "hora_inicio")
    asistencias = Asistencia.objects.filter(profesor_id=profesor_id, fecha__range=(inicio_semana, fin_semana))
    ahora = timezone.localtime()

    for clase in horario:
        clase.asistencia = asistencias.filter(horario_id=clase.id).first()
        if clase.asistencia:
            clase.estado = clase.asistencia.estado
            continue
            
        fecha_clase = inicio_semana + timezone.timedelta(days=dias_map[clase.dia_semana])
        fecha_hora_clase = timezone.make_aware(datetime.combine(fecha_clase, clase.hora_inicio,))

        if fecha_hora_clase < ahora:
            clase.estado = "FALTA"
        else:
            clase.estado = "PENDIENTE"

    return {
        "dias": ["LUN", "MAR", "MIE", "JUE", "VIE", "SAB"],
        "horas": list(range(6, 24)),
        "clases": horario,
    }

def get_faltas(profesor_id, inicio_semana, fin_semana):
    faltas = Asistencia.objects.filter(
        profesor_id=profesor_id,
        estado="FALTA",
        justificada=False,
        fecha__range=(inicio_semana, fin_semana)
    ).select_related("horario").order_by("-fecha", "-id")

    for falta in faltas:
        falta.tiene_incidencia_pendiente = Incidencia.objects.filter(
                asistencia=falta
        ).exists()

    return faltas

def get_incidencias(profesor_id):
    periodo = get_periodo_activo()
    profesor = Profesor.objects.get(id=profesor_id)
    faltas = get_faltas(profesor_id, periodo.fecha_inicio, periodo.fecha_fin)
    incidencias = Incidencia.objects.filter(
        solicitante=profesor.usuario,
        asistencia__in=faltas,
        estado="PENDIENTE",
    ).order_by("-asistencia__fecha", "-asistencia__id")

    return incidencias

def get_profesor_context(profesor_id):
    profesor = Profesor.objects.get(id=profesor_id)
    iniciales = f"{(profesor.usuario.nombre or 'U')[:1]}{(profesor.usuario.apellido or '')[:1]}".upper()
    nombre = profesor.usuario.get_full_name()
    puesto = "Profesor"
    estado = profesor.estado_laboral
    tiempo_institucion = (timezone.localdate() - profesor.fecha_ingreso).days if profesor.fecha_ingreso else None
    jornada_semanal = total_horas_periodo(profesor_id)
    experiencia = tiempo_institucion // 365 if tiempo_institucion is not None else None
    perfil_datos = [
        {"label": "Email", "value": profesor.usuario.email},
        {"label": "Teléfono", "value": profesor.telefono},
        {"label": "RFC", "value": profesor.rfc},
        {"label": "CURP", "value": profesor.curp},
        {"label": "Dirección", "value": profesor.direccion},
        {"label": "Fecha de ingreso", "value": profesor.fecha_ingreso.strftime("%d/%m/%Y") if profesor.fecha_ingreso else "N/A"},
        {"label": "Tipo de contrato", "value": profesor.tipo_contrato},
        {"label": "Costo por hora", "value": f"${format_money(profesor.costo_por_hora or Decimal(0))}"},
        {"label": "Departamentos", "value": ", ".join(profesor.departamentos.values_list("nombre", flat=True)) or "N/A"},
        {"label": "Planteles", "value": ", ".join(profesor.planteles.values_list("nombre", flat=True)) or "N/A"},
    ]

    return {
        "iniciales": iniciales,
        "nombre": nombre,
        "puesto": puesto,
        "estado": estado,
        "experiencia": experiencia,
        "jornada_semanal": f"{int(jornada_semanal)} horas" if jornada_semanal else "N/A",
        "perfil_datos": perfil_datos,
    }

def get_recibo_detalle(ultima_nomina, detalle_nomina):
        if not ultima_nomina:
            return []

        recibo_detalle = [
            {
                "concepto": "Salario base",
                "tipo_label": "PERCEPCIÓN",
                "tipo_clase": "percepcion",
                "importe": ultima_nomina.total_bruto,
            }
        ]
        recibo_detalle += [
            {
                "concepto": concepto.concepto.nombre,
                "tipo_label": concepto.concepto.tipo,
                "tipo_clase": concepto.concepto.tipo.lower(),
                "importe": concepto.monto,
            }
            for concepto in detalle_nomina
        ]
        recibo_detalle += [
            {
                "concepto": "Deducciones por faltas",
                "tipo_label": "DEDUCCIÓN",
                "tipo_clase": "deduccion",
                "importe": ultima_nomina.total_deducciones,
            },
            {
                "concepto": "NETO A PAGAR",
                "tipo_clase": "neto",
                "importe": ultima_nomina.total_neto,
            }
        ]

        return recibo_detalle
