from __future__ import annotations

from datetime import date, datetime, timedelta

from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone

from Asistencias.models import Asistencia
from Asistencias.services import current_payroll_period
from Profesores.models import Horario


class Command(BaseCommand):
    help = (
        "Genera registros de 'FALTA' para todas las clases del periodo vigente ya finalizadas "
        "sin registro de asistencia.\n"
        "\n"
        "Por defecto usa el Periodo ABIERTO (ignorando plantel) y procesa desde fecha_inicio "
        "hasta min(hoy, fecha_fin). En el día de hoy solo genera faltas de clases cuyo fin ya pasó.\n"
        "\n"
        "Uso:\n"
        "  python manage.py generar_faltas_periodo\n"
        "  python manage.py generar_faltas_periodo --dry-run\n"
        "  python manage.py generar_faltas_periodo --desde 2026-03-01 --hasta 2026-03-20\n"
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--desde",
            type=str,
            default=None,
            help="Fecha inicial (YYYY-MM-DD). Por defecto: inicio del periodo vigente.",
        )
        parser.add_argument(
            "--hasta",
            type=str,
            default=None,
            help="Fecha final (YYYY-MM-DD). Por defecto: fin del periodo vigente (acotado a hoy).",
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="No crea registros, solo muestra el conteo.",
        )
        parser.add_argument(
            "--verbose-days",
            action="store_true",
            help="Muestra conteo por día procesado.",
        )

    def handle(self, *args, **options):
        hoy = timezone.localdate()
        now = timezone.now()
        tz = timezone.get_current_timezone()

        periodo = current_payroll_period(hoy=hoy)
        if not periodo or not periodo.inicio or not periodo.fin:
            raise CommandError("No se pudo determinar el periodo vigente.")

        desde = self._parse_fecha(options.get("desde")) if options.get("desde") else periodo.inicio
        hasta = self._parse_fecha(options.get("hasta")) if options.get("hasta") else periodo.fin

        if hasta > hoy:
            hasta = hoy

        if desde > hasta:
            raise CommandError("Rango inválido: --desde no puede ser mayor que --hasta.")

        # Preparar horarios por día para no consultar en cada fecha.
        dias_codigos = ["LUN", "MAR", "MIE", "JUE", "VIE", "SAB", "DOM"]
        horarios_por_dia: dict[str, list[Horario]] = {}
        for dia in dias_codigos:
            if dia == "DOM":
                continue
            horarios_por_dia[dia] = list(
                Horario.objects.filter(dia_semana=dia, es_hora_clase=True, activo=True)
                .select_related("profesor")
                .only("id", "profesor_id", "hora_inicio", "hora_fin")
            )

        total_por_crear = 0
        total_creadas = 0
        verbose_days = bool(options.get("verbose_days"))

        fecha = desde
        while fecha <= hasta:
            dia_codigo = dias_codigos[fecha.weekday()]
            if dia_codigo == "DOM":
                fecha += timedelta(days=1)
                continue

            horarios = horarios_por_dia.get(dia_codigo, [])
            if not horarios:
                if verbose_days:
                    self.stdout.write(f"{fecha}: 0 faltas (sin horarios).")
                fecha += timedelta(days=1)
                continue

            existentes = set(
                Asistencia.objects.filter(fecha=fecha, horario__in=horarios).values_list("profesor_id", "horario_id")
            )

            por_crear: list[Asistencia] = []
            for horario in horarios:
                fin = timezone.make_aware(datetime.combine(fecha, horario.hora_fin), tz)
                if now <= fin:
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

            total_por_crear += len(por_crear)
            if verbose_days:
                self.stdout.write(f"{fecha}: {len(por_crear)} faltas por generar.")

            if not options.get("dry_run") and por_crear:
                Asistencia.objects.bulk_create(por_crear)
                total_creadas += len(por_crear)

            fecha += timedelta(days=1)

        if options.get("dry_run"):
            self.stdout.write(
                f"{total_por_crear} faltas por generar (dry-run) en rango {desde} a {hasta}."
            )
        else:
            self.stdout.write(f"{total_creadas} faltas generadas en rango {desde} a {hasta}.")

    def _parse_fecha(self, fecha_str: str) -> date:
        try:
            return date.fromisoformat(fecha_str)
        except Exception as exc:
            raise CommandError("Fecha inválida. Usa formato YYYY-MM-DD.") from exc

