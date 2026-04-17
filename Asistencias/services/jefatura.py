from __future__ import annotations

from dataclasses import dataclass
from datetime import date

from django.core.paginator import Paginator
from django.db.models import QuerySet

from Asistencias.models import Asistencia, Incidencia
from users.models import Departamento


@dataclass(frozen=True)
class PageData:
    items: list
    count: int
    page: int
    page_size: int
    has_next: bool
    has_prev: bool


def _safe_page_size(page_size: int | str | None, default: int = 10, max_size: int = 100) -> int:
    try:
        size = int(page_size or default)
    except (TypeError, ValueError):
        return default
    return max(1, min(size, max_size))


def _safe_page(page: int | str | None, default: int = 1) -> int:
    try:
        value = int(page or default)
    except (TypeError, ValueError):
        return default
    return max(1, value)


def is_admin(user) -> bool:
    rol = getattr(getattr(user, "rol_id", None), "nombre", "") or ""
    return rol.lower() == "administrador"


def is_jefatura(user) -> bool:
    rol = getattr(getattr(user, "rol_id", None), "nombre", "") or ""
    return rol.lower() == "jefatura"


def get_user_departamentos(user) -> QuerySet[Departamento]:
    return Departamento.objects.select_related("plantel", "jefe").filter(jefe=user, activo=True)


def scope_asistencias_for_user(user) -> QuerySet[Asistencia]:
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


def scope_incidencias_for_user(user) -> QuerySet[Incidencia]:
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
    qs: QuerySet[Asistencia],
    *,
    profesor_id: int | str | None = None,
    estado: str | None = None,
    fecha_inicio: date | None = None,
    fecha_fin: date | None = None,
) -> QuerySet[Asistencia]:
    if profesor_id:
        qs = qs.filter(profesor_id=profesor_id)
    if estado:
        estado = estado.strip().upper()
        if estado == "CANCELADA":
            qs = qs.filter(cancelada_institucional=True)
        elif estado in {choice[0] for choice in Asistencia.ESTADOS}:
            qs = qs.filter(estado=estado)
    if fecha_inicio:
        qs = qs.filter(fecha__gte=fecha_inicio)
    if fecha_fin:
        qs = qs.filter(fecha__lte=fecha_fin)
    return qs


def apply_incidencia_filters(
    qs: QuerySet[Incidencia],
    *,
    profesor_id: int | str | None = None,
    estado: str | None = None,
    fecha_inicio: date | None = None,
    fecha_fin: date | None = None,
) -> QuerySet[Incidencia]:
    if profesor_id:
        qs = qs.filter(asistencia__profesor_id=profesor_id)
    if estado:
        estado = estado.strip().upper()
        if estado in {choice[0] for choice in Incidencia.ESTADOS}:
            qs = qs.filter(estado=estado)
    if fecha_inicio:
        qs = qs.filter(fecha_solicitud__date__gte=fecha_inicio)
    if fecha_fin:
        qs = qs.filter(fecha_solicitud__date__lte=fecha_fin)
    return qs


def paginate_queryset(qs, *, page: int | str | None = 1, page_size: int | str | None = 10) -> PageData:
    current_page = _safe_page(page)
    current_page_size = _safe_page_size(page_size)
    paginator = Paginator(qs, current_page_size)
    current = paginator.get_page(current_page)
    return PageData(
        items=list(current.object_list),
        count=paginator.count,
        page=current.number,
        page_size=current_page_size,
        has_next=current.has_next(),
        has_prev=current.has_previous(),
    )


def format_full_name(usuario) -> str:
    if not usuario:
        return ""
    return f"{usuario.nombre} {usuario.apellido}".strip()


def serialize_asistencia(asistencia: Asistencia) -> dict:
    profesor_usuario = getattr(asistencia.profesor, "usuario", None)
    horario = getattr(asistencia, "horario", None)
    horario_label = ""
    if horario:
        horario_label = f"{horario.hora_inicio.strftime('%H:%M')} - {horario.hora_fin.strftime('%H:%M')}"
    estado_label = "Cancelada" if asistencia.cancelada_institucional else asistencia.get_estado_display()
    estado_code = "CANCELADA" if asistencia.cancelada_institucional else asistencia.estado
    return {
        "id": asistencia.id,
        "profesor_id": asistencia.profesor_id,
        "profesor_nombre": format_full_name(profesor_usuario),
        "fecha": asistencia.fecha.strftime("%Y-%m-%d"),
        "estado": estado_code,
        "estado_label": estado_label,
        "justificada": asistencia.justificada,
        "cancelada_institucional": asistencia.cancelada_institucional,
        "observaciones": asistencia.observaciones or "",
        "horario": horario_label,
        "tipo_registro": asistencia.tipo_registro,
    }


def serialize_incidencia(incidencia: Incidencia) -> dict:
    asistencia = incidencia.asistencia
    profesor_usuario = getattr(asistencia.profesor, "usuario", None)
    return {
        "id": incidencia.id,
        "asistencia_id": incidencia.asistencia_id,
        "profesor_id": asistencia.profesor_id,
        "profesor_nombre": format_full_name(profesor_usuario),
        "fecha_ausencia": asistencia.fecha.strftime("%Y-%m-%d"),
        "motivo": incidencia.motivo,
        "tipo": incidencia.tipo,
        "tipo_label": incidencia.get_tipo_display(),
        "estado": incidencia.estado,
        "estado_label": incidencia.get_estado_display(),
        "fecha_solicitud": incidencia.fecha_solicitud.strftime("%Y-%m-%d %H:%M"),
        "aprobador": format_full_name(incidencia.aprobador),
        "fecha_de_resolucion": (
            incidencia.fecha_de_resolucion.strftime("%Y-%m-%d %H:%M")
            if incidencia.fecha_de_resolucion
            else ""
        ),
    }
