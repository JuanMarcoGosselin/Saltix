from functools import wraps

from django.http import HttpResponseForbidden

from users.models import RolPermiso


# ─────────────────────────────────────────────
# Respuesta 403 centralizada
# ─────────────────────────────────────────────

def _forbid(mensaje: str = "No tienes permiso para realizar esta acción."):
    return HttpResponseForbidden(
        f"<h2>403 – Acceso denegado</h2><p>{mensaje}</p>",
        content_type="text/html; charset=utf-8",
    )


# ─────────────────────────────────────────────
# Decorador 1 – Filtro por rol
# ─────────────────────────────────────────────

def requiere_rol(*roles_permitidos: str):
    """
    Restringe el acceso a usuarios cuyo rol (Rol.nombre) coincida con
    alguno de los valores indicados (insensible a mayúsculas).

    Uso:
        @requiere_rol("administrador")
        @requiere_rol("administrador", "jefatura")
    """
    roles_lower = {r.lower() for r in roles_permitidos}

    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            user = getattr(request, "user", None)

            if user is None or not user.is_authenticated:
                return _forbid("Debes iniciar sesión.")

            rol = getattr(user, "rol_id", None)
            if rol is None or rol.nombre.lower() not in roles_lower:
                return _forbid(
                    f"Tu rol no tiene acceso a este recurso. "
                    f"Se requiere: {', '.join(roles_permitidos)}."
                )

            return view_func(request, *args, **kwargs)

        return wrapper
    return decorator


# ─────────────────────────────────────────────
# Decorador 2 – Filtro por permiso (RolPermiso)
# ─────────────────────────────────────────────

def requiere_permiso(codigo_permiso: str):
    """
    Verifica que el rol del usuario tenga asignado el permiso indicado
    mediante la tabla RolPermiso → Permiso.codigo.

    Uso:
        @requiere_permiso("crear_usuario")
        @requiere_permiso("eliminar_plantel")

    Los códigos de permiso sugeridos para este módulo están listados
    al final del archivo.
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            user = getattr(request, "user", None)

            if user is None or not user.is_authenticated:
                return _forbid("Debes iniciar sesión.")

            rol = getattr(user, "rol_id", None)
            if rol is None:
                return _forbid("Tu cuenta no tiene un rol asignado.")

            tiene_permiso = RolPermiso.objects.filter(
                rol=rol,
                permiso__codigo=codigo_permiso,
            ).exists()

            if not tiene_permiso:
                return _forbid(
                    f"No tienes el permiso «{codigo_permiso}» "
                    f"necesario para esta acción."
                )

            return view_func(request, *args, **kwargs)

        return wrapper
    return decorator


# ─────────────────────────────────────────────────────────────────────────────
# CÓDIGOS DE PERMISO SUGERIDOS
# Agrégalos en la tabla Permiso (o en un fixture/migration inicial).
#
#   Módulo Usuarios
#     ver_usuarios          – Acceder al listado de usuarios
#     crear_usuario         – Crear un nuevo usuario
#     editar_usuario        – Editar datos de un usuario existente
#
#   Módulo Planteles
#     ver_planteles         – Acceder al listado de planteles
#     crear_plantel         – Crear un nuevo plantel
#     editar_plantel        – Editar un plantel existente
#     eliminar_plantel      – Eliminar un plantel
#
#   Módulo Departamentos
#     ver_departamentos     – Acceder al listado de departamentos
#     crear_departamento    – Crear un nuevo departamento
#     editar_departamento   – Editar un departamento existente
#     eliminar_departamento – Eliminar un departamento
#
#   Módulo Notificaciones
#     gestionar_notificaciones – Marcar notificaciones como leídas
#
#   Dashboard general
#     ver_dashboard         – Acceder al dashboard de administración
# ─────────────────────────────────────────────────────────────────────────────

