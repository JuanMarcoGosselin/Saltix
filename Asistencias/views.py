import json

from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.http import JsonResponse
from django.views.decorators.http import require_POST

from Asistencias.models import Asistencia, Incidencia
from core.decorators import requiere_rol
from Profesores.models import Profesor


def _get_json_body(request):
    try:
        return json.loads(request.body or "{}")
    except json.JSONDecodeError:
        return None


@require_POST
@login_required
@requiere_rol("Profesor", "jefatura", "administrador")
def justificar_asistencia(request):
    payload = _get_json_body(request) if request.content_type.startswith("application/json") else request.POST
    if payload is None:
        return JsonResponse({"error": "JSON inválido."}, status=400)

    asistencia_id = payload.get("asistencia_id")
    motivo = (payload.get("motivo") or "").strip()

    if not motivo:
        return JsonResponse({"error": "El motivo de justificación es obligatorio."}, status=400)

    try:
        asistencia_id = int(asistencia_id)
    except (TypeError, ValueError):
        return JsonResponse({"error": "asistencia_id inválido."}, status=400)

    qs = Asistencia.objects.select_related("profesor", "profesor__usuario", "horario")

    rol_nombre = getattr(getattr(request.user, "rol_id", None), "nombre", "") or ""
    es_profesor = rol_nombre.lower() == "profesor"

    if es_profesor:
        try:
            profesor = Profesor.objects.get(usuario=request.user.id)
        except Profesor.DoesNotExist:
            return JsonResponse({"error": "Profesor no encontrado."}, status=403)
        qs = qs.filter(profesor=profesor)

    with transaction.atomic():
        asistencia = qs.select_for_update().filter(pk=asistencia_id).first()
        if not asistencia:
            return JsonResponse({"error": "Asistencia no encontrada."}, status=404)

        if asistencia.cancelada_institucional:
            return JsonResponse({"error": "La asistencia está cancelada institucionalmente."}, status=400)

        if es_profesor:
            # El profesor solo solicita una incidencia; la asistencia NO se marca como justificada
            # hasta que la incidencia sea aprobada.
            if asistencia.estado != "FALTA":
                return JsonResponse({"error": "Solo se pueden justificar faltas."}, status=400)

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

        # jefatura/administrador: comportamiento legado (justifica directamente)
        if asistencia.estado not in ("FALTA", "JUSTIFICADA"):
            return JsonResponse({"error": "Solo se pueden justificar faltas."}, status=400)

        if asistencia.justificada or asistencia.estado == "JUSTIFICADA":
            return JsonResponse({"ok": True, "already": True})

        asistencia.justificada = True
        asistencia.estado = "JUSTIFICADA"
        asistencia.observaciones = motivo
        asistencia.save(update_fields=["justificada", "estado", "observaciones"])

    return JsonResponse({"ok": True})
