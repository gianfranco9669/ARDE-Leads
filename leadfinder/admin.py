from django.contrib import admin
from .models import LeadSearch,Lead,LeadContactLog,MessageTemplate,Campaign,CampaignLead
for m in [LeadSearch,Lead,LeadContactLog,MessageTemplate,Campaign,CampaignLead]: admin.site.register(m)
