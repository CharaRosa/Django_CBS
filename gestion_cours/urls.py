from django.urls import path
from django.contrib.auth import views as auth_views
from . import views 

app_name = 'gestion_cours'

urlpatterns = [
    # ------------------ Authentification -------------------
    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    
    # ------------------ Pages Principales -------------------
    path('', views.landing_page, name='landing'),
    path('dashboard/', views.home_view, name='home'), 
    path('historique/', views.historique_view, name='historique'),
    path('cours/<int:pk>/historique/', views.historique_cours_view, name='historique_cours'),
    path('historique/export/excel/', views.export_emargements_to_excel, name='export_emargements_excel'),
    
    # 3. Chemin pour l'export PDF (l'erreur potentielle suivante à la ligne 30)
    path('historique/export/pdf/', views.export_emargements_to_pdf, name='export_emargements_pdf'),
    
    # ------------------ Émargements -------------------
    path('emargement/selection/', views.emargement_selection_view, name='emargement_selection'),
    path('emargement/<int:pk>/', views.emargement_view, name='emargement'),
    
    # ------------------ Professeurs -------------------
    path('professeurs/', views.professeur_list_view, name='professeur_list'),
    path('professeurs/create/', views.ProfesseurCreateView.as_view(), name='professeur_create'),
    path('professeurs/<int:pk>/update/', views.ProfesseurUpdateView.as_view(), name='professeur_update'),
    path('professeurs/<int:pk>/delete/', views.ProfesseurDeleteView.as_view(), name='professeur_delete'),
    
    # ------------------ Matières -------------------
    path('matieres/', views.MatiereListView.as_view(), name='matiere_list'),
    path('matieres/create/', views.MatiereCreateView.as_view(), name='matiere_create'),
    path('matieres/<int:pk>/update/', views.MatiereUpdateView.as_view(), name='matiere_update'),
    path('matieres/<int:pk>/delete/', views.MatiereDeleteView.as_view(), name='matiere_delete'),
    
    # ------------------ Filières -------------------
    path('filieres/', views.FiliereListView.as_view(), name='filiere_list'),
    path('filieres/create/', views.FiliereCreateView.as_view(), name='filiere_create'),
    path('filieres/<int:pk>/update/', views.FiliereUpdateView.as_view(), name='filiere_update'),
    path('filieres/<int:pk>/delete/', views.FiliereDeleteView.as_view(), name='filiere_delete'),
    
    # ------------------ Niveaux -------------------
    path('niveaux/', views.NiveauListView.as_view(), name='niveau_list'),
    path('niveaux/create/', views.NiveauCreateView.as_view(), name='niveau_create'),
    path('niveaux/<int:pk>/update/', views.NiveauUpdateView.as_view(), name='niveau_update'),
    path('niveaux/<int:pk>/delete/', views.NiveauDeleteView.as_view(), name='niveau_delete'),
    
    # ------------------ Années Académiques -------------------
    path('annees/', views.AnneeAcademiqueListView.as_view(), name='anneeacademique_list'),
    path('annees/create/', views.AnneeAcademiqueCreateView.as_view(), name='anneeacademique_create'),
    path('annees/<int:pk>/update/', views.AnneeAcademiqueUpdateView.as_view(), name='anneeacademique_update'),
    path('annees/<int:pk>/delete/', views.AnneeAcademiqueDeleteView.as_view(), name='anneeacademique_delete'),
    
    # ------------------ Cours Programmés -------------------
    path('cours-programmes/', views.matiereprogrammee_list_view, name='matiereprogrammee_list'),
    path('cours-programmes/create/', views.MatiereProgrammeeCreateView.as_view(), name='matiereprogrammee_create'),
    path('cours-programmes/<int:pk>/update/', views.MatiereProgrammeeUpdateView.as_view(), name='matiereprogrammee_update'),
    path('cours-programmes/<int:pk>/delete/', views.MatiereProgrammeeDeleteView.as_view(), name='matiereprogrammee_delete'),
    
    # ------------------ Évaluations -------------------
    path('evaluations/', views.evaluation_list_view, name='evaluation_list'),
    path('evaluations/<int:pk>/', views.EvaluationManagementView.as_view(), name='evaluation_manage'),
    
]
