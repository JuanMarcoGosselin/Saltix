import json
from datetime import datetime

from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.http import JsonResponse
from django.utils import timezone
from django.views.decorators.http import require_GET, require_POST

from Asistencias.models import Asistencia, Incidencia
from Profesores.models import Profesor
from core.decorators import requiere_rol
from core.models import BitacoraAuditoria


# ── Helpers ────────────────────────────────────────────────────────────────────

def leer_json(request):
    try:
        return json.loads(request.body or "{}")
    except json.JSONDecodeError:
        return None


def datos_request(request):
    if (request.content_type or "").startswith("application/json"):
        return leer_json(request)
    return request.POST


def get_profesor(user):
    return Profesor.objects.select_related("usuario").filter(usuario_id=user.id).first()


def es_rol_profesor(user):
    rol = getattr(getattr(user, "rol_id", None), "nombre", "") or ""
    return rol.lower() == "profesor"


def parsear_fecha(valor):
    try:
        return datetime.strptime(valor, "%Y-%m-%d").date()
    except (TypeError, ValueError):
        return None


def crear_asistencia_compensatoria(asistencia_original, aprobador):
    return Asistencia.objects.create(
        profesor=asistencia_original.profesor,
        fecha=timezone.localdate(),
        hora_entrada=asistencia_original.hora_entrada,
        hora_salida=asistencia_original.hora_salida,
        estado="COMPENSATORIA",
        justificada=False,
        observaciones=f"Compensatoria por falta del {asistencia_original.fecha}",
        horario=asistencia_original.horario,
        tolerancia_minutos=0,
        tipo_registro="COMPENSATORIA",
        creado_por=aprobador,
        asistencia_original=asistencia_original,
    )


# ── Justificaciones ────────────────────────────────────────────────────────────

@require_POST
@login_required
@requiere_rol("Profesor", "jefatura", "administrador")
def justificar_asistencia(request):
    payload = datos_request(request)
    if payload is None:
        return JsonResponse({"ok": False, "error": "JSON inválido."}, status=400)

    motivo = (payload.get("motivo") or "").strip()
    if not motivo:
        return JsonResponse({"ok": False, "error": "El motivo es obligatorio."}, status=400)

    try:
        asistencia_id = int(payload.get("asistencia_id"))
    except (TypeError, ValueError):
        return JsonResponse({"ok": False, "error": "asistencia_id inválido."}, status=400)

    es_profesor = es_rol_profesor(request.user)
    qs = Asistencia.objects.select_related("profesor", "profesor__usuario", "horario")

    if es_profesor:
        profesor = get_profesor(request.user)
        if not profesor:
            return JsonResponse({"ok": False, "error": "Profesor no encontrado."}, status=403)
        qs = qs.filter(profesor=profesor)

    with transaction.atomic():
        asistencia = qs.select_for_update().filter(pk=asistencia_id).first()

        if not asistencia:
            return JsonResponse({"ok": False, "error": "Asistencia no encontrada."}, status=404)

        if asistencia.cancelada_institucional:
            return JsonResponse({"ok": False, "error": "La asistencia está cancelada institucionalmente."}, status=400)

        # Flujo del profesor: crea una Incidencia pendiente para que jefatura apruebe.
        # Al aprobar, jefatura generará la asistencia compensatoria.
        if es_profesor:
            if asistencia.estado != "FALTA":
                return JsonResponse({"ok": False, "error": "Solo se pueden justificar faltas."}, status=400)

            ya_existe = Incidencia.objects.filter(asistencia=asistencia, estado="PENDIENTE").exists()
            if ya_existe:
                return JsonResponse({"ok": True, "already": True, "pending": True})

            Incidencia.objects.create(
                asistencia=asistencia,
                motivo=motivo,
                tipo="FALTA",
                estado="PENDIENTE",
                solicitante=request.user,
            )
            return JsonResponse({"ok": True, "pending": True})

        # Flujo de jefatura/admin: justifica directamente sin pasar por incidencia.
        # Para correcciones rápidas — no genera compensatoria.
        if asistencia.estado not in ("FALTA", "JUSTIFICADA"):
            return JsonResponse({"ok": False, "error": "Solo se pueden justificar faltas."}, status=400)

        if asistencia.justificada or asistencia.estado == "JUSTIFICADA":
            return JsonResponse({"ok": True, "already": True})

        asistencia.justificada = True
        asistencia.estado = "JUSTIFICADA"
        asistencia.observaciones = motivo
        asistencia.save(update_fields=["justificada", "estado", "observaciones"])

    return JsonResponse({"ok": True})


# ── Vistas de jefatura: asistencias ───────────────────────────────────────────

