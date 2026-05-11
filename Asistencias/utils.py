from datetime import datetime

from django.core.paginator import Paginator

from Contabilidad.utils import get_periodo_activo
from Profesores.models import Profesor


def get_profesor(user):
    return Profesor.objects.select_related("usuario").filter(usuario_id=user.id).first()


def parse_date(value):
    try:
        return datetime.strptime(value, "%Y-%m-%d").date()
    except (TypeError, ValueError):
        return None


def paginate(qs, page, page_size=20):
    try:
        page = int(page)
    except (TypeError, ValueError):
        page = 1

    try:
        page_size = int(page_size)
    except (TypeError, ValueError):
        page_size = 20

    paginator = Paginator(qs, page_size)
    return paginator.get_page(page)


def asistencia_to_json(asistencia):
    horario = asistencia.horario
    profesor = asistencia.profesor

    return {
        "id": asistencia.id,
        "profesor_id": profesor.id,
        "profesor_nombre": profesor.usuario.get_full_name(),
        "fecha": asistencia.fecha.isoformat(),
        "horario": f"{horario.hora_inicio:%H:%M} - {horario.hora_fin:%H:%M}",
        "estado": "CANCELADA" if asistencia.cancelada_institucional else asistencia.estado,
        "estado_label": "Cancelada" if asistencia.cancelada_institucional else asistencia.get_estado_display(),
        "observaciones": asistencia.observaciones or "",
        "cancelada_institucional": asistencia.cancelada_institucional,
    }


def incidencia_to_json(incidencia):
    asistencia = incidencia.asistencia
    profesor = asistencia.profesor

    return {
        "id": incidencia.id,
        "profesor_nombre": profesor.usuario.get_full_name(),
        "fecha_ausencia": asistencia.fecha.isoformat(),
        "tipo": incidencia.tipo,
        "tipo_label": incidencia.get_tipo_display(),
        "motivo": incidencia.motivo,
        "estado": incidencia.estado,
        "estado_label": incidencia.get_estado_display(),
    }


def obtener_periodo_actual():
    return get_periodo_activo()
