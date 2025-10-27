"""
VIEWS.PY COMPLET ET FUSIONNÉ - Gestion CBS Project
Intègre toutes les fonctionnalités : Filtres, Exports, CRUD complets, Émargements, Évaluations
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Sum, Q, Count, F
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, View
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.http import HttpResponse
from django.utils import timezone 
from datetime import date, timedelta
from decimal import Decimal
import json 

# Import des modèles
from .models import (
    Professeur, Filiere, Niveau, Matiere, 
    AnneeAcademique, MatiereProgrammee, 
    Emargement, Evaluation
)

# Import des formulaires
from .forms import (
    MatiereForm, ProfesseurForm, EmargementForm, 
    EvaluationForm, MatiereProgrammeeForm
)

# Import des filtres
from .filters_complete import (
    ProfesseurFilter, MatiereProgrammeeFilter, 
    EmargementFilterComplete, EvaluationFilter,
    CoursEmargementFilter
)



# Import des utilitaires
from .utils import calculer_progression
from .mixins import AssistantPedaRequiredMixin

# Import des exports
from .export_utils_complete import (
    export_professeurs_to_excel, export_professeurs_to_pdf,
    export_cours_to_excel, export_cours_to_pdf,
    export_emargements_to_excel, export_emargements_to_pdf,
    export_evaluations_to_excel, export_evaluations_to_pdf
)


# ==============================================================================
# FONCTIONS UTILITAIRES
# ==============================================================================

def est_administrateur_pedagogique(user):
    """Vérifie si l'utilisateur est AP ou superuser."""
    return user.groups.filter(name='Assistant').exists() or user.is_superuser


def get_active_annee_academique():
    """Récupère l'année académique active (fonction centralisée)."""
    try:
        return AnneeAcademique.objects.get(active=True)
    except AnneeAcademique.DoesNotExist:
        return None
    except AnneeAcademique.MultipleObjectsReturned:
        return AnneeAcademique.objects.filter(active=True).order_by('-id').first()


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
    Combine les fonctionnalités des deux versions.
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
    
    # CORRECTION CRITIQUE : Utilisation de 'matiere_programmer' au lieu de 'matiere_programmee'
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
    
    # Derniers émargements (CORRECTION: matiere_programmer)
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
    
    # Dernières évaluations (CORRECTION: matiere_programmer)
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


# ============================================================================
# VUES: Gestion des professeurs (avec filtres et exports)
# ============================================================================

@login_required
def professeur_list_view(request):
    """Liste des professeurs avec filtres et exports."""
    professeur_list = Professeur.objects.all().order_by('nom')
    professeur_filter = ProfesseurFilter(request.GET, queryset=professeur_list)
    
    # Gestion des exports
    if 'export' in request.GET:
        export_type = request.GET.get('export')
        filtered_qs = professeur_filter.qs
        
        if export_type == 'excel':
            return export_professeurs_to_excel(filtered_qs)
        elif export_type == 'pdf':
            return export_professeurs_to_pdf(filtered_qs)
    
    context = {
        'filter': professeur_filter,
        'object_list': professeur_filter.qs,
    }
    return render(request, 'gestion_cours/professeur_list.html', context)


class ProfesseurCreateView(BaseAPView, CreateView):
    """Création d'un professeur."""
    model = Professeur
    fields = ['nom', 'prenoms', 'contact', 'email', 'grade', 'domaine', 'cv', 'dernier_diplome']
    template_name = 'gestion_cours/professeur_form.html'
    success_url = reverse_lazy('gestion_cours:professeur_list')
    
    def form_valid(self, form):
        messages.success(self.request, "✅ Professeur créé avec succès.")
        return super().form_valid(form)


class ProfesseurUpdateView(BaseAPView, UpdateView):
    """Modification d'un professeur."""
    model = Professeur
    fields = ['nom', 'prenoms', 'contact', 'email', 'grade', 'domaine', 'cv', 'dernier_diplome']
    template_name = 'gestion_cours/professeur_form.html'
    success_url = reverse_lazy('gestion_cours:professeur_list')

    def form_valid(self, form):
        messages.success(self.request, "✅ Professeur modifié avec succès.")
        return super().form_valid(form)


