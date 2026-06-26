import csv
from django.core.management.base import BaseCommand
from prospeccion.models import Prospecto
class Command(BaseCommand):
    help='Exporta prospectos a CSV.'
    def add_arguments(self,p): p.add_argument('--output',default='prospectos_export.csv')
    def handle(self,*a,**o):
        campos=['place_id','nombre','rubro','ciudad','telefono_normalizado','sitio_web','url_google_maps','puntaje_total','estado_comercial']
        with open(o['output'],'w',newline='',encoding='utf-8') as archivo:
            escritor=csv.writer(archivo); escritor.writerow(campos)
            for prospecto in Prospecto.objects.all(): escritor.writerow([getattr(prospecto,campo) for campo in campos])
        self.stdout.write(self.style.SUCCESS(o['output']))
