import threading
from django.contrib import messages
from django.db.models import Count, Q
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.decorators.http import require_POST
from .forms import FormularioBusquedaProspectos, FormularioPlantillaMensaje, FormularioCampania
from .models import Prospecto, BusquedaProspectos, PlantillaMensaje, Campania, RegistroContacto
from .services.search_runner import EjecutorBusqueda
from .services.whatsapp import GeneradorLinkWhatsapp
from .templatetags.prospeccion_ui import RUBROS

ESTADOS_RAPIDOS = ['new','review','contacted','replied','interested','won','lost','discarded','do_not_contact']

def metricas_dashboard():
    explorador_url = reverse('prospeccion:explorador')
    campanias_url = reverse('prospeccion:campanias')
    return [
        {'titulo':'Prospectos totales','valor':Prospecto.objects.count(),'ayuda':'Base comercial','url':explorador_url,'icono':'◎','tono':'slate','microcopy':'Ver prospectos'},
        {'titulo':'Sin web detectada','valor':Prospecto.objects.filter(tiene_web=False).count(),'ayuda':'Oportunidad digital','url':f'{explorador_url}?sin_web=1','icono':'⚡','tono':'hot','microcopy':'Abrir segmento'},
        {'titulo':'Con teléfono','valor':Prospecto.objects.filter(tiene_telefono=True).count(),'ayuda':'Listos para contacto','url':f'{explorador_url}?con_telefono=1','icono':'☎','tono':'green','microcopy':'Ver contactables'},
        {'titulo':'Nuevos','valor':Prospecto.objects.filter(estado_comercial='new').count(),'ayuda':'Sin gestionar','url':f'{explorador_url}?estado=new','icono':'✦','tono':'blue','microcopy':'Revisar nuevos'},
        {'titulo':'Contactados','valor':Prospecto.objects.filter(estado_comercial='contacted').count(),'ayuda':'Primer toque','url':f'{explorador_url}?estado=contacted','icono':'↗','tono':'blue','microcopy':'Ver seguimiento'},
        {'titulo':'Respondieron','valor':Prospecto.objects.filter(estado_comercial='replied').count(),'ayuda':'Conversación abierta','url':f'{explorador_url}?estado=replied','icono':'✉','tono':'green','microcopy':'Ver respuestas'},
        {'titulo':'Interesados','valor':Prospecto.objects.filter(estado_comercial='interested').count(),'ayuda':'Alta intención','url':f'{explorador_url}?estado=interested','icono':'★','tono':'hot','microcopy':'Priorizar ahora'},
        {'titulo':'Campañas activas','valor':Campania.objects.filter(estado='active').count(),'ayuda':'En marcha','url':campanias_url,'icono':'◉','tono':'orange','microcopy':'Abrir campañas'},
    ]

def aplicar_busqueda_global(qs, texto):
    if not texto: return qs
    estados={v.lower():k for k,v in Prospecto.ESTADOS_COMERCIALES}
    filtro=Q(nombre__icontains=texto)|Q(rubro__icontains=texto)|Q(zona__icontains=texto)|Q(ciudad__icontains=texto)|Q(campanias__nombre__icontains=texto)|Q(campanias__rubro__icontains=texto)|Q(campanias__zona__icontains=texto)
    estado=estados.get(texto.lower())
    rubros_tecnicos=[clave for clave, etiqueta in RUBROS.items() if texto.lower() in etiqueta.lower()]
    if rubros_tecnicos: filtro |= Q(rubro__in=rubros_tecnicos) | Q(campanias__rubro__in=rubros_tecnicos)
    if estado: filtro |= Q(estado_comercial=estado)
    return qs.filter(filtro).distinct()

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
    else: formulario=FormularioBusquedaProspectos(initial={'radio_metros':3000,'max_resultados':60,'modo_busqueda':'balanced'})
    return render(request,'prospeccion/nueva_busqueda.html',{'formulario':formulario})

@require_POST
def cancelar_busqueda(request, pk):
    BusquedaProspectos.objects.filter(pk=pk,estado__in=['queued','running']).update(estado='cancelled'); messages.info(request,'Búsqueda cancelada.')
    return redirect('prospeccion:busquedas')

