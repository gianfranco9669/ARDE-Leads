from django.test import TestCase
from .forms import MessageTemplateForm
from .models import Lead, LeadSearch, MessageTemplate
from .services.phone import PhoneNormalizer
from .services.scoring import LeadScoringService
from .services.whatsapp import WhatsappLinkBuilder
from .services.dedupe import DuplicateDetector
class LeadfinderTests(TestCase):
    def lead(self, **kw):
        data={'place_id':'p1','name':'Barbería Norte','city':'Lomas','formatted_address':'Calle 1','phone_normalized':'+5491122223333','website_uri':''}; data.update(kw); return Lead.objects.create(**data)
    def test_models_and_search_metrics(self):
        s=LeadSearch.objects.create(query='barbería',city='Lomas',max_results=100); s.results_found=20; s.leads_created=3; s.save(); self.assertEqual(s.progress(),0); self.assertEqual(s.leads_created,3)
    def test_scoring(self):
        l=self.lead(); score=LeadScoringService().apply(l); self.assertGreaterEqual(score['opportunity_score'],60); self.assertTrue(l.score_reasons)
    def test_phone_normalizer_argentina(self):
        r=PhoneNormalizer().normalize('011 15 2222-3333'); self.assertTrue(r['normalized'].startswith('+549')); self.assertTrue(r['whatsapp_number'])
    def test_whatsapp_link(self):
        l=self.lead(); url=WhatsappLinkBuilder().build(l,'Hola mundo'); self.assertIn('wa.me/5491122223333',url); self.assertIn('Hola%20mundo',url)
    def test_dedupe_by_phone(self):
        self.lead(place_id='p1'); self.lead(place_id='p2',phone_normalized='+5491122223333'); self.assertGreater(DuplicateDetector().mark(),0); self.assertEqual(Lead.objects.filter(is_possible_duplicate=True).count(),2)
    def test_unique_place_id(self):
        self.lead(place_id='same');
        with self.assertRaises(Exception): self.lead(place_id='same')
    def test_template_render_and_validation(self):
        l=self.lead(); t=MessageTemplate.objects.create(name='T',body='Hola {nombre}, hacemos {servicio_ofrecido}',offer_type='webs'); self.assertIn('Barbería',t.render_for(l)); self.assertFalse(MessageTemplateForm(data={'name':'x','body':'{mala}','is_active':True}).is_valid())
    def test_no_message_for_do_not_contact(self):
        l=self.lead(commercial_status='do_not_contact')
        with self.assertRaises(ValueError): WhatsappLinkBuilder().build(l,'Hola')
