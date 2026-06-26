from django.conf import settings
from django.db import models
from django.utils import timezone

class TimeStamped(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta: abstract = True

class LeadSearch(TimeStamped):
    QUICK='quick'; BALANCED='balanced'; DEEP='deep'
    MODES=[(QUICK,'Quick'),(BALANCED,'Balanced'),(DEEP,'Deep')]
    STATUSES=[('draft','Draft'),('queued','Queued'),('running','Running'),('completed','Completed'),('failed','Failed'),('cancelled','Cancelled')]
    query=models.CharField(max_length=180); city=models.CharField(max_length=120, blank=True)
    area_label=models.CharField(max_length=160, blank=True)
    latitude=models.DecimalField(max_digits=10, decimal_places=7, null=True, blank=True)
    longitude=models.DecimalField(max_digits=10, decimal_places=7, null=True, blank=True)
    radius_meters=models.PositiveIntegerField(default=3000)
    search_mode=models.CharField(max_length=16, choices=MODES, default=BALANCED)
    requested_fields=models.TextField(blank=True)
    max_results=models.PositiveIntegerField(default=60)
    status=models.CharField(max_length=16, choices=STATUSES, default='draft', db_index=True)
    estimated_requests=models.PositiveIntegerField(default=0); actual_requests=models.PositiveIntegerField(default=0)
    results_found=models.PositiveIntegerField(default=0); leads_created=models.PositiveIntegerField(default=0); leads_updated=models.PositiveIntegerField(default=0)
    duplicates_detected=models.PositiveIntegerField(default=0); api_error_count=models.PositiveIntegerField(default=0)
    error_message=models.TextField(blank=True); audit_log=models.JSONField(default=list, blank=True)
    started_at=models.DateTimeField(null=True, blank=True); finished_at=models.DateTimeField(null=True, blank=True)
    created_by=models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL)
    def progress(self):
        return min(100, int((self.results_found or 0) / max(1,self.max_results) * 100)) if self.status=='running' else (100 if self.status=='completed' else 0)
    def mark_started(self): self.status='running'; self.started_at=timezone.now(); self.save(update_fields=['status','started_at','updated_at'])
    def mark_finished(self, status='completed'): self.status=status; self.finished_at=timezone.now(); self.save(update_fields=['status','finished_at','updated_at'])
    def __str__(self): return f'{self.query} · {self.city or self.area_label}'

class Lead(TimeStamped):
    STATUSES=[('new','Nuevo'),('review','Revisar'),('contacted','Contactado'),('replied','Respondió'),('interested','Interesado'),('won','Ganado'),('lost','Perdido'),('discarded','Descartado'),('do_not_contact','No contactar')]
    place_id=models.CharField(max_length=255, unique=True)
    name=models.CharField(max_length=255); normalized_name=models.CharField(max_length=255, db_index=True, blank=True)
    primary_type=models.CharField(max_length=100, blank=True); types=models.JSONField(default=list, blank=True)
    business_status=models.CharField(max_length=80, blank=True)
    formatted_address=models.TextField(blank=True); short_formatted_address=models.CharField(max_length=255, blank=True)
    city=models.CharField(max_length=120, blank=True); area_label=models.CharField(max_length=160, blank=True)
    latitude=models.DecimalField(max_digits=10, decimal_places=7, null=True, blank=True); longitude=models.DecimalField(max_digits=10, decimal_places=7, null=True, blank=True)
    national_phone_number=models.CharField(max_length=80, blank=True); international_phone_number=models.CharField(max_length=80, blank=True); phone_normalized=models.CharField(max_length=40, blank=True, db_index=True)
    website_uri=models.URLField(max_length=500, blank=True); google_maps_uri=models.URLField(max_length=500, blank=True)
    rating=models.DecimalField(max_digits=3, decimal_places=2, null=True, blank=True); user_rating_count=models.PositiveIntegerField(default=0)
    source_search=models.ForeignKey(LeadSearch, null=True, blank=True, on_delete=models.SET_NULL, related_name='leads')
    has_website=models.BooleanField(default=False, db_index=True); has_phone=models.BooleanField(default=False, db_index=True)
    is_possible_duplicate=models.BooleanField(default=False, db_index=True); duplicate_group_key=models.CharField(max_length=255, blank=True, db_index=True)
    opportunity_score=models.PositiveSmallIntegerField(default=0); contactability_score=models.PositiveSmallIntegerField(default=0); confidence_score=models.PositiveSmallIntegerField(default=0); total_score=models.PositiveSmallIntegerField(default=0); score_reasons=models.JSONField(default=list, blank=True)
    commercial_status=models.CharField(max_length=24, choices=STATUSES, default='new', db_index=True)
    last_contacted_at=models.DateTimeField(null=True, blank=True); next_follow_up_at=models.DateTimeField(null=True, blank=True)
    notes=models.TextField(blank=True)
    def save(self,*a,**k):
        from .services.text import normalize_name
        self.has_website=bool(self.website_uri); self.has_phone=bool(self.phone_normalized or self.national_phone_number or self.international_phone_number)
        self.normalized_name=self.normalized_name or normalize_name(self.name)
        super().save(*a,**k)
    def __str__(self): return self.name

