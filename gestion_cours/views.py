from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import F, Sum, Count
from django.utils import timezone
from datetime import date 
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator 
from decimal import Decimal # <-- IMPORT NÉCESSAIRE POUR LA GESTION DES DÉCIMALES
from .filters import EmargementFilter # <-- NOUVEL IMPORT AJOUTÉ

from .models import (
    Matiere, Professeur, Emargement, MatiereProgrammee, AnneeAcademique, Evaluation,
    Filiere,
    Niveau,
)
from .forms import MatiereForm, ProfesseurForm, EmargementForm, EvaluationForm, MatiereProgrammeeForm
from .mixins import AssistantPedaRequiredMixin 
from .utils import calculer_progression 

# --- Fonctions de test de permission ---
def est_administrateur_pedagogique(user):
    """Vérifie si l'utilisateur appartient au groupe ADMIN_PEDAGOGIQUE ou est super-utilisateur."""
    # NOTE: Le groupe 'Assistant' dans cette fonction est laissé tel quel (comme dans votre base de code fournie)
    return user.groups.filter(name='Assistant').exists() or user.is_superuser
# ---------------------------------------

# Ajoutez ou modifiez une fonction pour récupérer l'année active (UTILITAIRE CENTRALISÉ)
def get_active_annee_academique():
    try:
        # Utiliser .first() si vous ne voulez pas lancer d'exception MultipleObjectsReturned, 
        # mais .get() est plus approprié ici car une seule année doit être active.
        return AnneeAcademique.objects.get(active=True)
    except AnneeAcademique.DoesNotExist:
        return None # Retourne None si aucune année n'est active
    except AnneeAcademique.MultipleObjectsReturned:
        # Gérer le cas où plusieurs années sont actives (erreur de données)
        return AnneeAcademique.objects.filter(active=True).order_by('-id').first()

# ----------------------------------------------------------------------
# VUES GÉNÉRIQUES POUR L'ASSISTANT PÉDAGOGIQUE (CRUD)
# ----------------------------------------------------------------------

# Classe de base avec mixin de sécurité
class BaseAPView(AssistantPedaRequiredMixin):
    pass
    
# 1. Gestion des Matières (CRUD)
class MatiereListView(BaseAPView, ListView):
    model = Matiere
    template_name = 'gestion_cours/matiere_list.html'
    context_object_name = 'matieres'

class MatiereCreateView(BaseAPView, CreateView):
    model = Matiere
    form_class = MatiereForm
    template_name = 'gestion_cours/matiere_form.html'
    success_url = reverse_lazy('gestion_cours:matiere_list')

class MatiereUpdateView(BaseAPView, UpdateView):
    model = Matiere
    form_class = MatiereForm
    template_name = 'gestion_cours/matiere_form.html'
    success_url = reverse_lazy('gestion_cours:matiere_list')
    
class MatiereDeleteView(BaseAPView, DeleteView):
    model = Matiere
    template_name = 'gestion_cours/matiere_confirm_delete.html' 
    success_url = reverse_lazy('gestion_cours:matiere_list')
    context_object_name = 'matiere' 

# 2. Gestion des Professeurs (CRUD)
class ProfesseurListView(BaseAPView, ListView):
    """Affiche la liste de tous les professeurs."""
    model = Professeur
    template_name = 'gestion_cours/professeur_list.html'
    context_object_name = 'object_list' 

    def get_queryset(self):
        return Professeur.objects.all().order_by('nom')

class ProfesseurCreateView(BaseAPView, CreateView):
    """Gère la création d'un professeur."""
    model = Professeur
    fields = ['nom', 'prenoms', 'contact', 'email', 'grade', 'domaine', 'cv', 'dernier_diplome']
    template_name = 'gestion_cours/professeur_form.html'
    success_url = reverse_lazy('gestion_cours:professeur_list')

    def form_valid(self, form):
        messages.success(self.request, "Le professeur a été créé avec succès.")
        return super().form_valid(form)

