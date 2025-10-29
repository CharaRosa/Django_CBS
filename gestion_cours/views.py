"""
VIEWS.PY - Agrégateur central des vues
Importe et expose toutes les vues des modules spécialisés
"""

# Import des vues depuis les modules spécialisés
from .views_dashboard import (
    landing_page,
    home_view,
    BaseAPView,
    get_active_annee_academique,
    paginate_queryset,
)

from .views_crud import (
    # Professeurs
    professeur_list_view,
    ProfesseurCreateView,
    ProfesseurUpdateView,
    ProfesseurDeleteView,
    
    # Matières
    MatiereListView,
    MatiereCreateView,
    MatiereUpdateView,
    MatiereDeleteView,
    
    # Filières
    FiliereListView,
    FiliereCreateView,
    FiliereUpdateView,
    FiliereDeleteView,
    
    # Niveaux
    NiveauListView,
    NiveauCreateView,
    NiveauUpdateView,
    NiveauDeleteView,
    
    # Années académiques
    AnneeAcademiqueListView,
    AnneeAcademiqueCreateView,
    AnneeAcademiqueUpdateView,
    AnneeAcademiqueDeleteView,
)

from .views_cours_management import (
    # Cours programmés
    matiereprogrammee_list_view,
    MatiereProgrammeeCreateView,
    MatiereProgrammeeUpdateView,
    MatiereProgrammeeDeleteView,
    
    # Émargements
    emargement_selection_cours,
    emargement_view,
    
    # Historique
    historique_view,
    historique_cours_view,
    export_emargements_to_excel, # <-- AJOUT
    export_emargements_to_pdf,   # <-- AJOUT
    
    # Évaluations
    evaluation_list_view,
    EvaluationManagementView,
)

# Pour compatibilité avec urls.py existants
emargement_selection_view = emargement_selection_cours

__all__ = [
    # Dashboard
    'landing_page',
    'home_view',
    'BaseAPView',
    'get_active_annee_academique',
    'paginate_queryset',
    
    # Professeurs
    'professeur_list_view',
    'ProfesseurCreateView',
    'ProfesseurUpdateView',
    'ProfesseurDeleteView',
    
    # Matières
    'MatiereListView',
    'MatiereCreateView',
    'MatiereUpdateView',
    'MatiereDeleteView',
    
    # Filières
    'FiliereListView',
    'FiliereCreateView',
    'FiliereUpdateView',
    'FiliereDeleteView',
    
    # Niveaux
    'NiveauListView',
    'NiveauCreateView',
    'NiveauUpdateView',
    'NiveauDeleteView',
    
    # Années académiques
    'AnneeAcademiqueListView',
    'AnneeAcademiqueCreateView',
    'AnneeAcademiqueUpdateView',
    'AnneeAcademiqueDeleteView',
    
    # Cours programmés
    'matiereprogrammee_list_view',
    'MatiereProgrammeeCreateView',
    'MatiereProgrammeeUpdateView',
    'MatiereProgrammeeDeleteView',
    
    # Émargements
    'emargement_selection_cours',
    'emargement_selection_view',
    'emargement_view',
    
    # Historique
    'historique_view',
    'historique_cours_view',
    'export_emargements_to_excel', # <-- AJOUT
    'export_emargements_to_pdf',   # <-- AJOUT
    
    # Évaluations
    'evaluation_list_view',
    'EvaluationManagementView',
]