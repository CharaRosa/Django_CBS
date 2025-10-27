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
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Email...'})
    )
    
    grade = django_filters.CharFilter(
        field_name='grade',
        lookup_expr='icontains',
        label='Grade',
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Grade...'})
    )
    
    domaine = django_filters.CharFilter(
        field_name='domaine',
        lookup_expr='icontains',
        label="Domaine d'expertise",
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Domaine...'})
    )
    
    class Meta:
        model = Professeur
        fields = ['nom', 'prenoms', 'email', 'grade', 'domaine']


# ============= FILTRE POUR COURS PROGRAMMÉS =============
class MatiereProgrammeeFilter(django_filters.FilterSet):
    """Filtres pour les cours programmés."""
    
    matiere = django_filters.ModelChoiceFilter(
        field_name='matiere',
        queryset=Matiere.objects.all().order_by('libelle'),
        label='Matière',
        empty_label='Toutes les matières',
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    filiere = django_filters.ModelChoiceFilter(
        field_name='filiere',
        queryset=Filiere.objects.all().order_by('libelle'),
        label='Filière',
        empty_label='Toutes les filières',
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    niveau = django_filters.ModelChoiceFilter(
        field_name='niveau',
        queryset=Niveau.objects.all().order_by('niv'),
        label='Niveau',
        empty_label='Tous les niveaux',
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    professeur = django_filters.ModelChoiceFilter(
        field_name='professeur',
        queryset=Professeur.objects.all().order_by('nom'),
        label='Professeur',
        empty_label='Tous les professeurs',
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    semestre = django_filters.ChoiceFilter(
        field_name='semestre',
        choices=MatiereProgrammee.SEMESTRE_CHOICES,
        label='Semestre',
        empty_label='Tous les semestres',
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    annee_academique = django_filters.ModelChoiceFilter(
        field_name='annee_academique',
        queryset=AnneeAcademique.objects.all().order_by('-annee_accademique'),
        label='Année académique',
        empty_label='Toutes les années',
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    class Meta:
        model = MatiereProgrammee
        fields = ['matiere', 'filiere', 'niveau', 'professeur', 'semestre', 'annee_academique']


# ============= FILTRE POUR ÉMARGEMENTS =============
class EmargementFilterComplete(django_filters.FilterSet):
    """Filtres complets pour les émargements."""
    
    matiere = django_filters.ModelChoiceFilter(
        field_name='matiere_programmer__matiere',
        queryset=Matiere.objects.all().order_by('libelle'),
        label='Matière',
        empty_label='Toutes les matières',
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    professeur = django_filters.ModelChoiceFilter(
        field_name='matiere_programmer__professeur',
        queryset=Professeur.objects.all().order_by('nom'),
        label='Professeur',
        empty_label='Tous les professeurs',
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    filiere = django_filters.ModelChoiceFilter(
        field_name='matiere_programmer__filiere',
        queryset=Filiere.objects.all().order_by('libelle'),
        label='Filière',
        empty_label='Toutes les filières',
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    niveau = django_filters.ModelChoiceFilter(
        field_name='matiere_programmer__niveau',
        queryset=Niveau.objects.all().order_by('niv'),
        label='Niveau',
        empty_label='Tous les niveaux',
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    semestre = django_filters.ChoiceFilter(
        field_name='matiere_programmer__semestre',
        choices=MatiereProgrammee.SEMESTRE_CHOICES,
        label='Semestre',
        empty_label='Tous les semestres',
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    date_debut = django_filters.DateFilter(
        field_name='date_emar',
        lookup_expr='gte',
        label='Date début',
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'})
    )
    
    date_fin = django_filters.DateFilter(
        field_name='date_emar',
        lookup_expr='lte',
        label='Date fin',
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'})
    )
    
    class Meta:
        model = Emargement
        fields = ['matiere', 'professeur', 'filiere', 'niveau', 'semestre', 'date_debut', 'date_fin']


# ============= FILTRE POUR ÉVALUATIONS =============
class EvaluationFilter(django_filters.FilterSet):
    """Filtres pour les évaluations qualitatives."""
    
    matiere = django_filters.ModelChoiceFilter(
        field_name='matiere_programmer__matiere',
        queryset=Matiere.objects.all().order_by('libelle'),
        label='Matière',
        empty_label='Toutes les matières',
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    professeur = django_filters.ModelChoiceFilter(
        field_name='matiere_programmer__professeur',
        queryset=Professeur.objects.all().order_by('nom'),
        label='Professeur',
        empty_label='Tous les professeurs',
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    filiere = django_filters.ModelChoiceFilter(
        field_name='matiere_programmer__filiere',
        queryset=Filiere.objects.all().order_by('libelle'),
        label='Filière',
        empty_label='Toutes les filières',
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    niveau = django_filters.ModelChoiceFilter(
        field_name='matiere_programmer__niveau',
        queryset=Niveau.objects.all().order_by('niv'),
        label='Niveau',
        empty_label='Tous les niveaux',
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    semestre = django_filters.ChoiceFilter(
        field_name='matiere_programmer__semestre',
        choices=MatiereProgrammee.SEMESTRE_CHOICES,
        label='Semestre',
        empty_label='Tous les semestres',
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    evaluateur = django_filters.CharFilter(
        field_name='utilisateur_evaluation__username',
        lookup_expr='icontains',
        label='Évalué par',
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nom évaluateur...'})
    )
    
    class Meta:
        model = Evaluation
        fields = ['matiere', 'professeur', 'filiere', 'niveau', 'semestre', 'evaluateur']


# ============= FILTRE POUR SÉLECTION COURS À ÉMARGER =============
class CoursEmargementFilter(django_filters.FilterSet):
    """Filtres pour la sélection de cours à émarger."""
    
    filiere = django_filters.ModelChoiceFilter(
        field_name='filiere',
        queryset=Filiere.objects.all().order_by('libelle'),
        label='Filière',
        empty_label='Toutes les filières',
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    niveau = django_filters.ModelChoiceFilter(
        field_name='niveau',
        queryset=Niveau.objects.all().order_by('niv'),
        label='Niveau',
        empty_label='Tous les niveaux',
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    semestre = django_filters.ChoiceFilter(
        field_name='semestre',
        choices=MatiereProgrammee.SEMESTRE_CHOICES,
        label='Semestre',
        empty_label='Tous les semestres',
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    professeur = django_filters.ModelChoiceFilter(
        field_name='professeur',
        queryset=Professeur.objects.all().order_by('nom'),
        label='Professeur',
        empty_label='Tous les professeurs',
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    class Meta:
        model = MatiereProgrammee
        fields = ['filiere', 'niveau', 'semestre', 'professeur']