class ProfesseurUpdateView(BaseAPView, UpdateView):
    """Gère la modification d'un professeur existant."""
    model = Professeur
    fields = ['nom', 'prenoms', 'contact', 'email', 'grade', 'domaine', 'cv', 'dernier_diplome']
    template_name = 'gestion_cours/professeur_form.html'
    success_url = reverse_lazy('gestion_cours:professeur_list')

    def form_valid(self, form):
        messages.success(self.request, "Le professeur a été modifié avec succès.")
        return super().form_valid(form)

class ProfesseurDeleteView(BaseAPView, DeleteView):
    """Gère la suppression d'un professeur."""
    model = Professeur
    template_name = 'gestion_cours/confirm_delete_base.html'
    success_url = reverse_lazy('gestion_cours:professeur_list')

    def form_valid(self, form):
        messages.success(self.request, f"Le professeur '{self.object}' a été supprimé définitivement.")
        return super().form_valid(form)

# 3. Création d'Emargement (Vue générique AP)
class EmargementCreateView(BaseAPView, CreateView):
    model = Emargement
    form_class = EmargementForm
    template_name = 'gestion_cours/emargement_form.html'
    success_url = reverse_lazy('gestion_cours:home') 


# ------------------ VUES CRUD FILIERE -------------------

class FiliereListView(BaseAPView, ListView):
    model = Filiere
    template_name = 'gestion_cours/filiere_list.html'
    context_object_name = 'object_list'

class FiliereCreateView(BaseAPView, CreateView):
    model = Filiere
    fields = ['code', 'libelle']
    template_name = 'gestion_cours/form_base.html' 
    success_url = reverse_lazy('gestion_cours:filiere_list')
    def form_valid(self, form):
        messages.success(self.request, "La Filière a été créée avec succès.")
        return super().form_valid(form)

class FiliereUpdateView(BaseAPView, UpdateView):
    model = Filiere
    fields = ['code', 'libelle']
    template_name = 'gestion_cours/form_base.html'
    success_url = reverse_lazy('gestion_cours:filiere_list')
    def form_valid(self, form):
        messages.success(self.request, "La Filière a été modifiée avec succès.")
        return super().form_valid(form)

class FiliereDeleteView(BaseAPView, DeleteView):
    model = Filiere
    template_name = 'gestion_cours/confirm_delete_base.html' 
    success_url = reverse_lazy('gestion_cours:filiere_list')
    def form_valid(self, form):
        messages.success(self.request, f"La Filière '{self.object}' a été supprimée.")
        return super().form_valid(form)


# ------------------ VUES CRUD NIVEAU -------------------

class NiveauListView(BaseAPView, ListView):
    model = Niveau
    template_name = 'gestion_cours/niveau_list.html'
    context_object_name = 'object_list'

class NiveauCreateView(BaseAPView, CreateView):
    model = Niveau
    fields = ['libelle', 'niv', 'filiere'] 
    template_name = 'gestion_cours/form_base.html'
    success_url = reverse_lazy('gestion_cours:niveau_list')
    def form_valid(self, form):
        messages.success(self.request, "Le Niveau a été créé avec succès.")
        return super().form_valid(form)

class NiveauUpdateView(BaseAPView, UpdateView):
    model = Niveau
    fields = ['libelle', 'niv', 'filiere']
    template_name = 'gestion_cours/form_base.html'
    success_url = reverse_lazy('gestion_cours:niveau_list')
    def form_valid(self, form):
        messages.success(self.request, "Le Niveau a été modifié avec succès.")
        return super().form_valid(form)

class NiveauDeleteView(BaseAPView, DeleteView):
    model = Niveau
    template_name = 'gestion_cours/confirm_delete_base.html'
    success_url = reverse_lazy('gestion_cours:niveau_list')
    def form_valid(self, form):
        messages.success(self.request, f"Le Niveau '{self.object}' a été supprimé.")
        return super().form_valid(form)


