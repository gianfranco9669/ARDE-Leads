class CalculadorPuntajeProspecto:
    def calcular(self, prospecto):
        motivos=[]; oportunidad=20
        if not prospecto.sitio_web:
            oportunidad+=45; motivos.append('Sin web detectada: oportunidad principal')
        if prospecto.calificacion and float(prospecto.calificacion)>=4:
            oportunidad+=10; motivos.append('Buena reputación pública')
        if prospecto.cantidad_resenas>=20:
            oportunidad+=10; motivos.append('Volumen de reseñas confiable')
        contactabilidad=10
        if prospecto.telefono_normalizado or prospecto.telefono_nacional:
            contactabilidad+=55; motivos.append('Tiene teléfono para contacto')
        if prospecto.url_google_maps:
            contactabilidad+=15; motivos.append('Ficha de Google Maps disponible')
        confianza=30
        if prospecto.place_id: confianza+=25
        if prospecto.direccion_formateada: confianza+=15
        if prospecto.estado_google=='OPERATIONAL':
            confianza+=15; motivos.append('Negocio operativo según Google')
        total=round(oportunidad*.45+contactabilidad*.35+confianza*.20)
        return {'puntaje_oportunidad':min(100,oportunidad),'puntaje_contactabilidad':min(100,contactabilidad),'puntaje_confianza':min(100,confianza),'puntaje_total':min(100,total),'motivos':motivos}
    def aplicar(self, prospecto, guardar=True):
        puntaje=self.calcular(prospecto)
        prospecto.puntaje_oportunidad=puntaje['puntaje_oportunidad']; prospecto.puntaje_contactabilidad=puntaje['puntaje_contactabilidad']; prospecto.puntaje_confianza=puntaje['puntaje_confianza']; prospecto.puntaje_total=puntaje['puntaje_total']; prospecto.motivos_puntaje=puntaje['motivos']
        if guardar: prospecto.save(update_fields=['puntaje_oportunidad','puntaje_contactabilidad','puntaje_confianza','puntaje_total','motivos_puntaje','tiene_web','tiene_telefono','nombre_normalizado','actualizado_el'])
        return puntaje
