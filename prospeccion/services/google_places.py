import requests
from django.conf import settings
class ClienteGooglePlaces:
    URL_TEXT_SEARCH='https://places.googleapis.com/v1/places:searchText'
    CAMPOS_POR_MODO={
        'quick':'places.id,places.displayName,places.formattedAddress,places.location,places.websiteUri,places.nationalPhoneNumber,places.googleMapsUri',
        'balanced':settings.GOOGLE_PLACES_DEFAULT_FIELD_MASK,
        'deep':settings.GOOGLE_PLACES_DEFAULT_FIELD_MASK+',places.regularOpeningHours,places.editorialSummary',
    }
    def __init__(self, api_key=None): self.api_key=api_key or settings.GOOGLE_PLACES_API_KEY
    def mascara_campos(self, modo='balanced', campos_solicitados=''):
        return campos_solicitados or self.CAMPOS_POR_MODO.get(modo, self.CAMPOS_POR_MODO['balanced'])
    def buscar_texto(self, consulta, ciudad='', latitud=None, longitud=None, radio_metros=3000, max_resultados=20, modo='balanced', campos_solicitados=''):
        if not self.api_key: raise RuntimeError('GOOGLE_PLACES_API_KEY no configurada')
        cuerpo={'textQuery': f'{consulta} {ciudad}'.strip(), 'maxResultCount': min(max_resultados,20)}
        if latitud and longitud:
            cuerpo['locationBias']={'circle':{'center':{'latitude':float(latitud),'longitude':float(longitud)},'radius':float(radio_metros)}}
        respuesta=requests.post(self.URL_TEXT_SEARCH,json=cuerpo,headers={'X-Goog-Api-Key':self.api_key,'X-Goog-FieldMask':self.mascara_campos(modo,campos_solicitados)},timeout=30)
        if respuesta.status_code>=400: raise RuntimeError(f'Error Places API {respuesta.status_code}: {respuesta.text[:500]}')
        return respuesta.json()
