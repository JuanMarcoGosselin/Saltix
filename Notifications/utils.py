from django.db.models import Q

from users.models import Usuario

from .models import Notificacion


def notify_user(usuario, titulo, mensaje, tipo="info", url=""):
    if not usuario:
        return None
    return Notificacion.objects.create(
        usuario=usuario,
        titulo=titulo,
        mensaje=mensaje,
        tipo=tipo if tipo in {"info", "success", "warning", "danger"} else "info",
        url=url or "",
    )


def notify_role(rol, titulo, mensaje, tipo="info", url=""):
    rol_normalizado = (rol or "").strip().lower()
    if rol_normalizado in {"admin", "administrador"}:
        filtro = Q(rol_id__nombre__iexact="admin") | Q(rol_id__nombre__iexact="administrador")
    else:
        filtro = Q(rol_id__nombre__iexact=rol_normalizado)

    usuarios = Usuario.objects.filter(filtro, is_active=True).select_related("rol_id")
    notificaciones = [
        Notificacion(
            usuario=usuario,
            titulo=titulo,
            mensaje=mensaje,
            tipo=tipo if tipo in {"info", "success", "warning", "danger"} else "info",
            url=url or "",
        )
        for usuario in usuarios
    ]
    return Notificacion.objects.bulk_create(notificaciones)


def mark_as_read(notificacion, usuario):
    if notificacion.usuario_id != usuario.id:
        return False
    if not notificacion.leida:
        notificacion.leida = True
        notificacion.save(update_fields=["leida"])
    return True


def mark_all_as_read(usuario):
    return Notificacion.objects.filter(
        usuario=usuario,
        leida=False,
        archivada=False,
    ).update(leida=True)
