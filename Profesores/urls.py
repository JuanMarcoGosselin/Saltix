from django.urls import path

from . import views
from Asistencias import views as asistencias_views

urlpatterns = [
    path("", views.dashboard, name="profesores_dashboard"),
    path("registro-asistencia/", views.registro_asistencia, name="profesores_registro_asistencia"),
    path("registrar-asistencia/", views.asistencia_accion, name="asistencia_accion"),
    path("justificar-asistencia/", asistencias_views.justificar_asistencia, name="profesores_justificar_asistencia"),
]
