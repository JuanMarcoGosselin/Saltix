from django.urls import path

from . import views


app_name = "notifications"

urlpatterns = [
    path("", views.lista_notificaciones, name="list"),
    path("status/", views.estado_notificaciones, name="status"),
    path("<int:notificacion_id>/leida/", views.marcar_leida, name="mark_read"),
    path("leidas/", views.marcar_todas_leidas, name="mark_all_read"),
]
