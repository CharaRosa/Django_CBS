"""
FILTERS_COMPLETE.PY - Filtres de recherche pour toutes les vues

🔧 CORRECTIONS APPORTÉES:
1. ✅ Ajout du filtre SEMESTRE sur tous les filtres de cours/émargements/évaluations
2. ✅ Correction du filtre CoursEmargementFilter avec tous les champs nécessaires
3. ✅ Ajout de field_name correct pour les relations ForeignKey
"""

import django_filters
from django import forms
from .models import (
    Professeur, MatiereProgrammee, Emargement, Evaluation,
    Filiere, Niveau, Matiere, AnneeAcademique
)


# ============= FILTRE POUR PROFESSEURS =============
class ProfesseurFilter(django_filters.FilterSet):
    """Filtres pour la liste des professeurs."""
    
    nom = django_filters.CharFilter(
        field_name='nom',
        lookup_expr='icontains',
        label='Nom',
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Rechercher par nom...'})
    )
    
    prenoms = django_filters.CharFilter(
        field_name='prenoms',
        lookup_expr='icontains',
        label='Prénoms',
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Rechercher par prénoms...'})
    )
    
    email = django_filters.CharFilter(
        field_name='email',
        lookup_expr='icontains',
        label='Email',
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Rechercher par email...'})
    )
    
    contact = django_filters.CharFilter(
        field_name='contact',
        lookup_expr='icontains',
        label='Contact',
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Rechercher par contact...'})
    )
    
    class Meta:
        model = Professeur
        fields = ['nom', 'prenoms', 'email', 'contact']


# ============= FILTRE POUR MATIÈRES =============
class MatiereFilter(django_filters.FilterSet):
    """Filtres pour la liste des matières."""
    
    code = django_filters.CharFilter(
        field_name='code',
        lookup_expr='icontains',
        label='Code',
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Code de la matière...'})
    )
    
    libelle = django_filters.CharFilter(
        field_name='libelle',
        lookup_expr='icontains',
        label='Libellé',
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nom de la matière...'})
    )
    
    class Meta:
        model = Matiere
        fields = ['code', 'libelle']


# ============= FILTRE POUR FILIÈRES =============
class FiliereFilter(django_filters.FilterSet):
    """Filtres pour la liste des filières."""
    
    code = django_filters.CharFilter(
        field_name='code',
        lookup_expr='icontains',
        label='Code',
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Code de la filière...'})
    )
    
    libelle = django_filters.CharFilter(
        field_name='libelle',
        lookup_expr='icontains',
        label='Libellé',
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nom de la filière...'})
    )
    
    class Meta:
        model = Filiere
        fields = ['code', 'libelle']


