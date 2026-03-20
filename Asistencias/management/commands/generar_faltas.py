from __future__ import annotations

from datetime import date, datetime

from django.core.management.base import BaseCommand
from django.utils import timezone

from Asistencias.models import Asistencia
from Profesores.models import Horario


class Command(BaseCommand):
    help = "Genera registros de 'FALTA' para clases del día ya finalizadas sin registro de asistencia."

    def add_arguments(self, parser):
        parser.add_argument(
            "--fecha",
            type=str,
            default=None,
            help="Fecha a procesar en formato YYYY-MM-DD (por defecto: hoy en zona local).",
        )
        parser.add_argument("--dry-run", action="store_true", help="No crea registros, solo muestra el conteo.")

    def handle(self, *args, **options):
        fecha = self._parse_fecha(options.get("fecha"))

        # Horario.DIAS no incluye DOM; si hoy es domingo, no hay clases programadas.
        dias_codigos = ["LUN", "MAR", "MIE", "JUE", "VIE", "SAB", "DOM"]
        dia_codigo = dias_codigos[fecha.weekday()]
        if dia_codigo == "DOM":
            self.stdout.write("0 faltas generadas (domingo).")
            return

        ahora = timezone.now()
        tz = timezone.get_current_timezone()

        horarios = (
            Horario.objects.filter(dia_semana=dia_codigo, es_hora_clase=True)
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
                    estado="FALTA",
                )
            )

        if options.get("dry_run"):
            self.stdout.write(f"{len(por_crear)} faltas por generar (dry-run).")
            return

        if por_crear:
            Asistencia.objects.bulk_create(por_crear)
        self.stdout.write(f"{len(por_crear)} faltas generadas.")

    def _parse_fecha(self, fecha_str: str | None) -> date:
        if not fecha_str:
            return timezone.localdate()
        return date.fromisoformat(fecha_str)