class ProfesseurDeleteView(BaseAPView, DeleteView):
    """Suppression d'un professeur."""
    model = Professeur
    template_name = 'gestion_cours/confirm_delete_base.html'
    success_url = reverse_lazy('gestion_cours:professeur_list')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['list_url'] = 'gestion_cours:professeur_list'
        return context
    
    def delete(self, request, *args, **kwargs):
        messages.success(self.request, f"✅ Le professeur '{self.get_object()}' a été supprimé avec succès.")
        return super().delete(request, *args, **kwargs)


# ============================================================================
# VUES: Gestion des matières programmées (avec filtres et exports)
# ============================================================================

@login_required
def matiereprogrammee_list_view(request):
    """Liste des cours programmés avec filtres et exports."""
    annee_active = get_active_annee_academique()
    
    if not annee_active:
        messages.warning(request, "Attention : Aucune Année Académique active. Affichage de la liste vide.")
        matiere_list = MatiereProgrammee.objects.none()
    else:
        matiere_list = MatiereProgrammee.objects.filter(
            annee_academique=annee_active
        ).select_related(
            'matiere', 'professeur', 'niveau', 'filiere', 'annee_academique'
        ).order_by('filiere__libelle', 'niveau__niv')
    
    matiere_filter = MatiereProgrammeeFilter(request.GET, queryset=matiere_list)
    
    # Gestion des exports
    if 'export' in request.GET:
        export_type = request.GET.get('export')
        filtered_qs = matiere_filter.qs
        
        if export_type == 'excel':
            return export_cours_to_excel(filtered_qs)
        elif export_type == 'pdf':
            return export_cours_to_pdf(filtered_qs)
    
    context = {
        'filter': matiere_filter,
        'object_list': matiere_filter.qs,
    }
    return render(request, 'gestion_cours/matiereprogrammee_list.html', context)


class MatiereProgrammeeCreateView(BaseAPView, CreateView):
    """Création d'un cours programmé."""
    model = MatiereProgrammee
    form_class = MatiereProgrammeeForm
    template_name = 'gestion_cours/form_base.html'
    success_url = reverse_lazy('gestion_cours:matiereprogrammee_list')
    
    def form_valid(self, form):
        messages.success(self.request, "✅ Cours programmé créé avec succès.")
        return super().form_valid(form)


class MatiereProgrammeeUpdateView(BaseAPView, UpdateView):
    """Modification d'un cours programmé."""
    model = MatiereProgrammee
    form_class = MatiereProgrammeeForm
    template_name = 'gestion_cours/form_base.html'
    success_url = reverse_lazy('gestion_cours:matiereprogrammee_list')

    def form_valid(self, form):
        messages.success(self.request, "✅ Cours programmé modifié avec succès.")
        return super().form_valid(form)


class MatiereProgrammeeDeleteView(BaseAPView, DeleteView):
    """Suppression d'un cours programmé."""
    model = MatiereProgrammee
    template_name = 'gestion_cours/confirm_delete_base.html'
    success_url = reverse_lazy('gestion_cours:matiereprogrammee_list')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['list_url'] = 'gestion_cours:matiereprogrammee_list'
        return context
    
    def delete(self, request, *args, **kwargs):
        messages.success(self.request, "✅ Cours programmé supprimé avec succès.")
        return super().delete(request, *args, **kwargs)


# ============================================================================
# VUES: Gestion des émargements - VERSION COMPLÈTE AVEC FILTRES
# ============================================================================

