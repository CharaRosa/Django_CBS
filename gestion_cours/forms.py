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
# 1. Formulaires CRUD (Matiere et Professeur) - (LAISSÉS INCHANGÉS)
# ----------------------------------------------------------------------
class MatiereForm(BaseCrispyModelForm):
    class Meta:
        model = Matiere
        fields = ['code', 'libelle'] 
        
class ProfesseurForm(BaseCrispyModelForm):
    class Meta:
        model = Professeur
        fields = ['nom', 'prenoms', 'contact', 'email'] 
        
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
    
    # !!! SUPPRESSION des définitions explicites de champs pour utiliser Meta/widgets !!!
    # Exemples de champs retirés : date_seance, theme_chapitre_aborde, heure_debut, heure_fin, contenu_seance
    
    class Meta:
        model = Emargement
        # Utiliser les noms de champs exacts du modèle
        fields = ['date_emar', 'heure_eff'] 
        
        # Appliquer les widgets et les attributs dans Meta
        widgets = {
            # Ces noms de clés DOIVENT correspondre aux champs du modèle
            'date_emar': DateInput(attrs={'type': 'date'}),
            'heure_eff': NumberInput(attrs={'step': '0.5', 'placeholder': 'Ex: 2.0 ou 1.5', 'min': '0.5', 'max': '8.0'})
        }
        
        # Optionnel: Définir les libellés (labels) si nécessaire
        labels = {
            'date_emar': 'Date de la séance',
            'heure_eff': 'Durée de la séance (en heures décimales)',
        }
        
# ----------------------------------------------------------------------
# 4. Formulaire d'Évaluation - (LAISSÉ INCHANGÉ)
# ----------------------------------------------------------------------
class EvaluationForm(BaseCrispyModelForm): 
    class Meta:
        model = Evaluation
        fields = ['resume_evaluation', 'resume_ap', 'recommandation'] 
        
        widgets = {
            'resume_evaluation': Textarea(attrs={'rows': 4}),
            'resume_ap': Textarea(attrs={'rows': 4}),
            'recommandation': Textarea(attrs={'rows': 4}),
            
        }