from django.db import models
from django.core.validators import RegexValidator
from django.utils import timezone
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver


class EstadoVehiculo(models.TextChoices):
    """Estados posibles de un vehículo de sustitución"""
    DISPONIBLE = 'DISPONIBLE', 'Disponible'
    EN_USO = 'EN_USO', 'En Uso'
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


# Signals para automatizar estados de vehículos
@receiver(post_save, sender=Asignacion)
def actualizar_estado_vehiculo_en_asignacion(sender, instance, created, **kwargs):
    """
    Automáticamente cambia el estado del vehículo a EN_USO cuando se crea una asignación activa.
    Si la asignación se marca como inactiva, vuelve el vehículo a DISPONIBLE.
    """
    if instance.activa:
        # Si la asignación está activa, el vehículo debe estar EN_USO
        if instance.vehiculo.estado != EstadoVehiculo.EN_USO:
            instance.vehiculo.estado = EstadoVehiculo.EN_USO
            instance.vehiculo.save(update_fields=['estado'])
    else:
        # Si la asignación se finaliza, verificar si hay otras asignaciones activas
        tiene_otras_asignaciones_activas = Asignacion.objects.filter(
            vehiculo=instance.vehiculo,
            activa=True
        ).exclude(id=instance.id).exists()
        
        if not tiene_otras_asignaciones_activas:
            # No hay otras asignaciones activas, marcar como DISPONIBLE
            if instance.vehiculo.estado != EstadoVehiculo.DISPONIBLE:
                instance.vehiculo.estado = EstadoVehiculo.DISPONIBLE
                instance.vehiculo.save(update_fields=['estado'])
