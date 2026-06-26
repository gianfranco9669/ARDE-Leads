from django.core.management.base import BaseCommand
from leadfinder.models import Lead
from leadfinder.services.scoring import LeadScoringService
class Command(BaseCommand):
    def handle(self,*a,**o):
        svc=LeadScoringService(); n=0
        for lead in Lead.objects.all(): svc.apply(lead); n+=1
        self.stdout.write(self.style.SUCCESS(f'{n} leads repuntuados'))