# ------------------ VUES CRUD ANNEE ACADEMIQUE -------------------

class AnneeAcademiqueListView(BaseAPView, ListView):
    model = AnneeAcademique
    template_name = 'gestion_cours/anneeacademique_list.html'
    context_object_name = 'object_list'

class AnneeAcademiqueCreateView(BaseAPView, CreateView):
    model = AnneeAcademique
    fields = ['annee_accademique', 'active']
    template_name = 'gestion_cours/form_base.html'
    success_url = reverse_lazy('gestion_cours:anneeacademique_list')
    def form_valid(self, form):
        messages.success(self.request, "L'Année Académique a été créée avec succès.")
        return super().form_valid(form)

class AnneeAcademiqueUpdateView(BaseAPView, UpdateView):
    model = AnneeAcademique
    fields = ['annee_accademique', 'active']
    template_name = 'gestion_cours/form_base.html'
    success_url = reverse_lazy('gestion_cours:anneeacademique_list')
    def form_valid(self, form):
        messages.success(self.request, "L'Année Académique a été modifiée avec succès.")
        return super().form_valid(form)

class AnneeAcademiqueDeleteView(BaseAPView, DeleteView):
    model = AnneeAcademique
    template_name = 'gestion_cours/confirm_delete_base.html'
    success_url = reverse_lazy('gestion_cours:anneeacademique_list')
    def form_valid(self, form):
        messages.success(self.request, f"L'Année Académique '{self.object}' a été supprimée.")
        return super().form_valid(form)

# ------------------ VUES CRUD MATIERE PROGRAMMEE (Cours) -------------------

class MatiereProgrammeeListView(BaseAPView, ListView):
    """Affiche la liste des cours programmés."""
    model = MatiereProgrammee
    template_name = 'gestion_cours/matiereprogrammee_list.html'
    context_object_name = 'object_list'
    
    def get_queryset(self):
        # Utilisation de la fonction centralisée
        annee_active = get_active_annee_academique()
        if not annee_active:
            # Si aucune année active, retourne un QuerySet vide
            messages.warning(self.request, "Attention : Aucune Année Académique active. Affichage de la liste vide.")
            return MatiereProgrammee.objects.none()

        # Filtre par l'année active
        return MatiereProgrammee.objects.filter(annee_academique=annee_active).select_related(
            'matiere', 'filiere', 'niveau', 'professeur', 'annee_academique'
        ).order_by('filiere__libelle', 'niveau__niv')


class MatiereProgrammeeCreateView(BaseAPView, CreateView):
    """Gère la création d'un cours programmé."""
    model = MatiereProgrammee
    form_class = MatiereProgrammeeForm
    template_name = 'gestion_cours/form_base.html'
    success_url = reverse_lazy('gestion_cours:matiereprogrammee_list')
    
    def form_valid(self, form):
        messages.success(self.request, "Le cours a été programmé avec succès.")
        return super().form_valid(form)


class MatiereProgrammeeUpdateView(BaseAPView, UpdateView):
    """Gère la modification d'un cours programmé existant."""
    model = MatiereProgrammee
    form_class = MatiereProgrammeeForm
    template_name = 'gestion_cours/form_base.html'
    success_url = reverse_lazy('gestion_cours:matiereprogrammee_list')
    
    def form_valid(self, form):
        messages.success(self.request, "La programmation du cours a été modifiée avec succès.")
        return super().form_valid(form)


class MatiereProgrammeeDeleteView(BaseAPView, DeleteView):
    """Gère la suppression d'un cours programmé."""
    model = MatiereProgrammee
    template_name = 'gestion_cours/confirm_delete_base.html'
    success_url = reverse_lazy('gestion_cours:matiereprogrammee_list')
    
    def form_valid(self, form):
        messages.success(self.request, f"Le cours '{self.object}' a été supprimé.")
        return super().form_valid(form)

