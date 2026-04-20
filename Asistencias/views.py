import json
from datetime import datetime

from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.http import JsonResponse
from django.utils import timezone
from django.views.decorators.http import require_GET, require_POST

from Asistencias.models import Asistencia, Incidencia
from Asistencias.services import (
    apply_asistencia_filters,
    apply_incidencia_filters,
    get_user_departamentos,
    paginate_queryset,
    scope_asistencias_for_user,
    scope_incidencias_for_user,
    serialize_asistencia,
    serialize_incidencia,
)
from Profesores.models import Profesor
from core.decorators import requiere_rol
from core.models import BitacoraAuditoria


def _get_json_body(request):
    try:
        return json.loads(request.body or "{}")
    except json.JSONDecodeError:
        return None


def _json_or_post(request):
    if (request.content_type or "").startswith("application/json"):
        return _get_json_body(request)
    return request.POST


def _parse_date(value):
    if not value:
        return None
    try:
        return datetime.strptime(value, "%Y-%m-%d").date()
    except (TypeError, ValueError):
        return None


def _error(message, *, status=400):
    return JsonResponse({"ok": False, "error": message}, status=status)


def _success(message, **extra):
    payload = {"ok": True, "message": message}
    payload.update(extra)
    return JsonResponse(payload)


def _get_profesor_for_user(user):
    return Profesor.objects.select_related("usuario").filter(usuario_id=user.id).first()


def _user_can_manage_asistencia(user, asistencia: Asistencia) -> bool:
    scoped_ids = scope_asistencias_for_user(user).filter(id=asistencia.id).values_list("id", flat=True)
    return any(scoped_ids)


def _user_can_manage_incidencia(user, incidencia: Incidencia) -> bool:
    scoped_ids = scope_incidencias_for_user(user).filter(id=incidencia.id).values_list("id", flat=True)
    return any(scoped_ids)


def _paginated_response(page_data, serializer, **extra):
    payload = {
        "ok": True,
        "results": [serializer(item) for item in page_data.items],
        "count": page_data.count,
        "page": page_data.page,
        "page_size": page_data.page_size,
        "has_next": page_data.has_next,
        "has_prev": page_data.has_prev,
    }
    payload.update(extra)
    return JsonResponse(payload)


@require_POST
@login_required
@requiere_rol("Profesor", "jefatura", "administrador")
def justificar_asistencia(request):
    payload = _json_or_post(request)
    if payload is None:
        return _error("JSON invalido.")

    asistencia_id = payload.get("asistencia_id")
    motivo = (payload.get("motivo") or "").strip()

    if not motivo:
        return _error("El motivo de justificacion es obligatorio.")

    try:
        asistencia_id = int(asistencia_id)
    except (TypeError, ValueError):
        return _error("asistencia_id invalido.")

    qs = Asistencia.objects.select_related("profesor", "profesor__usuario", "horario")

    rol_nombre = getattr(getattr(request.user, "rol_id", None), "nombre", "") or ""
    es_profesor = rol_nombre.lower() == "profesor"

    if es_profesor:
        profesor = _get_profesor_for_user(request.user)
        if not profesor:
            return _error("Profesor no encontrado.", status=403)
        qs = qs.filter(profesor=profesor)

    with transaction.atomic():
        asistencia = qs.select_for_update().filter(pk=asistencia_id).first()
        if not asistencia:
            return _error("Asistencia no encontrada.", status=404)

        if asistencia.cancelada_institucional:
            return _error("La asistencia esta cancelada institucionalmente.")

        if es_profesor:
            if asistencia.estado != "FALTA":
                return _error("Solo se pueden justificar faltas.")

            if Incidencia.objects.filter(asistencia=asistencia, estado="PENDIENTE").exists():
                return JsonResponse({"ok": True, "already": True, "pending": True})

            Incidencia.objects.create(
                asistencia=asistencia,
                motivo=motivo,
                tipo="FALTA",
                estado="PENDIENTE",
                solicitante=request.user,
            )
            return JsonResponse({"ok": True, "pending": True})

        if asistencia.estado not in ("FALTA", "JUSTIFICADA"):
            return _error("Solo se pueden justificar faltas.")

        if asistencia.justificada or asistencia.estado == "JUSTIFICADA":
            return JsonResponse({"ok": True, "already": True})

        asistencia.justificada = True
        asistencia.estado = "JUSTIFICADA"
        asistencia.observaciones = motivo
        asistencia.save(update_fields=["justificada", "estado", "observaciones"])

    return JsonResponse({"ok": True})


