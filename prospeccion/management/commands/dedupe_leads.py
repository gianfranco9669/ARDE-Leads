from django.core.management.base import BaseCommand
from prospeccion.services.dedupe import DetectorDuplicados
class Command(BaseCommand):
    help='Marca duplicados probables para revisión visual.'
    def handle(self,*a,**o): self.stdout.write(self.style.SUCCESS(f'{DetectorDuplicados().marcar()} duplicados probables marcados'))
