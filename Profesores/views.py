import json
from datetime import datetime as dt
from datetime import timedelta

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render
from django.utils import timezone
from django.views.decorators.http import require_POST

from Contabilidad.utils import get_active_periodo, calculate_base_payment, get_deducciones_faltas
from Asistencias.models import Asistencia, Incidencia
from core.decorators import requiere_rol

from .models import Horario, Profesor
from .utils import *
from Contabilidad.models import Nomina, DetalleNomina

@login_required
def dashboard(request):
    usuario = request.user
    profesor = Profesor.objects.get(usuario_id=usuario.id)
    ultima_nomina = Nomina.objects.filter(profesor=profesor,estado='pagada').order_by('-fecha_de_generacion').first()
    detalle_nomina = DetalleNomina.objects.filter(nomina=ultima_nomina) if ultima_nomina else []

    recibo_detalle = []
    if ultima_nomina:
        recibo_detalle = [
            {
                "concepto": "Salario base",
                "tipo_label": "PERCEPCIÓN",
                "tipo_clase": "percepcion",
                "importe": ultima_nomina.total_bruto,
            }
        ]
        recibo_detalle += [
            {
                "concepto": concepto.concepto.nombre,
                "tipo_label": concepto.concepto.tipo,
                "tipo_clase": concepto.concepto.tipo.lower(),
                "importe": concepto.monto,
            }
            for concepto in detalle_nomina
        ]
        recibo_detalle += [
            {
                "concepto": "Deducciones por faltas",
                "tipo_label": "DEDUCCIÓN",
                "tipo_clase": "deduccion",
                "importe": ultima_nomina.total_deducciones,
            },
            {
                "concepto": "NETO A PAGAR",
                "tipo_clase": "neto",
                "importe": ultima_nomina.total_neto,
            }
        ]

    hoy = timezone.localdate()
    periodo = get_active_periodo()
    salario_bruto = calculate_base_payment(profesor.id)
    salario_deducido = get_deducciones_faltas(profesor.id)
    salario_neto = salario_bruto - salario_deducido
    week_offset = int(request.GET.get("week_offset", 0) or 0)
    inicio_semana = periodo.fecha_inicio
    fin_semana = inicio_semana + timedelta(days=6)
    attendance_stats = get_attendance_stats(profesor.id)
    horario_display = get_horario_display(profesor.id)
    perfil_contexto = get_profesor_context(profesor.id)

    context = {
        "fecha_actual": hoy,
        "nombrep": profesor.usuario.get_full_name(),
        "periodo_actual": periodo.display_label() if periodo else "Sin periodo activo",
        "salario_bruto": salario_bruto,
        "pagoxhora": f"${profesor.costo_por_hora:.2f}",
        "salario_neto": salario_neto,
        "horas_trabajadas": f"{salario_neto // profesor.costo_por_hora} horas" if profesor.costo_por_hora > 0 else "N/A",
        "horas_esperadas": f"{salario_bruto // profesor.costo_por_hora} horas" if profesor.costo_por_hora > 0 else "N/A",
        "proximo_pago_fecha": (periodo.fecha_fin + timedelta(days=1)).strftime("%d/%m/%Y") if periodo else "N/A",
        "week_offset_prev": week_offset - 1,
        "week_offset_next": week_offset + 1,
        "semana_inicio": inicio_semana,
        "semana_fin": fin_semana,
        "attendance_stats": attendance_stats,
        "horario_display": horario_display,
        "faltas": get_faltas(profesor.id),
        "incidencias": get_incidencias(profesor.id),
        "perfil": perfil_contexto,

        # Recibo de nómina
        "recibo_detalle": recibo_detalle,
    }

    return render(request, "Profesores/dashboard.html", context)

@login_required
@requiere_rol("Profesor")
def registro_asistencia(request):
    profesor = Profesor.objects.select_related("usuario").get(usuario_id=request.user.id)
    hoy = timezone.localdate()

    horarios_hoy = obtener_horario_hoy(profesor).order_by("hora_inicio")

    asistencias_hoy = {
        a.horario_id: a
        for a in Asistencia.objects.filter(profesor=profesor, fecha=hoy, horario__in=horarios_hoy)
    }

    for horario in horarios_hoy:
        asistencia = asistencias_hoy.get(horario.id)
        horario.ya_registrada = asistencia is not None
        horario.salida = asistencia.hora_salida if asistencia else None
        horario.asistencia_id = asistencia.id if asistencia else None

    context = {
        "profesor_nombre": f"{profesor.usuario.nombre} {profesor.usuario.apellido}".strip(),
        "profesor_iniciales": f"{(profesor.usuario.nombre or 'U')[:1]}{(profesor.usuario.apellido or '')[:1]}".upper(),
        "profesor_rol": "Profesor",
        "horarios_hoy": horarios_hoy,
        "fecha_hoy": hoy,
    }
    return render(request, "Profesores/registro_asistencia.html", context)


@require_POST
@requiere_rol("Profesor")
def asistencia_accion(request):
    try:
        body = json.loads(request.body)
        horario_id = body.get("horario_id")

        if not horario_id:
            return JsonResponse({'error': 'Horario no proporcionado'}, status=400)

        profesor = Profesor.objects.get(usuario_id=request.user.id)
        hoy = timezone.localdate()

        asistencia = Asistencia.objects.filter(
            profesor=profesor,
            horario_id=horario_id,
            fecha=hoy
        ).first()

        if not asistencia:
            if not verificar_entrada(horario_id):
                return JsonResponse({
                    'error': 'Fuera del horario permitido para registrar entrada'
                }, status=400)

            ahora = timezone.now()
            horario = Horario.objects.get(id=horario_id)
            tz = timezone.get_current_timezone()

            inicio = timezone.make_aware(dt.combine(hoy, horario.hora_inicio), tz)
            if ahora > inicio:
                estado = "RETARDO"
                tolerancia_minutos = int((ahora - inicio).total_seconds() // 60)
            else:
                estado = "ASISTENCIA"
                tolerancia_minutos = 0

            asistencia = Asistencia.objects.create(
                profesor=profesor,
                horario_id=horario_id,
                fecha=hoy,
                hora_entrada=ahora.time(),
                estado=estado,
                tolerancia_minutos=tolerancia_minutos,
                creado_por=request.user,
            )

            return JsonResponse({
                'tipo': 'entrada',
                'estado': estado,
                'message': 'Asistencia registrada correctamente',
                'asistencia_id': asistencia.id,
            })

        if not asistencia.hora_salida:
            if not verificar_salida(horario_id):
                return JsonResponse({
                    'error': 'Fuera del horario permitido para registrar salida'
                }, status=400)

            asistencia.hora_salida = timezone.now().time()
            asistencia.save(update_fields=["hora_salida"])

            return JsonResponse({
                'tipo': 'salida',
                'message': 'Salida registrada correctamente'
            })

        return JsonResponse({
            'error': 'Ya registraste entrada y salida para este horario'
        }, status=400)

    except Exception as e:
        return JsonResponse({
            'error': str(e)
        }, status=500)
