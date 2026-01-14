from django.contrib import admin
from django.db.models import Count, Q
from django.utils.html import format_html
from django.urls import reverse
from django.utils import timezone
from .models import Vehiculo, Asignacion, EstadoVehiculo


@admin.register(Vehiculo)
class VehiculoAdmin(admin.ModelAdmin):
    list_display = [
        'matricula', 
        'marca_modelo', 
        'color', 
        'año', 
        'estado_badge', 
        'kilometraje',
        'dias_sin_revision'
    ]
    list_filter = ['estado', 'marca', 'año']
    search_fields = ['matricula', 'marca', 'modelo']
    ordering = ['estado', 'matricula']
    
    fieldsets = (
        ('Información del Vehículo', {
            'fields': ('matricula', 'marca', 'modelo', 'color', 'año')
        }),
        ('Estado y Uso', {
            'fields': ('estado', 'kilometraje')
        }),
        ('Fechas', {
            'fields': ('fecha_alta', 'fecha_ultima_revision')
        }),
        ('Observaciones', {
            'fields': ('observaciones',),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['marcar_disponible', 'marcar_baja']
    
    def marca_modelo(self, obj):
        return f"{obj.marca} {obj.modelo}"
    marca_modelo.short_description = 'Vehículo'
    
    def estado_badge(self, obj):
        colors = {
            EstadoVehiculo.DISPONIBLE: '#28a745',
            EstadoVehiculo.EN_USO: '#007bff',
            EstadoVehiculo.BAJA: '#6c757d',
        }
        color = colors.get(obj.estado, '#6c757d')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; border-radius: 3px; font-weight: bold;">{}</span>',
            color,
            obj.get_estado_display()
        )
    estado_badge.short_description = 'Estado'
    
    def dias_sin_revision(self, obj):
        if obj.fecha_ultima_revision:
            dias = (timezone.now().date() - obj.fecha_ultima_revision).days
            if dias > 365:
                color = 'red'
            elif dias > 180:
                color = 'orange'
            else:
                color = 'green'
            return format_html(
                '<span style="color: {}; font-weight: bold;">{} días</span>',
                color,
                dias
            )
        return format_html('<span style="color: red;">Sin revisión</span>')
    dias_sin_revision.short_description = 'Última Revisión'
    
    def marcar_disponible(self, request, queryset):
        updated = queryset.update(estado=EstadoVehiculo.DISPONIBLE)
        self.message_user(request, f'{updated} vehículo(s) marcado(s) como disponible(s).')
    marcar_disponible.short_description = "Marcar como Disponible"
    
    def marcar_baja(self, request, queryset):
        updated = queryset.update(estado=EstadoVehiculo.BAJA)
        self.message_user(request, f'{updated} vehículo(s) dado(s) de baja.')
    marcar_baja.short_description = "Dar de Baja"


@admin.register(Asignacion)
class AsignacionAdmin(admin.ModelAdmin):
    list_display = [
        'vehiculo',
        'cliente',
        'fecha_inicio',
        'fecha_fin',
        'estado_asignacion',
        'km_recorridos'
    ]
    list_filter = ['activa', 'fecha_inicio']
    search_fields = ['vehiculo__matricula', 'cliente']
    date_hierarchy = 'fecha_inicio'
    ordering = ['-fecha_inicio']
    
    fieldsets = (
        ('Vehículo y Cliente', {
            'fields': ('vehiculo', 'cliente')
        }),
        ('Fechas', {
            'fields': ('fecha_inicio', 'fecha_fin')
        }),
        ('Kilometraje', {
            'fields': ('kilometraje_salida', 'kilometraje_entrada')
        }),
        ('Detalles', {
            'fields': ('motivo', 'observaciones', 'activa')
        }),
    )
    
    actions = ['finalizar_asignaciones']
    
    def estado_asignacion(self, obj):
        if obj.activa:
            return format_html(
                '<span style="background-color: #007bff; color: white; padding: 3px 10px; border-radius: 3px; font-weight: bold;">ACTIVA</span>'
            )
        else:
            return format_html(
                '<span style="background-color: #6c757d; color: white; padding: 3px 10px; border-radius: 3px;">Finalizada</span>'
            )
    estado_asignacion.short_description = 'Estado'
    
    def km_recorridos(self, obj):
        if obj.kilometraje_entrada:
            km = obj.kilometraje_entrada - obj.kilometraje_salida
            return f"{km} km"
        return "-"
    km_recorridos.short_description = 'Km Recorridos'
    
    def finalizar_asignaciones(self, request, queryset):
        count = 0
        for asignacion in queryset.filter(activa=True):
            if asignacion.vehiculo.kilometraje:
                asignacion.finalizar(asignacion.vehiculo.kilometraje)
                count += 1
        self.message_user(request, f'{count} asignación(es) finalizada(s).')
    finalizar_asignaciones.short_description = "Finalizar Asignaciones Seleccionadas"


# Personalización del Admin Site
admin.site.site_header = 'GesCoches - Gestión de Vehículos'
admin.site.site_title = 'GesCoches Admin'
admin.site.index_title = 'Panel de Control de Vehículos de Sustitución'