# ------------------ VUE DE SÉLECTION POUR ÉMARGEMENT (Étape 1) -------------------
class EmargementSelectionCoursView(BaseAPView, ListView):
    """Liste tous les cours programmés pour l'année active afin de sélectionner celui à émarger."""
    model = MatiereProgrammee
    template_name = 'gestion_cours/emargement_selection_cours.html' 
    context_object_name = 'cours_list'
    
    def get_queryset(self):
        # Utilisation de la fonction centralisée
        annee_active = get_active_annee_academique()
        
        if not annee_active:
            messages.error(self.request, "Erreur : Aucune Année Académique active n'a été trouvée pour l'émargement.")
            return MatiereProgrammee.objects.none()
            
        # Annoter avec le total des heures faites pour affichage et calcul
        return MatiereProgrammee.objects.filter(annee_academique=annee_active).select_related(
            'matiere', 'professeur', 'niveau', 'filiere'
        ).annotate(
                total_heures_faites=Sum('emargement__heure_eff') 
        ).order_by('filiere__libelle', 'niveau__niv')
            
# ------------------ VUES CRUD EVALUATION -------------------

class EvaluationListView(BaseAPView, ListView):
    """Affiche la liste de toutes les évaluations qualitatives."""
    model = Evaluation
    template_name = 'gestion_cours/evaluation_list.html'
    context_object_name = 'evaluations'

    def get_queryset(self):
        annee_active = get_active_annee_academique()
        if not annee_active:
            messages.warning(self.request, "Attention : Aucune Année Académique active. Affichage de la liste d'évaluations vide.")
            return Evaluation.objects.none()

        # Filtre les Évaluations dont la MatiereProgrammee correspond à l'année active
        return Evaluation.objects.filter(
            matiere_programmer__annee_academique=annee_active
        ).select_related(
            'matiere_programmer', 
            'matiere_programmer__matiere', 
            'matiere_programmer__professeur',
            'utilisateur_evaluation'
        ).order_by('-id')

# VUE DE GESTION DES ÉVALUATIONS (Création/Modification)
@method_decorator(login_required, name='dispatch')
class EvaluationManagementView(BaseAPView, UpdateView):
    """Permet à l'AP d'ajouter ou de modifier l'évaluation qualitative d'un cours complété."""
    model = Evaluation
    form_class = EvaluationForm
    template_name = 'gestion_cours/evaluation_form.html'
    success_url = reverse_lazy('gestion_cours:home')

    # Redéfinir dispatch pour gérer la création/modification et la vérification 100%
    def dispatch(self, request, *args, **kwargs):
        # Utiliser la logique de permission de BaseAPView
        if not self.check_permissions(request):
            return self.handle_no_permission()

        self.matiere_prog = get_object_or_404(MatiereProgrammee, pk=kwargs.get('pk'))
        
        # Vérification 100%
        total_faites = Emargement.objects.filter(matiere_programmer=self.matiere_prog).aggregate(total_faites=Sum('heure_eff'))['total_faites'] or 0
        volume_prevu = float(self.matiere_prog.nbr_heure)
        progression = (float(total_faites) / volume_prevu) * 100 if volume_prevu > 0 else 0

        if progression < 100:
            messages.error(request, "Impossible d'évaluer : le cours n'a pas atteint 100% de progression.")
            return redirect('gestion_cours:home')

        # Si l'évaluation existe, on modifie (UpdateView), sinon on crée
        try:
            self.object = Evaluation.objects.get(matiere_programmer=self.matiere_prog)
        except Evaluation.DoesNotExist:
            self.object = None # Permet à form_valid de créer l'objet

        return super().dispatch(request, *args, **kwargs)

    def get_object(self, queryset=None):
        return self.object # Retourne l'instance existante ou None (pour la création)

    def get_initial(self):
        # Si on crée une nouvelle évaluation, on utilise initial. Si elle existe, l'instance s'en charge.
        initial = super().get_initial()
        if not self.object:
             initial['matiere_programmer'] = self.matiere_prog
        return initial

    def form_valid(self, form):
        evaluation = form.save(commit=False)
        evaluation.matiere_programmer = self.matiere_prog
        evaluation.utilisateur_evaluation = self.request.user 
        evaluation.save()
        messages.success(self.request, f"Évaluation qualitative enregistrée pour {self.matiere_prog.matiere.libelle}!")
        return redirect('gestion_cours:home')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['matiere_prog'] = self.matiere_prog
        context['mode_edition'] = self.object is not None
        
        # Calcul de la progression pour l'affichage (répété du dispatch, mais utile pour le contexte)
        total_faites = Emargement.objects.filter(matiere_programmer=self.matiere_prog).aggregate(total_faites=Sum('heure_eff'))['total_faites'] or 0
        volume_prevu = float(self.matiere_prog.nbr_heure)
        context['progression'] = (float(total_faites) / volume_prevu) * 100 if volume_prevu > 0 else 0
        
        return context

