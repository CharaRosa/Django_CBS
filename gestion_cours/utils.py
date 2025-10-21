from datetime import date

def calculer_progression(cours, aujourdhui=None):
    """
    Calcule la progression réelle, théorique, le décalage et l'alerte de retard
    pour un objet MatiereProgrammee.
    (Votre code original)
    """
    if aujourdhui is None:
        aujourdhui = date.today()

    total_faites = float(cours.total_heures_faites or 0)
    volume_prevu = float(cours.nbr_heure)

    # 1. Progression Réelle et Heures Restantes
    if volume_prevu > 0:
        cours.progression_reelle = min(100, (total_faites / volume_prevu) * 100)
    else:
        cours.progression_reelle = 0
        
    cours.heures_restantes = volume_prevu - total_faites
    
    # Initialisation des propriétés théoriques
    cours.progression_theorique = 0
    cours.decalage = 0
    cours.alerte_retard = False
    
    # 2. Progression Théorique et Décalage
    if cours.date_debut_estimee and cours.date_fin_estimee:
        duree_totale_jours = (cours.date_fin_estimee - cours.date_debut_estimee).days
        
        if duree_totale_jours > 0:
            if aujourdhui < cours.date_debut_estimee:
                jours_ecoules = 0
            elif aujourdhui > cours.date_fin_estimee:
                jours_ecoules = duree_totale_jours 
            else:
                jours_ecoules = (aujourdhui - cours.date_debut_estimee).days

            # Calcul de la progression théorique
            cours.progression_theorique = min(100, (jours_ecoules / duree_totale_jours) * 100)
        else:
            cours.progression_theorique = 100 

        # Calcul du décalage (Théorique - Réel)
        cours.decalage = cours.progression_theorique - cours.progression_reelle
        
        # 3. Logique d'Alerte de Retard
        jours_restants = (cours.date_fin_estimee - aujourdhui).days

        if cours.decalage > 0: 
            if jours_restants <= 7 and jours_restants >= 0 and cours.progression_reelle < 75:
                cours.alerte_retard = True
            elif jours_restants < 0 and cours.progression_reelle < 100:
                cours.alerte_retard = True 

    return cours