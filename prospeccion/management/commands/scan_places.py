from django.core.management.base import BaseCommand
from prospeccion.models import BusquedaProspectos
from prospeccion.services.search_runner import EjecutorBusqueda
class Command(BaseCommand):
    help='Ejecuta una búsqueda en Google Places y guarda prospectos.'
    def add_arguments(self,p):
        p.add_argument('--query',required=True); p.add_argument('--city',default=''); p.add_argument('--radius',type=int,default=3000); p.add_argument('--max-results',type=int,default=100); p.add_argument('--mode',default='balanced')
    def handle(self,*a,**o):
        busqueda=BusquedaProspectos.objects.create(consulta=o['query'],ciudad=o['city'],radio_metros=o['radius'],max_resultados=o['max_results'],modo_busqueda=o['mode'],estado='queued',solicitudes_estimadas=max(1,(o['max_results']+19)//20))
        EjecutorBusqueda().ejecutar(busqueda.pk); self.stdout.write(self.style.SUCCESS(f'Búsqueda {busqueda.pk} finalizada: {BusquedaProspectos.objects.get(pk=busqueda.pk).get_estado_display()}'))
