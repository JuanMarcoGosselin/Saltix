from .estado import obtener_color_estado, obtener_estado_clase
from .faltas import (
    all_absences_queryset,
    current_payroll_period,
    period_stats,
    unjustified_absences_queryset,
    unjustified_absences_navigation,
    unjustified_absences_max_week_offset,
    week_range,
)
from .jefatura import (
    apply_asistencia_filters,
    apply_incidencia_filters,
    get_user_departamentos,
    is_admin,
    is_jefatura,
    paginate_queryset,
    scope_asistencias_for_user,
    scope_incidencias_for_user,
    serialize_asistencia,
    serialize_incidencia,
)
