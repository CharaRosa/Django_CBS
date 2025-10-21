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
    return user.groups.filter(name='ADMIN_PEDAGOGIQUE').exists() or user.is_superuser
# ---------------------------------------

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
        # Optimisation : Récupérer les données de toutes les clés étrangères en une seule requête
        return MatiereProgrammee.objects.select_related(
            'matiere', 'filiere', 'niveau', 'professeur', 'annee_academique'
        ).order_by('-annee_academique__active', 'filiere__libelle', 'niveau__niv')

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
        try:
            # Filtre les cours de l'année active
            annee_active = AnneeAcademique.objects.get(active=True)
            # Annoter avec le total des heures faites pour affichage et calcul
            return MatiereProgrammee.objects.filter(annee_academique=annee_active).select_related(
                'matiere', 'professeur', 'niveau', 'filiere'
            ).annotate(
                 total_heures_faites=Sum('emargement__heure_eff') 
            ).order_by('filiere__libelle', 'niveau__niv')
            
        except AnneeAcademique.DoesNotExist:
            messages.error(self.request, "Erreur : Aucune Année Académique active n'a été trouvée pour l'émargement.")
            return MatiereProgrammee.objects.none()
            
# ----------------------------------------------------------------------
# VUES FONCTIONNELLES (Landing, Tableau de Bord, Émargement, Évaluation, Historique)
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
    
    annee_active = AnneeAcademique.objects.filter(active=True).first()
    
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
    """Gère l'affichage et la soumission du formulaire d'émargement, avec contrôle strict de l'heure totale."""
    
    # 1. MODIFICATION: ANNOTER matiere_prog AVEC LE TOTAL DES HEURES FAITES
    matiere_prog = get_object_or_404(
        MatiereProgrammee.objects.annotate(
            total_heures_faites=Sum('emargement__heure_eff')
        ).select_related('matiere', 'professeur', 'niveau', 'filiere'),
        pk=pk
    )
    
    annee_active = AnneeAcademique.objects.filter(active=True).first()
    if not annee_active:
        messages.error(request, "Impossible d'émarger : Aucune année académique active trouvée.")
        return redirect('gestion_cours:home')

    if matiere_prog.annee_academique != annee_active:
        messages.error(request, "Erreur : La matière sélectionnée n'est pas programmée pour l'année académique active.")
        return redirect('gestion_cours:home')

    # Étant donné que cette vue est pour la CRÉATION, on ne cherche pas d'instance existante
    initial_data = {'date_emar': timezone.now().date()}
    form = EmargementForm(request.POST or None, initial=initial_data) # Simplification: pas d'instance
    
    # --- CALCUL DU VOLUME RESTANT (Correction pour utiliser Decimal) ---
    volume_prevu = matiere_prog.nbr_heure
    
    # 2. MODIFICATION: UTILISER DIRECTEMENT L'ANNOTATION POUR LA LOGIQUE
    # Nous utilisons matiere_prog.total_heures_faites qui est maintenant une Decimal (ou None)
    heures_faites_actuelles = matiere_prog.total_heures_faites or Decimal('0.00')

    # 3. Calculer le volume restant
    # volume_prevu est un DecimalField/FloatField du modèle, nous le convertissons si nécessaire,
    # ou nous supposons qu'il est déjà un Decimal pour une soustraction précise.
    volume_prevant_decimal = Decimal(str(volume_prevu)) # Conversion explicite au cas où nbr_heure est Float
    
    volume_restant = volume_prevant_decimal - heures_faites_actuelles
    volume_restant = volume_restant.quantize(Decimal('0.01')) # Arrondir à deux décimales (Decimal)
    volume_restant_float = float(volume_restant) # Utiliser la version float pour les comparaisons dans la validation ci-dessous (si nécessaire)
    # ----------------------------------------------------------------------
    
    if request.method == 'POST':
        if form.is_valid():
            
            # Récupération des données du formulaire
            date_emar = form.cleaned_data['date_emar'] 
            heure_eff_saisie = float(form.cleaned_data['heure_eff']) # Conversion en float pour les comparaisons directes

            # --- VÉRIFICATION D'UNICITÉ MANUELLE ---
            if Emargement.objects.filter(matiere_programmer=matiere_prog, date_emar=date_emar).exists():
                 messages.error(request, f"Échec de l'émargement : La matière {matiere_prog.matiere.libelle} a déjà été émargée à la date du {date_emar}.")
                 return render(request, 'gestion_cours/emargement_form.html', {'matiere_prog': matiere_prog, 'form': form, 'volume_restant': volume_restant})

            # --- LOGIQUE DE VALIDATION DES HEURES ---
            if heure_eff_saisie <= 0 or heure_eff_saisie > 8:
                messages.error(request, "Erreur: La durée du cours doit être comprise entre 0 et 8 heures.")
                return render(request, 'gestion_cours/emargement_form.html', {'matiere_prog': matiere_prog, 'form': form, 'volume_restant': volume_restant})

            # Utiliser la version float pour la validation
            if volume_restant_float <= 0:
                 messages.error(request, f"Échec de l'émargement : Le volume horaire prévu de {volume_prevu}h est déjà atteint ou dépassé ({heures_faites_actuelles:.2f}h).")
                 return render(request, 'gestion_cours/emargement_form.html', {'matiere_prog': matiere_prog, 'form': form, 'volume_restant': volume_restant})

            if heure_eff_saisie > volume_restant_float:
                 messages.error(request, f"Échec de l'émargement : La durée saisie ({heure_eff_saisie:.2f}h) dépasse le volume restant ({volume_restant_float:.2f}h). Veuillez ajuster votre saisie.")
                 return render(request, 'gestion_cours/emargement_form.html', {'matiere_prog': matiere_prog, 'form': form, 'volume_restant': volume_restant})
            
            # --- CRÉATION DE L'OBJET EMERARGEMENT ---
            emargement_obj = form.save(commit=False)
            emargement_obj.matiere_programmer = matiere_prog
            emargement_obj.save()
            
            messages.success(request, f"Séance d'émargement du {date_emar} (durée: {heure_eff_saisie:.2f}h) enregistrée avec succès.")
            
            return redirect('gestion_cours:emargement_selection_cours') 
            
        else:
            messages.error(request, "Erreur de formulaire. Veuillez vérifier les champs.")

    context = {
        'matiere_prog': matiere_prog,
        'form': form,
        # AJOUTER CETTE VARIABLE AU CONTEXTE
        'volume_restant': volume_restant, 
    }
    return render(request, 'gestion_cours/emargement_form.html', context)


