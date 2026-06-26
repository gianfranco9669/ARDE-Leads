import threading
from django.contrib import messages
from django.db.models import Count, Q
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.decorators.http import require_POST
from .forms import FormularioBusquedaProspectos, FormularioPlantillaMensaje, FormularioCampania
from .models import Prospecto, BusquedaProspectos, PlantillaMensaje, Campania
from .services.search_runner import EjecutorBusqueda
from .services.whatsapp import GeneradorLinkWhatsapp

def metricas_dashboard():
    return [
        ('Prospectos totales', Prospecto.objects.count(), 'Base comercial acumulada'),
        ('Sin web detectada', Prospecto.objects.filter(tiene_web=False).count(), 'Oportunidad digital principal'),
        ('Con teléfono', Prospecto.objects.filter(tiene_telefono=True).count(), 'Listos para contacto manual'),
        ('Nuevos', Prospecto.objects.filter(estado_comercial='new').count(), 'Sin gestionar'),
        ('Contactados', Prospecto.objects.filter(estado_comercial='contacted').count(), 'Primer toque realizado'),
        ('Respondieron', Prospecto.objects.filter(estado_comercial='replied').count(), 'Conversación abierta'),
        ('Interesados', Prospecto.objects.filter(estado_comercial='interested').count(), 'Alta intención'),
        ('Campañas activas', Campania.objects.filter(estado='active').count(), 'En ejecución comercial'),
    ]

def dashboard(request):
    contexto={'metricas':metricas_dashboard(),'busquedas':BusquedaProspectos.objects.order_by('-creado_el')[:6],'oportunidades':Prospecto.objects.exclude(estado_comercial='do_not_contact').order_by('-puntaje_total')[:8],'duplicados':Prospecto.objects.filter(es_posible_duplicado=True)[:6],'no_contactar':Prospecto.objects.filter(estado_comercial='do_not_contact')[:6]}
    return render(request,'prospeccion/dashboard.html',contexto)

def busquedas(request):
    return render(request,'prospeccion/busquedas.html',{'busquedas':BusquedaProspectos.objects.order_by('-creado_el')})

def nueva_busqueda(request):
    if request.method=='POST':
        formulario=FormularioBusquedaProspectos(request.POST)
        if formulario.is_valid():
            busqueda=formulario.save(commit=False); busqueda.estado='queued'; busqueda.creado_por=request.user if request.user.is_authenticated else None; busqueda.solicitudes_estimadas=max(1,(busqueda.max_resultados+19)//20); busqueda.save()
            threading.Thread(target=EjecutorBusqueda().ejecutar,args=(busqueda.pk,),daemon=True).start()
            messages.success(request,'Búsqueda enviada al motor de prospección. Podés seguir el progreso en el historial.')
            return redirect('prospeccion:busquedas')
    else:
        formulario=FormularioBusquedaProspectos(initial={'radio_metros':3000,'max_resultados':60,'modo_busqueda':'balanced'})
    return render(request,'prospeccion/nueva_busqueda.html',{'formulario':formulario})

@require_POST
def cancelar_busqueda(request, pk):
    BusquedaProspectos.objects.filter(pk=pk,estado__in=['queued','running']).update(estado='cancelled')
    messages.info(request,'Búsqueda cancelada.')
    return redirect('prospeccion:busquedas')

def explorador(request):
    prospectos=Prospecto.objects.all().select_related('busqueda_origen')
    if request.GET.get('sin_web'): prospectos=prospectos.filter(tiene_web=False)
    if request.GET.get('con_telefono'): prospectos=prospectos.filter(tiene_telefono=True)
    if request.GET.get('alta_prioridad'): prospectos=prospectos.filter(puntaje_total__gte=75)
    if request.GET.get('duplicados'): prospectos=prospectos.filter(es_posible_duplicado=True)
    if request.GET.get('estado'): prospectos=prospectos.filter(estado_comercial=request.GET['estado'])
    if request.GET.get('rubro'): prospectos=prospectos.filter(rubro__icontains=request.GET['rubro'])
    if request.GET.get('zona'): prospectos=prospectos.filter(Q(ciudad__icontains=request.GET['zona'])|Q(zona__icontains=request.GET['zona']))
    if request.GET.get('puntaje'): prospectos=prospectos.filter(puntaje_total__gte=request.GET['puntaje'])
    return render(request,'prospeccion/explorador.html',{'prospectos':prospectos.order_by('-puntaje_total')[:200],'estados':Prospecto.ESTADOS_COMERCIALES})

def drawer_prospecto(request, pk):
    return render(request,'prospeccion/partials/drawer_prospecto.html',{'prospecto':get_object_or_404(Prospecto,pk=pk),'plantillas':PlantillaMensaje.objects.filter(activa=True)})

@require_POST
def cambiar_estado(request, pk, estado):
    Prospecto.objects.filter(pk=pk).update(estado_comercial=estado)
    messages.success(request,'Estado comercial actualizado.')
    return redirect(request.META.get('HTTP_REFERER') or reverse('prospeccion:explorador'))

@require_POST
def accion_whatsapp(request, pk):
    prospecto=get_object_or_404(Prospecto,pk=pk)
    plantilla=PlantillaMensaje.objects.filter(pk=request.POST.get('plantilla')).first()
    mensaje=plantilla.renderizar_para(prospecto) if plantilla else request.POST.get('mensaje','')
    generador=GeneradorLinkWhatsapp(); accion=request.POST.get('accion','copiar')
    try:
        url=generador.generar(prospecto,mensaje)
        generador.registrar(prospecto,mensaje,'whatsapp_abierto' if accion=='abrir' else 'copiado', request.user if request.user.is_authenticated else None, plantilla.nombre if plantilla else '')
        messages.success(request,'Acción registrada en el historial del prospecto.')
        return redirect(url if accion=='abrir' else request.META.get('HTTP_REFERER', reverse('prospeccion:explorador')))
    except ValueError as exc:
        messages.error(request,str(exc)); return redirect(request.META.get('HTTP_REFERER') or reverse('prospeccion:explorador'))

def pipeline(request):
    columnas=[(clave,etiqueta,Prospecto.objects.filter(estado_comercial=clave).order_by('-puntaje_total')[:50]) for clave,etiqueta in Prospecto.ESTADOS_COMERCIALES if clave!='do_not_contact']
    return render(request,'prospeccion/pipeline.html',{'columnas':columnas})

def plantillas(request):
    formulario=FormularioPlantillaMensaje(request.POST or None)
    if request.method=='POST' and formulario.is_valid():
        formulario.save(); messages.success(request,'Plantilla creada.'); return redirect('prospeccion:plantillas')
    return render(request,'prospeccion/plantillas.html',{'formulario':formulario,'plantillas':PlantillaMensaje.objects.order_by('-creado_el')})

def campanias(request):
    formulario=FormularioCampania(request.POST or None)
    if request.method=='POST' and formulario.is_valid():
        campania=formulario.save();
        candidatos=Prospecto.objects.exclude(estado_comercial='do_not_contact')
        if campania.rubro: candidatos=candidatos.filter(rubro__icontains=campania.rubro)
        if campania.zona: candidatos=candidatos.filter(Q(zona__icontains=campania.zona)|Q(ciudad__icontains=campania.zona))
        campania.prospectos.add(*candidatos[:50]); messages.success(request,'Campaña creada y prospectos sugeridos asociados.'); return redirect('prospeccion:campanias')
    campanias_qs=Campania.objects.annotate(total=Count('prospectos')).order_by('-creado_el')
    return render(request,'prospeccion/campanias.html',{'formulario':formulario,'campanias':campanias_qs})
