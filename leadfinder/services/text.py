import re, unicodedata
def normalize_name(value):
    value=unicodedata.normalize('NFKD', value or '').encode('ascii','ignore').decode().lower()
    return re.sub(r'[^a-z0-9]+',' ',value).strip()
