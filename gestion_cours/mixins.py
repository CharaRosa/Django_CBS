from django.contrib.auth.mixins import AccessMixin
from django.shortcuts import redirect

class AssistantPedaRequiredMixin(AccessMixin):
    """Vérifie si l'utilisateur est un Assistant Peda ou un Superuser."""
    
    def dispatch(self, request, *args, **kwargs):
        # Vérifie l'authentification et l'appartenance au groupe
        is_assistant_peda = request.user.groups.filter(name='Assistant').exists()
        
        if not request.user.is_authenticated:
            # Redirige vers la page de connexion si non connecté
            return self.handle_no_permission()
        
        if not (request.user.is_superuser or is_assistant_peda):
            # CORRIGÉ: Utilise 'home' qui est le nom réel de l'URL du tableau de bord
            return redirect('gestion_cours:home') 
        
        return super().dispatch(request, *args, **kwargs)