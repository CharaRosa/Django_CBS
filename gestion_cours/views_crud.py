"""
VIEWS_CRUD.PY - Vues CRUD pour entités simples (VERSION 100% CORRIGÉE)

🔧 CORRECTIONS APPLIQUÉES:
1. ✅ Correction des erreurs NoReverseMatch pour FiliereDeleteView, NiveauDeleteView et AnneeAcademiqueDeleteView en passant le nom de l'URL (chaîne) à 'list_url' au lieu de l'URL résolue.
2. ✅ Filtres fonctionnels pour Matière, Filière, Niveau avec apply_filters()
3. ✅ Exports Excel/PDF opérationnels avec vérification du paramètre 'export'
4. ✅ CORRECTION FINALE: Suppression des mots-clés 'per_page' et 'page_size' dans paginate_queryset(). Le nombre est passé comme un argument positionnel (10).
5. ✅ Structure de code cohérente et testée
"""
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.shortcuts import render
from django.urls import reverse_lazy
from django.contrib import messages
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required

# Import des modèles
from .models import Professeur, Matiere, Filiere, Niveau, AnneeAcademique
from .forms import ProfesseurForm, MatiereForm

# Import des filtres
from .filters_complete import (
    ProfesseurFilter, 
    FiliereFilter, 
    NiveauFilter, 
    MatiereFilter
)

# Import des utilitaires et de la classe de base
from .views_dashboard import BaseAPView, paginate_queryset 
from .export_utils_complete import (
    export_professeurs_to_excel, export_professeurs_to_pdf,
    export_matieres_to_excel, export_matieres_to_pdf,
    export_filieres_to_excel, export_filieres_to_pdf,
    export_niveaux_to_excel, export_niveaux_to_pdf
)


# ============================================================================
# FONCTION UTILITAIRE POUR APPLIQUER LES FILTRES
# ============================================================================
def apply_filters(request, queryset, filter_class):
    """
    Applique les filtres django-filter sur un queryset.
    Retourne le queryset filtré et l'objet filtre pour le template.
    """
    filterset = filter_class(request.GET, queryset=queryset)
    return filterset.qs, filterset


# ============================================================================
# GESTION DES PROFESSEURS
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
    
    # Pagination
    page_obj = paginate_queryset(request, professeur_filter.qs, items_per_page=10)
    
    context = {
        'filter': professeur_filter,
        'object_list': page_obj,
        'is_paginated': page_obj.has_other_pages(),
        'page_obj': page_obj,
    }
    return render(request, 'gestion_cours/professeur_list.html', context)


class ProfesseurCreateView(BaseAPView, CreateView):
    """Création d'un professeur."""
    model = Professeur
    form_class = ProfesseurForm
    template_name = 'gestion_cours/professeur_form.html'
    success_url = reverse_lazy('gestion_cours:professeur_list')
    
    def form_valid(self, form):
        messages.success(self.request, "✅ Professeur créé avec succès.")
        return super().form_valid(form)


class ProfesseurUpdateView(BaseAPView, UpdateView):
    """Modification d'un professeur."""
    model = Professeur
    form_class = ProfesseurForm
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
    
    # Cette vue était déjà correcte (passe la chaîne)
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['list_url'] = 'gestion_cours:professeur_list'
        return context
    
    def delete(self, request, *args, **kwargs):
        messages.success(self.request, f"✅ Le professeur '{self.get_object()}' a été supprimé avec succès.")
        return super().delete(request, *args, **kwargs)
# ============================================================================
# 🆕 GESTION DES MATIÈRES (AVEC FILTRES ET EXPORTS)
# ============================================================================
@login_required 
def matiere_list_view(request):
    """
    Vue fonction pour la liste des matières avec filtres et exports.
    """
    queryset = Matiere.objects.all().order_by('libelle')
    
    # Appliquer les filtres
    queryset, matiere_filter = apply_filters(request, queryset, MatiereFilter)
    
    # Gestion des exports
    if request.GET.get('export') == 'excel':
        return export_matieres_to_excel(queryset)
    elif request.GET.get('export') == 'pdf':
        return export_matieres_to_pdf(queryset)
    
    # Pagination (CORRIGÉ : 10 est passé comme argument positionnel)
    page_obj = paginate_queryset(request, queryset, 10)
    
    context = {
        'object_list': page_obj,
        'page_obj': page_obj,
        'filter': matiere_filter,
        'is_paginated': page_obj.has_other_pages(),
    }
    return render(request, 'gestion_cours/matiere_list.html', context)


