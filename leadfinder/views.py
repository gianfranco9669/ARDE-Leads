import threading
from django.contrib import messages
from django.db.models import Count, Q
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.decorators.http import require_POST
from .forms import LeadSearchForm, MessageTemplateForm, CampaignForm
from .models import Lead, LeadSearch, MessageTemplate, Campaign, CampaignLead
from .services.search_runner import SearchRunner
from .services.whatsapp import WhatsappLinkBuilder

def metrics():
    return {'total':Lead.objects.count(),'sin_web':Lead.objects.filter(has_website=False).count(),'con_tel':Lead.objects.filter(has_phone=True).count(),'nuevos':Lead.objects.filter(commercial_status='new').count(),'contactados':Lead.objects.filter(commercial_status='contacted').count(),'respondieron':Lead.objects.filter(commercial_status='replied').count(),'interesados':Lead.objects.filter(commercial_status='interested').count(),'campanias':Campaign.objects.filter(status='active').count()}
def dashboard(request):
    return render(request,'leadfinder/dashboard.html',{'metrics':metrics(),'searches':LeadSearch.objects.order_by('-created_at')[:8],'opportunities':Lead.objects.exclude(commercial_status='do_not_contact').order_by('-total_score')[:8],'dupes':Lead.objects.filter(is_possible_duplicate=True)[:6]})
def searches(request): return render(request,'leadfinder/searches.html',{'searches':LeadSearch.objects.order_by('-created_at')})
def search_new(request):
    if request.method=='POST':
        form=LeadSearchForm(request.POST)
        if form.is_valid():
            s=form.save(commit=False); s.status='queued'; s.created_by=request.user if request.user.is_authenticated else None; s.estimated_requests=max(1,(s.max_results+19)//20); s.save()
            threading.Thread(target=SearchRunner().run,args=(s.pk,),daemon=True).start(); messages.success(request,'Búsqueda iniciada en segundo plano.'); return redirect('leadfinder:searches')
    else: form=LeadSearchForm(initial={'radius_meters':3000,'max_results':60,'search_mode':'balanced'})
    return render(request,'leadfinder/search_new.html',{'form':form})
@require_POST
def search_cancel(request, pk):
    LeadSearch.objects.filter(pk=pk,status__in=['queued','running']).update(status='cancelled'); return redirect('leadfinder:searches')
def explorer(request):
    qs=Lead.objects.all().select_related('source_search')
    if request.GET.get('sin_web'): qs=qs.filter(has_website=False)
    if request.GET.get('con_tel'): qs=qs.filter(has_phone=True)
    if request.GET.get('status'): qs=qs.filter(commercial_status=request.GET['status'])
    if request.GET.get('rubro'): qs=qs.filter(primary_type__icontains=request.GET['rubro'])
    if request.GET.get('zona'): qs=qs.filter(Q(city__icontains=request.GET['zona'])|Q(area_label__icontains=request.GET['zona']))
    if request.GET.get('score'): qs=qs.filter(total_score__gte=request.GET['score'])
    if request.GET.get('dupes'): qs=qs.filter(is_possible_duplicate=True)
    if request.GET.get('search'): qs=qs.filter(source_search_id=request.GET['search'])
    return render(request,'leadfinder/explorer.html',{'leads':qs.order_by('-total_score')[:200],'statuses':Lead.STATUSES,'searches':LeadSearch.objects.order_by('-created_at')[:50]})
def lead_drawer(request, pk): return render(request,'leadfinder/partials/lead_drawer.html',{'lead':get_object_or_404(Lead,pk=pk),'templates':MessageTemplate.objects.filter(is_active=True)})
@require_POST
def lead_status(request, pk, status):
    Lead.objects.filter(pk=pk).update(commercial_status=status); return redirect(request.META.get('HTTP_REFERER') or reverse('leadfinder:explorer'))
@require_POST
def whatsapp_action(request, pk):
    lead=get_object_or_404(Lead,pk=pk); template=MessageTemplate.objects.filter(pk=request.POST.get('template')).first(); msg=template.render_for(lead) if template else request.POST.get('message','')
    builder=WhatsappLinkBuilder(); action=request.POST.get('action','copied')
    try:
        url=builder.build(lead,msg); builder.record(lead,msg,'opened_whatsapp' if action=='open' else 'copied', request.user if request.user.is_authenticated else None, template.name if template else '')
        messages.success(request,'Acción registrada.'); return redirect(url if action=='open' else request.META.get('HTTP_REFERER', 'leadfinder:explorer'))
    except ValueError as e: messages.error(request,str(e)); return redirect(request.META.get('HTTP_REFERER') or reverse('leadfinder:explorer'))
def pipeline(request):
    columns=[(k,v,Lead.objects.filter(commercial_status=k).exclude(commercial_status='do_not_contact').order_by('-total_score')[:50]) for k,v in Lead.STATUSES if k!='do_not_contact']
    return render(request,'leadfinder/pipeline.html',{'columns':columns})
def templates(request):
    form=MessageTemplateForm(request.POST or None)
    if request.method=='POST' and form.is_valid(): form.save(); return redirect('leadfinder:templates')
    return render(request,'leadfinder/templates.html',{'form':form,'templates':MessageTemplate.objects.order_by('-created_at')})
def campaigns(request):
    form=CampaignForm(request.POST or None)
    if request.method=='POST' and form.is_valid(): form.save(); return redirect('leadfinder:campaigns')
    return render(request,'leadfinder/campaigns.html',{'form':form,'campaigns':Campaign.objects.annotate(total=Count('leads')).order_by('-created_at')})
