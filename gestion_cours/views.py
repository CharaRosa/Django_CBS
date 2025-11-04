"""
VIEWS.PY - Agrégateur central des vues
Importe et expose toutes les vues des modules spécialisés

🆕 MISE À JOUR: Ajout des nouvelles vues pour modification/suppression des émargements et évaluations
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
    
    # 🆕 Matières (avec fonction de liste pour filtres)
    matiere_list_view,  # NOUVEAU
    MatiereListView,
    MatiereCreateView,
    MatiereUpdateView,
    MatiereDeleteView,
    
    # 🆕 Filières (avec fonction de liste pour filtres)
    filiere_list_view,  # NOUVEAU
    FiliereListView,
    FiliereCreateView,
    FiliereUpdateView,
    FiliereDeleteView,
    
    # 🆕 Niveaux (avec fonction de liste pour filtres)
    niveau_list_view,  # NOUVEAU
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
    emargement_selection_view,
    emargement_view,
    emargement_update_view,  # 🆕 NOUVEAU
    emargement_delete_view,  # 🆕 NOUVEAU
    
    # Historique
    historique_view,
    historique_cours_view,
    export_emargements_to_excel,
    export_emargements_to_pdf,
    
    # Évaluations
    evaluation_list_view,
    EvaluationManagementView,
    evaluation_update_view,  # 🆕 NOUVEAU
    evaluation_delete_view,  # 🆕 NOUVEAU
)

# Liste explicite de tous les exports
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
    'matiere_list_view',
    'MatiereListView',
    'MatiereCreateView',
    'MatiereUpdateView',
    'MatiereDeleteView',
    
    # Filières
    'filiere_list_view',
    'FiliereListView',
    'FiliereCreateView',
    'FiliereUpdateView',
    'FiliereDeleteView',
    
    # Niveaux
    'niveau_list_view',
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
    'emargement_selection_view',
    'emargement_view',
    'emargement_update_view',
    'emargement_delete_view',
    
    # Historique
    'historique_view',
    'historique_cours_view',
    'export_emargements_to_excel',
    'export_emargements_to_pdf',
    
    # Évaluations
    'evaluation_list_view',
    'EvaluationManagementView',
    'evaluation_update_view',
    'evaluation_delete_view',
]