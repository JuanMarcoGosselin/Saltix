from datetime import date
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from Asistencias.models import Asistencia, Incidencia
from Profesores.models import Horario, Profesor
from core.models import Plantel
from users.models import Departamento, Rol


class ProfesorDashboardTests(TestCase):
    def setUp(self):
        user_model = get_user_model()
        rol_jefatura = Rol.objects.create(nombre="jefatura", descripcion="Jefatura")
        rol_profesor = Rol.objects.create(nombre="Profesor", descripcion="Profesor")

        self.profesor_user = user_model.objects.create_user(
            email="profe-dashboard@example.com",
            password="test12345",
            nombre="Mario",
            apellido="Perez",
            rol_id=rol_profesor,
        )
        jefe = user_model.objects.create_user(
            email="jefe-dashboard@example.com",
            password="test12345",
            nombre="Luz",
            apellido="Mora",
            rol_id=rol_jefatura,
        )
        plantel = Plantel.objects.create(nombre="Plantel Sur", direccion="Av. Sur")
        depto = Departamento.objects.create(
            nombre="Ingenieria",
            descripcion="Depto ingenieria",
            jefe=jefe,
            plantel=plantel,
        )
        self.profesor = Profesor.objects.create(
            usuario=self.profesor_user,
            rfc="DDDD010101DDD",
            curp="DDDD010101HDFBCD04",
            telefono="5512345681",
            direccion="Direccion 4",
            fecha_ingreso=date(2024, 1, 1),
            costo_por_hora=Decimal("200.00"),
            tipo_contrato="Asignatura",
        )
        self.profesor.departamentos.add(depto)
        self.profesor.planteles.add(plantel)
        horario = Horario.objects.create(
            profesor=self.profesor,
            dia_semana="LUN",
            hora_inicio="09:00",
            hora_fin="10:00",
            aula="C1",
            activo=True,
        )
        asistencia = Asistencia.objects.create(
            profesor=self.profesor,
            fecha=date(2026, 4, 14),
            hora_entrada="09:00",
            hora_salida="10:00",
            estado="FALTA",
            horario=horario,
            creado_por=self.profesor_user,
        )
        Incidencia.objects.create(
            asistencia=asistencia,
            motivo="Constancia medica",
            tipo="FALTA",
            estado="PENDIENTE",
            solicitante=self.profesor_user,
        )

    def test_dashboard_muestra_solicitudes_enviadas(self):
        self.client.force_login(self.profesor_user)
        response = self.client.get(reverse("profesores_dashboard"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Mis solicitudes enviadas")
        self.assertContains(response, "Constancia medica")
