"""
VIEWS_COURS_MANAGEMENT.PY - Vues complexes
(MatiereProgrammee, Emargement, Evaluation, Historique)

CORRECTIONS IMPLÉMENTÉES:
1. Messages d'erreur d'émargement affichés dans emargement_form.html
2. Évaluation - 3 colonnes complètes
3. Bouton évaluation après 100% de progression
4. Bouton historique par cours dans emargement_selection
5. Pagination pour historique_view
6. Pas de modification possible des évaluations existantes
7. FIX ATTRIBUTE ERROR: Ajout des vues wrapper pour export_emargements_to_excel/pdf
8. FIX IMPORTERROR: Réintégration de la fonction emargement_view.
"""
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Sum, F, Q, Count
from django.contrib import messages
from django.urls import reverse_lazy
from django.contrib.auth.decorators import login_required, user_passes_test
from django.utils.decorators import method_decorator
from decimal import Decimal
from datetime import date
from django.utils import timezone
from django.http import HttpResponse

# Import des modèles, formes et filtres
from .models import MatiereProgrammee, Emargement, Evaluation
from .forms import EmargementForm, EvaluationForm, MatiereProgrammeeForm
from .filters_complete import (
    MatiereProgrammeeFilter, CoursEmargementFilter, 
    EmargementFilterComplete, EvaluationFilter
)

# Import des utilitaires et de la classe de base
from .views_dashboard import (
    BaseAPView, get_active_annee_academique, paginate_queryset
)
from .utils import calculer_progression
from .export_utils_complete import (
    export_cours_to_excel, export_cours_to_pdf,
    export_emargements_to_excel as export_emargements_util, # FIX: Renommé
    export_emargements_to_pdf as export_emargements_pdf_util, # FIX: Renommé
    export_evaluations_to_excel, export_evaluations_to_pdf
)


# ==============================================================================
# UTILITAIRE POUR VÉRIFICATIONS
# ==============================================================================

def est_administrateur_pedagogique(user):
    """Vérifie si l'utilisateur est AP ou superuser."""
    return user.groups.filter(name='Assistant').exists() or user.is_superuser


# ==============================================================================
# CRUD - MATIÈRES PROGRAMMÉES (COURS)
# ==============================================================================

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

# ==============================================================================
# ÉMARGEMENTS - SÉLECTION DE COURS (AVEC CORRECTION: BOUTON HISTORIQUE + ÉVALUATION)
# ==============================================================================

@login_required
def emargement_selection_cours(request):
    """
    Sélection de cours pour émargement avec filtres.
    CORRECTION: Application du filtre sur le QuerySet avant de calculer la progression.
    """
    annee_active = get_active_annee_academique()
    
    if not annee_active:
        messages.error(request, "Impossible d'afficher les cours : Aucune année académique active trouvée.")
        cours_queryset = MatiereProgrammee.objects.none()
    else:
        # Annoter avec le total des heures faites (QuerySet)
        cours_queryset = MatiereProgrammee.objects.filter(
            annee_academique=annee_active
        ).select_related(
            'matiere', 'professeur', 'niveau', 'filiere'
        ).annotate(
            total_heures_faites=Sum('emargement__heure_eff')
        ).order_by('filiere__libelle', 'niveau__niv')
        
    
    # 1. APPLIQUER LES FILTRES SUR LE QUERYSET AVANT LA CONVERSION EN LISTE
    cours_filter = CoursEmargementFilter(request.GET, queryset=cours_queryset)
    
    # Récupérer les résultats filtrés (toujours un QuerySet ou un QuerySet vide)
    filtered_cours_list = cours_filter.qs
    
    # 2. CONVERTIR EN LISTE ET CALCULER LA PROGRESSION (seulement sur les résultats filtrés)
    cours_with_progression = []
    for cours in filtered_cours_list:
        cours = calculer_progression(cours, date.today())
        
        # Vérifier si le cours est déjà évalué
        cours.est_evalue = Evaluation.objects.filter(matiere_programmer=cours).exists()
        
        # Déterminer si le cours peut être évalué (100% et pas encore évalué)
        cours.peut_etre_evalue = (cours.progression_reelle >= 100) and not cours.est_evalue
        
        cours_with_progression.append(cours)
    
    # La liste finale à passer au template
    final_cours_list = cours_with_progression
    
    context = {
        'filter': cours_filter,
        # Passer la LISTE augmentée au template, mais le filtre a été créé avec le QuerySet
        'cours_list': final_cours_list, 
    }
    return render(request, 'gestion_cours/emargement_selection_cours.html', context)


# ==============================================================================
# ÉMARGEMENTS - FORMULAIRE (FONCTION MANQUANTE RÉINSÉRÉE)
# ==============================================================================

