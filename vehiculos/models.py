from django.db import models
from django.core.validators import RegexValidator
from django.utils import timezone


class EstadoVehiculo(models.TextChoices):
    """Estados posibles de un vehículo de sustitución"""
    DISPONIBLE = 'DISPONIBLE', 'Disponible'
    EN_USO = 'EN_USO', 'En Uso'
    MANTENIMIENTO = 'MANTENIMIENTO', 'Mantenimiento/Reparación'
    BAJA = 'BAJA', 'Dado de Baja'


class Vehiculo(models.Model):
    """Modelo principal para gestionar vehículos de sustitución"""
    
    # Validador para matrícula española
    matricula_validator = RegexValidator(
        regex=r'^[0-9]{4}[A-Z]{3}$',
        message='Formato de matrícula inválido. Debe ser 4 números seguidos de 3 letras (ej: 0987TRE)'
    )
    
    matricula = models.CharField(
        max_length=7,
        unique=True,
        validators=[matricula_validator],
        verbose_name='Matrícula',
        help_text='Formato: 0000XXX (4 números + 3 letras)'
    )
    marca = models.CharField(max_length=50, verbose_name='Marca')
    modelo = models.CharField(max_length=50, verbose_name='Modelo')
    color = models.CharField(max_length=30, verbose_name='Color')
    año = models.PositiveIntegerField(verbose_name='Año')
    
    estado = models.CharField(
        max_length=15,
        choices=EstadoVehiculo.choices,
        default=EstadoVehiculo.DISPONIBLE,
        verbose_name='Estado'
    )
    
    kilometraje = models.PositiveIntegerField(
        default=0,
        verbose_name='Kilometraje',
        help_text='Kilometraje actual del vehículo'
    )
    
    fecha_alta = models.DateField(
        default=timezone.now,
        verbose_name='Fecha de Alta'
    )
    
    fecha_ultima_revision = models.DateField(
        null=True,
        blank=True,
        verbose_name='Última Revisión'
    )
    
    observaciones = models.TextField(
        blank=True,
        verbose_name='Observaciones',
        help_text='Notas adicionales sobre el vehículo'
    )
    
    class Meta:
        verbose_name = 'Vehículo'
        verbose_name_plural = 'Vehículos'
        ordering = ['estado', 'matricula']
    
    def __str__(self):
        return f"{self.matricula} - {self.marca} {self.modelo} ({self.get_estado_display()})"
    
    def esta_disponible(self):
        """Verifica si el vehículo está disponible para asignación"""
        return self.estado == EstadoVehiculo.DISPONIBLE


class Asignacion(models.Model):
    """Registro de asignaciones de vehículos a clientes/trabajos"""
    
    vehiculo = models.ForeignKey(
        Vehiculo,
        on_delete=models.CASCADE,
        related_name='asignaciones',
        verbose_name='Vehículo'
    )
    
    cliente = models.CharField(
        max_length=100,
        verbose_name='Cliente/Asignado a'
    )
    
    fecha_inicio = models.DateTimeField(
        default=timezone.now,
        verbose_name='Fecha de Inicio'
    )
    
    fecha_fin = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Fecha de Fin'
    )
    
    kilometraje_salida = models.PositiveIntegerField(
        verbose_name='Kilometraje de Salida'
    )
    
    kilometraje_entrada = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name='Kilometraje de Entrada'
    )
    
    motivo = models.TextField(
        verbose_name='Motivo de Asignación'
    )
    
    observaciones = models.TextField(
        blank=True,
        verbose_name='Observaciones'
    )
    
    activa = models.BooleanField(
        default=True,
        verbose_name='Asignación Activa'
    )
    
    class Meta:
        verbose_name = 'Asignación'
        verbose_name_plural = 'Asignaciones'
        ordering = ['-fecha_inicio']
    
    def __str__(self):
        estado = "Activa" if self.activa else "Finalizada"
        return f"{self.vehiculo.matricula} - {self.cliente} ({estado})"
    
    def finalizar(self, kilometraje_entrada):
        """Finaliza una asignación y actualiza el estado del vehículo"""
        self.activa = False
        self.fecha_fin = timezone.now()
        self.kilometraje_entrada = kilometraje_entrada
        self.save()
        
        # Actualizar kilometraje del vehículo y estado
        self.vehiculo.kilometraje = kilometraje_entrada
        self.vehiculo.estado = EstadoVehiculo.DISPONIBLE
        self.vehiculo.save()


class Mantenimiento(models.Model):
    """Registro de mantenimientos y reparaciones"""
    
    TIPO_CHOICES = [
        ('REVISION', 'Revisión'),
        ('REPARACION', 'Reparación'),
        ('ITV', 'ITV'),
        ('NEUMATICOS', 'Cambio de Neumáticos'),
        ('OTROS', 'Otros'),
    ]
    
    vehiculo = models.ForeignKey(
        Vehiculo,
        on_delete=models.CASCADE,
        related_name='mantenimientos',
        verbose_name='Vehículo'
    )
    
    tipo = models.CharField(
        max_length=15,
        choices=TIPO_CHOICES,
        verbose_name='Tipo de Mantenimiento'
    )
    
    fecha_entrada = models.DateField(
        default=timezone.now,
        verbose_name='Fecha de Entrada'
    )
    
    fecha_salida = models.DateField(
        null=True,
        blank=True,
        verbose_name='Fecha de Salida'
    )
    
    descripcion = models.TextField(
        verbose_name='Descripción del Trabajo'
    )
    
    coste = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        default=0,
        verbose_name='Coste (€)'
    )
    
    taller = models.CharField(
        max_length=100,
        blank=True,
        verbose_name='Taller/Proveedor'
    )
    
    completado = models.BooleanField(
        default=False,
        verbose_name='Trabajo Completado'
    )
    
    class Meta:
        verbose_name = 'Mantenimiento'
        verbose_name_plural = 'Mantenimientos'
        ordering = ['-fecha_entrada']
    
    def __str__(self):
        return f"{self.vehiculo.matricula} - {self.get_tipo_display()} ({self.fecha_entrada})"
    
    def finalizar(self, fecha_salida=None):
        """Marca el mantenimiento como completado"""
        self.completado = True
        self.fecha_salida = fecha_salida or timezone.now().date()
        self.save()
        
        # Actualizar estado del vehículo a disponible
        self.vehiculo.estado = EstadoVehiculo.DISPONIBLE
        self.vehiculo.fecha_ultima_revision = self.fecha_salida
        self.vehiculo.save()