@login_required
def emargement_selection_cours(request):
    """
    Sélection de cours pour émargement avec filtres.
    Liste tous les cours programmés pour l'année active.
    """
    annee_active = get_active_annee_academique()
    
    if not annee_active:
        messages.error(request, "Impossible d'afficher les cours : Aucune année académique active trouvée.")
        cours_list = MatiereProgrammee.objects.none()
    else:
        # Annoter avec le total des heures faites
        cours_list = MatiereProgrammee.objects.filter(
            annee_academique=annee_active
        ).select_related(
            'matiere', 'professeur', 'niveau', 'filiere'
        ).annotate(
            total_heures_faites=Sum('emargement__heure_eff')
        ).order_by('filiere__libelle', 'niveau__niv')
    
    # Appliquer les filtres
    cours_filter = CoursEmargementFilter(request.GET, queryset=cours_list)
    
    context = {
        'filter': cours_filter,
        'cours_list': cours_filter.qs,
    }
    return render(request, 'gestion_cours/emargement_selection_cours.html', context)


# Alias pour la route 'emargement_selection'
emargement_selection_view = emargement_selection_cours


@login_required
def emargement_view(request, pk):
    """
    Gère l'affichage et la soumission du formulaire d'émargement.
    Contrôle strict de l'heure totale et enregistre l'utilisateur AP.
    VERSION COMPLÈTE ET CORRIGÉE.
    """
    # 1. Récupère la MatiereProgrammee avec le total des heures faites
    matiere_prog = get_object_or_404(
        MatiereProgrammee.objects.annotate(
            total_heures_faites=Sum('emargement__heure_eff')
        ).select_related('matiere', 'professeur', 'niveau', 'filiere', 'annee_academique'),
        pk=pk
    )
    
    # 2. Vérification de l'année active
    annee_active = get_active_annee_academique()
    if not annee_active:
        messages.error(request, "Impossible d'émarger : Aucune année académique active trouvée.")
        return redirect('gestion_cours:home')

    if matiere_prog.annee_academique != annee_active:
        messages.error(request, "Erreur : La matière sélectionnée n'est pas programmée pour l'année académique active.")
        return redirect('gestion_cours:home')

    # 3. Calcul des volumes
    volume_prevu = matiere_prog.nbr_heure
    heures_faites_actuelles = matiere_prog.total_heures_faites or Decimal('0.00')
    
    volume_prevant_decimal = Decimal(str(volume_prevu))
    volume_restant = volume_prevant_decimal - heures_faites_actuelles
    volume_restant = volume_restant.quantize(Decimal('0.01'))
    volume_restant_float = float(volume_restant)
    
    # 4. Initialisation du formulaire (pour GET et POST)
    initial_data = {'date_emar': timezone.now().date()}
    form = EmargementForm(request.POST or None, initial=initial_data)

    # 5. Contexte pour le template
    context = {
        'matiere_prog': matiere_prog,
        'form': form,
        'volume_restant': volume_restant,
    }

    # 6. Traitement du POST
    if request.method == 'POST':
        if form.is_valid():
            # Récupération des données
            date_emar = form.cleaned_data['date_emar']
            heure_eff_saisie = float(form.cleaned_data['heure_eff'])

            # --- VÉRIFICATION D'UNICITÉ ---
            if Emargement.objects.filter(matiere_programmer=matiere_prog, date_emar=date_emar).exists():
                messages.error(
                    request, 
                    f"Échec de l'émargement : La matière {matiere_prog.matiere.libelle} "
                    f"a déjà été émargée à la date du {date_emar}."
                )
                return render(request, 'gestion_cours/emargement_form.html', context)

            # --- VALIDATION DES HEURES ---
            if heure_eff_saisie <= 0 or heure_eff_saisie > 8:
                messages.error(request, "Erreur: La durée du cours doit être comprise entre 0 et 8 heures.")
                return render(request, 'gestion_cours/emargement_form.html', context)

            if volume_restant_float <= 0:
                messages.error(
                    request, 
                    f"Échec de l'émargement : Le volume horaire prévu de {volume_prevu}h "
                    f"est déjà atteint ou dépassé ({heures_faites_actuelles:.2f}h)."
                )
                return render(request, 'gestion_cours/emargement_form.html', context)

            if heure_eff_saisie > volume_restant_float:
                messages.error(
                    request, 
                    f"Échec de l'émargement : La durée saisie ({heure_eff_saisie:.2f}h) "
                    f"dépasse le volume restant ({volume_restant_float:.2f}h). "
                    f"Veuillez ajuster votre saisie."
                )
                return render(request, 'gestion_cours/emargement_form.html', context)
            
            # --- CRÉATION DE L'ÉMARGEMENT ---
            emargement_obj = form.save(commit=False)
            emargement_obj.matiere_programmer = matiere_prog
            emargement_obj.emarge_par = request.user  # Enregistre l'utilisateur connecté
            emargement_obj.save()
            
            messages.success(
                request, 
                f"Séance d'émargement du {date_emar} (durée: {heure_eff_saisie:.2f}h) "
                f"enregistrée avec succès."
            )
            
            return redirect('gestion_cours:emargement_selection')
            
        else:
            # Formulaire invalide
            messages.error(request, "Erreur de formulaire. Veuillez vérifier les champs.")
            return render(request, 'gestion_cours/emargement_form.html', context)

    # 7. Affichage GET
    return render(request, 'gestion_cours/emargement_form.html', context)


