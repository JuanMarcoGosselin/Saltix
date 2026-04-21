from django.core.paginator import Paginator

from Asistencias.models import Asistencia, Incidencia
from users.models import Departamento


class PageData:
    def __init__(self, items, count, page, page_size, has_next, has_prev):
        self.items = items
        self.count = count
        self.page = page
        self.page_size = page_size
        self.has_next = has_next
        self.has_prev = has_prev


def _safe_page_size(page_size, default=10, max_size=100):
    try:
        size = int(page_size or default)
    except (TypeError, ValueError):
        return default
    if size < 1:
        size = 1
    if size > max_size:
        size = max_size
    return size


def _safe_page(page, default=1):
    try:
        value = int(page or default)
    except (TypeError, ValueError):
        return default
    if value < 1:
        return 1
    return value


def is_admin(user):
    rol = getattr(getattr(user, "rol_id", None), "nombre", "") or ""
    return rol.lower() == "administrador"


def is_jefatura(user):
    rol = getattr(getattr(user, "rol_id", None), "nombre", "") or ""
    return rol.lower() == "jefatura"


def get_user_departamentos(user):
    return Departamento.objects.select_related("plantel", "jefe").filter(jefe=user, activo=True)


def scope_asistencias_for_user(user):
    qs = Asistencia.objects.select_related(
        "profesor",
        "profesor__usuario",
        "horario",
        "creado_por",
    ).order_by("-fecha", "-id")
    if is_admin(user):
        return qs
    dept_ids = list(get_user_departamentos(user).values_list("id", flat=True))
    return qs.filter(profesor__departamentos__id__in=dept_ids).distinct()


def scope_incidencias_for_user(user):
    qs = Incidencia.objects.select_related(
        "asistencia",
        "asistencia__profesor",
        "asistencia__profesor__usuario",
        "asistencia__horario",
        "solicitante",
        "aprobador",
    ).order_by("-fecha_solicitud", "-id")
    if is_admin(user):
        return qs
    dept_ids = list(get_user_departamentos(user).values_list("id", flat=True))
    return qs.filter(asistencia__profesor__departamentos__id__in=dept_ids).distinct()


def apply_asistencia_filters(
    qs,
    profesor_id=None,
    estado=None,
    fecha_inicio=None,
    fecha_fin=None,
):
    if profesor_id:
        qs = qs.filter(profesor_id=profesor_id)
    if estado:
        estado = estado.strip().upper()
        if estado == "CANCELADA":
            qs = qs.filter(cancelada_institucional=True)
        else:
            estados_validos = []
            for choice in Asistencia.ESTADOS:
                estados_validos.append(choice[0])
            if estado in estados_validos:
                qs = qs.filter(estado=estado)
    if fecha_inicio:
        qs = qs.filter(fecha__gte=fecha_inicio)
    if fecha_fin:
        qs = qs.filter(fecha__lte=fecha_fin)
    return qs


def apply_incidencia_filters(
    qs,
    profesor_id=None,
    estado=None,
    fecha_inicio=None,
    fecha_fin=None,
):
    if profesor_id:
        qs = qs.filter(asistencia__profesor_id=profesor_id)
    if estado:
        estado = estado.strip().upper()
        estados_validos = []
        for choice in Incidencia.ESTADOS:
            estados_validos.append(choice[0])
        if estado in estados_validos:
            qs = qs.filter(estado=estado)
    if fecha_inicio:
        qs = qs.filter(fecha_solicitud__date__gte=fecha_inicio)
    if fecha_fin:
        qs = qs.filter(fecha_solicitud__date__lte=fecha_fin)
    return qs


def paginate_queryset(qs, page=1, page_size=10):
    current_page = _safe_page(page)
    current_page_size = _safe_page_size(page_size)
    paginator = Paginator(qs, current_page_size)
    current = paginator.get_page(current_page)
    items = list(current.object_list)
    count = paginator.count
    page_number = current.number
    has_next = current.has_next()
    has_prev = current.has_previous()
    return PageData(items, count, page_number, current_page_size, has_next, has_prev)


def serialize_asistencia(asistencia):
    profesor_usuario = getattr(asistencia.profesor, "usuario", None)
    horario = getattr(asistencia, "horario", None)
    horario_label = ""
    if horario:
        horario_label = f"{horario.hora_inicio.strftime('%H:%M')} - {horario.hora_fin.strftime('%H:%M')}"
    profesor_nombre = ""
    if profesor_usuario:
        profesor_nombre = f"{profesor_usuario.nombre} {profesor_usuario.apellido}".strip()
    estado_label = "Cancelada" if asistencia.cancelada_institucional else asistencia.get_estado_display()
    estado_code = "CANCELADA" if asistencia.cancelada_institucional else asistencia.estado
    return {
        "id": asistencia.id,
        "profesor_id": asistencia.profesor_id,
        "profesor_nombre": profesor_nombre,
        "fecha": asistencia.fecha.strftime("%Y-%m-%d"),
        "estado": estado_code,
        "estado_label": estado_label,
        "justificada": asistencia.justificada,
        "cancelada_institucional": asistencia.cancelada_institucional,
        "observaciones": asistencia.observaciones or "",
        "horario": horario_label,
        "tipo_registro": asistencia.tipo_registro,
    }


def serialize_incidencia(incidencia):
    asistencia = incidencia.asistencia
    profesor_usuario = getattr(asistencia.profesor, "usuario", None)
    profesor_nombre = ""
    if profesor_usuario:
        profesor_nombre = f"{profesor_usuario.nombre} {profesor_usuario.apellido}".strip()
    aprobador_nombre = ""
    if incidencia.aprobador:
        aprobador_nombre = f"{incidencia.aprobador.nombre} {incidencia.aprobador.apellido}".strip()

    fecha_resolucion = ""
    if incidencia.fecha_de_resolucion:
        fecha_resolucion = incidencia.fecha_de_resolucion.strftime("%Y-%m-%d %H:%M")

    return {
        "id": incidencia.id,
        "asistencia_id": incidencia.asistencia_id,
        "profesor_id": asistencia.profesor_id,
        "profesor_nombre": profesor_nombre,
        "fecha_ausencia": asistencia.fecha.strftime("%Y-%m-%d"),
        "motivo": incidencia.motivo,
        "tipo": incidencia.tipo,
        "tipo_label": incidencia.get_tipo_display(),
        "estado": incidencia.estado,
        "estado_label": incidencia.get_estado_display(),
        "fecha_solicitud": incidencia.fecha_solicitud.strftime("%Y-%m-%d %H:%M"),
        "aprobador": aprobador_nombre,
        "fecha_de_resolucion": fecha_resolucion,
    }
