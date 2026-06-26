import re
class PhoneNormalizer:
    def normalize(self, raw):
        digits=re.sub(r'\D+','', raw or '')
        if not digits: return {'normalized':'','is_mobile':False,'is_landline':False,'whatsapp_number':''}
        if digits.startswith('00'): digits=digits[2:]
        if digits.startswith('54'):
            local=digits[2:]
        else:
            local=digits.lstrip('0')
        mobile=False
        if local.startswith('9'):
            mobile=True; local=local[1:]
        if '15' in local[:6]:
            mobile=True; local=local.replace('15','',1)
        normalized='54'+('9' if mobile else '')+local
        return {'normalized':'+'+normalized,'is_mobile':mobile,'is_landline':not mobile,'whatsapp_number':normalized if mobile or len(local)>=8 else ''}
