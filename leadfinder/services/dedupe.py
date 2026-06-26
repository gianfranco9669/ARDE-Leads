from .text import normalize_name
from leadfinder.models import Lead
class DuplicateDetector:
    def mark(self):
        count=0
        for lead in Lead.objects.exclude(phone_normalized=''):
            qs=Lead.objects.filter(phone_normalized=lead.phone_normalized).exclude(pk=lead.pk)
            if qs.exists():
                key=f'phone:{lead.phone_normalized}'; Lead.objects.filter(pk__in=[lead.pk,*qs.values_list('pk',flat=True)]).update(is_possible_duplicate=True, duplicate_group_key=key); count+=qs.count()
        for lead in Lead.objects.all():
            key=f'nameaddr:{normalize_name(lead.name)}:{normalize_name(lead.city or lead.formatted_address)[:40]}'
            qs=Lead.objects.filter(normalized_name=lead.normalized_name, city=lead.city).exclude(pk=lead.pk)
            if qs.exists(): Lead.objects.filter(pk__in=[lead.pk,*qs.values_list('pk',flat=True)]).update(is_possible_duplicate=True, duplicate_group_key=key); count+=qs.count()
        return count
