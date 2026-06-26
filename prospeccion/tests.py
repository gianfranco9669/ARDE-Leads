from django.test import TestCase
from .forms import FormularioPlantillaMensaje
from .models import Prospecto, BusquedaProspectos, PlantillaMensaje
from .services.phone import NormalizadorTelefono
from .services.scoring import CalculadorPuntajeProspecto
from .services.whatsapp import GeneradorLinkWhatsapp
from .services.dedupe import DetectorDuplicados

class ProspeccionTests(TestCase):
    def prospecto(self, **kwargs):
        datos={'place_id':'p1','nombre':'Barbería Norte','ciudad':'Lomas','direccion_formateada':'Calle 1','telefono_normalizado':'+5491122223333','sitio_web':''}
        datos.update(kwargs)
        return Prospecto.objects.create(**datos)
    def test_modelos_y_metricas_busqueda(self):
        busqueda=BusquedaProspectos.objects.create(consulta='barbería',ciudad='Lomas',max_resultados=100,estado='running')
        busqueda.resultados_encontrados=20; busqueda.prospectos_creados=3; busqueda.save()
        self.assertEqual(busqueda.progreso(),20); self.assertEqual(busqueda.prospectos_creados,3)
    def test_puntaje(self):
        prospecto=self.prospecto(); puntaje=CalculadorPuntajeProspecto().aplicar(prospecto)
        self.assertGreaterEqual(puntaje['puntaje_oportunidad'],60); self.assertTrue(prospecto.motivos_puntaje)
    def test_normalizador_telefono_argentino(self):
        resultado=NormalizadorTelefono().normalizar('011 15 2222-3333')
        self.assertTrue(resultado['normalizado'].startswith('+549')); self.assertTrue(resultado['numero_whatsapp'])
    def test_link_whatsapp(self):
        prospecto=self.prospecto(); url=GeneradorLinkWhatsapp().generar(prospecto,'Hola mundo')
        self.assertIn('wa.me/5491122223333',url); self.assertIn('Hola%20mundo',url)
    def test_dedupe_por_telefono(self):
        self.prospecto(place_id='p1'); self.prospecto(place_id='p2',telefono_normalizado='+5491122223333')
        self.assertGreater(DetectorDuplicados().marcar(),0); self.assertEqual(Prospecto.objects.filter(es_posible_duplicado=True).count(),2)
    def test_place_id_unico(self):
        self.prospecto(place_id='same')
        with self.assertRaises(Exception): self.prospecto(place_id='same')
    def test_render_plantilla_y_validacion(self):
        prospecto=self.prospecto(); plantilla=PlantillaMensaje.objects.create(nombre='T',cuerpo='Hola {nombre}, hacemos {servicio_ofrecido}',tipo_oferta='webs')
        self.assertIn('Barbería',plantilla.renderizar_para(prospecto)); self.assertFalse(FormularioPlantillaMensaje(data={'nombre':'x','cuerpo':'{mala}','activa':True}).is_valid())
    def test_no_generar_mensaje_para_no_contactar(self):
        prospecto=self.prospecto(estado_comercial='do_not_contact')
        with self.assertRaises(ValueError): GeneradorLinkWhatsapp().generar(prospecto,'Hola')
