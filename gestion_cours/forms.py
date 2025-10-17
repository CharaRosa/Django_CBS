from django import forms
from .models import Emargement

class EmargementForm(forms.ModelForm):
    
    # Champ personnalisé que la vue va lire
    duree_saisie = forms.DecimalField(
        label="Durée de la séance (en heures décimales, ex: 1.5 pour 1h30)",
        max_digits=4,
        decimal_places=2,
        # Assure un pas de 0.5 (30 minutes)
        widget=forms.NumberInput(attrs={'class': 'form-input', 'step': '0.5', 'placeholder': 'Ex: 2.0 ou 1.5'})
    )

    class Meta:
        model = Emargement
        # Inclure UNIQUEMENT les champs du modèle que nous voulons afficher
        # Le champ 'heure_eff' sera renseigné par la vue et n'est PAS inclus ici.
        fields = ['date_emar'] 
        
        widgets = {
            'date_emar': forms.DateInput(attrs={'type': 'date', 'class': 'form-input'}),
        }