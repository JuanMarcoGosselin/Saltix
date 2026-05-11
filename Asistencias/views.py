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


def _leer_json(request):
    try:
        return json.loads(request.body or "{}")
    except json.JSONDecodeError:
        return None


def _datos_request(request):
    if (request.content_type or "").startswith("application/json"):
        return _leer_json(request)
    return request.POST


def _get_profesor_for_user(user):
    return Profesor.objects.select_related("usuario").filter(usuario_id=user.id).first()


@require_POST
@login_required
@requiere_rol("Profesor", "jefatura", "administrador")
def justificar_asistencia(request):
    payload = _datos_request(request)
    if payload is None:
        return JsonResponse({"ok": False, "error": "JSON invalido."}, status=400)

    asistencia_id = payload.get("asistencia_id")
    motivo = (payload.get("motivo") or "").strip()

    if not motivo:
        return JsonResponse({"ok": False, "error": "El motivo de justificacion es obligatorio."}, status=400)

    try:
        asistencia_id = int(asistencia_id)
    except (TypeError, ValueError):
        return JsonResponse({"ok": False, "error": "asistencia_id invalido."}, status=400)

    qs = Asistencia.objects.select_related("profesor", "profesor__usuario", "horario")

    rol_nombre = getattr(getattr(request.user, "rol_id", None), "nombre", "") or ""
    es_profesor = rol_nombre.lower() == "profesor"

    if es_profesor:
        profesor = _get_profesor_for_user(request.user)
        if not profesor:
            return JsonResponse({"ok": False, "error": "Profesor no encontrado."}, status=403)
        qs = qs.filter(profesor=profesor)

    with transaction.atomic():
        asistencia = qs.select_for_update().filter(pk=asistencia_id).first()
        if not asistencia:
            return JsonResponse({"ok": False, "error": "Asistencia no encontrada."}, status=404)

        if asistencia.cancelada_institucional:
            return JsonResponse(
                {"ok": False, "error": "La asistencia esta cancelada institucionalmente."},
                status=400,
            )

        if es_profesor:
            if asistencia.estado != "FALTA":
                return JsonResponse({"ok": False, "error": "Solo se pueden justificar faltas."}, status=400)

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
            return JsonResponse({"ok": False, "error": "Solo se pueden justificar faltas."}, status=400)

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
    fecha_inicio = None
    fecha_fin = None
    fecha_inicio_raw = request.GET.get("fecha_inicio")
    fecha_fin_raw = request.GET.get("fecha_fin")
    if fecha_inicio_raw:
        try:
            fecha_inicio = datetime.strptime(fecha_inicio_raw, "%Y-%m-%d").date()
        except (TypeError, ValueError):
            fecha_inicio = None
    if fecha_fin_raw:
        try:
            fecha_fin = datetime.strptime(fecha_fin_raw, "%Y-%m-%d").date()
        except (TypeError, ValueError):
            fecha_fin = None

    qs = apply_asistencia_filters(
        qs,
        profesor_id=request.GET.get("profesor_id"),
        estado=request.GET.get("estado"),
        fecha_inicio=fecha_inicio,
        fecha_fin=fecha_fin,
    )
    page_data = paginate_queryset(qs, page=request.GET.get("page"), page_size=request.GET.get("page_size"))
    resultados = [serialize_asistencia(item) for item in page_data.items]
    return JsonResponse(
        {
            "ok": True,
            "results": resultados,
            "count": page_data.count,
            "page": page_data.page,
            "page_size": page_data.page_size,
            "has_next": page_data.has_next,
            "has_prev": page_data.has_prev,
        }
    )


@require_GET
@login_required
@requiere_rol("jefatura", "administrador")
def listar_incidencias_jefatura(request):
    scoped_qs = scope_incidencias_for_user(request.user)
    pending_total = scoped_qs.filter(estado="PENDIENTE").count()
    fecha_inicio = None
    fecha_fin = None
    fecha_inicio_raw = request.GET.get("fecha_inicio")
    fecha_fin_raw = request.GET.get("fecha_fin")
    if fecha_inicio_raw:
        try:
            fecha_inicio = datetime.strptime(fecha_inicio_raw, "%Y-%m-%d").date()
        except (TypeError, ValueError):
            fecha_inicio = None
    if fecha_fin_raw:
        try:
            fecha_fin = datetime.strptime(fecha_fin_raw, "%Y-%m-%d").date()
        except (TypeError, ValueError):
            fecha_fin = None

    filtered_qs = apply_incidencia_filters(
        scoped_qs,
        profesor_id=request.GET.get("profesor_id"),
        estado=request.GET.get("estado"),
        fecha_inicio=fecha_inicio,
        fecha_fin=fecha_fin,
    )
    page_data = paginate_queryset(filtered_qs, page=request.GET.get("page"), page_size=request.GET.get("page_size"))
    resultados = [serialize_incidencia(item) for item in page_data.items]
    return JsonResponse(
        {
            "ok": True,
            "results": resultados,
            "count": page_data.count,
            "page": page_data.page,
            "page_size": page_data.page_size,
            "has_next": page_data.has_next,
            "has_prev": page_data.has_prev,
            "pending_total": pending_total,
        }
    )


