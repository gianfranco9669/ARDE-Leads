from django.core.management.base import BaseCommand
from leadfinder.services.dedupe import DuplicateDetector
class Command(BaseCommand):
    def handle(self,*a,**o): self.stdout.write(self.style.SUCCESS(f'{DuplicateDetector().mark()} duplicados probables marcados'))
