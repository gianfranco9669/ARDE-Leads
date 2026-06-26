from django.core.management import call_command
from django.test import Client, TestCase
from django.urls import reverse
from prospeccion.forms import FormularioPlantillaMensaje
from prospeccion.models import Campania, PlantillaMensaje, Prospecto, RegistroContacto
from prospeccion.services.dedupe import DetectorDuplicados
from prospeccion.services.phone import NormalizadorTelefono
from prospeccion.services.scoring import CalculadorPuntajeProspecto
from prospeccion.services.whatsapp import GeneradorLinkWhatsapp

class ProspeccionFlujosTests(TestCase):
    def setUp(self):
        self.client=Client()
        self.prospecto=Prospecto.objects.create(place_id='p1',nombre='Barbería Norte',rubro='barber_shop',ciudad='Lomas de Zamora',zona='Las Lomitas',direccion_formateada='Calle 1',telefono_normalizado='+5491122223333',sitio_web='')
        CalculadorPuntajeProspecto().aplicar(self.prospecto)
        self.plantilla=PlantillaMensaje.objects.create(nombre='Inicial',rubro_objetivo='barber_shop',tipo_oferta='sitio web',cuerpo='Hola {nombre}, hacemos {servicio_ofrecido} en {zona}.')
    def test_cargar_demo_prospectos(self):
        call_command('cargar_demo_prospectos', verbosity=0)
        self.assertGreaterEqual(Prospecto.objects.count(), 10)
        self.assertGreaterEqual(PlantillaMensaje.objects.count(), 2)
        self.assertEqual(Campania.objects.count(), 1)
    def test_dashboard(self):
        r=self.client.get(reverse('prospeccion:dashboard'))
        self.assertEqual(r.status_code,200); self.assertContains(r,'Detectá oportunidades calientes antes que nadie')
    def test_explorador_y_filtros(self):
        r=self.client.get(reverse('prospeccion:explorador'), {'sin_web':'1','con_telefono':'1','q':'Barbería'})
        self.assertEqual(r.status_code,200); self.assertContains(r,'Barbería Norte'); self.assertNotContains(r,'barber_shop')
    def test_busqueda_global_por_zona_rubro_estado_y_campania(self):
        campania=Campania.objects.create(nombre='Campaña fuego',rubro='barber_shop',zona='Lomas',plantilla=self.plantilla,estado='active')
        campania.prospectos.add(self.prospecto)
        for q in ['Barbería','Las Lomitas','Lomas','Nuevo','Campaña fuego']:
            r=self.client.get(reverse('prospeccion:explorador'), {'q':q})
            self.assertContains(r,'Barbería Norte')
    def test_drawer_del_prospecto(self):
        r=self.client.get(reverse('prospeccion:drawer_prospecto', args=[self.prospecto.pk]))
        self.assertEqual(r.status_code,200); self.assertContains(r,'No contactar'); self.assertContains(r,'Marcar como contactado')
    def test_generacion_y_copia_mensaje(self):
        r=self.client.post(reverse('prospeccion:accion_whatsapp', args=[self.prospecto.pk]), {'plantilla':self.plantilla.pk,'accion':'copiar'}, follow=True)
        self.assertEqual(r.status_code,200); self.assertEqual(RegistroContacto.objects.filter(prospecto=self.prospecto, estado='copiado').count(),1)
    def test_bloqueo_no_contactar(self):
        self.prospecto.estado_comercial='do_not_contact'; self.prospecto.save(update_fields=['estado_comercial'])
        with self.assertRaises(ValueError): GeneradorLinkWhatsapp().generar(self.prospecto,'Hola')
        r=self.client.get(reverse('prospeccion:drawer_prospecto', args=[self.prospecto.pk]))
        self.assertContains(r,'WhatsApp deshabilitado')
    def test_cambio_estado_comercial_registra_historial(self):
        r=self.client.post(reverse('prospeccion:cambiar_estado', args=[self.prospecto.pk,'interested']), follow=True)
        self.assertEqual(r.status_code,200); self.prospecto.refresh_from_db(); self.assertEqual(self.prospecto.estado_comercial,'interested')
        self.assertTrue(RegistroContacto.objects.filter(prospecto=self.prospecto, cuerpo_mensaje__icontains='Estado cambiado').exists())
    def test_creacion_campania(self):
        r=self.client.post(reverse('prospeccion:campanias'), {'nombre':'Zona Sur','rubro':'barber_shop','zona':'Lomas','tipo_oferta':'web','plantilla':self.plantilla.pk,'estado':'active'}, follow=True)
        self.assertEqual(r.status_code,200); self.assertTrue(Campania.objects.filter(nombre='Zona Sur').exists())
    def test_creacion_plantilla(self):
        r=self.client.post(reverse('prospeccion:plantillas'), {'nombre':'Nueva','rubro_objetivo':'dentist','tipo_oferta':'landing','cuerpo':'Hola {nombre} en {zona}','activa':'on'}, follow=True)
        self.assertEqual(r.status_code,200); self.assertTrue(PlantillaMensaje.objects.filter(nombre='Nueva').exists())
    def test_pipeline(self):
        r=self.client.get(reverse('prospeccion:pipeline'))
        self.assertEqual(r.status_code,200); self.assertContains(r,'Ver detalle'); self.assertContains(r,'No contactar')

    def test_explorador_renderiza_acciones_visibles(self):
        r=self.client.get(reverse('prospeccion:explorador'))
        self.assertContains(r,'Ver detalle')
        self.assertContains(r,'Marcar como contactado')
        self.assertContains(r,'Marcar como interesado')
        self.assertContains(r,'No contactar')
        self.assertContains(r,'Descartar')
    def test_acciones_estado_desde_explorador(self):
        for estado in ['contacted','interested','do_not_contact','discarded']:
            prospecto=Prospecto.objects.create(place_id=f'accion-{estado}',nombre=f'Prospecto {estado}',rubro='store',ciudad='Lomas')
            r=self.client.post(reverse('prospeccion:cambiar_estado', args=[prospecto.pk,estado]), HTTP_REFERER=reverse('prospeccion:explorador'), follow=True)
            self.assertEqual(r.status_code,200)
            prospecto.refresh_from_db()
            self.assertEqual(prospecto.estado_comercial,estado)
            self.assertTrue(RegistroContacto.objects.filter(prospecto=prospecto, cuerpo_mensaje__icontains='Estado cambiado').exists())
    def test_normalizador_puntaje_dedupe_y_validacion(self):
        tel=NormalizadorTelefono().normalizar('011 15 2222-3333')
        self.assertTrue(tel['normalizado'].startswith('+549'))
        Prospecto.objects.create(place_id='p2',nombre='Barbería Norte 2',ciudad='Lomas de Zamora',telefono_normalizado='+5491122223333')
        self.assertGreater(DetectorDuplicados().marcar(),0)
        self.assertFalse(FormularioPlantillaMensaje(data={'nombre':'x','cuerpo':'{variable_mala}','activa':True}).is_valid())
