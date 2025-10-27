# gestion_cours/utils.py

from datetime import date
from django.db import models

def calculer_progression(cours, aujourdhui=None):
    """
    Calcule la progression réelle, théorique, le décalage et l'alerte de retard
    pour un objet MatiereProgrammee.
    """
    if aujourdhui is None:
        aujourdhui = date.today()

    # Récupération des heures effectuées (somme des émargements)
    from django.db.models import Sum
    
    total_faites = float(
        cours.emargement_set.aggregate(
            total=Sum('heure_eff')
        )['total'] or 0
    )
    
    volume_prevu = float(cours.nbr_heure)

    # 1. Progression Réelle et Heures Restantes
    if volume_prevu > 0:
        cours.progression_reelle = min(100, (total_faites / volume_prevu) * 100)
    else:
        cours.progression_reelle = 0
        
    cours.heures_restantes = max(0, volume_prevu - total_faites)
    cours.total_heures_faites = total_faites
    
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

        if jours_restants < 0:
            jours_restants = -1  # Cours déjà terminé théoriquement
        
        if cours.decalage > 0: 
            # Alerte si la fin approche (moins de 7 jours) et le cours n'est pas très avancé
            if 0 <= jours_restants <= 7 and cours.progression_reelle < 75:
                cours.alerte_retard = True
            # Alerte si la date de fin est dépassée et le cours n'est pas à 100%
            elif jours_restants < 0 and cours.progression_reelle < 100:
                cours.alerte_retard = True 

    return cours