# ----------------------------------------------------------------------
# VUES FONCTIONNELLES (Landing, Tableau de Bord, Émargement, Historique)
# ----------------------------------------------------------------------

# VUE PUBLIQUE (LANDING PAGE) - AVEC REDIRECTION
def landing_page(request):
    """
    Affiche la page d'accueil publique. 
    Redirige les utilisateurs connectés vers le Tableau de Bord AP.
    """
    if request.user.is_authenticated:
        return redirect('gestion_cours:home') 

    stats = {
        'total_professeurs': Professeur.objects.count(),
        'total_matieres': Matiere.objects.count(),
        'total_heures': Emargement.objects.aggregate(Sum('heure_eff'))['heure_eff__sum'] or 0,
    }
    
    return render(request, 'gestion_cours/landing.html', {'stats': stats})


# Tableau de Bord principal AP (home_view)
@login_required
def home_view(request):
    """Affiche la liste des cours programmés pour l'année académique active et calcule la progression."""
    
    annee_active = get_active_annee_academique() # Utilisation de la fonction centralisée
    
    if not annee_active:
        messages.error(request, "Erreur : Aucune Année Académique n'est marquée comme active. Veuillez en activer une.")
        cours_list = []
        return render(request, 'gestion_cours/home.html', {'cours_list': cours_list})

    # 1. Récupérer les cours programmés et ANNOTER le total des heures faites (1 requête SQL)
    cours_list_queryset = MatiereProgrammee.objects.filter(annee_academique=annee_active).select_related(
        'matiere', 'professeur', 'filiere', 'niveau'
    ).annotate(
        niveau_complet=F('niveau__libelle'),
        total_heures_faites=Sum('emargement__heure_eff') 
    ).order_by('filiere__libelle', 'niveau__niv')
    
    aujourdhui = date.today()

    # 2. Calculer la progression et le retard pour chaque cours
    cours_traites = []
    for cours in cours_list_queryset: 
        # Vérifie si le cours a déjà été évalué
        cours.est_evalue = Evaluation.objects.filter(matiere_programmer=cours).exists() 
        
        # Le calcul complexe est délégué à la fonction utilitaire
        cours_traites.append(calculer_progression(cours, aujourdhui))
    
    cours_list = cours_traites 

    # Calcul des totaux de dashboard
    total_heures_enseignees = Emargement.objects.filter(
        matiere_programmer__annee_academique=annee_active
    ).aggregate(total=Sum('heure_eff'))['total'] or 0

    context = {
        'annee_active': annee_active,
        'cours_list': cours_list,
        'heures_enseignees': total_heures_enseignees,
        'matieres_actives': Matiere.objects.count(),
        'professeurs_actifs': Professeur.objects.count(),
    }

    return render(request, 'gestion_cours/home.html', context)


