import re, unicodedata

def normalizar_nombre(valor):
    valor=unicodedata.normalize('NFKD', valor or '').encode('ascii','ignore').decode().lower()
    return re.sub(r'[^a-z0-9]+',' ',valor).strip()
