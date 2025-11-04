"""
VIEWS_ALERTS.PY - Vue pour gérer les alertes email
Permet aux administrateurs de déclencher manuellement les alertes
"""

from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from .email_alerts import verifier_et_envoyer_alertes, verifier_cours_en_alerte
from .views_dashboard import get_active_annee_academique


def est_administrateur_pedagogique(user):
    """Vérifie si l'utilisateur est AP ou superuser."""
    return user.groups.filter(name='Assistant').exists() or user.is_superuser


@login_required
@user_passes_test(est_administrateur_pedagogique, login_url='gestion_cours:home')
def alertes_view(request):
    """
    Affiche la page des alertes avec la liste des cours en retard.
    Permet de déclencher manuellement l'envoi des emails.
    """
    annee_active = get_active_annee_academique()
    
    # Vérifier les cours en alerte
    cours_en_alerte = verifier_cours_en_alerte()
    
    # Si l'utilisateur clique sur "Envoyer les alertes"
    if request.method == 'POST':
        if cours_en_alerte:
            from .email_alerts import envoyer_alertes_email
            nb_envoyes = envoyer_alertes_email(cours_en_alerte)
            
            if nb_envoyes > 0:
                messages.success(
                    request, 
                    f"✅ {nb_envoyes} email(s) d'alerte envoyé(s) avec succès!"
                )
            else:
                messages.error(
                    request,
                    "❌ Erreur lors de l'envoi des emails. Vérifiez la configuration SMTP."
                )
        else:
            messages.info(request, "ℹ️ Aucun cours en alerte à notifier.")
        
        return redirect('gestion_cours:alertes')
    
    context = {
        'cours_en_alerte': cours_en_alerte,
        'annee_active': annee_active.annee_accademique if annee_active else 'N/A',
        'nb_alertes': len(cours_en_alerte),
    }
    
    return render(request, 'gestion_cours/alertes.html', context)
