"""
EMAIL_ALERTS.PY - Système d'alertes email pour cours en retard

🔧 CORRECTION CRITIQUE DE LA LOGIQUE D'ALERTE:
Envoie des notifications aux professeurs et administrateurs quand:
- La progression est < 75% (EN RETARD)
- Il reste <= 7 jours avant la date de fin estimée

EXEMPLES DE DÉCLENCHEMENT:
✅ Progression 60%, 5 jours restants → ALERTE (retard critique)
❌ Progression 80%, 10 jours restants → PAS d'alerte (encore du temps)
❌ Progression 80%, 5 jours restants → PAS d'alerte (≥75%, dans les temps)
❌ Progression 76%, 7 jours restants → PAS d'alerte (≥75%, encore du temps)
✅ Progression 74%, 7 jours restants → ALERTE (retard)
❌ Progression 100%, 2 jours restants → PAS d'alerte (cours terminé)
"""

from django.core.mail import send_mail, send_mass_mail
from django.conf import settings
from django.contrib.auth import get_user_model
from datetime import date, timedelta
from decimal import Decimal
from .models import MatiereProgrammee, Emargement
from django.db.models import Sum

User = get_user_model()


def calculer_jours_restants(cours):
    """
    Calcule le nombre de jours restants avant la date de fin estimée.
    Retourne None si impossible à calculer.
    """
    try:
        # Récupérer la date de début du cours (première séance émargée)
        premier_emargement = Emargement.objects.filter(
            matiere_programmer=cours
        ).order_by('date_emar').first()
        
        if not premier_emargement:
            return None
        
        date_debut = premier_emargement.date_emar
        
        # Calculer le nombre de jours écoulés
        jours_ecoules = (date.today() - date_debut).days
        
        if jours_ecoules <= 0:
            return None
        
        # Calculer la progression réelle
        total_heures_faites = Emargement.objects.filter(
            matiere_programmer=cours
        ).aggregate(total=Sum('heure_eff'))['total'] or Decimal('0.00')
        
        volume_prevu = Decimal(str(cours.nbr_heure))
        
        if volume_prevu == 0:
            return None
        
        progression = (float(total_heures_faites) / float(volume_prevu)) * 100
        
        if progression <= 0 or progression >= 100:
            return None
        
        # Estimer la durée totale du cours
        duree_estimee_totale = (jours_ecoules / progression) * 100
        
        # Calculer les jours restants
        jours_restants = int(duree_estimee_totale - jours_ecoules)
        
        return jours_restants if jours_restants > 0 else 0
        
    except Exception as e:
        print(f"Erreur lors du calcul des jours restants pour le cours {cours.pk}: {e}")
        return None


def verifier_cours_en_alerte():
    """
    Vérifie tous les cours actifs et retourne ceux qui nécessitent une alerte.
    
    🔧 CORRECTION CRITIQUE: Critères d'alerte corrigés
    ANCIENNE LOGIQUE (INCORRECTE): progression >= 75% (alertait les cours avancés)
    NOUVELLE LOGIQUE (CORRECTE): progression < 75% (alerte les cours en retard)
    
    CONDITION COMPLÈTE:
    - progression < 75% (cours en retard)
    - progression > 0% (cours démarré)
    - jours_restants <= 7 (urgence temporelle)
    """
    from .views_dashboard import get_active_annee_academique
    
    annee_active = get_active_annee_academique()
    
    if not annee_active:
        return []
    
    cours_en_alerte = []
    
    # Récupérer tous les cours de l'année active
    cours_actifs = MatiereProgrammee.objects.filter(
        annee_academique=annee_active
    ).select_related('matiere', 'professeur', 'niveau', 'filiere').annotate(
        total_heures_faites=Sum('emargement__heure_eff')
    )
    
    for cours in cours_actifs:
        # Calculer la progression
        total_heures = float(cours.total_heures_faites or 0)
        volume_prevu = float(cours.nbr_heure)
        
        if volume_prevu == 0:
            continue
        
        progression = (total_heures / volume_prevu) * 100
        
        # 🔧 CORRECTION CRITIQUE: Vérifier si progression < 75% (EN RETARD)
        # Exclure les cours à 0% (pas encore démarrés) et >= 100% (terminés)
        if 0 < progression < 75:
            jours_restants = calculer_jours_restants(cours)
            
            # 🔧 CORRECTION: Alerte si jours_restants <= 7
            if jours_restants is not None and jours_restants <= 7:
                cours_en_alerte.append({
                    'cours': cours,
                    'progression': progression,
                    'jours_restants': jours_restants,
                    'heures_faites': total_heures,
                    'heures_restantes': volume_prevu - total_heures
                })
    
    return cours_en_alerte