# ============= FILTRE POUR NIVEAUX =============
class NiveauFilter(django_filters.FilterSet):
    """Filtres pour la liste des niveaux."""
    
    libelle = django_filters.CharFilter(
        field_name='libelle',
        lookup_expr='icontains',
        label='Libellé',
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nom du niveau...'})
    )
    
    niv = django_filters.CharFilter(
        field_name='niv',
        lookup_expr='icontains',
        label='Code niveau',
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'L1, L2, M1...'})
    )
    
    filiere = django_filters.ModelChoiceFilter(
        queryset=Filiere.objects.all(),
        label='Filière',
        empty_label='Toutes les filières',
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    class Meta:
        model = Niveau
        fields = ['libelle', 'niv', 'filiere']


# ============= 🔧 CORRECTION: FILTRE POUR COURS PROGRAMMÉS (AVEC SEMESTRE) =============
class MatiereProgrammeeFilter(django_filters.FilterSet):
    """
    Filtres pour la liste des cours programmés.
    🔧 CORRECTION: Ajout du filtre SEMESTRE
    """
    
    matiere = django_filters.ModelChoiceFilter(
        queryset=Matiere.objects.all(),
        label='Matière',
        empty_label='Toutes les matières',
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    professeur = django_filters.ModelChoiceFilter(
        queryset=Professeur.objects.all(),
        label='Professeur',
        empty_label='Tous les professeurs',
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    niveau = django_filters.ModelChoiceFilter(
        queryset=Niveau.objects.all(),
        label='Niveau',
        empty_label='Tous les niveaux',
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    filiere = django_filters.ModelChoiceFilter(
        queryset=Filiere.objects.all(),
        label='Filière',
        empty_label='Toutes les filières',
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    # 🔧 NOUVEAU: Filtre par SEMESTRE
    semestre = django_filters.ChoiceFilter(
        choices=MatiereProgrammee.SEMESTRE_CHOICES,
        label='Semestre',
        empty_label='Tous les semestres',
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    class Meta:
        model = MatiereProgrammee
        fields = ['matiere', 'professeur', 'niveau', 'filiere', 'semestre']


# ============= 🔧 CORRECTION: FILTRE POUR SÉLECTION DE COURS À ÉMARGER (AVEC SEMESTRE) =============
class CoursEmargementFilter(django_filters.FilterSet):
    """
    Filtres pour la sélection de cours à émarger.
    🔧 CORRECTIONS:
    1. Ajout du champ 'niveau' qui manquait
    2. Ajout du champ 'semestre'
    3. Utilisation du bon field_name pour les filtres
    """
    
    matiere = django_filters.ModelChoiceFilter(
        queryset=Matiere.objects.all(),
        label='Matière',
        empty_label='Toutes les matières',
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    professeur = django_filters.ModelChoiceFilter(
        queryset=Professeur.objects.all(),
        label='Professeur',
        empty_label='Tous les professeurs',
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    filiere = django_filters.ModelChoiceFilter(
        queryset=Filiere.objects.all(),
        label='Filière',
        empty_label='Toutes les filières',
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    # 🔧 CORRECTION 1: Ajout du filtre niveau manquant
    niveau = django_filters.ModelChoiceFilter(
        queryset=Niveau.objects.all(),
        label='Niveau',
        empty_label='Tous les niveaux',
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    # 🔧 CORRECTION 2: Ajout du filtre SEMESTRE
    semestre = django_filters.ChoiceFilter(
        choices=MatiereProgrammee.SEMESTRE_CHOICES,
        label='Semestre',
        empty_label='Tous les semestres',
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    class Meta:
        model = MatiereProgrammee
        fields = ['matiere', 'professeur', 'filiere', 'niveau', 'semestre']


# ============= 🔧 CORRECTION: FILTRE POUR HISTORIQUE DES ÉMARGEMENTS (AVEC SEMESTRE) =============
class EmargementFilterComplete(django_filters.FilterSet):
    """
    Filtres pour l'historique des émargements.
    🔧 CORRECTION: Ajout du filtre SEMESTRE
    """
    
    date_debut = django_filters.DateFilter(
        field_name='date_emar',
        lookup_expr='gte',
        label='Date début',
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date',
            'placeholder': 'JJ/MM/AAAA'
        })
    )
    
    date_fin = django_filters.DateFilter(
        field_name='date_emar',
        lookup_expr='lte',
        label='Date fin',
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date',
            'placeholder': 'JJ/MM/AAAA'
        })
    )
    
    matiere = django_filters.ModelChoiceFilter(
        field_name='matiere_programmer__matiere',
        queryset=Matiere.objects.all(),
        label='Matière',
        empty_label='Toutes les matières',
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    professeur = django_filters.ModelChoiceFilter(
        field_name='matiere_programmer__professeur',
        queryset=Professeur.objects.all(),
        label='Professeur',
        empty_label='Tous les professeurs',
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    filiere = django_filters.ModelChoiceFilter(
        field_name='matiere_programmer__filiere',
        queryset=Filiere.objects.all(),
        label='Filière',
        empty_label='Toutes les filières',
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    niveau = django_filters.ModelChoiceFilter(
        field_name='matiere_programmer__niveau',
        queryset=Niveau.objects.all(),
        label='Niveau',
        empty_label='Tous les niveaux',
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    # 🔧 NOUVEAU: Filtre par SEMESTRE
    semestre = django_filters.ChoiceFilter(
        field_name='matiere_programmer__semestre',
        choices=MatiereProgrammee.SEMESTRE_CHOICES,
        label='Semestre',
        empty_label='Tous les semestres',
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    class Meta:
        model = Emargement
        fields = ['date_debut', 'date_fin', 'matiere', 'professeur', 'filiere', 'niveau', 'semestre']


# ============= 🔧 CORRECTION: FILTRE POUR ÉVALUATIONS (AVEC SEMESTRE) =============
class EvaluationFilter(django_filters.FilterSet):
    """
    Filtres pour la liste des évaluations.
    🔧 CORRECTION: Ajout du filtre SEMESTRE
    """
    
    matiere = django_filters.ModelChoiceFilter(
        field_name='matiere_programmer__matiere',
        queryset=Matiere.objects.all(),
        label='Matière',
        empty_label='Toutes les matières',
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    professeur = django_filters.ModelChoiceFilter(
        field_name='matiere_programmer__professeur',
        queryset=Professeur.objects.all(),
        label='Professeur',
        empty_label='Tous les professeurs',
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    niveau = django_filters.ModelChoiceFilter(
        field_name='matiere_programmer__niveau',
        queryset=Niveau.objects.all(),
        label='Niveau',
        empty_label='Tous les niveaux',
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    filiere = django_filters.ModelChoiceFilter(
        field_name='matiere_programmer__filiere',
        queryset=Filiere.objects.all(),
        label='Filière',
        empty_label='Toutes les filières',
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    # 🔧 NOUVEAU: Filtre par SEMESTRE
    semestre = django_filters.ChoiceFilter(
        field_name='matiere_programmer__semestre',
        choices=MatiereProgrammee.SEMESTRE_CHOICES,
        label='Semestre',
        empty_label='Tous les semestres',
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    class Meta:
        model = Evaluation
        fields = ['matiere', 'professeur', 'niveau', 'filiere', 'semestre']
