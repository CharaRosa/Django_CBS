"""
VIEWS_DASHBOARD.PY - Vues d'Accueil, Landing Page et Utilitaires Partagés
"""
from django.shortcuts import render, redirect
from django.db.models import Sum, Q, Count, F
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils import timezone 
from datetime import date, timedelta
from decimal import Decimal
import json 
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

# Import des modèles
from .models import (
    Professeur, Filiere, Niveau, Matiere, 
    AnneeAcademique, MatiereProgrammee, 
    Emargement, Evaluation
)

# Import des utilitaires et mixins
from .utils import calculer_progression
from .mixins import AssistantPedaRequiredMixin


# ==============================================================================
# FONCTIONS UTILITAIRES PARTAGÉES
# ==============================================================================

def get_active_annee_academique():
    """Récupère l'année académique active (fonction centralisée)."""
    try:
        return AnneeAcademique.objects.get(active=True)
    except AnneeAcademique.DoesNotExist:
        return None
    except AnneeAcademique.MultipleObjectsReturned:
        return AnneeAcademique.objects.filter(active=True).order_by('-id').first()


def paginate_queryset(request, queryset, items_per_page=10):
    """
    Helper function for pagination
    Usage: page_obj = paginate_queryset(request, queryset, 10)
    """
    paginator = Paginator(queryset, items_per_page)
    page = request.GET.get('page', 1)
    
    try:
        page_obj = paginator.page(page)
    except PageNotAnInteger:
        page_obj = paginator.page(1)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)
    
    return page_obj


# ==============================================================================
# CLASSE DE BASE POUR LES VUES PROTÉGÉES
# ==============================================================================

class BaseAPView(AssistantPedaRequiredMixin):
    """Classe de base avec mixin de sécurité pour toutes les vues AP."""
    pass


# ============================================================================
# VUE: Page d'accueil publique (landing page) - AVEC REDIRECTION
# ============================================================================

def landing_page(request):
    """
    Page d'accueil publique avec statistiques globales et graphiques.
    Redirige les utilisateurs connectés vers le Tableau de Bord AP.
    """
    if request.user.is_authenticated:
        return redirect('gestion_cours:home')
    
    annee_active = AnneeAcademique.objects.filter(active=True).first()
    
    # Statistiques principales
    stats = {
        'total_professeurs': Professeur.objects.count(),
        'total_cours': MatiereProgrammee.objects.count(),
        'total_matieres': Matiere.objects.count(),
        'heures_totales': MatiereProgrammee.objects.aggregate(
            total=Sum('nbr_heure')
        )['total'] or 0,
        'total_emargements': Emargement.objects.count(),
        'cours_ce_mois': MatiereProgrammee.objects.filter(
            date_debut_estimee__month=timezone.now().month,
            date_debut_estimee__year=timezone.now().year
        ).count(),
        'emargements_ce_mois': Emargement.objects.filter(
            date_emar__month=timezone.now().month,
            date_emar__year=timezone.now().year
        ).count(),
    }
    
    # Données pour graphiques
    graphiques = {}
    
    # 1. Répartition des cours par filière
    filieres_data = MatiereProgrammee.objects.values(
        'niveau__filiere__libelle'
    ).annotate(
        count=Count('id')
    ).order_by('-count')[:6]
    
    graphiques['filieres_labels'] = json.dumps([
        item['niveau__filiere__libelle'] or 'Non défini' 
        for item in filieres_data
    ])
    graphiques['filieres_data'] = json.dumps([
        item['count'] for item in filieres_data
    ])
    
    # 2. Distribution par niveau
    niveaux_data = MatiereProgrammee.objects.values(
        'niveau__libelle'
    ).annotate(
        count=Count('id')
    ).order_by('-count')[:6]
    
    graphiques['niveaux_labels'] = json.dumps([
        item['niveau__libelle'] or 'Non défini' 
        for item in niveaux_data
    ])
    graphiques['niveaux_data'] = json.dumps([
        item['count'] for item in niveaux_data
    ])
    
    # 3. Évolution des émargements (6 derniers mois)
    mois_labels = []
    mois_data = []
    for i in range(5, -1, -1):
        date_obj = timezone.now() - timedelta(days=30*i)
        mois_labels.append(date_obj.strftime('%b %Y'))
        count = Emargement.objects.filter(
            date_emar__month=date_obj.month,
            date_emar__year=date_obj.year
        ).count()
        mois_data.append(count)
    
    graphiques['emargement_labels'] = json.dumps(mois_labels)
    graphiques['emargement_data'] = json.dumps(mois_data)
    
    # 4. Taux de complétion par filière
    completion_data = []
    for filiere in Filiere.objects.all()[:6]:
        cours_filiere = MatiereProgrammee.objects.filter(
            niveau__filiere=filiere
        )
        total_cours = cours_filiere.count()
        if total_cours > 0:
            cours_emarges = cours_filiere.filter(
                emargement__isnull=False
            ).distinct().count()
            taux = round((cours_emarges / total_cours) * 100, 1)
        else:
            taux = 0
        
        completion_data.append({
            'nom': filiere.libelle, 
            'taux': taux
        })
    
    graphiques['completion_labels'] = json.dumps([
        item['nom'] for item in completion_data
    ])
    graphiques['completion_data'] = json.dumps([
        item['taux'] for item in completion_data
    ])
    
    context = {
        'stats': stats,
        'graphiques': graphiques,
        'current_year': timezone.now().year,
    }
    
    return render(request, 'gestion_cours/landing.html', context)