@require_GET
@login_required
@requiere_rol("jefatura", "administrador")
def listar_asistencias_jefatura(request):
    qs = scope_asistencias_for_user(request.user)

    qs = apply_asistencia_filters(
        qs,
        profesor_id=request.GET.get("profesor_id"),
        estado=request.GET.get("estado"),
        fecha_inicio=parsear_fecha(request.GET.get("fecha_inicio")),
        fecha_fin=parsear_fecha(request.GET.get("fecha_fin")),
    )

    page_data = paginate_queryset(qs, page=request.GET.get("page"), page_size=request.GET.get("page_size"))

    return JsonResponse({
        "ok": True,
        "results": [serialize_asistencia(a) for a in page_data.items],
        "count": page_data.count,
        "page": page_data.page,
        "page_size": page_data.page_size,
        "has_next": page_data.has_next,
        "has_prev": page_data.has_prev,
    })


@require_POST
@login_required
@requiere_rol("jefatura", "administrador")
def cancelar_asistencia_institucional(request):
    payload = datos_request(request)
    if payload is None:
        return JsonResponse({"ok": False, "error": "JSON inválido."}, status=400)

    try:
        asistencia_id = int(payload.get("asistencia_id"))
    except (TypeError, ValueError):
        return JsonResponse({"ok": False, "error": "asistencia_id inválido."}, status=400)

    with transaction.atomic():
        asistencia = (
            Asistencia.objects.select_for_update()
            .select_related("profesor", "profesor__usuario", "horario")
            .filter(id=asistencia_id)
            .first()
        )

        if not asistencia:
            return JsonResponse({"ok": False, "error": "Asistencia no encontrada."}, status=404)
        if not scope_asistencias_for_user(request.user).filter(id=asistencia.id).exists():
            return JsonResponse({"ok": False, "error": "Sin acceso a esta asistencia."}, status=403)
        if asistencia.cancelada_institucional:
            return JsonResponse({"ok": False, "error": "La asistencia ya fue cancelada."}, status=400)

        asistencia.cancelada_institucional = True
        observaciones = (payload.get("observaciones") or "").strip()
        if observaciones:
            asistencia.observaciones = observaciones
        asistencia.save(update_fields=["cancelada_institucional", "observaciones"])

    return JsonResponse({
        "ok": True,
        "message": "Asistencia cancelada institucionalmente.",
        "asistencia": serialize_asistencia(asistencia),
    })