@require_GET
@login_required
@requiere_rol("Profesor")
def listar_incidencias_profesor(request):
    profesor = _get_profesor_for_user(request.user)
    if not profesor:
        return JsonResponse({"ok": False, "error": "Profesor no encontrado."}, status=404)

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
    resultados = [serialize_incidencia(item) for item in page_data.items]
    return JsonResponse(
        {
            "ok": True,
            "results": resultados,
            "count": page_data.count,
            "page": page_data.page,
            "page_size": page_data.page_size,
            "has_next": page_data.has_next,
            "has_prev": page_data.has_prev,
        }
    )


@require_POST
@login_required
@requiere_rol("jefatura", "administrador")
def aprobar_incidencia(request):
    payload = _datos_request(request)
    if payload is None:
        return JsonResponse({"ok": False, "error": "JSON invalido."}, status=400)

    try:
        incidencia_id = int(payload.get("incidencia_id"))
    except (TypeError, ValueError):
        return JsonResponse({"ok": False, "error": "incidencia_id invalido."}, status=400)

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
            return JsonResponse({"ok": False, "error": "No tienes acceso a esta incidencia."}, status=403)
        if incidencia.estado != "PENDIENTE":
            return JsonResponse({"ok": False, "error": "La incidencia ya fue resuelta."}, status=400)

        asistencia = incidencia.asistencia
        incidencia.estado = "APROBADA"
        incidencia.aprobador = request.user
        incidencia.fecha_de_resolucion = timezone.now()
        incidencia.save(update_fields=["estado", "aprobador", "fecha_de_resolucion"])

        asistencia.justificada = True
        asistencia.estado = "JUSTIFICADA"
        asistencia.observaciones = incidencia.motivo
        asistencia.save(update_fields=["justificada", "estado", "observaciones"])

    return JsonResponse(
        {
            "ok": True,
            "message": "Incidencia aprobada correctamente.",
            "incidencia": serialize_incidencia(incidencia),
        }
    )


@require_POST
@login_required
@requiere_rol("jefatura", "administrador")
def rechazar_incidencia(request):
    payload = _datos_request(request)
    if payload is None:
        return JsonResponse({"ok": False, "error": "JSON invalido."}, status=400)

    try:
        incidencia_id = int(payload.get("incidencia_id"))
    except (TypeError, ValueError):
        return JsonResponse({"ok": False, "error": "incidencia_id invalido."}, status=400)

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
            return JsonResponse({"ok": False, "error": "No tienes acceso a esta incidencia."}, status=403)
        if incidencia.estado != "PENDIENTE":
            return JsonResponse({"ok": False, "error": "La incidencia ya fue resuelta."}, status=400)

        incidencia.estado = "RECHAZADA"
        incidencia.aprobador = request.user
        incidencia.fecha_de_resolucion = timezone.now()
        incidencia.save(update_fields=["estado", "aprobador", "fecha_de_resolucion"])

    return JsonResponse(
        {
            "ok": True,
            "message": "Incidencia rechazada correctamente.",
            "incidencia": serialize_incidencia(incidencia),
        }
    )


@require_POST
@login_required
@requiere_rol("jefatura", "administrador")
def cancelar_asistencia_institucional(request):
    payload = _datos_request(request)
    if payload is None:
        return JsonResponse({"ok": False, "error": "JSON invalido."}, status=400)

    try:
        asistencia_id = int(payload.get("asistencia_id"))
    except (TypeError, ValueError):
        return JsonResponse({"ok": False, "error": "asistencia_id invalido."}, status=400)

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
            return JsonResponse({"ok": False, "error": "No tienes acceso a esta asistencia."}, status=403)
        if asistencia.cancelada_institucional:
            return JsonResponse(
                {"ok": False, "error": "La asistencia ya fue cancelada institucionalmente."},
                status=400,
            )

        asistencia.cancelada_institucional = True
        observaciones = (payload.get("observaciones") or "").strip()
        if observaciones:
            asistencia.observaciones = observaciones
        asistencia.save(update_fields=["cancelada_institucional", "observaciones"])

    return JsonResponse(
        {
            "ok": True,
            "message": "Asistencia cancelada institucionalmente.",
            "asistencia": serialize_asistencia(asistencia),
        }
    )


@require_POST
@login_required
@requiere_rol("jefatura", "administrador")
def corregir_asistencia_jefatura(request):
    payload = _datos_request(request)
    if payload is None:
        return JsonResponse({"ok": False, "error": "JSON invalido."}, status=400)

    try:
        asistencia_id = int(payload.get("asistencia_id"))
    except (TypeError, ValueError):
        return JsonResponse({"ok": False, "error": "asistencia_id invalido."}, status=400)

    nuevo_estado = (payload.get("estado") or "").strip().upper()
    observaciones = (payload.get("observaciones") or "").strip()
    estados_validos = {choice[0] for choice in Asistencia.ESTADOS}

    if nuevo_estado not in estados_validos:
        return JsonResponse({"ok": False, "error": "Estado de asistencia invalido."}, status=400)

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
            return JsonResponse({"ok": False, "error": "No tienes acceso a esta asistencia."}, status=403)

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

    return JsonResponse(
        {
            "ok": True,
            "message": "Asistencia corregida correctamente.",
            "asistencia": serialize_asistencia(asistencia),
        }
    )
