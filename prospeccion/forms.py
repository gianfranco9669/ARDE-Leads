from django import forms
from .models import BusquedaProspectos, PlantillaMensaje, Campania

CLASE_INPUT = 'w-full rounded-2xl border border-white/10 bg-slate-950/70 px-4 py-3 text-slate-100 placeholder:text-slate-500 focus:border-orange-400 focus:ring-2 focus:ring-orange-400/30 outline-none transition'

class FormularioPremium(forms.ModelForm):
    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        for campo in self.fields.values():
            campo.widget.attrs.setdefault('class', CLASE_INPUT)

class FormularioBusquedaProspectos(FormularioPremium):
    class Meta:
        model=BusquedaProspectos
        fields=['consulta','ciudad','zona','latitud','longitud','radio_metros','modo_busqueda','campos_solicitados','max_resultados']
        labels={'consulta':'Rubro objetivo','ciudad':'Ciudad','zona':'Zona comercial','latitud':'Latitud','longitud':'Longitud','radio_metros':'Radio en metros','modo_busqueda':'Modo de búsqueda','campos_solicitados':'FieldMask personalizado','max_resultados':'Límite de resultados'}
        widgets={'campos_solicitados':forms.Textarea(attrs={'rows':3,'placeholder':'Dejar vacío para usar el FieldMask optimizado del modo elegido'})}

class FormularioPlantillaMensaje(FormularioPremium):
    class Meta:
        model=PlantillaMensaje
        fields=['nombre','rubro_objetivo','tipo_oferta','cuerpo','activa']
        labels={'nombre':'Nombre','rubro_objetivo':'Rubro objetivo','tipo_oferta':'Tipo de oferta','cuerpo':'Mensaje','activa':'Activa'}
        widgets={'cuerpo':forms.Textarea(attrs={'rows':6,'placeholder':'Hola {nombre}, vi que tu negocio en {zona} podría mejorar su presencia digital...'})}
    def clean_cuerpo(self):
        cuerpo=self.cleaned_data['cuerpo']; permitidas={'nombre','rubro','zona','direccion','servicio_ofrecido'}
        import string
        for _,campo,_,_ in string.Formatter().parse(cuerpo):
            if campo and campo not in permitidas:
                raise forms.ValidationError(f'Variable no soportada: {campo}')
        return cuerpo

class FormularioCampania(FormularioPremium):
    class Meta:
        model=Campania
        fields=['nombre','rubro','zona','tipo_oferta','plantilla','estado']
        labels={'nombre':'Nombre','rubro':'Rubro','zona':'Zona','tipo_oferta':'Tipo de oferta','plantilla':'Plantilla','estado':'Estado'}
