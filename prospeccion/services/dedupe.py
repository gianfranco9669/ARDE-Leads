from .text import normalizar_nombre
from prospeccion.models import Prospecto
class DetectorDuplicados:
    def marcar(self):
        marcados=0
        for prospecto in Prospecto.objects.exclude(telefono_normalizado=''):
            similares=Prospecto.objects.filter(telefono_normalizado=prospecto.telefono_normalizado).exclude(pk=prospecto.pk)
            if similares.exists():
                clave=f'telefono:{prospecto.telefono_normalizado}'
                Prospecto.objects.filter(pk__in=[prospecto.pk,*similares.values_list('pk',flat=True)]).update(es_posible_duplicado=True, clave_grupo_duplicado=clave)
                marcados+=similares.count()
        for prospecto in Prospecto.objects.all():
            clave=f'nombre-zona:{normalizar_nombre(prospecto.nombre)}:{normalizar_nombre(prospecto.ciudad or prospecto.direccion_formateada)[:40]}'
            similares=Prospecto.objects.filter(nombre_normalizado=prospecto.nombre_normalizado, ciudad=prospecto.ciudad).exclude(pk=prospecto.pk)
            if similares.exists():
                Prospecto.objects.filter(pk__in=[prospecto.pk,*similares.values_list('pk',flat=True)]).update(es_posible_duplicado=True, clave_grupo_duplicado=clave)
                marcados+=similares.count()
        return marcados
