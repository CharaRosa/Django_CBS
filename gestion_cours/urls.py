# gestion_cours/urls.py



from django.urls import path
from . import views

# Le nom de l'application est utilisé pour les chemins (ex: gestion_cours:home)
app_name = 'gestion_cours' 

urlpatterns = [
    # Page d'accueil : Affiche tous les cours programmés pour l'année active
    path('', views.home_view, name='home'),
    
    # Page pour faire l'émargement d'un cours spécifique
    # <int:pk> est l'ID de la MatiereProgrammee
    path('emargement/<int:pk>/', views.emargement_view, name='emargement'),
    
    # Page de confirmation/historique (optionnel)
    path('historique/', views.historique_view, name='historique'),
    path('evaluer/<int:pk>/', views.evaluation_view, name='evaluation'), 
]
