from django.urls import path
from django.contrib.auth import views as auth_views
from . import views
from .views import (
    MatiereListView, MatiereCreateView, MatiereUpdateView, MatiereDeleteView,
    ProfesseurListView, ProfesseurCreateView, ProfesseurUpdateView, ProfesseurDeleteView,
    EmargementCreateView # Vue générique AP
)

# Le nom de l'application est utilisé pour les chemins (ex: gestion_cours:home)
app_name = 'gestion_cours'

urlpatterns = [
    # ------------------ Vues d'Authentification -------------------
    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),

    # ------------------ Vues Fonctionnelles Générales -------------
    
    # Tableau de Bord principal (Affichage de la progression des cours - home_view remplace tableau_de_bord_ap)
    path('', views.home_view, name='home'),
    
    # Émargement (pour le professeur) : Saisie d'une séance pour une MatiereProgrammee spécifique
    path('emargement/<int:pk>/', views.emargement_view, name='emargement'),
    
    # Évaluation (pour l'AP) : Saisie de l'évaluation qualitative d'un cours
    path('evaluer/<int:pk>/', views.evaluation_view, name='evaluation'),
    
    # Historique des émargements (pour l'AP)
    path('historique/', views.historique_view, name='historique'),
    
    # ------------------ Vues de Gestion AP (CRUD) -------------------
    
    # 1. Gestion des Matières
    path('ap/matieres/', MatiereListView.as_view(), name='matiere_list'),
    path('ap/matieres/creer/', MatiereCreateView.as_view(), name='matiere_create'),
    path('ap/matieres/modifier/<int:pk>/', MatiereUpdateView.as_view(), name='matiere_update'),
    path('ap/matieres/supprimer/<int:pk>/', MatiereDeleteView.as_view(), name='matiere_delete'),
    
    # 2. Gestion des Professeurs
    path('ap/professeurs/', ProfesseurListView.as_view(), name='professeur_list'),
    path('ap/professeurs/creer/', ProfesseurCreateView.as_view(), name='professeur_create'),
    path('ap/professeurs/modifier/<int:pk>/', ProfesseurUpdateView.as_view(), name='professeur_update'),
    path('ap/professeurs/supprimer/<int:pk>/', ProfesseurDeleteView.as_view(), name='professeur_delete'),

    # 3. Création d'Emargement (Vue générique AP pour l'administration)
    path('ap/emargement/creer/', EmargementCreateView.as_view(), name='emargement_create_ap'),

    # NOTE: Il faudrait ajouter le CRUD pour Filiere, Niveau, AnneeAcademique et MatiereProgrammee si ces modèles doivent être gérés par l'AP.
]