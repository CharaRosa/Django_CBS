from django.contrib import admin
from .models import (
    Professeur, Filiere, Niveau, Matiere, 
    AnneeAcademique, MatiereProgrammee, 
    Emargement, Evaluation
)

# Enregistrement des modèles de base
@admin.register(Professeur)
class ProfesseurAdmin(admin.ModelAdmin):
    # CORRECTION : Suppression des champs 'status' et 'domaine_enseignement' qui n'existent pas dans models.py
    list_display = ('nom', 'prenoms', 'email', 'contact') # 'contact' est ajouté car il existe dans le modèle
    search_fields = ('nom', 'prenoms', 'email', 'contact')
    # CORRECTION : Suppression de 'status' de list_filter
    list_filter = [] 

@admin.register(Filiere)
class FiliereAdmin(admin.ModelAdmin):
    list_display = ('code', 'libelle')
    search_fields = ('libelle', 'code')

@admin.register(Niveau)
class NiveauAdmin(admin.ModelAdmin):
    list_display = ('libelle', 'filiere', 'niv')
    list_filter = ('filiere',)

@admin.register(Matiere)
class MatiereAdmin(admin.ModelAdmin):
    list_display = ('code', 'libelle') # Ajout de 'code' pour plus de clarté
    search_fields = ('libelle', 'code')

@admin.register(AnneeAcademique)
class AnneeAcademiqueAdmin(admin.ModelAdmin):
    # CORRECTION : 'annee_encours' n'existe pas, il est remplacé par 'active'
    list_display = ('annee_accademique', 'active') 
    list_editable = ('active',) 

# Enregistrement du modèle principal de programmation
@admin.register(MatiereProgrammee)
class MatiereProgrammeeAdmin(admin.ModelAdmin):
    list_display = ('matiere', 'professeur', 'niveau_filiere', 'nbr_heure', 'annee_academique', 'date_debut_estimee')
    list_filter = ('annee_academique', 'filiere', 'niveau')
    search_fields = ('matiere__libelle', 'professeur__nom', 'professeur__prenoms')

    def niveau_filiere(self, obj):
        return f"{obj.niveau.libelle} {obj.niveau.niv} ({obj.filiere.code})"
    niveau_filiere.short_description = 'Filière/Niveau'

# Enregistrement du modèle d'émargement
@admin.register(Emargement)
class EmargementAdmin(admin.ModelAdmin):
    list_display = ('matiere_programmer', 'date_emar', 'heure_eff')
    list_filter = ('matiere_programmer__annee_academique', 'date_emar')
    date_hierarchy = 'date_emar'

# Enregistrement du modèle d'évaluation
@admin.register(Evaluation)
class EvaluationAdmin(admin.ModelAdmin):
    # Ajout du champ utilisateur pour voir qui a fait l'évaluation
    list_display = ('matiere_programmer', 'utilisateur_evaluation') 
    list_filter = ('matiere_programmer__annee_academique',)
    search_fields = ('matiere_programmer__matiere__libelle',)