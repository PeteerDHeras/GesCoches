from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Q
from django.contrib import messages
from .models import Vehiculo, Asignacion, EstadoVehiculo


@login_required
def dashboard(request):
    """Vista principal del dashboard con estadísticas y lista de vehículos"""
    
    # Contar vehículos por estado
    total_vehiculos = Vehiculo.objects.count()
    disponibles = Vehiculo.objects.filter(estado=EstadoVehiculo.DISPONIBLE).count()
    en_uso = Vehiculo.objects.filter(estado=EstadoVehiculo.EN_USO).count()
    
    # Lista completa de vehículos con su estado
    vehiculos = Vehiculo.objects.all().order_by('estado', 'matricula')
    
    # Asignaciones activas recientes
    asignaciones_activas = Asignacion.objects.filter(activa=True).select_related('vehiculo')[:5]
    
    context = {
        'total_vehiculos': total_vehiculos,
        'disponibles': disponibles,
        'en_uso': en_uso,
        'vehiculos': vehiculos,
        'asignaciones_activas': asignaciones_activas,
    }
    
    return render(request, 'vehiculos/dashboard.html', context)


@login_required
def lista_vehiculos(request):
    """Lista todos los vehículos con filtros"""
    
    estado_filtro = request.GET.get('estado', '')
    
    vehiculos = Vehiculo.objects.all()
    
    if estado_filtro:
        vehiculos = vehiculos.filter(estado=estado_filtro)
    
    context = {
        'vehiculos': vehiculos,
        'estado_filtro': estado_filtro,
        'estados': EstadoVehiculo.choices,
    }
    
    return render(request, 'vehiculos/lista_vehiculos.html', context)


@login_required
def detalle_vehiculo(request, vehiculo_id):
    """Detalle de un vehículo específico"""
    
    vehiculo = get_object_or_404(Vehiculo, id=vehiculo_id)
    asignaciones = vehiculo.asignaciones.all()[:10]
    
    context = {
        'vehiculo': vehiculo,
        'asignaciones': asignaciones,
    }
    
    return render(request, 'vehiculos/detalle_vehiculo.html', context)


@login_required
def lista_asignaciones(request):
    """Lista de asignaciones con filtro de activas/finalizadas"""
    
    filtro = request.GET.get('filtro', 'activas')
    
    if filtro == 'activas':
        asignaciones = Asignacion.objects.filter(activa=True)
    elif filtro == 'finalizadas':
        asignaciones = Asignacion.objects.filter(activa=False)
    else:
        asignaciones = Asignacion.objects.all()
    
    asignaciones = asignaciones.select_related('vehiculo')
    
    context = {
        'asignaciones': asignaciones,
        'filtro': filtro,
    }
    
    return render(request, 'vehiculos/lista_asignaciones.html', context)
