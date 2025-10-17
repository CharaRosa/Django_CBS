from django import forms
from .models import Matiere, Professeur, Emargement, Evaluation, MatiereProgrammee # Importez tous les modèles

# ----------------------------------------------------------------------
# CLASSE DE BASE POUR LE STYLING (Bootstrap)
# ----------------------------------------------------------------------
class BootstrapModelForm(forms.ModelForm):
    """Classe de base appliquant les styles Bootstrap 'form-control' et 'form-select'."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            # Initialise ou ajoute la classe 'form-control'
            current_class = field.widget.attrs.get('class', '')
            if 'form-control' not in current_class:
                 field.widget.attrs['class'] = (current_class + ' form-control').strip()

            # Ajoute 'form-select' pour les Selects
            if isinstance(field.widget, forms.Select):
                field.widget.attrs['class'] += ' form-select'
            
            # Ajustement spécifique pour les DateInput standard
            if isinstance(field.widget, forms.DateInput):
                 field.widget.attrs['type'] = 'date'

# ----------------------------------------------------------------------
# 1. Formulaires CRUD (Matiere et Professeur)
# ----------------------------------------------------------------------
class MatiereForm(BootstrapModelForm):
    class Meta:
        model = Matiere
        # Correction: Seuls 'code' et 'libelle' sont sur le modèle Matiere
        fields = ['code', 'libelle'] 
        
class ProfesseurForm(BootstrapModelForm):
    class Meta:
        model = Professeur
        # Ajout de 'email' supposé nécessaire
        fields = ['nom', 'prenoms', 'contact', 'email'] 
        
# ----------------------------------------------------------------------
# 2. Formulaire de Programmation (Nouveau)
# ----------------------------------------------------------------------
class MatiereProgrammeeForm(BootstrapModelForm):
    class Meta:
        model = MatiereProgrammee
        # Champs spécifiques à la programmation d'un cours
        fields = [
            'matiere', 'filiere', 'niveau', 'professeur', 
            'annee_academique', 'semestre', 'nbr_heure', 
            'date_debut_estimee', 'date_fin_estimee'
        ]
        # Ajustement des widgets pour le calendrier
        widgets = {
            'date_debut_estimee': forms.DateInput(attrs={'type': 'date'}),
            'date_fin_estimee': forms.DateInput(attrs={'type': 'date'}),
        }
        
# ----------------------------------------------------------------------
# 3. Formulaire d'Émargement (Logique Spécifique pour 'emargement_view')
# ----------------------------------------------------------------------
class EmargementForm(forms.ModelForm):
    
    # Champ de date recréé pour un contrôle strict et un widget HTML5
    date_emar = forms.DateField(
        label="Date de la séance",
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}) 
    )

    # Champ non-modèle pour la saisie de durée (utilisé pour la validation dans la vue)
    duree_saisie = forms.DecimalField(
        label="Durée de la séance (en heures décimales)",
        max_digits=4,
        decimal_places=2,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.5', 'placeholder': 'Ex: 2.0 ou 1.5', 'min': '0.5', 'max': '8.0'})
    )
    
    # Champ d'observation stylisé
    observation = forms.CharField(
        required=False,
        label="Observation/Détails de la séance",
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3})
    )

    class Meta:
        model = Emargement
        # Laissez fields vide ou incluez 'observation' si c'est le seul champ du modèle direct.
        # Les champs date_emar et heure_eff (via duree_saisie) sont gérés par les champs de classe/vue.
        fields = ['observation'] 
        
# ----------------------------------------------------------------------
# 4. Formulaire d'Évaluation
# ----------------------------------------------------------------------
class EvaluationForm(BootstrapModelForm): 
    class Meta:
        model = Evaluation
        fields = ['resume_evaluation', 'resume_ap', 'recommandation'] 
        
        widgets = {
            'resume_evaluation': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'resume_ap': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'recommandation': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
        }