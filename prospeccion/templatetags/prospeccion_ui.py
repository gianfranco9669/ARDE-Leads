from django import template
register = template.Library()
RUBROS = {
    'barber_shop':'Barbería','dentist':'Odontología','gym':'Gimnasio','real_estate_agency':'Inmobiliaria','car_repair':'Taller mecánico','restaurant':'Restaurante','beauty_salon':'Estética','store':'Comercio','cafe':'Cafetería','bakery':'Panadería','doctor':'Consultorio médico','lawyer':'Estudio jurídico','accounting':'Estudio contable',
}
@register.filter
def rubro_legible(valor):
    if not valor: return 'Rubro no informado'
    valor = str(valor).strip()
    return RUBROS.get(valor, valor.replace('_',' ').replace('-',' ').capitalize())
@register.filter
def estado_legible(valor):
    estados={'new':'Nuevo','review':'Revisar','contacted':'Contactado','replied':'Respondió','interested':'Interesado','won':'Ganado','lost':'Perdido','discarded':'Descartado','do_not_contact':'No contactar'}
    return estados.get(valor, str(valor).replace('_',' ').capitalize())
