"""
VIEWS_COURS_MANAGEMENT.PY - Vues complexes
(MatiereProgrammee, Emargement, Evaluation, Historique)

🔧 CORRECTIONS APPORTÉES:
1. ✅ Pagination corrigée à 10 lignes (pas 20)
2. ✅ Filtres fonctionnels avec semestre
3. ✅ Utilisation correcte de page_obj dans toutes les vues paginées
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
from django.db import transaction

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
    export_emargements_to_excel as export_emargements_util,
    export_emargements_to_pdf as export_emargements_pdf_util,
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
# ÉMARGEMENTS - SÉLECTION DE COURS
# ==============================================================================

@login_required
def emargement_selection_view(request):
    """
    Sélection de cours pour émargement avec filtres.
    """
    annee_active = get_active_annee_academique()
    
    if not annee_active:
        messages.error(request, "Impossible d'afficher les cours : Aucune année académique active trouvée.")
        cours_queryset = MatiereProgrammee.objects.none()
    else:
        cours_queryset = MatiereProgrammee.objects.filter(
            annee_academique=annee_active
        ).select_related(
            'matiere', 'professeur', 'niveau', 'filiere'
        ).annotate(
            total_heures_faites=Sum('emargement__heure_eff')
        ).order_by('filiere__libelle', 'niveau__niv')
    
    # Appliquer les filtres
    cours_filter = CoursEmargementFilter(request.GET, queryset=cours_queryset)
    filtered_cours_list = cours_filter.qs
    
    # Convertir en liste et calculer la progression
    cours_with_progression = []
    for cours in filtered_cours_list:
        cours = calculer_progression(cours, date.today())
        cours.est_evalue = Evaluation.objects.filter(matiere_programmer=cours).exists()
        cours.peut_etre_evalue = (cours.progression_reelle >= 100) and not cours.est_evalue
        cours_with_progression.append(cours)
    
    context = {
        'filter': cours_filter,
        'cours_list': cours_with_progression,
    }
    return render(request, 'gestion_cours/emargement_selection_cours.html', context)


# ==============================================================================
# ÉMARGEMENTS - CRÉATION
# ==============================================================================

@login_required
def emargement_view(request, pk):
    """Gère l'affichage et la soumission du formulaire d'émargement."""
    matiere_prog = get_object_or_404(
        MatiereProgrammee.objects.annotate(
            total_heures_faites=Sum('emargement__heure_eff')
        ).select_related('matiere', 'professeur', 'niveau', 'filiere', 'annee_academique'),
        pk=pk
    )
    
    annee_active = get_active_annee_academique()
    if not annee_active:
        messages.error(request, "Impossible d'émarger : Aucune année académique active trouvée.")
        return redirect('gestion_cours:home')

    if matiere_prog.annee_academique != annee_active:
        messages.error(request, "Erreur : La matière sélectionnée n'est pas programmée pour l'année académique active.")
        return redirect('gestion_cours:home')

    volume_prevu = matiere_prog.nbr_heure
    heures_faites_actuelles = matiere_prog.total_heures_faites or Decimal('0.00')
    volume_prevant_decimal = Decimal(str(volume_prevu))
    volume_restant = volume_prevant_decimal - heures_faites_actuelles
    volume_restant = volume_restant.quantize(Decimal('0.01'))
    volume_restant_float = float(volume_restant)
    
    initial_data = {'date_emar': timezone.now().date()}
    form = EmargementForm(request.POST or None, initial=initial_data)

    context = {
        'matiere_prog': matiere_prog,
        'form': form,
        'volume_restant': volume_restant,
    }

    if request.method == 'POST':
        if form.is_valid():
            date_emar = form.cleaned_data['date_emar']
            heure_eff_saisie = float(form.cleaned_data['heure_eff'])

            if Emargement.objects.filter(matiere_programmer=matiere_prog, date_emar=date_emar).exists():
                messages.error(
                    request, 
                    f"❌ Échec de l'émargement : La matière {matiere_prog.matiere.libelle} "
                    f"a déjà été émargée à la date du {date_emar}."
                )
                return render(request, 'gestion_cours/emargement_form.html', context)

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
            
            emargement_obj = form.save(commit=False)
            emargement_obj.matiere_programmer = matiere_prog
            emargement_obj.emarge_par = request.user
            emargement_obj.save()
            
            messages.success(
                request, 
                f"✅ Séance d'émargement du {date_emar} (durée: {heure_eff_saisie:.2f}h) "
                f"enregistrée avec succès."
            )
            
            return redirect('gestion_cours:emargement_selection')
            
        else:
            messages.error(request, "❌ Erreur de formulaire. Veuillez vérifier les champs.")
            return render(request, 'gestion_cours/emargement_form.html', context)

    return render(request, 'gestion_cours/emargement_form.html', context)


# ==============================================================================
# ÉMARGEMENTS - MODIFICATION
# ==============================================================================

@login_required
@user_passes_test(est_administrateur_pedagogique, login_url=reverse_lazy('gestion_cours:home'))
def emargement_update_view(request, pk):
    """Modifie un émargement existant."""
    emargement = get_object_or_404(Emargement, pk=pk)
    matiere_prog = emargement.matiere_programmer
    
    # Calcul du volume restant (en tenant compte de l'émargement actuel)
    total_heures_faites = Emargement.objects.filter(
        matiere_programmer=matiere_prog
    ).exclude(pk=pk).aggregate(
        total=Sum('heure_eff')
    )['total'] or Decimal('0.00')
    
    volume_prevu = Decimal(str(matiere_prog.nbr_heure))
    volume_restant = volume_prevu - total_heures_faites
    volume_restant = volume_restant.quantize(Decimal('0.01'))
    volume_restant_float = float(volume_restant)
    
    form = EmargementForm(request.POST or None, instance=emargement)
    
    context = {
        'form': form,
        'matiere_prog': matiere_prog,
        'volume_restant': volume_restant,
        'emargement': emargement,
        'mode_edition': True,
    }
    
    if request.method == 'POST':
        if form.is_valid():
            date_emar = form.cleaned_data['date_emar']
            heure_eff_saisie = float(form.cleaned_data['heure_eff'])
            
            # Vérification d'unicité (en excluant l'émargement actuel)
            if Emargement.objects.filter(
                matiere_programmer=matiere_prog, 
                date_emar=date_emar
            ).exclude(pk=pk).exists():
                messages.error(
                    request, 
                    f"❌ Échec de la modification : Un autre émargement existe déjà pour cette date ({date_emar})."
                )
                return render(request, 'gestion_cours/emargement_form.html', context)
            
            # Validation des heures
            if heure_eff_saisie <= 0 or heure_eff_saisie > 8:
                messages.error(request, "❌ Erreur: La durée du cours doit être comprise entre 0 et 8 heures.")
                return render(request, 'gestion_cours/emargement_form.html', context)
            
            if heure_eff_saisie > volume_restant_float:
                messages.error(
                    request, 
                    f"❌ Échec de la modification : La durée saisie ({heure_eff_saisie:.2f}h) "
                    f"dépasse le volume restant ({volume_restant_float:.2f}h)."
                )
                return render(request, 'gestion_cours/emargement_form.html', context)
            
            form.save()
            messages.success(request, "✅ Émargement modifié avec succès.")
            return redirect('gestion_cours:historique_cours', pk=matiere_prog.pk)
        
        else:
            messages.error(request, "❌ Erreur de formulaire. Veuillez vérifier les champs.")
    
    return render(request, 'gestion_cours/emargement_form.html', context)


# ==============================================================================
# ÉMARGEMENTS - SUPPRESSION (AVEC CASCADE SUR ÉVALUATION)
# ==============================================================================

@login_required
@user_passes_test(est_administrateur_pedagogique, login_url=reverse_lazy('gestion_cours:home'))
def emargement_delete_view(request, pk):
    """Supprime un émargement."""
    emargement = get_object_or_404(Emargement, pk=pk)
    matiere_prog = emargement.matiere_programmer
    
    if request.method == 'POST':
        with transaction.atomic():
            # Supprimer l'émargement
            emargement.delete()
            
            # Recalculer la progression
            total_heures_faites = Emargement.objects.filter(
                matiere_programmer=matiere_prog
            ).aggregate(total=Sum('heure_eff'))['total'] or Decimal('0.00')
            
            volume_prevu = Decimal(str(matiere_prog.nbr_heure))
            progression = (float(total_heures_faites) / float(volume_prevu)) * 100 if volume_prevu > 0 else 0
            
            # Si progression < 100%, supprimer l'évaluation si elle existe
            if progression < 100:
                evaluations_supprimees = Evaluation.objects.filter(matiere_programmer=matiere_prog).delete()[0]
                if evaluations_supprimees > 0:
                    messages.warning(
                        request, 
                        f"⚠️ L'évaluation du cours a été supprimée automatiquement car la progression "
                        f"est passée sous 100% ({progression:.1f}%)."
                    )
            
            messages.success(request, "✅ Émargement supprimé avec succès.")
            return redirect('gestion_cours:historique_cours', pk=matiere_prog.pk)
    
    context = {
        'object': emargement,
        'list_url': 'gestion_cours:historique_cours',
        'list_url_pk': matiere_prog.pk,
    }
    return render(request, 'gestion_cours/emargement_confirm_delete.html', context)


# ==============================================================================
# 🔧 CORRECTION CRITIQUE: HISTORIQUE - GLOBAL (PAGINATION À 10 LIGNES)
# ==============================================================================

@login_required
@user_passes_test(est_administrateur_pedagogique, login_url=reverse_lazy('gestion_cours:home'))
def historique_view(request):
    """
    Affiche l'historique des émargements pour l'année académique active.
    🔧 CORRECTION: Pagination fonctionnelle à 10 lignes/page (pas 20)
    """
    annee_active = get_active_annee_academique()
    
    if not annee_active:
        messages.warning(request, "Impossible d'afficher l'historique : Aucune année académique active trouvée.")
        queryset = Emargement.objects.none()
    else:
        queryset = Emargement.objects.filter(
            matiere_programmer__annee_academique=annee_active
        ).select_related(
            'matiere_programmer__professeur', 
            'matiere_programmer__matiere',
            'matiere_programmer__filiere',
            'matiere_programmer__niveau',
        ).order_by('-date_emar')
    
    # 🔧 CORRECTION CLÉE: Appliquer les filtres PUIS la pagination
    emargement_filter = EmargementFilterComplete(request.GET, queryset=queryset)
    
    # 🔧 CORRECTION: Paginer à 10 lignes par page (pas 20)
    page_obj = paginate_queryset(request, emargement_filter.qs, items_per_page=10)
    
    context = {
        'page_obj': page_obj,  # 🔧 CORRECTION: Utiliser page_obj dans le template
        'historique': page_obj,  # Garder pour compatibilité
        'filter': emargement_filter,
        'annee_active': annee_active.annee_accademique if annee_active else 'N/A',
        'is_paginated': page_obj.has_other_pages() if hasattr(page_obj, 'has_other_pages') else False,
    }
    return render(request, 'gestion_cours/historique_global.html', context)


# ==============================================================================
# EXPORTS HISTORIQUE DES ÉMARGEMENTS
# ==============================================================================

@login_required
@user_passes_test(est_administrateur_pedagogique, login_url=reverse_lazy('gestion_cours:home'))
def export_emargements_to_excel(request):
    """Vue wrapper pour l'export Excel de l'historique des émargements."""
    annee_active = get_active_annee_academique()
    
    if not annee_active:
        messages.error(request, "Impossible d'exporter : Aucune Année Académique active trouvée.")
        return redirect('gestion_cours:home')

    queryset = Emargement.objects.filter(
        matiere_programmer__annee_academique=annee_active
    ).select_related(
        'matiere_programmer__professeur', 
        'matiere_programmer__matiere',
    ).order_by('-date_emar')

    emargement_filter = EmargementFilterComplete(request.GET, queryset=queryset)
    filtered_qs = emargement_filter.qs
    
    return export_emargements_util(filtered_qs)


@login_required
@user_passes_test(est_administrateur_pedagogique, login_url=reverse_lazy('gestion_cours:home'))
def export_emargements_to_pdf(request):
    """Vue wrapper pour l'export PDF de l'historique des émargements."""
    annee_active = get_active_annee_academique()
    
    if not annee_active:
        messages.error(request, "Impossible d'exporter : Aucune Année Académique active trouvée.")
        return redirect('gestion_cours:home')

    queryset = Emargement.objects.filter(
        matiere_programmer__annee_academique=annee_active
    ).select_related(
        'matiere_programmer__professeur', 
        'matiere_programmer__matiere',
    ).order_by('-date_emar')

    emargement_filter = EmargementFilterComplete(request.GET, queryset=queryset)
    filtered_qs = emargement_filter.qs
    
    return export_emargements_pdf_util(filtered_qs)


# ==============================================================================
# HISTORIQUE - PAR COURS
# ==============================================================================

@login_required
@user_passes_test(est_administrateur_pedagogique, login_url=reverse_lazy('gestion_cours:home'))
def historique_cours_view(request, pk):
    """Affiche l'historique détaillé des émargements pour un cours programmé spécifique."""
    matiere_prog = get_object_or_404(
        MatiereProgrammee.objects.select_related(
            'matiere', 'professeur', 'niveau', 'filiere', 'annee_academique'
        ).annotate(
            total_heures_faites=Sum('emargement__heure_eff')
        ), 
        pk=pk
    )
    
    historique_emargement_list = Emargement.objects.filter(
        matiere_programmer=matiere_prog
    ).order_by('-date_emar')

    progression_details = calculer_progression(matiere_prog, date.today())
    
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
# ÉVALUATIONS - LISTE
# ==============================================================================

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
# ÉVALUATIONS - CRÉATION
# ==============================================================================

