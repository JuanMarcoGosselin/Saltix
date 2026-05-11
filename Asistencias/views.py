import json

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_GET, require_POST

from Asistencias.services import incidencias, listados
from Asistencias.utils import (
    asistencia_to_json,
    get_profesor,
    incidencia_to_json,
    paginate,
)
from core.decorators import requiere_rol


def _payload(request):
    if not (request.content_type or "").startswith("application/json"):
        return request.POST

    try:
        return json.loads(request.body or "{}")
    except json.JSONDecodeError:
        return None


def _int(value):
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def _service_response(result):
    ok, message, status = result
    return JsonResponse({"ok": ok, "message": message}, status=status)


@require_POST
@login_required
@requiere_rol("Profesor", "jefatura", "administrador")
def justificar_asistencia(request):
    data = _payload(request)
    if data is None:
        return JsonResponse({"ok": False, "message": "JSON invalido."}, status=400)

    asistencia_id = _int(data.get("asistencia_id"))
    motivo = (data.get("motivo") or "").strip()
    if not asistencia_id:
        return JsonResponse({"ok": False, "message": "asistencia_id invalido."}, status=400)

    return _service_response(
        incidencias.justificar_asistencia(request.user, asistencia_id, motivo)
    )


@require_GET
@login_required
@requiere_rol("jefatura", "administrador")
def listar_asistencias_jefatura(request):
    page = paginate(
        listados.listar_asistencias(request.GET, request.user),
        request.GET.get("page"),
        request.GET.get("page_size", 20),
    )

    return JsonResponse({
        "ok": True,
        "results": [asistencia_to_json(asistencia) for asistencia in page],
        "page": page.number,
        "has_next": page.has_next(),
        "has_prev": page.has_previous(),
    })


@require_GET
@login_required
@requiere_rol("jefatura", "administrador")
def listar_incidencias_jefatura(request):
    qs = listados.listar_incidencias(request.GET, request.user)
    pending_total = listados.listar_incidencias({}, request.user).filter(estado="PENDIENTE").count()
    page = paginate(qs, request.GET.get("page"), request.GET.get("page_size", 20))

    return JsonResponse({
        "ok": True,
        "results": [incidencia_to_json(incidencia) for incidencia in page],
        "page": page.number,
        "has_next": page.has_next(),
        "has_prev": page.has_previous(),
        "pending_total": pending_total,
    })


@require_GET
@login_required
@requiere_rol("Profesor")
def listar_incidencias_profesor(request):
    profesor = get_profesor(request.user)
    if not profesor:
        return JsonResponse({"ok": False, "message": "Profesor no encontrado."}, status=404)

    page = paginate(
        listados.listar_incidencias_profesor(profesor),
        request.GET.get("page"),
        request.GET.get("page_size", 10),
    )

    return JsonResponse({
        "ok": True,
        "results": [incidencia_to_json(incidencia) for incidencia in page],
        "page": page.number,
        "has_next": page.has_next(),
        "has_prev": page.has_previous(),
    })


@require_POST
@login_required
@requiere_rol("jefatura", "administrador")
def aprobar_incidencia(request):
    data = _payload(request)
    if data is None:
        return JsonResponse({"ok": False, "message": "JSON invalido."}, status=400)

    incidencia_id = _int(data.get("incidencia_id"))
    if not incidencia_id:
        return JsonResponse({"ok": False, "message": "incidencia_id invalido."}, status=400)

    return _service_response(incidencias.aprobar_incidencia(incidencia_id, request.user))


@require_POST
@login_required
@requiere_rol("jefatura", "administrador")
def rechazar_incidencia(request):
    data = _payload(request)
    if data is None:
        return JsonResponse({"ok": False, "message": "JSON invalido."}, status=400)

    incidencia_id = _int(data.get("incidencia_id"))
    if not incidencia_id:
        return JsonResponse({"ok": False, "message": "incidencia_id invalido."}, status=400)

    return _service_response(incidencias.rechazar_incidencia(incidencia_id, request.user))


@require_POST
@login_required
@requiere_rol("jefatura", "administrador")
def cancelar_asistencia_institucional(request):
    data = _payload(request)
    if data is None:
        return JsonResponse({"ok": False, "message": "JSON invalido."}, status=400)

    asistencia_id = _int(data.get("asistencia_id"))
    if not asistencia_id:
        return JsonResponse({"ok": False, "message": "asistencia_id invalido."}, status=400)

    observaciones = (data.get("observaciones") or "").strip()
    return _service_response(
        incidencias.cancelar_asistencia_institucional(asistencia_id, observaciones, request.user)
    )


@require_POST
@login_required
@requiere_rol("jefatura", "administrador")
def corregir_asistencia_jefatura(request):
    data = _payload(request)
    if data is None:
        return JsonResponse({"ok": False, "message": "JSON invalido."}, status=400)

    asistencia_id = _int(data.get("asistencia_id"))
    if not asistencia_id:
        return JsonResponse({"ok": False, "message": "asistencia_id invalido."}, status=400)

    estado = (data.get("estado") or "").strip().upper()
    observaciones = (data.get("observaciones") or "").strip()

    return _service_response(
        incidencias.corregir_asistencia_jefatura(
            asistencia_id,
            estado,
            observaciones,
            request.user,
        )
    )
