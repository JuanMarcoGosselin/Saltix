from functools import wraps

from django.http import HttpResponseForbidden, JsonResponse

from users.models import RolPermiso


def _wants_json(request):
    return (
        request.headers.get("x-requested-with") == "XMLHttpRequest"
        or "application/json" in request.headers.get("accept", "")
    )


def _forbid(mensaje="No tienes permiso para realizar esta accion.", request=None):
    if request is not None and _wants_json(request):
        return JsonResponse({"ok": False, "message": mensaje}, status=403)
    return HttpResponseForbidden(
        f"<h2>403 - Acceso denegado</h2><p>{mensaje}</p>",
        content_type="text/html; charset=utf-8",
    )


def requiere_rol(*roles_permitidos):
    """
    Restringe el acceso a usuarios cuyo rol (Rol.nombre) coincida con
    alguno de los valores indicados, sin distinguir mayusculas.
    """
    roles_lower = {r.lower() for r in roles_permitidos}

    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            user = getattr(request, "user", None)

            if user is None or not user.is_authenticated:
                return _forbid("Debes iniciar sesion.", request)

            rol = getattr(user, "rol_id", None)
            if rol is None or rol.nombre.lower() not in roles_lower:
                return _forbid(
                    f"Tu rol no tiene acceso a este recurso. "
                    f"Se requiere: {', '.join(roles_permitidos)}.",
                    request,
                )

            return view_func(request, *args, **kwargs)

        return wrapper
    return decorator


def requiere_permiso(codigo_permiso):
    """
    Verifica que el rol del usuario tenga asignado el permiso indicado
    mediante la tabla RolPermiso -> Permiso.codigo.
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            user = getattr(request, "user", None)

            if user is None or not user.is_authenticated:
                return _forbid("Debes iniciar sesion.", request)

            rol = getattr(user, "rol_id", None)
            if rol is None:
                return _forbid("Tu cuenta no tiene un rol asignado.", request)

            tiene_permiso = RolPermiso.objects.filter(
                rol=rol,
                permiso__codigo=codigo_permiso,
            ).exists()

            if not tiene_permiso:
                return _forbid(
                    f"No tienes el permiso {codigo_permiso} necesario para esta accion.",
                    request,
                )

            return view_func(request, *args, **kwargs)

        return wrapper
    return decorator
