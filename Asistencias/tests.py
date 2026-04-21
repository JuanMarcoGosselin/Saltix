import json
from datetime import date, time
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from Asistencias.models import Asistencia, Incidencia
from Profesores.models import Horario, Profesor
from core.models import Plantel
from users.models import Departamento, Rol


class AsistenciasSprint3Tests(TestCase):
    def setUp(self):
        user_model = get_user_model()
        self.rol_jefatura = Rol.objects.create(nombre="jefatura", descripcion="Jefatura")
        self.rol_profesor = Rol.objects.create(nombre="Profesor", descripcion="Profesor")
        self.rol_admin = Rol.objects.create(nombre="administrador", descripcion="Administrador")

        self.plantel = Plantel.objects.create(nombre="Campus Centro", direccion="Av. 1")
        self.jefe = user_model.objects.create_user(
            email="jefe@example.com",
            password="test12345",
            nombre="Jefa",
            apellido="Centro",
            rol_id=self.rol_jefatura,
        )
        self.otro_jefe = user_model.objects.create_user(
            email="jefe2@example.com",
            password="test12345",
            nombre="Jefa",
            apellido="Sur",
            rol_id=self.rol_jefatura,
        )
        self.admin = user_model.objects.create_user(
            email="admin@example.com",
            password="test12345",
            nombre="Admin",
            apellido="Global",
            rol_id=self.rol_admin,
        )
        self.profesor_user = user_model.objects.create_user(
            email="profe@example.com",
            password="test12345",
            nombre="Ana",
            apellido="Lopez",
            rol_id=self.rol_profesor,
        )
        self.profesor_user_2 = user_model.objects.create_user(
            email="profe2@example.com",
            password="test12345",
            nombre="Luis",
            apellido="Martinez",
            rol_id=self.rol_profesor,
        )

        self.depto = Departamento.objects.create(
            nombre="Matematicas",
            descripcion="Depto principal",
            jefe=self.jefe,
            plantel=self.plantel,
        )
        self.depto_otro = Departamento.objects.create(
            nombre="Historia",
            descripcion="Depto secundario",
            jefe=self.otro_jefe,
            plantel=self.plantel,
        )

        self.profesor = Profesor.objects.create(
            usuario=self.profesor_user,
            rfc="AAAA010101AAA",
            curp="AAAA010101HDFBCD01",
            telefono="5512345678",
            direccion="Direccion 1",
            fecha_ingreso=date(2024, 1, 1),
            costo_por_hora=Decimal("150.00"),
            tipo_contrato="Asignatura",
        )
        self.profesor.departamentos.add(self.depto)
        self.profesor.planteles.add(self.plantel)

        self.profesor_otro = Profesor.objects.create(
            usuario=self.profesor_user_2,
            rfc="BBBB010101BBB",
            curp="BBBB010101HDFBCD02",
            telefono="5512345679",
            direccion="Direccion 2",
            fecha_ingreso=date(2024, 1, 1),
            costo_por_hora=Decimal("160.00"),
            tipo_contrato="Asignatura",
        )
        self.profesor_otro.departamentos.add(self.depto_otro)
        self.profesor_otro.planteles.add(self.plantel)

        self.horario = Horario.objects.create(
            profesor=self.profesor,
            dia_semana="LUN",
            hora_inicio=time(8, 0),
            hora_fin=time(9, 0),
            aula="A1",
            activo=True,
        )
        self.horario_otro = Horario.objects.create(
            profesor=self.profesor_otro,
            dia_semana="LUN",
            hora_inicio=time(10, 0),
            hora_fin=time(11, 0),
            aula="A2",
            activo=True,
        )

        self.asistencia = Asistencia.objects.create(
            profesor=self.profesor,
            fecha=date(2026, 4, 14),
            hora_entrada=time(8, 5),
            hora_salida=time(9, 0),
            estado="FALTA",
            horario=self.horario,
            creado_por=self.profesor_user,
        )
        self.asistencia_otra = Asistencia.objects.create(
            profesor=self.profesor_otro,
            fecha=date(2026, 4, 14),
            hora_entrada=time(10, 5),
            hora_salida=time(11, 0),
            estado="FALTA",
            horario=self.horario_otro,
            creado_por=self.profesor_user_2,
        )

        self.incidencia = Incidencia.objects.create(
            asistencia=self.asistencia,
            motivo="Consulta medica",
            tipo="FALTA",
            estado="PENDIENTE",
            solicitante=self.profesor_user,
        )
        self.incidencia_ajena = Incidencia.objects.create(
            asistencia=self.asistencia_otra,
            motivo="Motivo ajeno",
            tipo="FALTA",
            estado="PENDIENTE",
            solicitante=self.profesor_user_2,
        )

    def test_jefatura_solo_ve_asistencias_de_su_ambito(self):
        self.client.force_login(self.jefe)
        response = self.client.get(reverse("asistencias:listar_asistencias_jefatura"))
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["count"], 1)
        self.assertEqual(data["results"][0]["profesor_id"], self.profesor.id)

    def test_filtros_por_estado_en_asistencias(self):
        self.client.force_login(self.jefe)
        response = self.client.get(
            reverse("asistencias:listar_asistencias_jefatura"),
            {"estado": "FALTA"},
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["count"], 1)

    def test_aprobar_incidencia_pendiente(self):
        self.client.force_login(self.jefe)
        response = self.client.post(
            reverse("asistencias:aprobar_incidencia"),
            data=json.dumps({"incidencia_id": self.incidencia.id}),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)
        self.incidencia.refresh_from_db()
        self.asistencia.refresh_from_db()
        self.assertEqual(self.incidencia.estado, "APROBADA")
        self.assertEqual(self.incidencia.aprobador_id, self.jefe.id)
        self.assertEqual(self.asistencia.estado, "JUSTIFICADA")
        self.assertTrue(self.asistencia.justificada)

    def test_rechazar_incidencia_pendiente(self):
        self.client.force_login(self.jefe)
        response = self.client.post(
            reverse("asistencias:rechazar_incidencia"),
            data=json.dumps({"incidencia_id": self.incidencia.id}),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)
        self.incidencia.refresh_from_db()
        self.asistencia.refresh_from_db()
        self.assertEqual(self.incidencia.estado, "RECHAZADA")
        self.assertEqual(self.asistencia.estado, "FALTA")

    def test_no_puede_resolver_incidencia_ya_resuelta(self):
        self.incidencia.estado = "APROBADA"
        self.incidencia.save(update_fields=["estado"])
        self.client.force_login(self.jefe)
        response = self.client.post(
            reverse("asistencias:rechazar_incidencia"),
            data=json.dumps({"incidencia_id": self.incidencia.id}),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 400)

    def test_cancelacion_institucional_duplicada(self):
        self.client.force_login(self.jefe)
        first = self.client.post(
            reverse("asistencias:cancelar_asistencia_institucional"),
            data=json.dumps({"asistencia_id": self.asistencia.id}),
            content_type="application/json",
        )
        second = self.client.post(
            reverse("asistencias:cancelar_asistencia_institucional"),
            data=json.dumps({"asistencia_id": self.asistencia.id}),
            content_type="application/json",
        )
        self.assertEqual(first.status_code, 200)
        self.assertEqual(second.status_code, 400)

    def test_profesor_consulta_sus_incidencias(self):
        self.client.force_login(self.profesor_user)
        response = self.client.get(reverse("asistencias:listar_incidencias_profesor"))
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["count"], 1)
        self.assertEqual(data["results"][0]["id"], self.incidencia.id)

    def test_correccion_manual_guarda_trazabilidad(self):
        self.client.force_login(self.jefe)
        response = self.client.post(
            reverse("asistencias:corregir_asistencia_jefatura"),
            data=json.dumps(
                {
                    "asistencia_id": self.asistencia.id,
                    "estado": "JUSTIFICADA",
                    "observaciones": "Ajuste por validacion de jefatura",
                }
            ),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)
        self.asistencia.refresh_from_db()
        self.assertEqual(self.asistencia.estado, "JUSTIFICADA")
        self.assertEqual(self.asistencia.creado_por_id, self.jefe.id)
        self.assertIsNotNone(self.asistencia.bitacora_id)

    def test_admin_puede_ver_registros_globales(self):
        self.client.force_login(self.admin)
        response = self.client.get(reverse("asistencias:listar_asistencias_jefatura"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["count"], 2)
