from django.utils import timezone
from prospeccion.models import Prospecto, BusquedaProspectos
from .google_places import ClienteGooglePlaces
from .phone import NormalizadorTelefono
from .scoring import CalculadorPuntajeProspecto
from .dedupe import DetectorDuplicados
class EjecutorBusqueda:
    def __init__(self):
        self.cliente=ClienteGooglePlaces(); self.telefonos=NormalizadorTelefono(); self.puntajes=CalculadorPuntajeProspecto()
    def ejecutar(self, busqueda_id):
        busqueda=BusquedaProspectos.objects.get(pk=busqueda_id); busqueda.marcar_iniciada(); creados=actualizados=0
        try:
            datos=self.cliente.buscar_texto(busqueda.consulta,busqueda.ciudad,busqueda.latitud,busqueda.longitud,busqueda.radio_metros,busqueda.max_resultados,busqueda.modo_busqueda,busqueda.campos_solicitados)
            busqueda.solicitudes_reales+=1; busqueda.bitacora_api.append({'fecha':timezone.now().isoformat(),'claves_respuesta':list(datos.keys())})
            for item in datos.get('places',[])[:busqueda.max_resultados]:
                if BusquedaProspectos.objects.get(pk=busqueda.pk).estado=='cancelled': return
                ubicacion=item.get('location') or {}; telefono=self.telefonos.normalizar(item.get('nationalPhoneNumber') or item.get('internationalPhoneNumber'))
                prospecto,fue_creado=Prospecto.objects.update_or_create(place_id=item.get('id'),defaults={'nombre':(item.get('displayName') or {}).get('text','Sin nombre'),'rubro':item.get('primaryType',''),'tipos':item.get('types',[]),'estado_google':item.get('businessStatus',''),'direccion_formateada':item.get('formattedAddress',''),'direccion_corta':item.get('shortFormattedAddress',''),'ciudad':busqueda.ciudad,'zona':busqueda.zona,'latitud':ubicacion.get('latitude'),'longitud':ubicacion.get('longitude'),'telefono_nacional':item.get('nationalPhoneNumber',''),'telefono_internacional':item.get('internationalPhoneNumber',''),'telefono_normalizado':telefono['normalizado'],'sitio_web':item.get('websiteUri','') or '','url_google_maps':item.get('googleMapsUri','') or '','calificacion':item.get('rating'),'cantidad_resenas':item.get('userRatingCount') or 0,'busqueda_origen':busqueda})
                self.puntajes.aplicar(prospecto); creados+=fue_creado; actualizados+=0 if fue_creado else 1; busqueda.resultados_encontrados+=1; busqueda.save(update_fields=['resultados_encontrados','solicitudes_reales','bitacora_api','actualizado_el'])
            busqueda.prospectos_creados=creados; busqueda.prospectos_actualizados=actualizados; busqueda.duplicados_detectados=DetectorDuplicados().marcar(); busqueda.marcar_finalizada('completed')
        except Exception as exc:
            busqueda.errores_api+=1; busqueda.mensaje_error=str(exc); busqueda.save(update_fields=['errores_api','mensaje_error','actualizado_el']); busqueda.marcar_finalizada('failed')