@require_GET
@login_required
@requiere_rol("jefatura", "administrador")
def listar_asistencias_jefatura(request):
    qs = scope_asistencias_for_user(request.user)
    qs = apply_asistencia_filters(
        qs,
        profesor_id=request.GET.get("profesor_id"),
        estado=request.GET.get("estado"),
        fecha_inicio=_parse_date(request.GET.get("fecha_inicio")),
        fecha_fin=_parse_date(request.GET.get("fecha_fin")),
    )
    page_data = paginate_queryset(qs, page=request.GET.get("page"), page_size=request.GET.get("page_size"))
    return _paginated_response(page_data, serialize_asistencia)


@require_GET
@login_required
@requiere_rol("jefatura", "administrador")
def listar_incidencias_jefatura(request):
    scoped_qs = scope_incidencias_for_user(request.user)
    pending_total = scoped_qs.filter(estado="PENDIENTE").count()
    filtered_qs = apply_incidencia_filters(
        scoped_qs,
        profesor_id=request.GET.get("profesor_id"),
        estado=request.GET.get("estado"),
        fecha_inicio=_parse_date(request.GET.get("fecha_inicio")),
        fecha_fin=_parse_date(request.GET.get("fecha_fin")),
    )
    page_data = paginate_queryset(filtered_qs, page=request.GET.get("page"), page_size=request.GET.get("page_size"))
    return _paginated_response(page_data, serialize_incidencia, pending_total=pending_total)


@require_GET
@login_required
@requiere_rol("Profesor")
def listar_incidencias_profesor(request):
    profesor = _get_profesor_for_user(request.user)
    if not profesor:
        return _error("Profesor no encontrado.", status=404)

    qs = (
        Incidencia.objects.select_related(
            "asistencia",
            "asistencia__profesor",
            "asistencia__horario",
            "aprobador",
        )
        .filter(asistencia__profesor=profesor)
        .order_by("-fecha_solicitud", "-id")
    )
    page_data = paginate_queryset(qs, page=request.GET.get("page"), page_size=request.GET.get("page_size", 10))
    return _paginated_response(page_data, serialize_incidencia)


@require_POST
@login_required
@requiere_rol("jefatura", "administrador")
def aprobar_incidencia(request):
    payload = _json_or_post(request)
    if payload is None:
        return _error("JSON invalido.")

    try:
        incidencia_id = int(payload.get("incidencia_id"))
    except (TypeError, ValueError):
        return _error("incidencia_id invalido.")

    with transaction.atomic():
        incidencia = (
            Incidencia.objects.select_for_update()
            .select_related("asistencia", "asistencia__profesor", "asistencia__profesor__usuario")
            .filter(id=incidencia_id)
            .first()
        )
        if not incidencia:
            return _error("Incidencia no encontrada.", status=404)
        if not _user_can_manage_incidencia(request.user, incidencia):
            return _error("No tienes acceso a esta incidencia.", status=403)
        if incidencia.estado != "PENDIENTE":
            return _error("La incidencia ya fue resuelta.")

        asistencia = incidencia.asistencia
        incidencia.estado = "APROBADA"
        incidencia.aprobador = request.user
        incidencia.fecha_de_resolucion = timezone.now()
        incidencia.save(update_fields=["estado", "aprobador", "fecha_de_resolucion"])

        asistencia.justificada = True
        asistencia.estado = "JUSTIFICADA"
        asistencia.observaciones = incidencia.motivo
        asistencia.save(update_fields=["justificada", "estado", "observaciones"])

    return _success("Incidencia aprobada correctamente.", incidencia=serialize_incidencia(incidencia))


