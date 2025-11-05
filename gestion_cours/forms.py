# gestion_cours/forms.py - VERSION CORRIGÉE
"""
CORRECTIONS APPORTÉES:
1. ✅ Correction de ProfesseurForm pour inclure grade, domaine, cv et dernier_diplome.
2. ✅ Champs textarea EvaluationForm rendus saisissables (ajout d'attrs appropriés)
3. ✅ Widgets avec classes CSS pour compatibilité Crispy Forms/Bootstrap
"""

from django import forms
from .models import Matiere, Professeur, Emargement, Evaluation, MatiereProgrammee, AnneeAcademique
from django.forms.widgets import DateInput, Textarea, NumberInput

# ----------------------------------------------------------------------
# CLASSE DE BASE POUR LE STYLING GÉNÉRIQUE (Pour les formulaires de modèles)
# ----------------------------------------------------------------------
class BaseCrispyModelForm(forms.ModelForm):
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # 1. Assurer le widget date HTML5 pour le calendrier
        for field_name, field in self.fields.items():
            if isinstance(field.widget, forms.DateInput):
                 field.widget.attrs['type'] = 'date'
        
        # 2. FILTRAGE POUR AFFICHER SEULEMENT L'ANNÉE ACADÉMIQUE ACTIVE
        if 'annee_academique' in self.fields:
             try:
                self.fields['annee_academique'].queryset = AnneeAcademique.objects.filter(active=True)
                # Si une seule année est active, la présélectionner
                if self.fields['annee_academique'].queryset.count() == 1:
                     active_annee = self.fields['annee_academique'].queryset.first()
                     self.initial['annee_academique'] = active_annee.pk
             except AnneeAcademique.DoesNotExist:
                 pass
        
# ----------------------------------------------------------------------
# 1. Formulaires CRUD (Matiere et Professeur)
# ----------------------------------------------------------------------
class MatiereForm(BaseCrispyModelForm):
    class Meta:
        model = Matiere
        fields = ['code', 'libelle'] 
        
class ProfesseurForm(BaseCrispyModelForm):
    class Meta:
        model = Professeur
        # 🟢 CORRECTION : Ajout de tous les champs du modèle Professeur
        fields = ['nom', 'prenoms', 'contact', 'email', 'grade', 'domaine', 'cv', 'dernier_diplome'] 
        
# ----------------------------------------------------------------------
# 2. Formulaire de Programmation - (LAISSÉ INCHANGÉ)
# ----------------------------------------------------------------------
class MatiereProgrammeeForm(BaseCrispyModelForm):
    class Meta:
        model = MatiereProgrammee
        fields = [
            'matiere', 'filiere', 'niveau', 'professeur', 
            'annee_academique', 'semestre', 'nbr_heure', 
            'date_debut_estimee', 'date_fin_estimee'
        ]
        
        widgets = {
            'date_debut_estimee': DateInput(attrs={'type': 'date'}),
            'date_fin_estimee': DateInput(attrs={'type': 'date'}),
        }
        
# ----------------------------------------------------------------------
# 3. Formulaire d'Émargement (Alignement strict avec le Modèle)
# ----------------------------------------------------------------------
class EmargementForm(forms.ModelForm):
    
    class Meta:
        model = Emargement
        fields = ['date_emar', 'heure_eff'] 
        
        widgets = {
            'date_emar': DateInput(attrs={
                'type': 'date',
                'class': 'form-control'
            }),
            'heure_eff': NumberInput(attrs={
                'step': '0.5', 
                'placeholder': 'Ex: 2.0 ou 1.5', 
                'min': '0.5', 
                'max': '8.0',
                'class': 'form-control'
            })
        }
        
        labels = {
            'date_emar': 'Date de la séance',
            'heure_eff': 'Durée de la séance (en heures décimales)',
        }
        
# ----------------------------------------------------------------------
# 4. Formulaire d'Évaluation - 🆕 CORRIGÉ AVEC TEXTAREAS SAISISSABLES
# ----------------------------------------------------------------------
class EvaluationForm(BaseCrispyModelForm): 
    class Meta:
        model = Evaluation
        fields = ['resume_evaluation', 'resume_ap', 'recommandation'] 
        
        widgets = {
            'resume_evaluation': Textarea(attrs={
                'rows': 5,
                'class': 'form-control',
                'placeholder': 'Décrivez le déroulement du cours, les points forts et les difficultés rencontrées...'
            }),
            'resume_ap': Textarea(attrs={
                'rows': 5,
                'class': 'form-control',
                'placeholder': 'Votre appréciation personnelle sur la qualité du cours et l\'implication du professeur...'
            }),
            'recommandation': Textarea(attrs={
                'rows': 5,
                'class': 'form-control',
                'placeholder': 'Proposez des améliorations pour les prochaines sessions de ce cours...'
            }),
        }
        
        labels = {
            'resume_evaluation': 'Résumé de l\'Évaluation du Cours',
            'resume_ap': 'Appréciation de l\'Assistant Pédagogique (AP)',
            'recommandation': 'Recommandations et Suggestions',
        }