# ============================================================================
# VUES: Historique des émargements - VERSION COMPLÈTE AVEC FILTRES
# ============================================================================

@login_required
@user_passes_test(est_administrateur_pedagogique, login_url=reverse_lazy('gestion_cours:home'))
def historique_view(request):
    """
    Affiche l'historique des émargements pour l'année académique active.
    AVEC FILTRES django-filter.
    """
    annee_active = get_active_annee_academique()
    
    if not annee_active:
        messages.warning(request, "Impossible d'afficher l'historique : Aucune année académique active trouvée.")
        historique = Emargement.objects.none()
        emargement_filter = EmargementFilterComplete(request.GET, queryset=historique)
    else:
        # Base du QuerySet (filtré par année active)
        queryset = Emargement.objects.filter(
            matiere_programmer__annee_academique=annee_active
        ).select_related(
            'matiere_programmer__professeur', 
            'matiere_programmer__matiere',
        ).order_by('-date_emar')

        # Appliquer les filtres
        emargement_filter = EmargementFilterComplete(request.GET, queryset=queryset)
        historique = emargement_filter.qs

        # Limiter à 50 si AUCUN filtre n'est appliqué
        if not request.GET:
            historique = historique[:50]
        
    context = {
        'historique': historique,
        'filter': emargement_filter,
        'annee_active': annee_active.annee_accademique if annee_active else 'N/A'
    }
    return render(request, 'gestion_cours/historique_global.html', context)


@login_required
@user_passes_test(est_administrateur_pedagogique, login_url=reverse_lazy('gestion_cours:home'))
def historique_cours_view(request, pk):
    """
    Affiche l'historique détaillé des émargements pour un cours programmé spécifique.
    """
    # 1. Récupère le cours avec annotations
    matiere_prog = get_object_or_404(
        MatiereProgrammee.objects.select_related(
            'matiere', 'professeur', 'niveau', 'filiere', 'annee_academique'
        ).annotate(
            total_heures_faites=Sum('emargement__heure_eff')
        ), 
        pk=pk
    )
    
    # 2. Récupère tous les émargements pour ce cours
    historique_emargement_list = Emargement.objects.filter(
        matiere_programmer=matiere_prog
    ).select_related('emarge_par').order_by('-date_emar')

    # 3. Calcule la progression
    progression_details = calculer_progression(matiere_prog, date.today())
    
    # 4. Récupère l'évaluation si elle existe
    try:
        evaluation = Evaluation.objects.get(matiere_programmer=matiere_prog)
    except Evaluation.DoesNotExist:
        evaluation = None

    context = {
        'matiere_prog': matiere_prog,
        'historique_emargement': historique_emargement_list,
        'progression_details': progression_details,
        'evaluation': evaluation,
    }
    return render(request, 'gestion_cours/historique_cours.html', context)


