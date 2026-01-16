from django.core.management.base import BaseCommand
from vehiculos.models import Asignacion


class Command(BaseCommand):
    """
    Management command para limpiar asignaciones finalizadas antiguas.
    
    Uso:
        python manage.py limpiar_asignaciones --semanas=3
        python manage.py limpiar_asignaciones --semanas=4 --confirmar
    """
    
    help = 'Limpia asignaciones finalizadas de hace más de N semanas'

    def add_arguments(self, parser):
        parser.add_argument(
            '--semanas',
            type=int,
            default=3,
            help='Número de semanas a partir de las cuales se eliminan asignaciones (default: 3)'
        )
        parser.add_argument(
            '--confirmar',
            action='store_true',
            help='Confirma la eliminación. Sin este flag, solo muestra lo que se eliminaría'
        )

    def handle(self, *args, **options):
        semanas = options['semanas']
        confirmar = options['confirmar']
        
        from django.utils import timezone
        from datetime import timedelta
        
        # Calcular fecha límite
        fecha_limite = timezone.now() - timedelta(weeks=semanas)
        
        # Obtener asignaciones a eliminar
        asignaciones_a_eliminar = Asignacion.objects.filter(
            activa=False,
            fecha_fin__lt=fecha_limite
        )
        
        cantidad = asignaciones_a_eliminar.count()
        
        if cantidad == 0:
            self.stdout.write(
                self.style.SUCCESS(
                    f'✅ No hay asignaciones para eliminar (anterior a {fecha_limite.strftime("%d/%m/%Y")})'
                )
            )
            return
        
        # Mostrar información
        self.stdout.write(
            self.style.WARNING(
                f'⚠️  Se encontraron {cantidad} asignaciones finalizadas hace más de {semanas} semanas'
            )
        )
        self.stdout.write(f'   Fecha límite: {fecha_limite.strftime("%d/%m/%Y %H:%M")}')
        self.stdout.write('   Asignaciones:')
        
        for asignacion in asignaciones_a_eliminar[:10]:  # Mostrar máximo 10
            self.stdout.write(
                f'   - {asignacion.vehiculo.matricula} ({asignacion.cliente}) '
                f'finalizada el {asignacion.fecha_fin.strftime("%d/%m/%Y")}'
            )
        
        if cantidad > 10:
            self.stdout.write(f'   ... y {cantidad - 10} más')
        
        # Si no se confirma, solo mostrar
        if not confirmar:
            self.stdout.write(
                self.style.WARNING(
                    '\n⚠️  Uso --confirmar para ejecutar la eliminación'
                )
            )
            self.stdout.write(
                '   Comando: python manage.py limpiar_asignaciones --semanas=3 --confirmar'
            )
            return
        
        # Confirmar con el usuario
        confirmacion = input(f'\n¿Eliminar {cantidad} asignaciones? (s/n): ')
        if confirmacion.lower() != 's':
            self.stdout.write(self.style.WARNING('Operación cancelada'))
            return
        
        # Ejecutar la eliminación
        asignaciones_a_eliminar.delete()
        
        self.stdout.write(
            self.style.SUCCESS(
                f'✅ Se eliminaron {cantidad} asignaciones exitosamente'
            )
        )
