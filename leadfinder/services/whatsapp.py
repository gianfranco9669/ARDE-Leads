from urllib.parse import quote
from django.utils import timezone
from leadfinder.models import LeadContactLog
class WhatsappLinkBuilder:
    def build(self, lead, message):
        if lead.commercial_status == 'do_not_contact':
            raise ValueError('No se puede generar mensaje para leads marcados como no contactar')
        number=(lead.phone_normalized or '').replace('+','')
        if not number: raise ValueError('El lead no tiene teléfono normalizado')
        return f'https://wa.me/{number}?text={quote(message)}'
    def record(self, lead, message, status, user=None, template=''):
        if status in {'opened_whatsapp','sent_manually'}:
            lead.last_contacted_at=timezone.now(); lead.commercial_status='contacted'; lead.save(update_fields=['last_contacted_at','commercial_status','updated_at'])
        return LeadContactLog.objects.create(lead=lead,channel='whatsapp',direction='outbound',message_template=template,message_body=message,status=status,created_by=user)