# ============================================================================
# VUES: Gestion des évaluations (avec filtres et exports)
# ============================================================================

@login_required
def evaluation_list_view(request):
    """Liste des évaluations avec filtres et exports."""
    annee_active = get_active_annee_academique()
    
    if not annee_active:
        messages.warning(request, "Attention : Aucune Année Académique active.")
        evaluation_list = Evaluation.objects.none()
    else:
        evaluation_list = Evaluation.objects.filter(
            matiere_programmer__annee_academique=annee_active
        ).select_related(
            'matiere_programmer__matiere',
            'matiere_programmer__professeur',
            'matiere_programmer__niveau',
            'utilisateur_evaluation'
        ).order_by('-id')
    
    evaluation_filter = EvaluationFilter(request.GET, queryset=evaluation_list)
    
    # Gestion des exports
    if 'export' in request.GET:
        export_type = request.GET.get('export')
        filtered_qs = evaluation_filter.qs
        
        if export_type == 'excel':
            return export_evaluations_to_excel(filtered_qs)
        elif export_type == 'pdf':
            return export_evaluations_to_pdf(filtered_qs)
    
    context = {
        'filter': evaluation_filter,
        'evaluations': evaluation_filter.qs,
    }
    return render(request, 'gestion_cours/evaluation_list.html', context)


@method_decorator(login_required, name='dispatch')
class EvaluationManagementView(BaseAPView, UpdateView):
    """
    Permet à l'AP d'ajouter ou de modifier l'évaluation qualitative d'un cours complété.
    VERSION COMPLÈTE ET CORRIGÉE.
    """
    model = Evaluation
    form_class = EvaluationForm
    template_name = 'gestion_cours/evaluation_form.html'
    success_url = reverse_lazy('gestion_cours:home')

    def dispatch(self, request, *args, **kwargs):
        # Vérification des permissions (via BaseAPView)
        if not self.has_permission():
            return self.handle_no_permission()

        # Récupération de la MatiereProgrammee
        self.matiere_prog = get_object_or_404(MatiereProgrammee, pk=kwargs.get('pk'))
        
        # Vérification 100% de progression
        total_faites = Emargement.objects.filter(
            matiere_programmer=self.matiere_prog
        ).aggregate(total_faites=Sum('heure_eff'))['total_faites'] or 0
        
        volume_prevu = float(self.matiere_prog.nbr_heure)
        progression = (float(total_faites) / volume_prevu) * 100 if volume_prevu > 0 else 0

        if progression < 100:
            messages.error(request, "Impossible d'évaluer : le cours n'a pas atteint 100% de progression.")
            return redirect('gestion_cours:home')

        # Récupération ou création de l'évaluation
        try:
            self.object = Evaluation.objects.get(matiere_programmer=self.matiere_prog)
        except Evaluation.DoesNotExist:
            self.object = None

        return super().dispatch(request, *args, **kwargs)

    def get_object(self, queryset=None):
        return self.object

    def get_initial(self):
        initial = super().get_initial()
        if not self.object:
            initial['matiere_programmer'] = self.matiere_prog
        return initial

    def form_valid(self, form):
        evaluation = form.save(commit=False)
        evaluation.matiere_programmer = self.matiere_prog
        evaluation.utilisateur_evaluation = self.request.user
        evaluation.save()
        
        messages.success(
            self.request, 
            f"Évaluation qualitative enregistrée pour {self.matiere_prog.matiere.libelle}!"
        )
        return redirect('gestion_cours:home')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['matiere_prog'] = self.matiere_prog
        context['mode_edition'] = self.object is not None
        
        # Calcul de la progression pour l'affichage
        total_faites = Emargement.objects.filter(
            matiere_programmer=self.matiere_prog
        ).aggregate(total_faites=Sum('heure_eff'))['total_faites'] or 0
        
        volume_prevu = float(self.matiere_prog.nbr_heure)
        context['progression'] = (float(total_faites) / volume_prevu) * 100 if volume_prevu > 0 else 0
        
        return context


