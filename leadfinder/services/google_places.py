import requests
from django.conf import settings
class GooglePlacesClient:
    BASE='https://places.googleapis.com/v1/places:searchText'
    MODE_FIELDS={
        'quick':'places.id,places.displayName,places.formattedAddress,places.location,places.websiteUri,places.nationalPhoneNumber,places.googleMapsUri',
        'balanced':settings.GOOGLE_PLACES_DEFAULT_FIELD_MASK,
        'deep':settings.GOOGLE_PLACES_DEFAULT_FIELD_MASK+',places.regularOpeningHours,places.editorialSummary'
    }
    def __init__(self, api_key=None): self.api_key=api_key or settings.GOOGLE_PLACES_API_KEY
    def field_mask(self, mode='balanced', requested_fields=''):
        return requested_fields or self.MODE_FIELDS.get(mode, self.MODE_FIELDS['balanced'])
    def text_search(self, query, city='', latitude=None, longitude=None, radius_meters=3000, max_results=20, mode='balanced', requested_fields=''):
        if not self.api_key: raise RuntimeError('GOOGLE_PLACES_API_KEY no configurada')
        body={'textQuery': f'{query} {city}'.strip(), 'maxResultCount': min(max_results,20)}
        if latitude and longitude: body['locationBias']={'circle':{'center':{'latitude':float(latitude),'longitude':float(longitude)},'radius':float(radius_meters)}}
        r=requests.post(self.BASE,json=body,headers={'X-Goog-Api-Key':self.api_key,'X-Goog-FieldMask':self.field_mask(mode,requested_fields)},timeout=30)
        if r.status_code>=400: raise RuntimeError(f'Places API error {r.status_code}: {r.text[:500]}')
        return r.json()
