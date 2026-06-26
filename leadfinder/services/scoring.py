class LeadScoringService:
    def score(self, lead):
        reasons=[]; opp=20
        if not lead.website_uri: opp+=45; reasons.append('Sin web detectada: oportunidad principal')
        if lead.rating and float(lead.rating)>=4: opp+=10; reasons.append('Buena reputación pública')
        if lead.user_rating_count>=20: opp+=10; reasons.append('Volumen de reseñas confiable')
        cont=10
        if lead.phone_normalized or lead.national_phone_number: cont+=55; reasons.append('Tiene teléfono para contacto')
        if lead.google_maps_uri: cont+=15; reasons.append('Ficha de Google Maps disponible')
        conf=30
        if lead.place_id: conf+=25
        if lead.formatted_address: conf+=15
        if lead.business_status=='OPERATIONAL': conf+=15; reasons.append('Negocio operativo')
        total=round(opp*.45+cont*.35+conf*.20)
        return {'opportunity_score':min(100,opp),'contactability_score':min(100,cont),'confidence_score':min(100,conf),'total_score':min(100,total),'reasons':reasons}
    def apply(self, lead, save=True):
        s=self.score(lead)
        lead.opportunity_score=s['opportunity_score']; lead.contactability_score=s['contactability_score']; lead.confidence_score=s['confidence_score']; lead.total_score=s['total_score']; lead.score_reasons=s['reasons']
        if save: lead.save(update_fields=['opportunity_score','contactability_score','confidence_score','total_score','score_reasons','has_website','has_phone','normalized_name','updated_at'])
        return s