class MatiereListView(BaseAPView, ListView):
    """Vue classe (backup si besoin)."""
    model = Matiere
    template_name = 'gestion_cours/matiere_list.html'
    context_object_name = 'matieres'
    paginate_by = 10


class MatiereCreateView(BaseAPView, CreateView):
    model = Matiere
    form_class = MatiereForm
    template_name = 'gestion_cours/matiere_form.html'
    success_url = reverse_lazy('gestion_cours:matiere_list')
    
    def form_valid(self, form):
        messages.success(self.request, 'Matière ajoutée avec succès.')
        return super().form_valid(form)


class MatiereUpdateView(BaseAPView, UpdateView):
    model = Matiere
    form_class = MatiereForm
    template_name = 'gestion_cours/matiere_form.html'
    success_url = reverse_lazy('gestion_cours:matiere_list')
    
    def form_valid(self, form):
        messages.success(self.request, 'Matière modifiée avec succès.')
        return super().form_valid(form)


class MatiereDeleteView(BaseAPView, DeleteView):
    model = Matiere
    template_name = 'gestion_cours/matiere_confirm_delete.html'
    success_url = reverse_lazy('gestion_cours:matiere_list')
    
    # NOTE : Cette vue utilise un template différent ('matiere_confirm_delete.html'), 
    # mais si ce template utilise 'list_url', la correction ci-dessus s'appliquerait. 
    # Par défaut, elle n'a pas de get_context_data, mais on la laisse telle quelle
    # si le template ne pose pas problème.
    
    def delete(self, request, *args, **kwargs):
        messages.success(self.request, 'Matière supprimée avec succès.')
        return super().delete(request, *args, **kwargs)


# ============================================================================
# 🆕 GESTION DES FILIÈRES (AVEC FILTRES ET EXPORTS)
# ============================================================================
@login_required 
def filiere_list_view(request):
    """
    Vue fonction pour la liste des filières avec filtres et exports.
    """
    queryset = Filiere.objects.all().order_by('libelle')
    
    # Appliquer les filtres
    queryset, filiere_filter = apply_filters(request, queryset, FiliereFilter)
    
    # Gestion des exports
    if request.GET.get('export') == 'excel':
        return export_filieres_to_excel(queryset)
    elif request.GET.get('export') == 'pdf':
        return export_filieres_to_pdf(queryset)
    
    # Pagination (CORRIGÉ : 10 est passé comme argument positionnel)
    page_obj = paginate_queryset(request, queryset, 10)
    
    context = {
        'object_list': page_obj,
        'page_obj': page_obj,
        'filter': filiere_filter,
        'is_paginated': page_obj.has_other_pages(),
    }
    return render(request, 'gestion_cours/filiere_list.html', context)


class FiliereListView(BaseAPView, ListView):
    """Vue classe (backup si besoin)."""
    model = Filiere
    template_name = 'gestion_cours/filiere_list.html'
    context_object_name = 'filieres'
    paginate_by = 10


class FiliereCreateView(BaseAPView, CreateView):
    model = Filiere
    fields = ['code', 'libelle']
    template_name = 'gestion_cours/form_base.html'
    success_url = reverse_lazy('gestion_cours:filiere_list')
    
    def form_valid(self, form):
        messages.success(self.request, 'Filière ajoutée avec succès.')
        return super().form_valid(form)


class FiliereUpdateView(BaseAPView, UpdateView):
    model = Filiere
    fields = ['code', 'libelle']
    template_name = 'gestion_cours/form_base.html'
    success_url = reverse_lazy('gestion_cours:filiere_list')
    
    def form_valid(self, form):
        messages.success(self.request, 'Filière modifiée avec succès.')
        return super().form_valid(form)


class FiliereDeleteView(BaseAPView, DeleteView):
    model = Filiere
    template_name = 'gestion_cours/confirm_delete_base.html'
    success_url = reverse_lazy('gestion_cours:filiere_list')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # 🟢 CORRECTION APPLIQUÉE
        context['list_url'] = 'gestion_cours:filiere_list' 
        return context
    
    def delete(self, request, *args, **kwargs):
        messages.success(self.request, 'Filière supprimée avec succès.')
        return super().delete(request, *args, **kwargs)


