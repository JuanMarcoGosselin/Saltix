import json

from django.utils import timezone

from Asistencias.models import Asistencia, CorreccionAsistencia, Incidencia
from Asistencias.services.listados import (
    usuario_puede_ver_asistencia,
    usuario_puede_ver_incidencia,
)
from Asistencias.utils import get_profesor, obtener_periodo_actual
from core.models import BitacoraAuditoria


def _fecha_compensatoria():
    periodo = obtener_periodo_actual()
    hoy = timezone.localdate()

    if not periodo:
        return hoy
    if periodo.fecha_inicio <= hoy <= periodo.fecha_fin:
        return hoy
    return periodo.fecha_inicio


def _crear_compensatoria(asistencia, user, motivo):
    return Asistencia.objects.create(
        profesor=asistencia.profesor,
        fecha=_fecha_compensatoria(),
        hora_entrada=asistencia.hora_entrada,
        hora_salida=asistencia.hora_salida,
        estado="COMPENSATORIA",
        justificada=False,
        observaciones=motivo,
        horario=asistencia.horario,
        tolerancia_minutos=0,
        tipo_registro="COMPENSATORIA",
        creado_por=user,
    )


def _es_profesor(user):
    rol = getattr(getattr(user, "rol_id", None), "nombre", "") or ""
    return rol.lower() == "profesor"


def justificar_asistencia(user, asistencia_id, motivo):
    if not motivo:
        return False, "El motivo es obligatorio.", 400

    qs = Asistencia.objects.select_related("profesor", "profesor__usuario", "horario")

    if _es_profesor(user):
        profesor = get_profesor(user)
        if not profesor:
            return False, "Profesor no encontrado.", 403
        qs = qs.filter(profesor=profesor)

    asistencia = qs.filter(pk=asistencia_id).first()
    if not asistencia:
        return False, "Asistencia no encontrada.", 404
    if asistencia.cancelada_institucional:
        return False, "La asistencia esta cancelada institucionalmente.", 400
    if asistencia.estado != "FALTA":
        return False, "Solo se pueden justificar faltas.", 400

    if _es_profesor(user):
        existe = Incidencia.objects.filter(asistencia=asistencia, estado="PENDIENTE").exists()
        if existe:
            return True, "La justificacion ya esta en revision.", 200

        Incidencia.objects.create(
            asistencia=asistencia,
            motivo=motivo,
            tipo="FALTA",
            estado="PENDIENTE",
            solicitante=user,
        )
        return True, "Justificacion enviada.", 200

    if asistencia.justificada:
        return True, "La asistencia ya estaba justificada.", 200

    asistencia.justificada = True
    asistencia.estado = "JUSTIFICADA"
    asistencia.observaciones = motivo
    asistencia.creado_por = user
    asistencia.save(update_fields=["justificada", "estado", "observaciones", "creado_por"])
    return True, "Asistencia justificada.", 200


def aprobar_incidencia(incidencia_id, user):
    incidencia = (
        Incidencia.objects
        .select_related("asistencia", "asistencia__profesor", "asistencia__horario")
        .filter(id=incidencia_id)
        .first()
    )

    if not incidencia:
        return False, "Incidencia no encontrada.", 404
    if not usuario_puede_ver_incidencia(user, incidencia):
        return False, "Sin acceso a esta incidencia.", 403
    if incidencia.estado != "PENDIENTE":
        return False, "La incidencia ya fue resuelta.", 400

    compensatoria = _crear_compensatoria(incidencia.asistencia, user, incidencia.motivo)
    CorreccionAsistencia.objects.create(
        asistencia_original=incidencia.asistencia,
        asistencia_compensatoria=compensatoria,
        motivo=incidencia.motivo,
        aprobada_por=user,
        fecha_aprobacion=timezone.now(),
    )

    incidencia.estado = "APROBADA"
    incidencia.aprobador = user
    incidencia.fecha_de_resolucion = timezone.now()
    incidencia.save(update_fields=["estado", "aprobador", "fecha_de_resolucion"])

    return True, "Incidencia aprobada.", 200


def rechazar_incidencia(incidencia_id, user):
    incidencia = (
        Incidencia.objects
        .select_related("asistencia", "asistencia__profesor")
        .filter(id=incidencia_id)
        .first()
    )

    if not incidencia:
        return False, "Incidencia no encontrada.", 404
    if not usuario_puede_ver_incidencia(user, incidencia):
        return False, "Sin acceso a esta incidencia.", 403
    if incidencia.estado != "PENDIENTE":
        return False, "La incidencia ya fue resuelta.", 400

    incidencia.estado = "RECHAZADA"
    incidencia.aprobador = user
    incidencia.fecha_de_resolucion = timezone.now()
    incidencia.save(update_fields=["estado", "aprobador", "fecha_de_resolucion"])

    return True, "Incidencia rechazada.", 200


def cancelar_asistencia_institucional(asistencia_id, observaciones, user):
    asistencia = (
        Asistencia.objects
        .select_related("profesor")
        .filter(id=asistencia_id)
        .first()
    )

    if not asistencia:
        return False, "Asistencia no encontrada.", 404
    if not usuario_puede_ver_asistencia(user, asistencia):
        return False, "Sin acceso a esta asistencia.", 403
    if asistencia.cancelada_institucional:
        return False, "La asistencia ya fue cancelada.", 400

    asistencia.cancelada_institucional = True
    if observaciones:
        asistencia.observaciones = observaciones
    asistencia.save(update_fields=["cancelada_institucional", "observaciones"])

    return True, "Asistencia cancelada institucionalmente.", 200


def corregir_asistencia_jefatura(asistencia_id, estado, observaciones, user):
    estados_validos = {choice[0] for choice in Asistencia.ESTADOS}
    if estado not in estados_validos:
        return False, "Estado invalido.", 400

    asistencia = (
        Asistencia.objects
        .select_related("profesor")
        .filter(id=asistencia_id)
        .first()
    )
    if not asistencia:
        return False, "Asistencia no encontrada.", 404
    if not usuario_puede_ver_asistencia(user, asistencia):
        return False, "Sin acceso a esta asistencia.", 403

    valor_anterior = {
        "estado": asistencia.estado,
        "justificada": asistencia.justificada,
        "observaciones": asistencia.observaciones or "",
    }

    asistencia.estado = estado
    asistencia.justificada = estado == "JUSTIFICADA"
    asistencia.observaciones = observaciones
    asistencia.creado_por = user

    bitacora = BitacoraAuditoria.objects.create(
        usuario=user,
        modelo="Asistencia",
        objeto_id=asistencia.id,
        accion="CORRECCION_MANUAL",
        valor_anterior=json.dumps(valor_anterior, ensure_ascii=True),
        valor_nuevo=json.dumps({
            "estado": asistencia.estado,
            "justificada": asistencia.justificada,
            "observaciones": asistencia.observaciones or "",
        }, ensure_ascii=True),
    )

    asistencia.bitacora = bitacora
    asistencia.save(update_fields=["estado", "justificada", "observaciones", "creado_por", "bitacora"])

    Incidencia.objects.filter(asistencia=asistencia, estado="PENDIENTE").update(
        estado="RECHAZADA",
        aprobador=user,
        fecha_de_resolucion=timezone.now(),
    )

    return True, "Asistencia corregida correctamente.", 200
