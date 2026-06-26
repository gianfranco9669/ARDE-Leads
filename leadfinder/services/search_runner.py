from django.utils import timezone
from leadfinder.models import Lead, LeadSearch
from .google_places import GooglePlacesClient
from .phone import PhoneNormalizer
from .scoring import LeadScoringService
from .dedupe import DuplicateDetector
class SearchRunner:
    def __init__(self): self.client=GooglePlacesClient(); self.phones=PhoneNormalizer(); self.scoring=LeadScoringService()
    def run(self, search_id):
        s=LeadSearch.objects.get(pk=search_id); s.mark_started()
        created=updated=0
        try:
            data=self.client.text_search(s.query,s.city,s.latitude,s.longitude,s.radius_meters,s.max_results,s.search_mode,s.requested_fields); s.actual_requests+=1; s.audit_log.append({'at':timezone.now().isoformat(),'response_keys':list(data.keys())})
            for p in data.get('places',[])[:s.max_results]:
                if LeadSearch.objects.get(pk=s.pk).status=='cancelled': return
                loc=p.get('location') or {}; phone=self.phones.normalize(p.get('nationalPhoneNumber') or p.get('internationalPhoneNumber'))
                lead,was_created=Lead.objects.update_or_create(place_id=p.get('id'),defaults={'name':(p.get('displayName') or {}).get('text','Sin nombre'),'primary_type':p.get('primaryType',''),'types':p.get('types',[]),'business_status':p.get('businessStatus',''),'formatted_address':p.get('formattedAddress',''),'short_formatted_address':p.get('shortFormattedAddress',''),'city':s.city,'area_label':s.area_label,'latitude':loc.get('latitude'),'longitude':loc.get('longitude'),'national_phone_number':p.get('nationalPhoneNumber',''),'international_phone_number':p.get('internationalPhoneNumber',''),'phone_normalized':phone['normalized'],'website_uri':p.get('websiteUri','') or '','google_maps_uri':p.get('googleMapsUri','') or '','rating':p.get('rating'),'user_rating_count':p.get('userRatingCount') or 0,'source_search':s})
                self.scoring.apply(lead); created+=was_created; updated+=0 if was_created else 1; s.results_found+=1; s.save(update_fields=['results_found','actual_requests','audit_log','updated_at'])
            s.leads_created=created; s.leads_updated=updated; s.duplicates_detected=DuplicateDetector().mark(); s.mark_finished('completed')
        except Exception as e:
            s.api_error_count+=1; s.error_message=str(e); s.save(update_fields=['api_error_count','error_message','updated_at']); s.mark_finished('failed')
