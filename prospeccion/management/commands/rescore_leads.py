from django.core.management.base import BaseCommand
from prospeccion.models import Prospecto
from prospeccion.services.scoring import CalculadorPuntajeProspecto
class Command(BaseCommand):
    help='Recalcula puntajes de prospectos.'
    def handle(self,*a,**o):
        calculador=CalculadorPuntajeProspecto(); total=0
        for prospecto in Prospecto.objects.all(): calculador.aplicar(prospecto); total+=1
        self.stdout.write(self.style.SUCCESS(f'{total} prospectos repuntuados'))
