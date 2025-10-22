import django_filters
from .models import Emargement, Professeur, Matiere

class EmargementFilter(django_filters.FilterSet):
    """Filtres pour la liste des émargements (historique global)."""
    
    # Filtrer par le nom du professeur
    professeur = django_filters.ModelChoiceFilter(
        field_name='matiere_programmer__professeur',
        queryset=Professeur.objects.all().order_by('nom'),
        label='Professeur',
        empty_label='Tous les professeurs'
    )
    
    # Filtrer par la matière
    matiere = django_filters.ModelChoiceFilter(
        field_name='matiere_programmer__matiere',
        queryset=Matiere.objects.all().order_by('libelle'),
        label='Matière',
        empty_label='Toutes les matières'
    )
    
    # Filtrer par plage de dates
    date_min = django_filters.DateFilter(
        field_name='date_emar', 
        lookup_expr='gte', # greater than or equal (>=)
        label='Date de début'
    )
    date_max = django_filters.DateFilter(
        field_name='date_emar', 
        lookup_expr='lte', # less than or equal (<=)
        label='Date de fin'
    )

    class Meta:
        model = Emargement
        fields = ['professeur', 'matiere', 'date_min', 'date_max']