"""
VIEWS_CRUD.PY - Vues CRUD pour entités simples
(Professeur, Matiere, Filiere, Niveau, AnneeAcademique)
"""
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.shortcuts import render
from django.urls import reverse_lazy
from django.contrib import messages

# Import des modèles
from .models import Professeur, Matiere, Filiere, Niveau, AnneeAcademique
from .forms import ProfesseurForm, MatiereForm
from .filters_complete import ProfesseurFilter 

# Import des utilitaires et de la classe de base
from .views_dashboard import BaseAPView, paginate_queryset 
from .export_utils_complete import (
    export_professeurs_to_excel, export_professeurs_to_pdf
)


# ==============================================================================
# CRUD - PROFESSEURS
# ==============================================================================

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
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['list_url'] = 'gestion_cours:professeur_list'
        return context
    
    def delete(self, request, *args, **kwargs):
        messages.success(self.request, f"✅ Le professeur '{self.get_object()}' a été supprimé avec succès.")
        return super().delete(request, *args, **kwargs)


# ==============================================================================
# CRUD - MATIÈRES
# ==============================================================================

class MatiereListView(BaseAPView, ListView):
    model = Matiere
    template_name = 'gestion_cours/matiere_list.html'
    context_object_name = 'object_list'
    ordering = ['libelle']
    paginate_by = 10


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
    paginate_by = 10


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
    paginate_by = 10


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
    paginate_by = 10


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
