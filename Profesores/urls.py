from django.urls import path

from . import views

urlpatterns = [
    path("", views.dashboard, name="profesores_dashboard"),
    path("registro-asistencia/", views.registro_asistencia, name="profesores_registro_asistencia"),
]
