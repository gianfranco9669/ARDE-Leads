from django.core.management.base import BaseCommand
from prospeccion.models import Prospecto, PlantillaMensaje, Campania
from prospeccion.services.scoring import CalculadorPuntajeProspecto
from prospeccion.services.dedupe import DetectorDuplicados
class Command(BaseCommand):
    help='Carga datos demo premium para ARDE Leads.'
    def handle(self,*args,**options):
        datos=[('demo-1','Barbería Fuego Norte','barber_shop','Lomas de Zamora','Las Lomitas','+5491122223333','',4.7,89,'new'),('demo-2','Taller Ruta 7','car_repair','Lomas de Zamora','Banfield','+541142223333','https://tallerruta7.com',4.2,35,'review'),('demo-3','Odonto Sur','dentist','Temperley','Temperley Centro','+5491133344455','',4.8,120,'contacted'),('demo-4','Gimnasio Pulso','gym','Adrogué','Adrogué','+5491144455566','',4.4,67,'replied'),('demo-5','Parrilla Don Tito','restaurant','Lomas de Zamora','Centro','+541142221111','https://dontito.example',4.1,240,'interested'),('demo-6','Inmobiliaria Horizonte','real_estate_agency','Banfield','Banfield Este','+5491155566677','',3.9,18,'won'),('demo-7','Barbería Fuego Norte Sucursal','barber_shop','Lomas de Zamora','Las Lomitas','+5491122223333','',4.6,55,'new'),('demo-8','Estética Aurora','beauty_salon','Lanús','Lanús Oeste','+5491166677788','',4.9,44,'lost'),('demo-9','Veterinaria Patitas','veterinary_care','Lomas de Zamora','Turdera','+541142229999','https://patitas.example',4.5,101,'discarded'),('demo-10','Café Brasa','cafe','Lomas de Zamora','Centro','+5491177788899','',4.3,73,'do_not_contact')]
        for place_id,nombre,rubro,ciudad,zona,tel,web,calif,resenas,estado in datos:
            p,_=Prospecto.objects.update_or_create(place_id=place_id,defaults={'nombre':nombre,'rubro':rubro,'ciudad':ciudad,'zona':zona,'direccion_formateada':f'{zona}, {ciudad}, Buenos Aires','direccion_corta':f'{zona}, {ciudad}','telefono_normalizado':tel,'sitio_web':web,'url_google_maps':'https://maps.google.com/?q='+nombre.replace(' ','+'),'calificacion':calif,'cantidad_resenas':resenas,'estado_google':'OPERATIONAL','estado_comercial':estado})
            CalculadorPuntajeProspecto().aplicar(p)
        plantilla1,_=PlantillaMensaje.objects.get_or_create(nombre='Oferta web inicial',defaults={'rubro_objetivo':'negocios locales','tipo_oferta':'sitio web premium','cuerpo':'Hola {nombre}, vi tu ficha en {zona} y noté que no aparece una web clara. En ARDE creamos {servicio_ofrecido} para {rubro}. ¿Te puedo mostrar una idea rápida?'})
        plantilla2,_=PlantillaMensaje.objects.get_or_create(nombre='Optimización presencia digital',defaults={'rubro_objetivo':'servicios locales','tipo_oferta':'mejora de presencia digital','cuerpo':'Hola {nombre}, trabajo con negocios de {zona} para mejorar consultas desde Google. Vi tu perfil y creo que hay una oportunidad concreta para {servicio_ofrecido}.'})
        campania,_=Campania.objects.get_or_create(nombre='Demo sin web zona sur',defaults={'rubro':'','zona':'Lomas','tipo_oferta':'sitio web premium','plantilla':plantilla1,'estado':'active'})
        campania.prospectos.set(Prospecto.objects.exclude(estado_comercial='do_not_contact').filter(sitio_web='')[:8])
        duplicados=DetectorDuplicados().marcar()
        self.stdout.write(self.style.SUCCESS(f'Demo cargada: {Prospecto.objects.count()} prospectos, 2 plantillas, 1 campaña, {duplicados} duplicados posibles.'))