@require_POST
@login_required
@requiere_rol("jefatura", "administrador")
def rechazar_incidencia(request):
    payload = _json_or_post(request)
    if payload is None:
        return _error("JSON invalido.")

    try:
        incidencia_id = int(payload.get("incidencia_id"))
    except (TypeError, ValueError):
        return _error("incidencia_id invalido.")

    with transaction.atomic():
        incidencia = (
            Incidencia.objects.select_for_update()
            .select_related("asistencia", "asistencia__profesor", "asistencia__profesor__usuario")
            .filter(id=incidencia_id)
            .first()
        )
        if not incidencia:
            return _error("Incidencia no encontrada.", status=404)
        if not _user_can_manage_incidencia(request.user, incidencia):
            return _error("No tienes acceso a esta incidencia.", status=403)
        if incidencia.estado != "PENDIENTE":
            return _error("La incidencia ya fue resuelta.")

        incidencia.estado = "RECHAZADA"
        incidencia.aprobador = request.user
        incidencia.fecha_de_resolucion = timezone.now()
        incidencia.save(update_fields=["estado", "aprobador", "fecha_de_resolucion"])

    return _success("Incidencia rechazada correctamente.", incidencia=serialize_incidencia(incidencia))


@require_POST
@login_required
@requiere_rol("jefatura", "administrador")
def cancelar_asistencia_institucional(request):
    payload = _json_or_post(request)
    if payload is None:
        return _error("JSON invalido.")

    try:
        asistencia_id = int(payload.get("asistencia_id"))
    except (TypeError, ValueError):
        return _error("asistencia_id invalido.")

    with transaction.atomic():
        asistencia = (
            Asistencia.objects.select_for_update()
            .select_related("profesor", "profesor__usuario", "horario")
            .filter(id=asistencia_id)
            .first()
        )
        if not asistencia:
            return _error("Asistencia no encontrada.", status=404)
        if not _user_can_manage_asistencia(request.user, asistencia):
            return _error("No tienes acceso a esta asistencia.", status=403)
        if asistencia.cancelada_institucional:
            return _error("La asistencia ya fue cancelada institucionalmente.")

        asistencia.cancelada_institucional = True
        observaciones = (payload.get("observaciones") or "").strip()
        if observaciones:
            asistencia.observaciones = observaciones
        asistencia.save(update_fields=["cancelada_institucional", "observaciones"])

    return _success("Asistencia cancelada institucionalmente.", asistencia=serialize_asistencia(asistencia))


@require_POST
@login_required
@requiere_rol("jefatura", "administrador")
def corregir_asistencia_jefatura(request):
    payload = _json_or_post(request)
    if payload is None:
        return _error("JSON invalido.")

    try:
        asistencia_id = int(payload.get("asistencia_id"))
    except (TypeError, ValueError):
        return _error("asistencia_id invalido.")

    nuevo_estado = (payload.get("estado") or "").strip().upper()
    observaciones = (payload.get("observaciones") or "").strip()
    estados_validos = {choice[0] for choice in Asistencia.ESTADOS}

    if nuevo_estado not in estados_validos:
        return _error("Estado de asistencia invalido.")

    with transaction.atomic():
        asistencia = (
            Asistencia.objects.select_for_update()
            .select_related("profesor", "profesor__usuario", "horario")
            .filter(id=asistencia_id)
            .first()
        )
        if not asistencia:
            return _error("Asistencia no encontrada.", status=404)
        if not _user_can_manage_asistencia(request.user, asistencia):
            return _error("No tienes acceso a esta asistencia.", status=403)

        valor_anterior = json.dumps(
            {
                "estado": asistencia.estado,
                "justificada": asistencia.justificada,
                "observaciones": asistencia.observaciones or "",
            },
            ensure_ascii=True,
        )

        asistencia.estado = nuevo_estado
        asistencia.justificada = nuevo_estado == "JUSTIFICADA"
        asistencia.observaciones = observaciones
        asistencia.creado_por = request.user
        bitacora = BitacoraAuditoria.objects.create(
            usuario=request.user,
            modelo="Asistencia",
            objeto_id=asistencia.id,
            accion="CORRECCION_MANUAL",
            valor_anterior=valor_anterior,
            valor_nuevo=json.dumps(
                {
                    "estado": asistencia.estado,
                    "justificada": asistencia.justificada,
                    "observaciones": asistencia.observaciones or "",
                },
                ensure_ascii=True,
            ),
        )
        asistencia.bitacora = bitacora
        asistencia.save(update_fields=["estado", "justificada", "observaciones", "creado_por", "bitacora"])

    return _success("Asistencia corregida correctamente.", asistencia=serialize_asistencia(asistencia))
