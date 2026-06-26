from django import forms
from .models import LeadSearch, MessageTemplate, Campaign
class LeadSearchForm(forms.ModelForm):
    class Meta:
        model=LeadSearch; fields=['query','city','area_label','latitude','longitude','radius_meters','search_mode','requested_fields','max_results']
class MessageTemplateForm(forms.ModelForm):
    class Meta: model=MessageTemplate; fields=['name','target_business_type','offer_type','body','is_active']
    def clean_body(self):
        body=self.cleaned_data['body']; allowed={'nombre','rubro','zona','direccion','servicio_ofrecido'}
        import string
        for _,field,_,_ in string.Formatter().parse(body):
            if field and field not in allowed: raise forms.ValidationError(f'Variable no soportada: {field}')
        return body
class CampaignForm(forms.ModelForm):
    class Meta: model=Campaign; fields=['name','business_type','area_label','offer_type','message_template','status']