# Seul l'Administrateur Pédagogique ou le Super-utilisateur peut évaluer un cours
@login_required
@user_passes_test(est_administrateur_pedagogique, login_url='/') 
def evaluation_view(request, pk):
    """Permet d'ajouter ou de modifier l'évaluation qualitative d'un cours complété."""
    
    matiere_prog = get_object_or_404(MatiereProgrammee, pk=pk)
    
    # 1. Vérifier si le cours est à 100% (Sécurité)
    total_faites = float(Emargement.objects.filter(matiere_programmer=matiere_prog).aggregate(total_faites=Sum('heure_eff'))['total_faites'] or 0)
    volume_prevu = float(matiere_prog.nbr_heure)
    progression = min(100, (total_faites / volume_prevu) * 100) if volume_prevu > 0 else 0

    if progression < 100:
        messages.error(request, "Impossible d'évaluer : le cours n'a pas atteint 100% de progression.")
        return redirect('gestion_cours:home')

    # 2. Récupérer l'évaluation existante (si elle existe)
    try:
        instance = Evaluation.objects.get(matiere_programmer=matiere_prog)
    except Evaluation.DoesNotExist:
        instance = None
    
    if request.method == 'POST':
        form = EvaluationForm(request.POST, instance=instance)
        if form.is_valid():
            evaluation = form.save(commit=False)
            evaluation.matiere_programmer = matiere_prog
            evaluation.utilisateur_evaluation = request.user 
            evaluation.save()
            messages.success(request, f"Évaluation qualitative enregistrée pour {matiere_prog.matiere.libelle}!")
            return redirect('gestion_cours:home')
        else:
             messages.error(request, "Erreur de formulaire. Veuillez vérifier les informations saisies.")

    else:
        form = EvaluationForm(instance=instance)

    context = {
        'matiere_prog': matiere_prog,
        'form': form,
        'progression': progression,
        'mode_edition': instance is not None,
    }
    return render(request, 'gestion_cours/evaluation_form.html', context)


# L'utilisateur DOIT être un AP ou Super-utilisateur pour voir l'historique
@login_required
@user_passes_test(est_administrateur_pedagogique, login_url='/')
def historique_view(request):
    """Affiche l'historique des émargements pour l'année académique active."""

    annee_active = AnneeAcademique.objects.filter(active=True).first()
    
    if not annee_active:
        messages.warning(request, "Impossible d'afficher l'historique : Aucune année académique active trouvée.")
        historique = []
        return render(request, 'gestion_cours/historique.html', {'historique': historique})
        
    historique = Emargement.objects.filter(
        matiere_programmer__annee_academique=annee_active
    ).select_related(
        'matiere_programmer__professeur', 
        'matiere_programmer__matiere'
    ).order_by('-date_emar')[:50] 
    
    context = {
        'historique': historique
    }
    return render(request, 'gestion_cours/historique.html', context)