# L'utilisateur DOIT être connecté pour gérer l'émargement
@login_required
def emargement_view(request, pk):
    """Gère l'affichage et la soumission du formulaire d'émargement, avec contrôle strict de l'heure totale, et enregistre l'utilisateur AP."""
    
    # 1. Récupère la MatiereProgrammee avec le total des heures faites
    matiere_prog = get_object_or_404(
        MatiereProgrammee.objects.annotate(
            total_heures_faites=Sum('emargement__heure_eff')
        ).select_related('matiere', 'professeur', 'niveau', 'filiere'),
        pk=pk
    )
    
    annee_active = get_active_annee_academique() # Utilisation de la fonction centralisée
    if not annee_active:
        messages.error(request, "Impossible d'émarger : Aucune année académique active trouvée.")
        return redirect('gestion_cours:home')

    if matiere_prog.annee_academique != annee_active:
        messages.error(request, "Erreur : La matière sélectionnée n'est pas programmée pour l'année académique active.")
        return redirect('gestion_cours:home')

    # Calcul des volumes
    volume_prevu = matiere_prog.nbr_heure
    heures_faites_actuelles = matiere_prog.total_heures_faites or Decimal('0.00')
    
    volume_prevant_decimal = Decimal(str(volume_prevu))
    volume_restant = volume_prevant_decimal - heures_faites_actuelles
    volume_restant = volume_restant.quantize(Decimal('0.01'))
    volume_restant_float = float(volume_restant)
    
    # Initialisation du formulaire
    initial_data = {'date_emar': timezone.now().date()}
    # Initialisation du formulaire pour le GET ou le POST
    form = EmargementForm(request.POST or None, initial=initial_data) # <--- CORRIGÉ POUR INITIALISER AVANT LE CONTEXT

    # Initialisation du contexte pour le POST/GET
    # Le contexte est completé ici, il pourra être utilisé dans tous les chemins de retour (GET, POST valide, POST invalide)
    context = {
        'matiere_prog': matiere_prog,
        'form': form,
        'volume_restant': volume_restant, 
    }

    if request.method == 'POST':
        # Le formulaire a déjà été initialisé avec request.POST
        if form.is_valid():
            
            # Récupération des données du formulaire
            date_emar = form.cleaned_data['date_emar'] 
            heure_eff_saisie = float(form.cleaned_data['heure_eff'])

            # --- VÉRIFICATION D'UNICITÉ ---
            if Emargement.objects.filter(matiere_programmer=matiere_prog, date_emar=date_emar).exists():
                 messages.error(request, f"Échec de l'émargement : La matière {matiere_prog.matiere.libelle} a déjà été émargée à la date du {date_emar}.")
                 # Renvoyer le formulaire et le contexte pour réafficher la page SANS REDIRECTION
                 return render(request, 'gestion_cours/emargement_form.html', context)

            # --- LOGIQUE DE VALIDATION DES HEURES ---
            if heure_eff_saisie <= 0 or heure_eff_saisie > 8:
                messages.error(request, "Erreur: La durée du cours doit être comprise entre 0 et 8 heures.")
                return render(request, 'gestion_cours/emargement_form.html', context)

            if volume_restant_float <= 0:
                 messages.error(request, f"Échec de l'émargement : Le volume horaire prévu de {volume_prevu}h est déjà atteint ou dépassé ({heures_faites_actuelles:.2f}h).")
                 return render(request, 'gestion_cours/emargement_form.html', context)

            if heure_eff_saisie > volume_restant_float:
                 messages.error(request, f"Échec de l'émargement : La durée saisie ({heure_eff_saisie:.2f}h) dépasse le volume restant ({volume_restant_float:.2f}h). Veuillez ajuster votre saisie.")
                 return render(request, 'gestion_cours/emargement_form.html', context)
            
            # --- CRÉATION DE L'OBJET EMERARGEMENT (CORRIGÉE) ---
            emargement_obj = form.save(commit=False)
            emargement_obj.matiere_programmer = matiere_prog
            emargement_obj.emarge_par = request.user # 👈 ENREGISTRE L'UTILISATEUR CONNECTÉ
            emargement_obj.save()
            
            messages.success(request, f"Séance d'émargement du {date_emar} (durée: {heure_eff_saisie:.2f}h) enregistrée avec succès.")
            
            return redirect('gestion_cours:emargement_selection_cours') 
            
        else:
            # Erreur de formulaire (champs manquants/invalides)
            messages.error(request, "Erreur de formulaire. Veuillez vérifier les champs.")
            # Le contexte contient le formulaire invalide et les autres données
            return render(request, 'gestion_cours/emargement_form.html', context)

    # Cas GET (Affichage initial du formulaire)
    # Le contexte contient déjà le formulaire initialisé (vide)
    return render(request, 'gestion_cours/emargement_form.html', context)