@method_decorator(login_required, name='dispatch')
class EvaluationManagementView(BaseAPView, CreateView):
    """Permet à l'AP d'ajouter l'évaluation qualitative d'un cours complété (100%)."""
    model = Evaluation
    form_class = EvaluationForm
    template_name = 'gestion_cours/evaluation_form.html'
    success_url = reverse_lazy('gestion_cours:evaluation_list')

    def dispatch(self, request, *args, **kwargs):
        self.matiere_prog = get_object_or_404(MatiereProgrammee, pk=kwargs.get('pk'))
        
        total_faites = Emargement.objects.filter(
            matiere_programmer=self.matiere_prog
        ).aggregate(total_faites=Sum('heure_eff'))['total_faites'] or 0
        
        volume_prevu = float(self.matiere_prog.nbr_heure)
        progression = (float(total_faites) / volume_prevu) * 100 if volume_prevu > 0 else 0

        if progression < 100:
            messages.error(request, "❌ Impossible d'évaluer : le cours n'a pas atteint 100% de progression.")
            return redirect('gestion_cours:emargement_selection')

        try:
            self.existing_evaluation = Evaluation.objects.get(matiere_programmer=self.matiere_prog)
            messages.warning(
                request, 
                f"ℹ️ Une évaluation existe déjà pour ce cours."
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
        context['mode_edition'] = False
        
        total_faites = Emargement.objects.filter(
            matiere_programmer=self.matiere_prog
        ).aggregate(total_faites=Sum('heure_eff'))['total_faites'] or 0
        
        volume_prevu = float(self.matiere_prog.nbr_heure)
        context['progression'] = (float(total_faites) / volume_prevu) * 100 if volume_prevu > 0 else 0
        
        return context


# ==============================================================================
# ÉVALUATIONS - MODIFICATION
# ==============================================================================

@login_required
@user_passes_test(est_administrateur_pedagogique, login_url=reverse_lazy('gestion_cours:home'))
def evaluation_update_view(request, pk):
    """Modifie une évaluation existante."""
    evaluation = get_object_or_404(Evaluation, pk=pk)
    matiere_prog = evaluation.matiere_programmer
    
    form = EvaluationForm(request.POST or None, instance=evaluation)
    
    context = {
        'form': form,
        'matiere_prog': matiere_prog,
        'evaluation': evaluation,
        'mode_edition': True,
    }
    
    if request.method == 'POST':
        if form.is_valid():
            form.save()
            messages.success(request, "✅ Évaluation modifiée avec succès.")
            return redirect('gestion_cours:evaluation_list')
        else:
            messages.error(request, "❌ Erreur de formulaire. Veuillez vérifier les champs.")
    
    return render(request, 'gestion_cours/evaluation_form.html', context)


# ==============================================================================
# ÉVALUATIONS - SUPPRESSION
# ==============================================================================

@login_required
@user_passes_test(est_administrateur_pedagogique, login_url=reverse_lazy('gestion_cours:home'))
def evaluation_delete_view(request, pk):
    """Supprime une évaluation existante."""
    evaluation = get_object_or_404(Evaluation, pk=pk)
    matiere_prog = evaluation.matiere_programmer
    
    if request.method == 'POST':
        evaluation.delete()
        messages.success(request, "✅ Évaluation supprimée avec succès.")
        return redirect('gestion_cours:evaluation_list')
    
    context = {
        'object': evaluation,
        'list_url': 'gestion_cours:evaluation_list',
    }
    return render(request, 'gestion_cours/evaluation_confirm_delete.html', context)
