from urllib.parse import quote
from django.utils import timezone
from prospeccion.models import RegistroContacto
class GeneradorLinkWhatsapp:
    def generar(self, prospecto, mensaje):
        if prospecto.estado_comercial == 'do_not_contact':
            raise ValueError('No se puede generar mensaje para prospectos marcados como No contactar')
        numero=(prospecto.telefono_normalizado or '').replace('+','')
        if not numero: raise ValueError('El prospecto no tiene teléfono normalizado')
        return f'https://wa.me/{numero}?text={quote(mensaje)}'
    def registrar(self, prospecto, mensaje, estado, usuario=None, plantilla=''):
        if estado in {'whatsapp_abierto','enviado_manual'}:
            prospecto.ultimo_contacto_el=timezone.now(); prospecto.estado_comercial='contacted'; prospecto.save(update_fields=['ultimo_contacto_el','estado_comercial','actualizado_el'])
        return RegistroContacto.objects.create(prospecto=prospecto,canal='whatsapp',direccion='saliente',plantilla_mensaje=plantilla,cuerpo_mensaje=mensaje,estado=estado,creado_por=usuario)