@login_required
def emargement_view(request, pk):
    """
    Gère l'affichage et la soumission du formulaire d'émargement.
    CORRECTION: Les messages d'erreur s'affichent dans le formulaire, pas dans la page de sélection.
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
    # Assurez-vous que total_heures_faites est traité comme Decimal
    heures_faites_actuelles = matiere_prog.total_heures_faites or Decimal('0.00')
    
    volume_prevant_decimal = Decimal(str(volume_prevu))
    volume_restant = volume_prevant_decimal - heures_faites_actuelles
    volume_restant = volume_restant.quantize(Decimal('0.01'))
    volume_restant_float = float(volume_restant) # Nécessaire pour les comparaisons float dans le corps de la vue
    
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
                    f"❌ Échec de l'émargement : La matière {matiere_prog.matiere.libelle} "
                    f"a déjà été émargée à la date du {date_emar}."
                )
                return render(request, 'gestion_cours/emargement_form.html', context)

            # --- VALIDATION DES HEURES ---
            if heure_eff_saisie <= 0 or heure_eff_saisie > 8:
                messages.error(request, "❌ Erreur: La durée du cours doit être comprise entre 0 et 8 heures.")
                return render(request, 'gestion_cours/emargement_form.html', context)

            if volume_restant_float <= 0:
                messages.error(
                    request, 
                    f"❌ Échec de l'émargement : Le volume horaire prévu de {volume_prevu}h "
                    f"est déjà atteint ou dépassé ({heures_faites_actuelles:.2f}h)."
                )
                return render(request, 'gestion_cours/emargement_form.html', context)

            if heure_eff_saisie > volume_restant_float:
                messages.error(
                    request, 
                    f"❌ Échec de l'émargement : La durée saisie ({heure_eff_saisie:.2f}h) "
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
                f"✅ Séance d'émargement du {date_emar} (durée: {heure_eff_saisie:.2f}h) "
                f"enregistrée avec succès."
            )
            
            return redirect('gestion_cours:emargement_selection')
            
        else:
            # Formulaire invalide
            messages.error(request, "❌ Erreur de formulaire. Veuillez vérifier les champs.")
            return render(request, 'gestion_cours/emargement_form.html', context)

    # 7. Affichage GET
    return render(request, 'gestion_cours/emargement_form.html', context)

# ==============================================================================
# HISTORIQUE - GLOBAL (AVEC CORRECTION: PAGINATION)
# ==============================================================================

@login_required
@user_passes_test(est_administrateur_pedagogique, login_url=reverse_lazy('gestion_cours:home'))
def historique_view(request):
    """
    Affiche l'historique des émargements pour l'année académique active.
    CORRECTION: Pagination ajoutée.
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
        
        # CORRECTION: Pagination ajoutée (20 éléments par page)
        page_obj = paginate_queryset(request, emargement_filter.qs, items_per_page=20)
        historique = page_obj
    
    context = {
        'historique': historique,
        'filter': emargement_filter,
        'annee_active': annee_active.annee_accademique if annee_active else 'N/A',
        'is_paginated': historique.has_other_pages() if hasattr(historique, 'has_other_pages') else False,
        'page_obj': historique,
    }
    return render(request, 'gestion_cours/historique_global.html', context)


# ==============================================================================
# EXPORTS HISTORIQUE DES ÉMARGEMENTS (CORRECTION: VUES DE WRAPPER)
# ==============================================================================

@login_required
@user_passes_test(est_administrateur_pedagogique, login_url=reverse_lazy('gestion_cours:home'))
def export_emargements_to_excel(request):
    """
    Vue wrapper pour l'export Excel de l'historique des émargements.
    Cette fonction est désormais référencée dans urls.py pour résoudre l'AttributeError.
    """
    annee_active = get_active_annee_academique()
    
    if not annee_active:
        messages.error(request, "Impossible d'exporter : Aucune Année Académique active trouvée.")
        return redirect('gestion_cours:home')

    # Base du QuerySet (filtré par année active)
    queryset = Emargement.objects.filter(
        matiere_programmer__annee_academique=annee_active
    ).select_related(
        'matiere_programmer__professeur', 
        'matiere_programmer__matiere',
    ).order_by('-date_emar')

    # Appliquer les filtres
    emargement_filter = EmargementFilterComplete(request.GET, queryset=queryset)
    filtered_qs = emargement_filter.qs
    
    # Appeler la fonction utilitaire renommée (export_emargements_util)
    return export_emargements_util(filtered_qs)