# L'utilisateur DOIT être un AP ou Super-utilisateur pour voir l'historique global
@login_required
@user_passes_test(est_administrateur_pedagogique, login_url=reverse_lazy('gestion_cours:home'))
def historique_view(request):
    """Affiche l'historique des émargements pour l'année académique active, AVEC FILTRES."""

    annee_active = get_active_annee_academique()
    
    if not annee_active:
        messages.warning(request, "Impossible d'afficher l'historique : Aucune année académique active trouvée.")
        historique = Emargement.objects.none() # QuerySet vide
        # Le filtre est quand même créé pour passer au template, mais sur un queryset vide
        emargement_filter = EmargementFilter(request.GET, queryset=historique)
        
    else:
        # 1. Base du QuerySet (Filtré par année active)
        queryset = Emargement.objects.filter(
            matiere_programmer__annee_academique=annee_active
        ).select_related(
            'matiere_programmer__professeur', 
            'matiere_programmer__matiere'
        ).order_by('-date_emar')

        # 2. Appliquer les filtres
        emargement_filter = EmargementFilter(request.GET, queryset=queryset)
        historique = emargement_filter.qs # Le QuerySet filtré

        # 3. Limiter à 50 seulement si AUCUN filtre n'est appliqué (pas de paramètres GET)
        if not request.GET: 
            historique = historique[:50] 
        
    context = {
        'historique': historique,
        'filter': emargement_filter, # <-- IMPORTANT : Passer l'objet filtre au template
        'annee_active': annee_active.annee_accademique if annee_active else 'N/A'
    }
    return render(request, 'gestion_cours/historique_global.html', context)


# -----------------------------------------------------------------------------------
# VUE DÉTAILLÉE DE L'HISTORIQUE D'UN COURS
# -----------------------------------------------------------------------------------

# L'utilisateur DOIT être un AP ou Super-utilisateur pour voir l'historique
@login_required
@user_passes_test(est_administrateur_pedagogique, login_url=reverse_lazy('gestion_cours:home'))
def historique_cours_view(request, pk):
    """Affiche l'historique détaillé des émargements pour un cours programmé spécifique."""
    
    # 1. Récupère le cours avec toutes les relations nécessaires pour l'affichage
    matiere_prog = get_object_or_404(MatiereProgrammee.objects.select_related(
        'matiere', 'professeur', 'niveau', 'filiere', 'annee_academique'
    ).annotate(
        total_heures_faites=Sum('emargement__heure_eff') 
    ), pk=pk)
    
    # 2. Récupère tous les émargements pour ce cours, triés par date décroissante
    historique_emargement_list = Emargement.objects.filter(
        matiere_programmer=matiere_prog
    ).order_by('-date_emar')

    # 3. Calcule la progression pour l'affichage
    progression_details = calculer_progression(matiere_prog, date.today())
    
    # 4. Récupère l'évaluation (pour la section conditionnelle du template)
    try:
        evaluation = Evaluation.objects.get(matiere_programmer=matiere_prog)
    except Evaluation.DoesNotExist:
        evaluation = None

    context = {
        'matiere_prog': matiere_prog,
        'historique_emargement': historique_emargement_list,
        'progression_details': progression_details, 
        'evaluation': evaluation,
    }
    return render(request, 'gestion_cours/historique_cours.html', context)