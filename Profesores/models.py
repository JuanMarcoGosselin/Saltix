from django.db import models

class Profesor(models.Model): 
    # Datos principales del profesor: identidad, estado laboral y adscripcion.
    ESTADOS = [
        ("ACTIVO", "Activo"),
        ("SUSPENDIDO", "Suspendido"),
        ("BAJA_TEMPORAL", "Baja temporal"),
        ("BAJA_DEFINITIVA", "Baja definitiva"),
    ]

    usuario = models.ForeignKey("users.Usuario", on_delete=models.CASCADE)
    rfc = models.CharField(max_length=13)
    curp = models.CharField(max_length=18)
    telefono = models.CharField(max_length=10)
    direccion = models.TextField(max_length=100)
    fecha_ingreso = models.DateField()
    estado_laboral = models.CharField(max_length=20, choices=ESTADOS, default="ACTIVO")
    costo_por_hora = models.DecimalField(max_digits=12, decimal_places=4)
    tipo_contrato = models.CharField(max_length=25)
    departamentos = models.ManyToManyField("users.Departamento", related_name="profesores")
    planteles = models.ManyToManyField("core.Plantel", related_name="profesores")

    def __str__(self):
        return f"{self.usuario} | {self.rfc}"

class Horario(models.Model): 
    # Horario por profesor para horas clase programadas.
    DIAS = [
        ("LUN", "Lunes"),
        ("MAR", "Martes"),
        ("MIE", "Miercoles"), 
        ("JUE", "Jueves"),
        ("VIE", "Viernes"),
        ("SAB", "Sabado"),
    ]
    profesor = models.ForeignKey("Profesor", on_delete=models.CASCADE)
    dia_semana = models.CharField(max_length=3, choices=DIAS)
    hora_inicio = models.TimeField()
    hora_fin = models.TimeField()
    aula = models.CharField(max_length=10)
    es_hora_clase = models.BooleanField(default=True) # Indica si esta hora es una clase programada o una hora de disponibilidad general. Se paga o no

    def __str__(self):
        return f"{self.profesor} | {self.dia_semana} {self.hora_inicio}-{self.hora_fin}"

class TransferenciaDepartamento(models.Model):
    # Historial de cambios de departamento del profesor.
    profesor = models.ForeignKey("Profesor", on_delete=models.PROTECT)
    departamento_origen = models.ForeignKey("users.Departamento", on_delete=models.PROTECT, related_name="transferencias_origen")
    departamento_destino = models.ForeignKey("users.Departamento", on_delete=models.PROTECT, related_name="transferencias_destino")
    fecha = models.DateTimeField(auto_now_add=True)
    aprobado_por = models.ForeignKey("users.Usuario", on_delete=models.PROTECT, null=True, blank=True)

    def __str__(self):
        return f"{self.profesor} | {self.departamento_origen} -> {self.departamento_destino}"
    
