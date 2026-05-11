from django.urls import path

from . import views

urlpatterns = [
    path("", views.dashboard, name="contabilidad_dashboard"),
    path("procesar-nomina/<int:profesor_id>/", views.procesar_nomina, name="procesar_nomina"),

    # Rutas para gestión de periodos
    path("abrir-periodo/", views.abrir_periodo, name="abrir_periodo"),
    path("cerrar-periodo/<str:periodo_id>/", views.cerrar_periodo, name="cerrar_periodo"),
    path("pagar-nomina/<int:nomina_id>/", views.pagar_nomina, name="pagar_nomina"),
]
