from __future__ import annotations

from datetime import date, datetime

from django.core.management.base import BaseCommand
from django.utils import timezone

from Asistencias.models import Asistencia
from Profesores.models import Horario


class Command(BaseCommand):
    help = (
        "Genera registros de 'FALTA' para clases del día ya finalizadas sin registro de asistencia.\n"
        "\n"
        "Uso en producción (cron job diario, ej. a las 23:30):\n"
        "  python manage.py generar_faltas\n"
        "\n"
        "Uso en desarrollo (simular cualquier fecha pasada):\n"
        "  python manage.py generar_faltas --fecha 2026-03-18\n"
        "  python manage.py generar_faltas --fecha 2026-03-18 --dry-run\n"
        "\n"
        "Configuración de cron recomendada (crontab -e):\n"
        "  30 23 * * 1-6 /ruta/venv/bin/python /ruta/manage.py generar_faltas >> /var/log/saltix_faltas.log 2>&1\n"
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--fecha",
            type=str,
            default=None,
            help="Fecha a procesar en formato YYYY-MM-DD (por defecto: hoy en zona local). "
                "Útil en desarrollo para simular días pasados.",
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="No crea registros, solo muestra el conteo.",
        )

    def handle(self, *args, **options):
        fecha = self._parse_fecha(options.get("fecha"))

        dias_codigos = ["LUN", "MAR", "MIE", "JUE", "VIE", "SAB", "DOM"]
        dia_codigo = dias_codigos[fecha.weekday()]
        if dia_codigo == "DOM":
            self.stdout.write("0 faltas generadas (domingo).")
            return

        ahora = timezone.now()
        tz = timezone.get_current_timezone()

        horarios = (
            Horario.objects.filter(dia_semana=dia_codigo, es_hora_clase=True, activo=True)
            .select_related("profesor")
            .only("id", "profesor_id", "hora_inicio", "hora_fin")
        )

        existentes = set(
            Asistencia.objects.filter(fecha=fecha, horario__in=horarios).values_list("profesor_id", "horario_id")
        )

        por_crear: list[Asistencia] = []
        for horario in horarios:
            fin = timezone.make_aware(datetime.combine(fecha, horario.hora_fin), tz)
            if ahora <= fin:
                continue

            key = (horario.profesor_id, horario.id)
            if key in existentes:
                continue

            por_crear.append(
                Asistencia(
                    profesor_id=horario.profesor_id,
                    horario_id=horario.id,
                    fecha=fecha,
                    hora_entrada=horario.hora_inicio,
                    hora_salida=horario.hora_fin,
                    estado="FALTA",
                    tipo_registro="MANUAL",
                    justificada=False,
                )
            )

        if options.get("dry_run"):
            self.stdout.write(f"{len(por_crear)} faltas por generar (dry-run).")
            return

        if por_crear:
            Asistencia.objects.bulk_create(por_crear)
        self.stdout.write(f"{len(por_crear)} faltas generadas para {fecha}.")

    def _parse_fecha(self, fecha_str: str | None) -> date:
        if not fecha_str:
            return timezone.localdate()
        return date.fromisoformat(fecha_str)