class LeadContactLog(models.Model):
    CHANNELS=[('whatsapp','WhatsApp'),('phone','Teléfono'),('email','Email'),('other','Otro')]; DIRECTIONS=[('outbound','Saliente'),('inbound','Entrante')]
    STATUSES=[('drafted','Borrador'),('copied','Copiado'),('opened_whatsapp','WhatsApp abierto'),('sent_manually','Enviado manual'),('replied','Respondió'),('failed','Falló')]
    lead=models.ForeignKey(Lead,on_delete=models.CASCADE,related_name='contact_logs'); channel=models.CharField(max_length=16,choices=CHANNELS,default='whatsapp')
    direction=models.CharField(max_length=16,choices=DIRECTIONS,default='outbound'); message_template=models.CharField(max_length=180,blank=True); message_body=models.TextField(blank=True)
    status=models.CharField(max_length=24,choices=STATUSES,default='drafted'); created_by=models.ForeignKey(settings.AUTH_USER_MODEL,null=True,blank=True,on_delete=models.SET_NULL); created_at=models.DateTimeField(auto_now_add=True)

class MessageTemplate(TimeStamped):
    name=models.CharField(max_length=160); target_business_type=models.CharField(max_length=120,blank=True); offer_type=models.CharField(max_length=120,blank=True); body=models.TextField(); is_active=models.BooleanField(default=True)
    def render_for(self, lead, servicio_ofrecido=''):
        vals={'nombre':lead.name,'rubro':lead.primary_type,'zona':lead.area_label or lead.city,'direccion':lead.short_formatted_address or lead.formatted_address,'servicio_ofrecido':servicio_ofrecido or self.offer_type}
        return self.body.format(**vals)
    def __str__(self): return self.name

class Campaign(TimeStamped):
    STATUSES=[('draft','Draft'),('active','Activa'),('paused','Pausada'),('completed','Completada')]
    name=models.CharField(max_length=160); business_type=models.CharField(max_length=120,blank=True); area_label=models.CharField(max_length=160,blank=True); offer_type=models.CharField(max_length=120,blank=True)
    message_template=models.ForeignKey(MessageTemplate,null=True,blank=True,on_delete=models.SET_NULL); status=models.CharField(max_length=16,choices=STATUSES,default='draft')
    leads=models.ManyToManyField(Lead,through='CampaignLead',related_name='campaigns')

class CampaignLead(models.Model):
    campaign=models.ForeignKey(Campaign,on_delete=models.CASCADE); lead=models.ForeignKey(Lead,on_delete=models.CASCADE); status=models.CharField(max_length=32,default='new'); added_at=models.DateTimeField(auto_now_add=True)
    class Meta: unique_together=[('campaign','lead')]