def explorador(request):
    q=request.GET.get('q','').strip(); prospectos=aplicar_busqueda_global(Prospecto.objects.all().select_related('busqueda_origen').prefetch_related('campanias'), q)
    if request.GET.get('sin_web'): prospectos=prospectos.filter(tiene_web=False)
    if request.GET.get('con_telefono'): prospectos=prospectos.filter(tiene_telefono=True)
    if request.GET.get('alta_prioridad'): prospectos=prospectos.filter(puntaje_total__gte=75)
    if request.GET.get('duplicados'): prospectos=prospectos.filter(es_posible_duplicado=True)
    if request.GET.get('estado'): prospectos=prospectos.filter(estado_comercial=request.GET['estado'])
    if request.GET.get('rubro'): prospectos=prospectos.filter(rubro__icontains=request.GET['rubro'])
    if request.GET.get('zona'): prospectos=prospectos.filter(Q(ciudad__icontains=request.GET['zona'])|Q(zona__icontains=request.GET['zona']))
    if request.GET.get('puntaje'): prospectos=prospectos.filter(puntaje_total__gte=request.GET['puntaje'])
    return render(request,'prospeccion/explorador.html',{'prospectos':prospectos.order_by('-puntaje_total')[:200],'estados':Prospecto.ESTADOS_COMERCIALES,'q':q})

def drawer_prospecto(request, pk):
    return render(request,'prospeccion/partials/drawer_prospecto.html',{'prospecto':get_object_or_404(Prospecto,pk=pk),'plantillas':PlantillaMensaje.objects.filter(activa=True),'estados':Prospecto.ESTADOS_COMERCIALES})

@require_POST
def cambiar_estado(request, pk, estado):
    prospecto=get_object_or_404(Prospecto,pk=pk)
    etiquetas=dict(Prospecto.ESTADOS_COMERCIALES)
    anterior=prospecto.get_estado_comercial_display(); prospecto.estado_comercial=estado; prospecto.save(update_fields=['estado_comercial','actualizado_el'])
    RegistroContacto.objects.create(prospecto=prospecto,canal='otro',direccion='saliente',estado='borrador',cuerpo_mensaje=f'Estado cambiado de {anterior} a {etiquetas.get(estado, estado)}')
    messages.success(request,f'Estado actualizado a {etiquetas.get(estado, estado)}.')
    return redirect(request.META.get('HTTP_REFERER') or reverse('prospeccion:pipeline'))

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
    columnas=[(clave,etiqueta,Prospecto.objects.filter(estado_comercial=clave).order_by('-puntaje_total')[:50],Prospecto.objects.filter(estado_comercial=clave).count()) for clave,etiqueta in Prospecto.ESTADOS_COMERCIALES if clave!='do_not_contact']
    return render(request,'prospeccion/pipeline.html',{'columnas':columnas})

def plantillas(request):
    formulario=FormularioPlantillaMensaje(request.POST or None)
    if request.method=='POST' and formulario.is_valid(): formulario.save(); messages.success(request,'Plantilla creada.'); return redirect('prospeccion:plantillas')
    return render(request,'prospeccion/plantillas.html',{'formulario':formulario,'plantillas':PlantillaMensaje.objects.order_by('-creado_el')})

@require_POST
def desactivar_plantilla(request, pk):
    PlantillaMensaje.objects.filter(pk=pk).update(activa=False); messages.success(request,'Plantilla desactivada.'); return redirect('prospeccion:plantillas')

def campanias(request):
    formulario=FormularioCampania(request.POST or None); criterio=''
    if request.method=='POST' and formulario.is_valid():
        campania=formulario.save(); candidatos=Prospecto.objects.exclude(estado_comercial='do_not_contact')
        partes=[]
        if campania.rubro: candidatos=candidatos.filter(rubro__icontains=campania.rubro); partes.append(f"rubro similar a {RUBROS.get(campania.rubro, campania.rubro.replace('_',' ').capitalize())}")
        if campania.zona: candidatos=candidatos.filter(Q(zona__icontains=campania.zona)|Q(ciudad__icontains=campania.zona)); partes.append(f'zona {campania.zona}')
        campania.prospectos.add(*candidatos[:50]); criterio=', '.join(partes) or 'prospectos disponibles excluyendo No contactar'
        messages.success(request,f'Campaña creada. Se asociaron prospectos sugeridos por criterio: {criterio}.'); return redirect('prospeccion:campanias')
    campanias_qs=Campania.objects.annotate(total=Count('prospectos'),contactados=Count('prospectos',filter=Q(prospectos__estado_comercial='contacted')),respondieron=Count('prospectos',filter=Q(prospectos__estado_comercial='replied')),interesados=Count('prospectos',filter=Q(prospectos__estado_comercial='interested')),ganados=Count('prospectos',filter=Q(prospectos__estado_comercial='won'))).order_by('-creado_el')
    return render(request,'prospeccion/campanias.html',{'formulario':formulario,'campanias':campanias_qs})

@require_POST
def alternar_campania(request, pk):
    campania=get_object_or_404(Campania,pk=pk); campania.estado='paused' if campania.estado=='active' else 'active'; campania.save(update_fields=['estado','actualizado_el']); messages.success(request,'Estado de campaña actualizado.'); return redirect('prospeccion:campanias')