def envoyer_alertes_email(cours_en_alerte):
    """
    Envoie des emails d'alerte pour chaque cours en retard.
    Destinataires: Professeur + Administrateurs pédagogiques
    """
    if not cours_en_alerte:
        print("Aucun cours en alerte.")
        return
    
    # Récupérer tous les administrateurs pédagogiques (groupe 'Assistant')
    admins = User.objects.filter(groups__name='Assistant', is_active=True)
    
    # Préparer les emails
    messages_email = []
    
    for alerte in cours_en_alerte:
        cours = alerte['cours']
        progression = alerte['progression']
        jours_restants = alerte['jours_restants']
        heures_faites = alerte['heures_faites']
        heures_restantes = alerte['heures_restantes']
        
        # Préparer le sujet et le corps de l'email
        sujet = f"🚨 ALERTE RETARD CRITIQUE: Cours en retard - {cours.matiere.libelle}"
        
        corps = f"""
Bonjour,

⚠️ UNE ALERTE DE RETARD CRITIQUE A ÉTÉ DÉCLENCHÉE pour le cours suivant:

📚 INFORMATIONS DU COURS:
- Matière: {cours.matiere.libelle} ({cours.matiere.code})
- Professeur: {cours.professeur.nom} {cours.professeur.prenoms}
- Niveau: {cours.filiere.code} - {cours.niveau.libelle}
- Semestre: {cours.get_semestre_display()}

📊 ÉTAT D'AVANCEMENT (EN RETARD):
- Progression: {progression:.1f}% (< 75% requis)
- Heures effectuées: {heures_faites:.1f}h / {cours.nbr_heure}h
- Heures restantes: {heures_restantes:.1f}h

⏰ URGENCE CRITIQUE:
- Jours restants estimés: {jours_restants} jour(s)
- Date d'alerte: {date.today().strftime('%d/%m/%Y')}

🚨 ACTION URGENTE REQUISE:
Le cours a atteint seulement {progression:.1f}% de progression et il reste {jours_restants} jour(s) 
pour terminer les {heures_restantes:.1f}h restantes avant la date de fin estimée.

Ce retard nécessite une action IMMÉDIATE pour rattraper le retard accumulé.

Merci de prendre les mesures nécessaires RAPIDEMENT pour rattraper le retard.

---
CBS Business School - Système de Gestion des Cours
Cet email est généré automatiquement.
"""
        
        # Liste des destinataires
        destinataires = []
        
        # Ajouter le professeur si son email existe
        if cours.professeur.email:
            destinataires.append(cours.professeur.email)
        
        # Ajouter les administrateurs pédagogiques
        for admin in admins:
            if admin.email:
                destinataires.append(admin.email)
        
        # Supprimer les doublons
        destinataires = list(set(destinataires))
        
        if destinataires:
            messages_email.append((
                sujet,
                corps,
                settings.DEFAULT_FROM_EMAIL,
                destinataires
            ))
    
    # Envoyer tous les emails en une seule fois
    if messages_email:
        try:
            nb_envoyes = send_mass_mail(messages_email, fail_silently=False)
            print(f"✅ {nb_envoyes} email(s) d'alerte envoyé(s) avec succès.")
            return nb_envoyes
        except Exception as e:
            print(f"❌ Erreur lors de l'envoi des emails: {e}")
            return 0
    else:
        print("Aucun destinataire valide trouvé.")
        return 0


def verifier_et_envoyer_alertes():
    """
    Fonction principale à appeler pour vérifier et envoyer les alertes.
    Peut être appelée manuellement ou via une tâche CRON.
    """
    print(f"🔍 Vérification des cours en alerte - {date.today()}")
    
    cours_en_alerte = verifier_cours_en_alerte()
    
    if cours_en_alerte:
        print(f"⚠️ {len(cours_en_alerte)} cours en alerte détecté(s):")
        for alerte in cours_en_alerte:
            cours = alerte['cours']
            print(f"  - {cours.matiere.libelle} ({alerte['progression']:.1f}%, {alerte['jours_restants']}j restants)")
        
        nb_envoyes = envoyer_alertes_email(cours_en_alerte)
        print(f"📧 {nb_envoyes} email(s) envoyé(s).")
    else:
        print("✅ Aucun cours en alerte.")
    
    return cours_en_alerte


def envoyer_email_test():
    """
    Fonction de test pour vérifier la configuration des emails.
    """
    try:
        send_mail(
            subject='Test - Système d\'alertes CBS',
            message='Ceci est un email de test pour vérifier la configuration SMTP.',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[settings.DEFAULT_FROM_EMAIL],
            fail_silently=False,
        )
        print("✅ Email de test envoyé avec succès!")
        return True
    except Exception as e:
        print(f"❌ Erreur lors de l'envoi de l'email de test: {e}")
        return False
