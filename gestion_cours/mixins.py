# gestion_cours/mixins.py
from django.contrib.auth.mixins import AccessMixin
from django.shortcuts import redirect

class AssistantPedaRequiredMixin(AccessMixin):
    """Vérifie si l'utilisateur est un Assistant Peda ou un Superuser."""
    
    def dispatch(self, request, *args, **kwargs):
        # Vérifie l'authentification et l'appartenance au groupe
        is_assistant_peda = request.user.groups.filter(name='Assistant_Peda').exists()
        
        if not request.user.is_authenticated:
            # Redirige vers la page de connexion si non connecté
            return self.handle_no_permission()
        
        if not (request.user.is_superuser or is_assistant_peda):
            # Redirige vers une page d'erreur ou le tableau de bord avec un message
            return redirect('gestion_cours:tableau_de_bord_ap') 
        
        return super().dispatch(request, *args, **kwargs)