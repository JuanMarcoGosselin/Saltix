from __future__ import annotations

from datetime import datetime

from django.utils import timezone

from Asistencias.models import Asistencia


def obtener_estado_clase(profesor, horario, fecha):
    """
    Determina el estado "real" de una clase programada (Horario) en una fecha.

    Reglas:
    - Si existe Asistencia: si está justificada => JUSTIFICADA, si no => asistencia.estado
    - Si no existe Asistencia: si ya terminó => FALTA, si no => PENDIENTE
    """
    profesor_id = getattr(profesor, "pk", profesor)
    horario_id = getattr(horario, "pk", horario)

    asistencias_prefetch = getattr(horario, "_asistencias_semana", None)
    if asistencias_prefetch is not None:
        for asistencia in asistencias_prefetch:
            if asistencia.fecha == fecha:
                return "JUSTIFICADA" if asistencia.justificada else asistencia.estado

    asistencia = (
        Asistencia.objects.filter(profesor_id=profesor_id, horario_id=horario_id, fecha=fecha)
        .only("estado", "justificada")
        .first()
    )
    if asistencia:
        return "JUSTIFICADA" if asistencia.justificada else asistencia.estado

    fin_naive = datetime.combine(fecha, horario.hora_fin)
    fin = timezone.make_aware(fin_naive, timezone.get_current_timezone())
    return "FALTA" if timezone.now() > fin else "PENDIENTE"


def obtener_color_estado(estado: str) -> str:
    return {
        "ASISTENCIA": "presente",
        "RETARDO": "retardo",
        "FALTA": "falta",
        "JUSTIFICADA": "justificada",
        "PENDIENTE": "pendiente",
    }.get(estado, "pendiente")

