from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Q
from django.contrib import messages
from django.http import HttpResponseRedirect, HttpResponseForbidden
from django.urls import reverse
from .models import Vehiculo, Asignacion, EstadoVehiculo


# SISTEMA DE LIMPIEZA DE ASIGNACIONES ANTIGUAS
# =============================================
# Para limpiar asignaciones finalizadas de hace más de 3 semanas, usa cualquiera de estos métodos:
#
# OPCIÓN 1: Management Command (RECOMENDADO)
#   python manage.py limpiar_asignaciones --semanas=3
#   python manage.py limpiar_asignaciones --semanas=3 --confirmar  # Para ejecutar de verdad
#
# OPCIÓN 2: Llamada directa en el shell de Django
#   python manage.py shell
#   >>> from vehiculos.models import Asignacion
#   >>> Asignacion.limpiar_asignaciones_antiguas(semanas=3)
#
# OPCIÓN 3: Desde una tarea programada (Celery)
#   Agregar una tarea periódica que ejecute:
#   Asignacion.limpiar_asignaciones_antiguas(semanas=3)
#
# OPCIÓN 4: Botón en el Admin de Django (VER ABAJO)
#   ↓↓↓
#


@login_required
def limpiar_asignaciones_admin(request):
    """
    Vista para limpiar asignaciones antiguas desde el admin de Django.
    Solo accesible a usuarios staff (admin).
    """
    # Verificar permisos de staff
    if not request.user.is_staff:
        return HttpResponseForbidden("No tienes permisos para acceder a esta página")
    
    semanas = int(request.GET.get('semanas', 3))
    
    # Calcular fecha límite
    from django.utils import timezone
    from datetime import timedelta
    fecha_limite = timezone.now() - timedelta(weeks=semanas)
    
    # Obtener asignaciones a eliminar
    asignaciones_a_eliminar = Asignacion.objects.filter(
        activa=False,
        fecha_fin__lt=fecha_limite
    )
    
    cantidad = asignaciones_a_eliminar.count()
    
    if request.method == 'POST' and request.POST.get('confirmar') == 'si':
        # Ejecutar eliminación
        asignaciones_a_eliminar.delete()
        messages.success(request, f'✅ Se eliminaron {cantidad} asignaciones finalizadas hace más de {semanas} semanas.')
        return HttpResponseRedirect(reverse('admin:vehiculos_asignacion_changelist'))
    
    # Mostrar confirmación
    context = {
        'cantidad': cantidad,
        'semanas': semanas,
        'fecha_limite': fecha_limite,
        'asignaciones': asignaciones_a_eliminar[:20],
        'total_mostrado': min(20, cantidad),
    }
    
    return render(request, 'admin/limpiar_asignaciones.html', context)


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
