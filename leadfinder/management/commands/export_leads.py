import csv
from django.core.management.base import BaseCommand
from leadfinder.models import Lead
class Command(BaseCommand):
    def add_arguments(self,p): p.add_argument('--output',default='leads_export.csv')
    def handle(self,*a,**o):
        fields=['place_id','name','primary_type','city','phone_normalized','website_uri','google_maps_uri','total_score','commercial_status']
        with open(o['output'],'w',newline='',encoding='utf-8') as f:
            w=csv.writer(f); w.writerow(fields)
            for l in Lead.objects.all(): w.writerow([getattr(l,x) for x in fields])
        self.stdout.write(self.style.SUCCESS(o['output']))