# ==============================================================================
# CRUD - MATIÈRES
# ==============================================================================

class MatiereListView(BaseAPView, ListView):
    model = Matiere
    template_name = 'gestion_cours/matiere_list.html'
    context_object_name = 'object_list'
    ordering = ['libelle']


class MatiereCreateView(BaseAPView, CreateView):
    model = Matiere
    form_class = MatiereForm
    template_name = 'gestion_cours/matiere_form.html'
    success_url = reverse_lazy('gestion_cours:matiere_list')
    
    def form_valid(self, form):
        messages.success(self.request, "✅ Matière créée avec succès.")
        return super().form_valid(form)


class MatiereUpdateView(BaseAPView, UpdateView):
    model = Matiere
    form_class = MatiereForm
    template_name = 'gestion_cours/matiere_form.html'
    success_url = reverse_lazy('gestion_cours:matiere_list')
    
    def form_valid(self, form):
        messages.success(self.request, "✅ Matière modifiée avec succès.")
        return super().form_valid(form)


class MatiereDeleteView(BaseAPView, DeleteView):
    model = Matiere
    template_name = 'gestion_cours/matiere_confirm_delete.html'
    success_url = reverse_lazy('gestion_cours:matiere_list')
    
    def delete(self, request, *args, **kwargs):
        messages.success(self.request, "✅ Matière supprimée avec succès.")
        return super().delete(request, *args, **kwargs)


# ==============================================================================
# CRUD - FILIÈRES
# ==============================================================================

class FiliereListView(BaseAPView, ListView):
    model = Filiere
    template_name = 'gestion_cours/filiere_list.html'
    context_object_name = 'object_list'
    ordering = ['libelle']


class FiliereCreateView(BaseAPView, CreateView):
    model = Filiere
    fields = ['code', 'libelle']
    template_name = 'gestion_cours/form_base.html'
    success_url = reverse_lazy('gestion_cours:filiere_list')
    
    def form_valid(self, form):
        messages.success(self.request, "✅ Filière créée avec succès.")
        return super().form_valid(form)


class FiliereUpdateView(BaseAPView, UpdateView):
    model = Filiere
    fields = ['code', 'libelle']
    template_name = 'gestion_cours/form_base.html'
    success_url = reverse_lazy('gestion_cours:filiere_list')
    
    def form_valid(self, form):
        messages.success(self.request, "✅ Filière modifiée avec succès.")
        return super().form_valid(form)


class FiliereDeleteView(BaseAPView, DeleteView):
    model = Filiere
    template_name = 'gestion_cours/confirm_delete_base.html'
    success_url = reverse_lazy('gestion_cours:filiere_list')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['list_url'] = 'gestion_cours:filiere_list'
        return context
    
    def delete(self, request, *args, **kwargs):
        messages.success(self.request, "✅ Filière supprimée avec succès.")
        return super().delete(request, *args, **kwargs)


# ==============================================================================
# CRUD - NIVEAUX
# ==============================================================================

class NiveauListView(BaseAPView, ListView):
    model = Niveau
    template_name = 'gestion_cours/niveau_list.html'
    context_object_name = 'object_list'
    ordering = ['filiere', 'niv']


class NiveauCreateView(BaseAPView, CreateView):
    model = Niveau
    fields = ['libelle', 'niv', 'filiere']
    template_name = 'gestion_cours/form_base.html'
    success_url = reverse_lazy('gestion_cours:niveau_list')
    
    def form_valid(self, form):
        messages.success(self.request, "✅ Niveau créé avec succès.")
        return super().form_valid(form)


class NiveauUpdateView(BaseAPView, UpdateView):
    model = Niveau
    fields = ['libelle', 'niv', 'filiere']
    template_name = 'gestion_cours/form_base.html'
    success_url = reverse_lazy('gestion_cours:niveau_list')
    
    def form_valid(self, form):
        messages.success(self.request, "✅ Niveau modifié avec succès.")
        return super().form_valid(form)


