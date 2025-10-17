from django.contrib import admin
from .models import (
    Professeur, Filiere, Niveau, Matiere, 
    AnneeAcademique, MatiereProgrammee, 
    Emargement, Evaluation
)

# Enregistrement des modèles de base
@admin.register(Professeur)
class ProfesseurAdmin(admin.ModelAdmin):
    list_display = ('nom', 'prenoms', 'email', 'status', 'domaine_enseignement')
    search_fields = ('nom', 'prenoms', 'email')
    list_filter = ('status',)

@admin.register(Filiere)
class FiliereAdmin(admin.ModelAdmin):
    list_display = ('code', 'libelle')

@admin.register(Niveau)
class NiveauAdmin(admin.ModelAdmin):
    list_display = ('libelle', 'filiere', 'niv')
    list_filter = ('filiere',)

@admin.register(Matiere)
class MatiereAdmin(admin.ModelAdmin):
    list_display = ('libelle',)
    search_fields = ('libelle',)

@admin.register(AnneeAcademique)
class AnneeAcademiqueAdmin(admin.ModelAdmin):
    list_display = ('annee_accademique', 'active', 'annee_encours')
    list_editable = ('active',) # Permet de changer rapidement l'année active

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
    list_display = ('matiere_programmer',)
    list_filter = ('matiere_programmer__annee_academique',)
