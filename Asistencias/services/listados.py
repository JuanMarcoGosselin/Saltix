from Asistencias.models import Asistencia, Incidencia
from Asistencias.utils import parse_date


def _rol(user):
    rol = getattr(getattr(user, "rol_id", None), "nombre", "") or ""
    return rol.lower()


def _filtrar_asistencias_por_usuario(qs, user):
    if _rol(user) in {"administrador", "admin"}:
        return qs
    return qs.filter(profesor__departamento__jefe=user)


def _filtrar_incidencias_por_usuario(qs, user):
    if _rol(user) in {"administrador", "admin"}:
        return qs
    return qs.filter(asistencia__profesor__departamento__jefe=user)


def listar_asistencias(params, user=None):
    qs = (
        Asistencia.objects
        .select_related("profesor", "profesor__usuario", "horario")
        .order_by("-fecha", "-id")
    )
    if user is not None:
        qs = _filtrar_asistencias_por_usuario(qs, user)

    profesor_id = params.get("profesor_id")
    estado = params.get("estado")
    fecha_inicio = parse_date(params.get("fecha_inicio"))
    fecha_fin = parse_date(params.get("fecha_fin"))

    if profesor_id:
        qs = qs.filter(profesor_id=profesor_id)
    if estado == "CANCELADA":
        qs = qs.filter(cancelada_institucional=True)
    elif estado:
        qs = qs.filter(estado=estado)
    if fecha_inicio:
        qs = qs.filter(fecha__gte=fecha_inicio)
    if fecha_fin:
        qs = qs.filter(fecha__lte=fecha_fin)

    return qs


def listar_incidencias(params, user=None):
    qs = (
        Incidencia.objects
        .select_related("asistencia", "asistencia__profesor", "asistencia__profesor__usuario", "aprobador")
        .order_by("-fecha_solicitud", "-id")
    )
    if user is not None:
        qs = _filtrar_incidencias_por_usuario(qs, user)

    profesor_id = params.get("profesor_id")
    estado = params.get("estado")
    fecha_inicio = parse_date(params.get("fecha_inicio"))
    fecha_fin = parse_date(params.get("fecha_fin"))

    if profesor_id:
        qs = qs.filter(asistencia__profesor_id=profesor_id)
    if estado:
        qs = qs.filter(estado=estado)
    if fecha_inicio:
        qs = qs.filter(fecha_solicitud__date__gte=fecha_inicio)
    if fecha_fin:
        qs = qs.filter(fecha_solicitud__date__lte=fecha_fin)

    return qs


def usuario_puede_ver_asistencia(user, asistencia):
    if _rol(user) in {"administrador", "admin"}:
        return True
    return asistencia.profesor.departamento.jefe_id == user.id


def usuario_puede_ver_incidencia(user, incidencia):
    return usuario_puede_ver_asistencia(user, incidencia.asistencia)


def listar_incidencias_profesor(profesor):
    return (
        Incidencia.objects
        .select_related("asistencia", "asistencia__horario", "aprobador")
        .filter(asistencia__profesor=profesor)
        .order_by("-fecha_solicitud", "-id")
    )
