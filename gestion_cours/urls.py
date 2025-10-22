from django.urls import path
from django.contrib.auth import views as auth_views
from . import views 

# Le nom de l'application est utilisé pour les chemins (ex: gestion_cours:home)
app_name = 'gestion_cours'

urlpatterns = [
    # ------------------ Vues d'Authentification -------------------
    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    # Chemin pour le tableau de bord
    path('dashboard/', views.home_view, name='dashboard'),
    
    # Chemin que le bouton du tableau de bord appelle
    path('cours/<int:pk>/historique/', views.historique_cours_view, name='historique_cours'),
    

    # ------------------ Vues Fonctionnelles Générales -------------
    
    # Nouvelle Page d'Accueil PUBLIQUE (landing page)
    path('', views.landing_page, name='landing'),
    
    # Tableau de Bord principal AP (Destination après login)
    path('dashboard/', views.home_view, name='home'),
    
    # Évaluation (pour l'AP) : Saisie de l'évaluation qualitative d'un cours
    # ANCIEN CHEMIN SUPPRIMÉ: path('evaluer/<int:pk>/', views.evaluation_view, name='evaluation'),
    
    # Historique des émargements (pour l'AP)
    path('historique/', views.historique_view, name='historique'),
    
    # ------------------ NOUVELLES VUES D'ÉMARGEMENT (Flux en 2 Étapes) -------------------

    # 1. ÉTAPE 1: Sélection du cours à émarger pour l'année active
    path('ap/emargement/selection/', views.EmargementSelectionCoursView.as_view(), name='emargement_selection_cours'),
    
    # 2. ÉTAPE 2: Saisie de la séance d'émargement (utilise votre vue fonctionnelle existante)
    path('ap/emargement/<int:pk>/saisir/', views.emargement_view, name='emargement_saisir'),
    
    # ------------------ Vues de Gestion AP (CRUD) -------------------
    
    # 1. Gestion des Matières
    path('ap/matieres/', views.MatiereListView.as_view(), name='matiere_list'),
    path('ap/matieres/creer/', views.MatiereCreateView.as_view(), name='matiere_create'),
    path('ap/matieres/modifier/<int:pk>/', views.MatiereUpdateView.as_view(), name='matiere_update'),
    path('ap/matieres/supprimer/<int:pk>/', views.MatiereDeleteView.as_view(), name='matiere_delete'),
    
    # 2. Gestion des Professeurs
    path('ap/professeurs/', views.ProfesseurListView.as_view(), name='professeur_list'),
    path('ap/professeurs/creer/', views.ProfesseurCreateView.as_view(), name='professeur_create'),
    path('ap/professeurs/modifier/<int:pk>/', views.ProfesseurUpdateView.as_view(), name='professeur_update'),
    path('ap/professeurs/supprimer/<int:pk>/', views.ProfesseurDeleteView.as_view(), name='professeur_delete'),

    # 3. Gestion des Filières
    path('ap/filieres/', views.FiliereListView.as_view(), name='filiere_list'),
    path('ap/filieres/creer/', views.FiliereCreateView.as_view(), name='filiere_create'),
    path('ap/filieres/modifier/<int:pk>/', views.FiliereUpdateView.as_view(), name='filiere_update'),
    path('ap/filieres/supprimer/<int:pk>/', views.FiliereDeleteView.as_view(), name='filiere_delete'),

    # 4. Gestion des Niveaux
    path('ap/niveaux/', views.NiveauListView.as_view(), name='niveau_list'),
    path('ap/niveaux/creer/', views.NiveauCreateView.as_view(), name='niveau_create'),
    path('ap/niveaux/modifier/<int:pk>/', views.NiveauUpdateView.as_view(), name='niveau_update'),
    path('ap/niveaux/supprimer/<int:pk>/', views.NiveauDeleteView.as_view(), name='niveau_delete'),

    # 5. Gestion des Années Académiques
    path('ap/annees/', views.AnneeAcademiqueListView.as_view(), name='anneeacademique_list'),
    path('ap/annees/creer/', views.AnneeAcademiqueCreateView.as_view(), name='anneeacademique_create'),
    path('ap/annees/modifier/<int:pk>/', views.AnneeAcademiqueUpdateView.as_view(), name='anneeacademique_update'),
    path('ap/annees/supprimer/<int:pk>/', views.AnneeAcademiqueDeleteView.as_view(), name='anneeacademique_delete'),

    # 6. Gestion des Matières Programmées
    path('ap/cours/', views.MatiereProgrammeeListView.as_view(), name='matiereprogrammee_list'),
    path('ap/cours/creer/', views.MatiereProgrammeeCreateView.as_view(), name='matiereprogrammee_create'),
    path('ap/cours/modifier/<int:pk>/', views.MatiereProgrammeeUpdateView.as_view(), name='matiereprogrammee_update'),
    path('ap/cours/supprimer/<int:pk>/', views.MatiereProgrammeeDeleteView.as_view(), name='matiereprogrammee_delete'),
    
    # 7. Gestion des Évaluations 
    path('ap/evaluations/', views.EvaluationListView.as_view(), name='evaluation_list'), 
    
    # Gestion de l'évaluation (Création/Modification)
    path('cours/<int:pk>/evaluer/', views.EvaluationManagementView.as_view(), name='evaluation_management'),
]