from django.urls import path

from . import views

urlpatterns = [
    path("", views.dashboard, name="profesores_dashboard"),
    path("registro-asistencia/", views.registro_asistencia, name="profesores_registro_asistencia"),
    path("registrar-asistencia/", views.registrar_asistencia, name="profesores_registrar_asistencia"),
    path("registrar-salida/", views.registrar_salida, name="profesores_registrar_salida"),
]
