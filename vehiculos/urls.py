from django.urls import path
from . import views

app_name = 'vehiculos'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('vehiculos/', views.lista_vehiculos, name='lista_vehiculos'),
    path('vehiculos/<int:vehiculo_id>/', views.detalle_vehiculo, name='detalle_vehiculo'),
    path('asignaciones/', views.lista_asignaciones, name='lista_asignaciones'),
]