# ============================================================================
# VUE: Tableau de bord admin (home) - VERSION FUSIONNÉE
# ============================================================================

@login_required
def home_view(request):
    """
    Tableau de bord administratif avec statistiques, alertes, graphiques et cours programmés.
    """
    annee_active = get_active_annee_academique()
    
    if not annee_active:
        messages.error(request, "Erreur : Aucune Année Académique n'est marquée comme active. Veuillez en activer une.")
        context = {
            'annee_active': None,
            'cours_list': [],
            'stats': {},
            'alertes': [],
            'graphiques': {},
            'activites_recentes': [],
        }
        return render(request, 'gestion_cours/home.html', context)

    # 1. RÉCUPÉRATION DES COURS AVEC ANNOTATIONS (OPTIMISÉ)
    cours_list_queryset = MatiereProgrammee.objects.filter(
        annee_academique=annee_active
    ).select_related(
        'matiere', 'professeur', 'filiere', 'niveau'
    ).annotate(
        niveau_complet=F('niveau__libelle'),
        total_heures_faites=Sum('emargement__heure_eff')
    ).order_by('filiere__libelle', 'niveau__niv')
    
    aujourdhui = date.today()

    # 2. CALCUL DE LA PROGRESSION POUR CHAQUE COURS
    cours_traites = []
    for cours in cours_list_queryset:
        cours.est_evalue = Evaluation.objects.filter(matiere_programmer=cours).exists()
        cours_traites.append(calculer_progression(cours, aujourdhui))
    
    cours_list = cours_traites

    # 3. STATISTIQUES PRINCIPALES
    total_cours_count = MatiereProgrammee.objects.filter(annee_academique=annee_active).count()
    total_heures = MatiereProgrammee.objects.filter(
        annee_academique=annee_active
    ).aggregate(Sum('nbr_heure'))['nbr_heure__sum'] or 0
    
    total_emargements_count = Emargement.objects.filter(
        matiere_programmer__annee_academique=annee_active
    ).count()
    
    total_heures_enseignees = Emargement.objects.filter(
        matiere_programmer__annee_academique=annee_active
    ).aggregate(total=Sum('heure_eff'))['total'] or 0

    stats = {
        'total_professeurs': Professeur.objects.count(),
        'nouveaux_professeurs': 0,
        'total_cours': total_cours_count,
        'heures_totales': total_heures,
        'heures_enseignees': total_heures_enseignees,
        'total_emargements': total_emargements_count,
        'matieres_actives': Matiere.objects.count(),
        'professeurs_actifs': Professeur.objects.count(),
        'total_evaluations': Evaluation.objects.filter(
            matiere_programmer__annee_academique=annee_active
        ).count(),
        'evaluations_en_attente': Evaluation.objects.filter(
            matiere_programmer__annee_academique=annee_active
        ).filter(
            Q(resume_evaluation__isnull=True) | Q(resume_evaluation='')
        ).count(),
    }
    
    # Calcul du taux d'émargement
    if stats['total_cours'] > 0:
        cours_emarges_count = MatiereProgrammee.objects.filter(
            annee_academique=annee_active,
            emargement__isnull=False
        ).distinct().count()
        stats['taux_emargement'] = round((cours_emarges_count / stats['total_cours']) * 100, 2)
    else:
        stats['taux_emargement'] = 0
    
    # 4. ALERTES SYSTÈME
    alertes = []
    
    # Alerte: Cours sans émargement depuis plus de 7 jours
    cours_sans_emargement = MatiereProgrammee.objects.filter(
        annee_academique=annee_active, 
        date_debut_estimee__lte=timezone.now() - timedelta(days=7),
        emargement__isnull=True
    ).count()
    if cours_sans_emargement > 0:
        alertes.append({
            'titre': 'Cours sans émargement',
            'description': f'{cours_sans_emargement} cours nécessitent un émargement',
            'type': 'Urgent',
            'priorite': 'danger'
        })
    
    # Alerte: Évaluations en attente
    if stats['evaluations_en_attente'] > 10:
        alertes.append({
            'titre': 'Évaluations en attente',
            'description': f'{stats["evaluations_en_attente"]} évaluations sans résumé/note',
            'type': 'Important',
            'priorite': 'warning'
        })
    
    # Alerte: Professeurs sans cours
    profs_sans_cours = Professeur.objects.annotate(
        nb_cours=Count('matiereprogrammee', filter=Q(matiereprogrammee__annee_academique=annee_active))
    ).filter(nb_cours=0).count()
    if profs_sans_cours > 0:
        alertes.append({
            'titre': 'Professeurs inactifs',
            'description': f'{profs_sans_cours} professeurs sans cours assigné',
            'type': 'Info',
            'priorite': 'info'
        })
    
    # 5. DONNÉES POUR GRAPHIQUES
    graphiques = {}
    
    # Graphique 1: Cours par filière
    filieres_data = MatiereProgrammee.objects.filter(
        annee_academique=annee_active
    ).values(
        'niveau__filiere__libelle' 
    ).annotate(
        count=Count('id')
    ).order_by('-count')[:6]
    
    graphiques['filieres_labels'] = json.dumps([
        item['niveau__filiere__libelle'] or 'Non défini' 
        for item in filieres_data
    ])
    graphiques['filieres_data'] = json.dumps([
        item['count'] for item in filieres_data
    ])
    
    # Graphique 2: Progression émargements (7 derniers jours)
    jours_labels = []
    jours_data = []
    for i in range(6, -1, -1):
        date_obj = timezone.now() - timedelta(days=i)
        jours_labels.append(date_obj.strftime('%d/%m'))
        count = Emargement.objects.filter(date_emar=date_obj.date()).count()
        jours_data.append(count)
    
    graphiques['emargement_labels'] = json.dumps(jours_labels)
    graphiques['emargement_data'] = json.dumps(jours_data)
    
    # Graphique 3: Top 5 professeurs actifs
    top_profs = Professeur.objects.annotate(
        nb_emargements=Count(
            'matiereprogrammee__emargement', 
            filter=Q(matiereprogrammee__annee_academique=annee_active)
        )
    ).order_by('-nb_emargements')[:5]
    
    graphiques['top_prof_labels'] = json.dumps([
        f"{prof.nom} {prof.prenoms}" for prof in top_profs 
    ])
    graphiques['top_prof_data'] = json.dumps([
        prof.nb_emargements for prof in top_profs
    ])
    
    # 6. ACTIVITÉS RÉCENTES
    activites_recentes = []
    
    # Derniers émargements
    derniers_emargements = Emargement.objects.filter(
        matiere_programmer__annee_academique=annee_active
    ).select_related(
        'matiere_programmer__professeur',
        'matiere_programmer__matiere'
    ).order_by('-date_emar')[:5]
    
    for emarg in derniers_emargements:
        activites_recentes.append({
            'date': emarg.date_emar,
            'type': 'Émargement',
            'badge_class': 'success',
            'description': f"{emarg.matiere_programmer.matiere.libelle} - {emarg.matiere_programmer.professeur}",
            'utilisateur': 'Système',
            'lien': None
        })
    
    # Dernières évaluations
    dernieres_eval = Evaluation.objects.filter(
        matiere_programmer__annee_academique=annee_active
    ).select_related(
        'matiere_programmer__matiere',
        'matiere_programmer__professeur'
    ).order_by('-id')[:3]
    
    for eval_obj in dernieres_eval:
        description_note = eval_obj.resume_evaluation[:20] if eval_obj.resume_evaluation else 'En attente'
        eval_date_proxy = eval_obj.matiere_programmer.date_debut_estimee or timezone.now().date()

        activites_recentes.append({
            'date': eval_date_proxy,
            'type': 'Évaluation',
            'badge_class': 'warning',
            'description': f"{eval_obj.matiere_programmer.matiere.libelle} - Résumé: {description_note}",
            'utilisateur': eval_obj.utilisateur_evaluation.get_full_name() if eval_obj.utilisateur_evaluation else 'Système',
            'lien': None
        })
    
    # Trier par date
    activites_recentes.sort(key=lambda x: x['date'], reverse=True)
    activites_recentes = activites_recentes[:10]
    
    context = {
        'annee_active': annee_active,
        'cours_list': cours_list,
        'stats': stats,
        'alertes': alertes,
        'graphiques': graphiques,
        'activites_recentes': activites_recentes,
        'now': timezone.now(),
    }
    
    return render(request, 'gestion_cours/home.html', context)