class NiveauDeleteView(BaseAPView, DeleteView):
    model = Niveau
    template_name = 'gestion_cours/confirm_delete_base.html'
    success_url = reverse_lazy('gestion_cours:niveau_list')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['list_url'] = 'gestion_cours:niveau_list'
        return context
    
    def delete(self, request, *args, **kwargs):
        messages.success(self.request, "✅ Niveau supprimé avec succès.")
        return super().delete(request, *args, **kwargs)


# ==============================================================================
# CRUD - ANNÉES ACADÉMIQUES
# ==============================================================================

class AnneeAcademiqueListView(BaseAPView, ListView):
    model = AnneeAcademique
    template_name = 'gestion_cours/anneeacademique_list.html'
    context_object_name = 'object_list'
    ordering = ['-annee_accademique']


class AnneeAcademiqueCreateView(BaseAPView, CreateView):
    model = AnneeAcademique
    fields = ['annee_accademique', 'active']
    template_name = 'gestion_cours/form_base.html'
    success_url = reverse_lazy('gestion_cours:anneeacademique_list')
    
    def form_valid(self, form):
        # Désactiver toutes les autres années si celle-ci est active
        if form.instance.active:
            AnneeAcademique.objects.filter(active=True).update(active=False)
        
        messages.success(self.request, "✅ Année académique créée avec succès.")
        return super().form_valid(form)


class AnneeAcademiqueUpdateView(BaseAPView, UpdateView):
    model = AnneeAcademique
    fields = ['annee_accademique', 'active']
    template_name = 'gestion_cours/form_base.html'
    success_url = reverse_lazy('gestion_cours:anneeacademique_list')
    
    def form_valid(self, form):
        # Désactiver toutes les autres années si celle-ci est active
        if form.instance.active:
            AnneeAcademique.objects.exclude(pk=form.instance.pk).update(active=False)
        
        messages.success(self.request, "✅ Année académique modifiée avec succès.")
        return super().form_valid(form)


class AnneeAcademiqueDeleteView(BaseAPView, DeleteView):
    model = AnneeAcademique
    template_name = 'gestion_cours/confirm_delete_base.html'
    success_url = reverse_lazy('gestion_cours:anneeacademique_list')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['list_url'] = 'gestion_cours:anneeacademique_list'
        return context
    
    def delete(self, request, *args, **kwargs):
        messages.success(self.request, "✅ Année académique supprimée avec succès.")
        return super().delete(request, *args, **kwargs)


# ==============================================================================
# VUES ADDITIONNELLES (CLASS-BASED POUR ÉMARGEMENT)
# ==============================================================================

class EmargementCreateView(BaseAPView, CreateView):
    """Vue générique pour la création d'émargement (alternative)."""
    model = Emargement
    form_class = EmargementForm
    template_name = 'gestion_cours/emargement_form.html'
    success_url = reverse_lazy('gestion_cours:home')
    
    def form_valid(self, form):
        form.instance.emarge_par = self.request.user
        messages.success(self.request, "✅ Émargement enregistré avec succès.")
        return super().form_valid(form)


class EmargementSelectionCoursView(BaseAPView, ListView):
    """
    Vue de classe alternative pour la sélection de cours à émarger.
    Utilise les filtres et annotations.
    """
    model = MatiereProgrammee
    template_name = 'gestion_cours/emargement_selection_cours.html'
    context_object_name = 'cours_list'
    
    def get_queryset(self):
        annee_active = get_active_annee_academique()
        
        if not annee_active:
            messages.error(self.request, "Erreur : Aucune Année Académique active trouvée.")
            return MatiereProgrammee.objects.none()
        
        return MatiereProgrammee.objects.filter(
            annee_academique=annee_active
        ).select_related(
            'matiere', 'professeur', 'niveau', 'filiere'
        ).annotate(
            total_heures_faites=Sum('emargement__heure_eff')
        ).order_by('filiere__libelle', 'niveau__niv')