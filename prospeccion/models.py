from django.conf import settings
from django.db import models
from django.utils import timezone

class FechasModelo(models.Model):
    creado_el = models.DateTimeField(auto_now_add=True)
    actualizado_el = models.DateTimeField(auto_now=True)
    class Meta:
        abstract = True

class BusquedaProspectos(FechasModelo):
    MODOS = [('quick','Rápida'),('balanced','Equilibrada'),('deep','Profunda')]
    ESTADOS = [('draft','Borrador'),('queued','En cola'),('running','En ejecución'),('completed','Completada'),('failed','Fallida'),('cancelled','Cancelada')]
    consulta = models.CharField(max_length=180)
    ciudad = models.CharField(max_length=120, blank=True)
    zona = models.CharField(max_length=160, blank=True)
    latitud = models.DecimalField(max_digits=10, decimal_places=7, null=True, blank=True)
    longitud = models.DecimalField(max_digits=10, decimal_places=7, null=True, blank=True)
    radio_metros = models.PositiveIntegerField(default=3000)
    modo_busqueda = models.CharField(max_length=16, choices=MODOS, default='balanced')
    campos_solicitados = models.TextField(blank=True)
    max_resultados = models.PositiveIntegerField(default=60)
    estado = models.CharField(max_length=16, choices=ESTADOS, default='draft', db_index=True)
    solicitudes_estimadas = models.PositiveIntegerField(default=0)
    solicitudes_reales = models.PositiveIntegerField(default=0)
    resultados_encontrados = models.PositiveIntegerField(default=0)
    prospectos_creados = models.PositiveIntegerField(default=0)
    prospectos_actualizados = models.PositiveIntegerField(default=0)
    duplicados_detectados = models.PositiveIntegerField(default=0)
    errores_api = models.PositiveIntegerField(default=0)
    mensaje_error = models.TextField(blank=True)
    bitacora_api = models.JSONField(default=list, blank=True)
    iniciado_el = models.DateTimeField(null=True, blank=True)
    finalizado_el = models.DateTimeField(null=True, blank=True)
    creado_por = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL)
    class Meta:
        verbose_name = 'búsqueda de prospectos'
        verbose_name_plural = 'búsquedas de prospectos'
    def progreso(self):
        if self.estado == 'completed': return 100
        if self.estado == 'running': return min(100, int((self.resultados_encontrados or 0) / max(1, self.max_resultados) * 100))
        return 0
    def marcar_iniciada(self):
        self.estado='running'; self.iniciado_el=timezone.now(); self.save(update_fields=['estado','iniciado_el','actualizado_el'])
    def marcar_finalizada(self, estado='completed'):
        self.estado=estado; self.finalizado_el=timezone.now(); self.save(update_fields=['estado','finalizado_el','actualizado_el'])
    def __str__(self): return f'{self.consulta} · {self.ciudad or self.zona}'

class Prospecto(FechasModelo):
    ESTADOS_COMERCIALES=[('new','Nuevo'),('review','Revisar'),('contacted','Contactado'),('replied','Respondió'),('interested','Interesado'),('won','Ganado'),('lost','Perdido'),('discarded','Descartado'),('do_not_contact','No contactar')]
    place_id = models.CharField(max_length=255, unique=True)
    nombre = models.CharField(max_length=255)
    nombre_normalizado = models.CharField(max_length=255, db_index=True, blank=True)
    rubro = models.CharField(max_length=100, blank=True)
    tipos = models.JSONField(default=list, blank=True)
    estado_google = models.CharField(max_length=80, blank=True)
    direccion_formateada = models.TextField(blank=True)
    direccion_corta = models.CharField(max_length=255, blank=True)
    ciudad = models.CharField(max_length=120, blank=True)
    zona = models.CharField(max_length=160, blank=True)
    latitud = models.DecimalField(max_digits=10, decimal_places=7, null=True, blank=True)
    longitud = models.DecimalField(max_digits=10, decimal_places=7, null=True, blank=True)
    telefono_nacional = models.CharField(max_length=80, blank=True)
    telefono_internacional = models.CharField(max_length=80, blank=True)
    telefono_normalizado = models.CharField(max_length=40, blank=True, db_index=True)
    sitio_web = models.URLField(max_length=500, blank=True)
    url_google_maps = models.URLField(max_length=500, blank=True)
    calificacion = models.DecimalField(max_digits=3, decimal_places=2, null=True, blank=True)
    cantidad_resenas = models.PositiveIntegerField(default=0)
    busqueda_origen = models.ForeignKey(BusquedaProspectos, null=True, blank=True, on_delete=models.SET_NULL, related_name='prospectos')
    tiene_web = models.BooleanField(default=False, db_index=True)
    tiene_telefono = models.BooleanField(default=False, db_index=True)
    es_posible_duplicado = models.BooleanField(default=False, db_index=True)
    clave_grupo_duplicado = models.CharField(max_length=255, blank=True, db_index=True)
    puntaje_oportunidad = models.PositiveSmallIntegerField(default=0)
    puntaje_contactabilidad = models.PositiveSmallIntegerField(default=0)
    puntaje_confianza = models.PositiveSmallIntegerField(default=0)
    puntaje_total = models.PositiveSmallIntegerField(default=0)
    motivos_puntaje = models.JSONField(default=list, blank=True)
    estado_comercial = models.CharField(max_length=24, choices=ESTADOS_COMERCIALES, default='new', db_index=True)
    ultimo_contacto_el = models.DateTimeField(null=True, blank=True)
    proximo_seguimiento_el = models.DateTimeField(null=True, blank=True)
    notas = models.TextField(blank=True)
    class Meta:
        verbose_name = 'prospecto'
        verbose_name_plural = 'prospectos'
    def save(self,*args,**kwargs):
        from .services.text import normalizar_nombre
        self.tiene_web = bool(self.sitio_web)
        self.tiene_telefono = bool(self.telefono_normalizado or self.telefono_nacional or self.telefono_internacional)
        self.nombre_normalizado = self.nombre_normalizado or normalizar_nombre(self.nombre)
        super().save(*args,**kwargs)
    def __str__(self): return self.nombre