@login_required
@user_passes_test(est_administrateur_pedagogique, login_url=reverse_lazy('gestion_cours:home'))
def export_emargements_to_pdf(request):
    """
    Vue wrapper pour l'export PDF de l'historique des émargements.
    Cette fonction est désormais référencée dans urls.py pour résoudre l'AttributeError.
    """
    annee_active = get_active_annee_academique()
    
    if not annee_active:
        messages.error(request, "Impossible d'exporter : Aucune Année Académique active trouvée.")
        return redirect('gestion_cours:home')

    # Base du QuerySet (filtré par année active)
    queryset = Emargement.objects.filter(
        matiere_programmer__annee_academique=annee_active
    ).select_related(
        'matiere_programmer__professeur', 
        'matiere_programmer__matiere',
    ).order_by('-date_emar')

    # Appliquer les filtres
    emargement_filter = EmargementFilterComplete(request.GET, queryset=queryset)
    filtered_qs = emargement_filter.qs
    
    # Appeler la fonction utilitaire renommée (export_emargements_pdf_util)
    return export_emargements_pdf_util(filtered_qs)


# ==============================================================================
# HISTORIQUE - PAR COURS (ACCESSIBLE DEPUIS EMARGEMENT_SELECTION)
# ==============================================================================

@login_required
@user_passes_test(est_administrateur_pedagogique, login_url=reverse_lazy('gestion_cours:home'))
def historique_cours_view(request, pk):
    """
    Affiche l'historique détaillé des émargements pour un cours programmé spécifique.
    CORRECTION: Accessible via bouton dans emargement_selection_cours.html
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
    ).order_by('-date_emar')

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


# ==============================================================================
# ÉVALUATIONS - LISTE (AVEC CORRECTION: 3 COLONNES)
# ==============================================================================

@login_required
def evaluation_list_view(request):
    """
    Liste des évaluations avec filtres et exports.
    CORRECTION: Affiche les 3 colonnes (resume_evaluation, appreciation_ap, recommandations)
    """
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
    
    # Gestion des exports (avec 3 colonnes)
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


# ==============================================================================
# ÉVALUATIONS - CRÉATION/MODIFICATION (AVEC CORRECTION: PAS DE MODIFICATION)
# ==============================================================================

@method_decorator(login_required, name='dispatch')
class EvaluationManagementView(BaseAPView, CreateView):
    """
    Permet à l'AP d'ajouter l'évaluation qualitative d'un cours complété (100%).
    CORRECTION: 
    - Changé de UpdateView à CreateView (pas de modification possible)
    - Formulaire en lecture seule si évaluation existe déjà
    - Affiche les 3 colonnes complètes
    """
    model = Evaluation
    form_class = EvaluationForm
    template_name = 'gestion_cours/evaluation_form.html'
    success_url = reverse_lazy('gestion_cours:evaluation_list')

    def dispatch(self, request, *args, **kwargs):
        # Récupération de la MatiereProgrammee
        self.matiere_prog = get_object_or_404(MatiereProgrammee, pk=kwargs.get('pk'))
        
        # Vérification 100% de progression
        total_faites = Emargement.objects.filter(
            matiere_programmer=self.matiere_prog
        ).aggregate(total_faites=Sum('heure_eff'))['total_faites'] or 0
        
        volume_prevu = float(self.matiere_prog.nbr_heure)
        progression = (float(total_faites) / volume_prevu) * 100 if volume_prevu > 0 else 0

        if progression < 100:
            messages.error(request, "❌ Impossible d'évaluer : le cours n'a pas atteint 100% de progression.")
            return redirect('gestion_cours:emargement_selection')

        # CORRECTION: Vérifier si une évaluation existe déjà
        try:
            self.existing_evaluation = Evaluation.objects.get(matiere_programmer=self.matiere_prog)
            # Une évaluation existe déjà, redirection vers la liste
            messages.warning(
                request, 
                f"ℹ️ Une évaluation existe déjà pour ce cours. Les évaluations ne peuvent pas être modifiées."
            )
            return redirect('gestion_cours:evaluation_list')
        except Evaluation.DoesNotExist:
            self.existing_evaluation = None

        return super().dispatch(request, *args, **kwargs)

    def get_initial(self):
        initial = super().get_initial()
        initial['matiere_programmer'] = self.matiere_prog
        return initial

    def form_valid(self, form):
        evaluation = form.save(commit=False)
        evaluation.matiere_programmer = self.matiere_prog
        evaluation.utilisateur_evaluation = self.request.user
        evaluation.save()
        
        messages.success(
            self.request, 
            f"✅ Évaluation qualitative enregistrée pour {self.matiere_prog.matiere.libelle}!"
        )
        return redirect('gestion_cours:evaluation_list')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['matiere_prog'] = self.matiere_prog
        context['mode_edition'] = False  # Toujours False car pas de modification
        
        # Calcul de la progression pour l'affichage
        total_faites = Emargement.objects.filter(
            matiere_programmer=self.matiere_prog
        ).aggregate(total_faites=Sum('heure_eff'))['total_faites'] or 0
        
        volume_prevu = float(self.matiere_prog.nbr_heure)
        context['progression'] = (float(total_faites) / volume_prevu) * 100 if volume_prevu > 0 else 0
        
        return context