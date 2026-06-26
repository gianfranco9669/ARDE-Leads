from django.core.management.base import BaseCommand
from leadfinder.models import LeadSearch
from leadfinder.services.search_runner import SearchRunner
class Command(BaseCommand):
    def add_arguments(self,p):
        p.add_argument('--query',required=True); p.add_argument('--city',default=''); p.add_argument('--radius',type=int,default=3000); p.add_argument('--max-results',type=int,default=100); p.add_argument('--mode',default='balanced')
    def handle(self,*a,**o):
        s=LeadSearch.objects.create(query=o['query'],city=o['city'],radius_meters=o['radius'],max_results=o['max_results'],search_mode=o['mode'],status='queued',estimated_requests=max(1,(o['max_results']+19)//20))
        SearchRunner().run(s.pk); self.stdout.write(self.style.SUCCESS(f'Búsqueda {s.pk} finalizada: {LeadSearch.objects.get(pk=s.pk).status}'))
