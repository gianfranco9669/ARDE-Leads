import re
class NormalizadorTelefono:
    def normalizar(self, telefono):
        digitos=re.sub(r'\D+','', telefono or '')
        if not digitos: return {'normalizado':'','es_celular':False,'es_fijo':False,'numero_whatsapp':''}
        if digitos.startswith('00'): digitos=digitos[2:]
        local=digitos[2:] if digitos.startswith('54') else digitos.lstrip('0')
        es_celular=False
        if local.startswith('9'):
            es_celular=True; local=local[1:]
        if '15' in local[:6]:
            es_celular=True; local=local.replace('15','',1)
        normalizado='54'+('9' if es_celular else '')+local
        return {'normalizado':'+'+normalizado,'es_celular':es_celular,'es_fijo':not es_celular,'numero_whatsapp':normalizado if es_celular or len(local)>=8 else ''}