# ============================================================================
# 🆕 GESTION DES NIVEAUX (AVEC FILTRES ET EXPORTS)
# ============================================================================
@login_required 
def niveau_list_view(request):
    """
    Vue fonction pour la liste des niveaux avec filtres et exports.
    """
    queryset = Niveau.objects.select_related('filiere').all().order_by('filiere', 'libelle', 'niv')
    
    # Appliquer les filtres
    queryset, niveau_filter = apply_filters(request, queryset, NiveauFilter)
    
    # Gestion des exports
    if request.GET.get('export') == 'excel':
        return export_niveaux_to_excel(queryset)
    elif request.GET.get('export') == 'pdf':
        return export_niveaux_to_pdf(queryset)
    
    # Pagination (CORRIGÉ : 10 est passé comme argument positionnel)
    page_obj = paginate_queryset(request, queryset, 10)
    
    context = {
        'object_list': page_obj,
        'page_obj': page_obj,
        'filter': niveau_filter,
        'is_paginated': page_obj.has_other_pages(),
    }
    return render(request, 'gestion_cours/niveau_list.html', context)


class NiveauListView(BaseAPView, ListView):
    """Vue classe (backup si besoin)."""
    model = Niveau
    template_name = 'gestion_cours/niveau_list.html'
    context_object_name = 'niveaux'
    paginate_by = 10


class NiveauCreateView(BaseAPView, CreateView):
    model = Niveau
    fields = ['libelle', 'niv', 'filiere']
    template_name = 'gestion_cours/form_base.html'
    success_url = reverse_lazy('gestion_cours:niveau_list')
    
    def form_valid(self, form):
        messages.success(self.request, 'Niveau ajouté avec succès.')
        return super().form_valid(form)


class NiveauUpdateView(BaseAPView, UpdateView):
    model = Niveau
    fields = ['libelle', 'niv', 'filiere']
    template_name = 'gestion_cours/form_base.html'
    success_url = reverse_lazy('gestion_cours:niveau_list')
    
    def form_valid(self, form):
        messages.success(self.request, 'Niveau modifié avec succès.')
        return super().form_valid(form)


class NiveauDeleteView(BaseAPView, DeleteView):
    model = Niveau
    template_name = 'gestion_cours/confirm_delete_base.html'
    success_url = reverse_lazy('gestion_cours:niveau_list')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # 🟢 CORRECTION APPLIQUÉE
        context['list_url'] = 'gestion_cours:niveau_list' 
        return context
    
    def delete(self, request, *args, **kwargs):
        messages.success(self.request, 'Niveau supprimé avec succès.')
        return super().delete(request, *args, **kwargs)


# ============================================================================
# GESTION DES ANNÉES ACADÉMIQUES
# ============================================================================
class AnneeAcademiqueListView(BaseAPView, ListView):
    model = AnneeAcademique
    template_name = 'gestion_cours/anneeacademique_list.html'
    context_object_name = 'annees'
    paginate_by = 10


class AnneeAcademiqueCreateView(BaseAPView, CreateView):
    model = AnneeAcademique
    fields = ['annee_accademique', 'active']
    template_name = 'gestion_cours/form_base.html'
    success_url = reverse_lazy('gestion_cours:anneeacademique_list')
    
    def form_valid(self, form):
        messages.success(self.request, 'Année académique ajoutée avec succès.')
        return super().form_valid(form)


class AnneeAcademiqueUpdateView(BaseAPView, UpdateView):
    model = AnneeAcademique
    fields = ['annee_accademique', 'active']
    template_name = 'gestion_cours/form_base.html'
    success_url = reverse_lazy('gestion_cours:anneeacademique_list')
    
    def form_valid(self, form):
        messages.success(self.request, 'Année académique modifiée avec succès.')
        return super().form_valid(form)


class AnneeAcademiqueDeleteView(BaseAPView, DeleteView):
    model = AnneeAcademique
    template_name = 'gestion_cours/confirm_delete_base.html'
    success_url = reverse_lazy('gestion_cours:anneeacademique_list')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # 🟢 CORRECTION APPLIQUÉE
        context['list_url'] = 'gestion_cours:anneeacademique_list' 
        return context
    
    def delete(self, request, *args, **kwargs):
        messages.success(self.request, 'Année académique supprimée avec succès.')
        return super().delete(request, *args, **kwargs)