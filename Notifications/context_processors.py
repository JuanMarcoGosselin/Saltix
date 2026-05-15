from .models import Notificacion


def notifications(request):
    user = getattr(request, "user", None)
    if not user or not user.is_authenticated:
        return {}

    qs = Notificacion.objects.filter(usuario=user, archivada=False)
    return {
        "notification_unread_count": qs.filter(leida=False).count(),
        "notification_latest": qs.order_by("-creada_en")[:5],
    }
