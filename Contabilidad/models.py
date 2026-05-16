from django.db import models

class Nomina(models.Model): 
    ESTADOS = [
        ("pendiente", "Pendiente"),
        ("procesando", "Procesando"),
        ("cerrada", "Cerrada"),
        ("pagada", "Pagada"),
    ]
    # Resultado final de nomina por profesor y periodo (totales y fecha).
    profesor = models.ForeignKey("Profesores.Profesor", on_delete=models.PROTECT)
    periodo = models.ForeignKey("Periodo", on_delete=models.PROTECT)
    horas_trabajadas = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    faltas = models.PositiveIntegerField(default=0)
    retardos = models.PositiveIntegerField(default=0)
    faltas_equivalentes = models.PositiveIntegerField(default=0)
    total_bruto = models.DecimalField(max_digits=12, decimal_places=4)
    total_percepciones = models.DecimalField(max_digits=12, decimal_places=4)
    total_impuestos = models.DecimalField(max_digits=12, decimal_places=4)
    total_deducciones = models.DecimalField(max_digits=12, decimal_places=4) 
    total_neto = models.DecimalField(max_digits=12, decimal_places=4)
    fecha_de_generacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    estado = models.CharField(max_length=20, choices=ESTADOS, default="procesando")

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["profesor", "periodo"],
                name="unique_nomina_profesor_periodo",
            ),
        ]
        indexes = [
            models.Index(fields=["periodo", "estado"]),
            models.Index(fields=["profesor", "periodo"]),
        ]

    def __str__(self):
        return f"{self.profesor} | {self.periodo}"

class Periodo(models.Model):
    # Periodos generales de nomina.
    TIPOS = [
        ("SEMANAL", "Semanal"),
        ("QUINCENAL", "Quincenal"),
        ("MENSUAL", "Mensual"),
    ]
    ESTADOS = [
        ("ABIERTO", "Abierto"),
        ("CERRADO", "Cerrado"),
    ]

    fecha_inicio = models.DateField()
    fecha_fin = models.DateField()
    tipo = models.CharField(max_length=10, choices=TIPOS, default="QUINCENAL")
    estado = models.CharField(max_length=10, choices=ESTADOS, default="ABIERTO")
    fecha_cierre = models.DateTimeField(null=True, blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["fecha_inicio", "fecha_fin", "tipo"],
                name="unique_periodo_rango_tipo",
            ),
        ]

    def __str__(self):
        return f"{self.tipo} | {self.fecha_inicio} - {self.fecha_fin}"

    def display_label(self):
        return f"{self.fecha_inicio.strftime('%d %B')} - {self.fecha_fin.strftime('%d %B')}"

class CatalogoConcepto(models.Model):
    # Catalogo de conceptos de percepciones/deducciones y su clasificacion fiscal.
    TIPOS = [
        ("PERCEPCION", "Percepcion"),
        ("DEDUCCION", "Deduccion"),
    ]
    CLASIFICACION_FISCAL = [
        ("GRAVADA", "Gravada"),
        ("EXENTA", "Exenta"),
        ("MIXTA", "Mixta"),
    ]

    nombre = models.CharField(max_length=80)
    tipo = models.CharField(max_length=10, choices=TIPOS)
    clasificacion_fiscal = models.CharField(max_length=10, choices=CLASIFICACION_FISCAL)
    activo = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.nombre} | {self.tipo}"

class DetalleNomina(models.Model): 
    # Partidas que componen la nomina (concepto + monto).
    nomina = models.ForeignKey("Nomina", on_delete=models.CASCADE)
    concepto = models.ForeignKey("CatalogoConcepto", on_delete=models.PROTECT)
    monto = models.DecimalField(max_digits=12, decimal_places=4)
    descripcion = models.CharField(max_length=255, blank=True)
    creado_en = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.nomina} | {self.concepto}"

class ReciboNomina(models.Model):
    # Recibo PDF generado cuando la nomina se cierra.
    nomina = models.OneToOneField("Nomina", on_delete=models.CASCADE)
    pdf = models.FileField(upload_to="recibos/")
    fecha_emision = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Recibo {self.nomina_id}"

class VistaPreviaNomina(models.Model):
    # Calculo previo de nomina, sin cerrar el periodo.
    periodo = models.ForeignKey("Periodo", on_delete=models.CASCADE)
    generado_por = models.ForeignKey("users.Usuario", on_delete=models.PROTECT)
    fecha_generacion = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Vista previa {self.periodo_id}"
