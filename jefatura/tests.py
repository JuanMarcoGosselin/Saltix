from datetime import date
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from Asistencias.models import Asistencia, Incidencia
from Profesores.models import Horario, Profesor
from core.models import Plantel
from users.models import Departamento, Rol


class JefaturaDashboardTests(TestCase):
    def setUp(self):
        user_model = get_user_model()
        rol_jefatura = Rol.objects.create(nombre="jefatura", descripcion="Jefatura")
        rol_profesor = Rol.objects.create(nombre="Profesor", descripcion="Profesor")

        self.jefe = user_model.objects.create_user(
            email="jefatura@example.com",
            password="test12345",
            nombre="Jefa",
            apellido="Demo",
            rol_id=rol_jefatura,
        )
        self.profesor_user = user_model.objects.create_user(
            email="profesor@example.com",
            password="test12345",
            nombre="Ana",
            apellido="Demo",
            rol_id=rol_profesor,
        )
        plantel = Plantel.objects.create(nombre="Plantel Norte", direccion="Av. Norte")
        depto = Departamento.objects.create(
            nombre="Ciencias",
            descripcion="Depto ciencias",
            jefe=self.jefe,
            plantel=plantel,
        )
        profesor = Profesor.objects.create(
            usuario=self.profesor_user,
            rfc="CCCC010101CCC",
            curp="CCCC010101HDFBCD03",
            telefono="5512345680",
            direccion="Direccion 3",
            fecha_ingreso=date(2024, 1, 1),
            costo_por_hora=Decimal("180.00"),
            tipo_contrato="Asignatura",
        )
        profesor.departamentos.add(depto)
        profesor.planteles.add(plantel)
        horario = Horario.objects.create(
            profesor=profesor,
            dia_semana="LUN",
            hora_inicio="07:00",
            hora_fin="08:00",
            aula="B1",
            activo=True,
        )
        asistencia = Asistencia.objects.create(
            profesor=profesor,
            fecha=date(2026, 4, 14),
            hora_entrada="07:00",
            hora_salida="08:00",
            estado="FALTA",
            horario=horario,
            creado_por=self.profesor_user,
        )
        Incidencia.objects.create(
            asistencia=asistencia,
            motivo="Motivo test",
            tipo="FALTA",
            estado="PENDIENTE",
            solicitante=self.profesor_user,
        )

    def test_dashboard_jefatura_renderiza_datos_reales(self):
        self.client.force_login(self.jefe)
        response = self.client.get(reverse("jefatura_dashboard"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Gestion de Asistencias")
        self.assertContains(response, "Solicitudes de Justificacion")
        self.assertContains(response, "Ana Demo")
