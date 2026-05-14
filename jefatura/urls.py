from django.urls import path

from . import views

urlpatterns = [
    path("", views.dashboard, name="jefatura_dashboard"),
    path("horarios/guardar/", views.guardar_horario, name="jefatura_guardar_horario"),
    path("horarios/eliminar/", views.eliminar_horario, name="jefatura_eliminar_horario"),
    path("transferencias/crear/", views.crear_transferencia, name="jefatura_crear_transferencia"),
    path("transferencias/resolver/", views.resolver_transferencia, name="jefatura_resolver_transferencia"),
    path("transferencias/cancelar/", views.cancelar_transferencia, name="jefatura_cancelar_transferencia"),
    path("reportes/", views.reporte_jefatura, name="jefatura_reporte"),
]