class RegistroContacto(models.Model):
    CANALES=[('whatsapp','WhatsApp'),('telefono','Teléfono'),('email','Email'),('otro','Otro')]
    DIRECCIONES=[('saliente','Saliente'),('entrante','Entrante')]
    ESTADOS=[('borrador','Borrador'),('copiado','Copiado'),('whatsapp_abierto','WhatsApp abierto'),('enviado_manual','Enviado manualmente'),('respondio','Respondió'),('fallo','Falló')]
    prospecto=models.ForeignKey(Prospecto,on_delete=models.CASCADE,related_name='registros_contacto')
    canal=models.CharField(max_length=16,choices=CANALES,default='whatsapp')
    direccion=models.CharField(max_length=16,choices=DIRECCIONES,default='saliente')
    plantilla_mensaje=models.CharField(max_length=180,blank=True)
    cuerpo_mensaje=models.TextField(blank=True)
    estado=models.CharField(max_length=24,choices=ESTADOS,default='borrador')
    creado_por=models.ForeignKey(settings.AUTH_USER_MODEL,null=True,blank=True,on_delete=models.SET_NULL)
    creado_el=models.DateTimeField(auto_now_add=True)

class PlantillaMensaje(FechasModelo):
    nombre=models.CharField(max_length=160)
    rubro_objetivo=models.CharField(max_length=120,blank=True)
    tipo_oferta=models.CharField(max_length=120,blank=True)
    cuerpo=models.TextField()
    activa=models.BooleanField(default=True)
    def renderizar_para(self, prospecto, servicio_ofrecido=''):
        valores={'nombre':prospecto.nombre,'rubro':prospecto.rubro,'zona':prospecto.zona or prospecto.ciudad,'direccion':prospecto.direccion_corta or prospecto.direccion_formateada,'servicio_ofrecido':servicio_ofrecido or self.tipo_oferta}
        return self.cuerpo.format(**valores)
    def __str__(self): return self.nombre

class Campania(FechasModelo):
    ESTADOS=[('draft','Borrador'),('active','Activa'),('paused','Pausada'),('completed','Completada')]
    nombre=models.CharField(max_length=160)
    rubro=models.CharField(max_length=120,blank=True)
    zona=models.CharField(max_length=160,blank=True)
    tipo_oferta=models.CharField(max_length=120,blank=True)
    plantilla=models.ForeignKey(PlantillaMensaje,null=True,blank=True,on_delete=models.SET_NULL)
    estado=models.CharField(max_length=16,choices=ESTADOS,default='draft')
    prospectos=models.ManyToManyField(Prospecto,through='ProspectoCampania',related_name='campanias')

class ProspectoCampania(models.Model):
    campania=models.ForeignKey(Campania,on_delete=models.CASCADE)
    prospecto=models.ForeignKey(Prospecto,on_delete=models.CASCADE)
    estado=models.CharField(max_length=32,default='nuevo')
    agregado_el=models.DateTimeField(auto_now_add=True)
    class Meta:
        unique_together=[('campania','prospecto')]