@require_POST
@login_required
@requiere_rol("jefatura", "administrador")
def corregir_asistencia_jefatura(request):
    payload = datos_request(request)
    if payload is None:
        return JsonResponse({"ok": False, "error": "JSON inválido."}, status=400)

    try:
        asistencia_id = int(payload.get("asistencia_id"))
    except (TypeError, ValueError):
        return JsonResponse({"ok": False, "error": "asistencia_id inválido."}, status=400)

    nuevo_estado = (payload.get("estado") or "").strip().upper()
    observaciones = (payload.get("observaciones") or "").strip()
    estados_validos = {choice[0] for choice in Asistencia.ESTADOS}

    if nuevo_estado not in estados_validos:
        return JsonResponse({"ok": False, "error": "Estado inválido."}, status=400)

    with transaction.atomic():
        asistencia = (
            Asistencia.objects.select_for_update()
            .select_related("profesor", "profesor__usuario", "horario")
            .filter(id=asistencia_id)
            .first()
        )

        if not asistencia:
            return JsonResponse({"ok": False, "error": "Asistencia no encontrada."}, status=404)
        if not scope_asistencias_for_user(request.user).filter(id=asistencia.id).exists():
            return JsonResponse({"ok": False, "error": "Sin acceso a esta asistencia."}, status=403)

        valor_anterior = {
            "estado": asistencia.estado,
            "justificada": asistencia.justificada,
            "observaciones": asistencia.observaciones or "",
        }

        asistencia.estado = nuevo_estado
        asistencia.justificada = nuevo_estado == "JUSTIFICADA"
        asistencia.observaciones = observaciones
        asistencia.creado_por = request.user

        bitacora = BitacoraAuditoria.objects.create(
            usuario=request.user,
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

        # Cancelar incidencias pendientes para no dejarlas huérfanas
        Incidencia.objects.filter(asistencia=asistencia, estado="PENDIENTE").update(
            estado="RECHAZADA",
            aprobador=request.user,
            fecha_de_resolucion=timezone.now(),
        )

    return JsonResponse({
        "ok": True,
        "message": "Asistencia corregida correctamente.",
        "asistencia": serialize_asistencia(asistencia),
    })


# ── Vistas de jefatura: incidencias ───────────────────────────────────────────

@require_GET
@login_required
@requiere_rol("jefatura", "administrador")
def listar_incidencias_jefatura(request):
    qs = scope_incidencias_for_user(request.user)
    pending_total = qs.filter(estado="PENDIENTE").count()

    qs = apply_incidencia_filters(
        qs,
        profesor_id=request.GET.get("profesor_id"),
        estado=request.GET.get("estado"),
        fecha_inicio=parsear_fecha(request.GET.get("fecha_inicio")),
        fecha_fin=parsear_fecha(request.GET.get("fecha_fin")),
    )

    page_data = paginate_queryset(qs, page=request.GET.get("page"), page_size=request.GET.get("page_size"))

    return JsonResponse({
        "ok": True,
        "results": [serialize_incidencia(i) for i in page_data.items],
        "count": page_data.count,
        "page": page_data.page,
        "page_size": page_data.page_size,
        "has_next": page_data.has_next,
        "has_prev": page_data.has_prev,
        "pending_total": pending_total,
    })

@require_POST
@login_required
@requiere_rol("jefatura", "administrador")
def aprobar_incidencia(request):
    payload = datos_request(request)
    if payload is None:
        return JsonResponse({"ok": False, "error": "JSON inválido."}, status=400)

    try:
        incidencia_id = int(payload.get("incidencia_id"))
    except (TypeError, ValueError):
        return JsonResponse({"ok": False, "error": "incidencia_id inválido."}, status=400)

    with transaction.atomic():
        incidencia = (
            Incidencia.objects.select_for_update()
            .select_related(
                "asistencia",
                "asistencia__profesor",
                "asistencia__profesor__usuario",
                "asistencia__horario",
            )
            .filter(id=incidencia_id)
            .first()
        )

        if not incidencia:
            return JsonResponse({"ok": False, "error": "Incidencia no encontrada."}, status=404)
        if not scope_incidencias_for_user(request.user).filter(id=incidencia.id).exists():
            return JsonResponse({"ok": False, "error": "Sin acceso a esta incidencia."}, status=403)
        if incidencia.estado != "PENDIENTE":
            return JsonResponse({"ok": False, "error": "La incidencia ya fue resuelta."}, status=400)

        # Crear la asistencia compensatoria en el periodo activo.
        # La falta original NO se toca — sigue siendo FALTA en su periodo.
        # La compensatoria suma horas al periodo donde se registra (hoy).
        compensatoria = crear_asistencia_compensatoria(
            asistencia_original=incidencia.asistencia,
            aprobador=request.user,
        )

        incidencia.estado = "APROBADA"
        incidencia.aprobador = request.user
        incidencia.fecha_de_resolucion = timezone.now()
        incidencia.asistencia_compensatoria = compensatoria
        incidencia.save(update_fields=["estado", "aprobador", "fecha_de_resolucion", "asistencia_compensatoria"])

    return JsonResponse({
        "ok": True,
        "message": "Incidencia aprobada. Se creó una asistencia compensatoria.",
        "incidencia": serialize_incidencia(incidencia),
        "compensatoria": serialize_asistencia(compensatoria),
    })


@require_POST
@login_required
@requiere_rol("jefatura", "administrador")
def rechazar_incidencia(request):
    payload = datos_request(request)
    if payload is None:
        return JsonResponse({"ok": False, "error": "JSON inválido."}, status=400)

    try:
        incidencia_id = int(payload.get("incidencia_id"))
    except (TypeError, ValueError):
        return JsonResponse({"ok": False, "error": "incidencia_id inválido."}, status=400)

    with transaction.atomic():
        incidencia = (
            Incidencia.objects.select_for_update()
            .select_related("asistencia", "asistencia__profesor", "asistencia__profesor__usuario")
            .filter(id=incidencia_id)
            .first()
        )

        if not incidencia:
            return JsonResponse({"ok": False, "error": "Incidencia no encontrada."}, status=404)
        if not scope_incidencias_for_user(request.user).filter(id=incidencia.id).exists():
            return JsonResponse({"ok": False, "error": "Sin acceso a esta incidencia."}, status=403)
        if incidencia.estado != "PENDIENTE":
            return JsonResponse({"ok": False, "error": "La incidencia ya fue resuelta."}, status=400)

        incidencia.estado = "RECHAZADA"
        incidencia.aprobador = request.user
        incidencia.fecha_de_resolucion = timezone.now()
        incidencia.save(update_fields=["estado", "aprobador", "fecha_de_resolucion"])

    return JsonResponse({
        "ok": True,
        "message": "Incidencia rechazada.",
        "incidencia": serialize_incidencia(incidencia),
    })