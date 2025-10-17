from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import F, Sum, Count # Ajout de Count pour la vue tableau_de_bord_ap (ancien)
from django.utils import timezone
from datetime import date 
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator 
from .models import Matiere, Professeur, Emargement, MatiereProgrammee, AnneeAcademique, Evaluation
# Assurez-vous d'avoir MatiereProgrammeeForm si vous l'utilisez
from .forms import MatiereForm, ProfesseurForm, EmargementForm, EvaluationForm 
from .mixins import AssistantPedaRequiredMixin # Ce mixin doit être défini dans .mixins

# --- Fonctions de test de permission ---
def est_administrateur_pedagogique(user):
    """Vérifie si l'utilisateur appartient au groupe ADMIN_PEDAGOGIQUE ou est super-utilisateur."""
    # Assurez-vous que 'ADMIN_PEDAGOGIQUE' est le nom exact de votre groupe.
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
    model = Professeur
    template_name = 'gestion_cours/professeur_list.html'
    context_object_name = 'professeurs'

class ProfesseurCreateView(BaseAPView, CreateView):
    model = Professeur
    form_class = ProfesseurForm
    template_name = 'gestion_cours/professeur_form.html'
    success_url = reverse_lazy('gestion_cours:professeur_list')

class ProfesseurUpdateView(BaseAPView, UpdateView):
    model = Professeur
    form_class = ProfesseurForm
    template_name = 'gestion_cours/professeur_form.html'
    success_url = reverse_lazy('gestion_cours:professeur_list')

class ProfesseurDeleteView(BaseAPView, DeleteView):
    model = Professeur
    # Utilisation d'un template générique pour la suppression si 'professeur_confirm_delete.html' n'existe pas
    template_name = 'gestion_cours/professeur_confirm_delete.html' 
    success_url = reverse_lazy('gestion_cours:professeur_list')
    context_object_name = 'professeur' 

# 3. Création d'Emargement (Vue générique AP)
class EmargementCreateView(BaseAPView, CreateView):
    model = Emargement
    form_class = EmargementForm
    template_name = 'gestion_cours/emargement_form.html'
    # Redirige vers la vue principale du tableau de bord
    success_url = reverse_lazy('gestion_cours:home') 


# ----------------------------------------------------------------------
# VUES FONCTIONNELLES (Tableau de Bord, Émargement, Évaluation, Historique)
# ----------------------------------------------------------------------

# La vue 'home_view' prend le rôle de 'tableau_de_bord_ap' en affichant la progression
@login_required
def home_view(request):
    """Affiche la liste des cours programmés pour l'année académique active et calcule la progression."""
    
    annee_active = AnneeAcademique.objects.filter(active=True).first()
    
    if not annee_active:
        messages.error(request, "Erreur : Aucune Année Académique n'est marquée comme active. Veuillez en activer une.")
        cours_list = []
        return render(request, 'gestion_cours/home.html', {'cours_list': cours_list})

    # 2. Récupérer les cours programmés pour cette année (Filtrage)
    cours_list = MatiereProgrammee.objects.filter(annee_academique=annee_active).select_related(
        'matiere', 'professeur', 'filiere', 'niveau'
    ).annotate(
        niveau_complet=F('niveau__libelle'),
        total_heures_faites=Sum('emargement__heure_eff')
    ).order_by('filiere__libelle', 'niveau__niv')
    
    aujourdhui = date.today()

    # 3. Calculer la progression et le retard pour chaque cours
    for cours in cours_list:
        total_faites = float(cours.total_heures_faites or 0)
        volume_prevu = float(cours.nbr_heure)

        # Progression Réelle
        if volume_prevu > 0:
            cours.progression_reelle = min(100, (total_faites / volume_prevu) * 100)
        else:
            cours.progression_reelle = 0
            
        cours.heures_restantes = volume_prevu - total_faites
        
        # Initialisation du statut de retard/alerte
        cours.progression_theorique = None
        cours.decalage = None
        cours.alerte_retard = False
        cours.est_evalue = Evaluation.objects.filter(matiere_programmer=cours).exists() 

        # Progression Théorique et Décalage
        if cours.date_debut_estimee and cours.date_fin_estimee:
            duree_totale_jours = (cours.date_fin_estimee - cours.date_debut_estimee).days
            
            if duree_totale_jours > 0:
                if aujourdhui < cours.date_debut_estimee:
                    jours_ecoules = 0
                elif aujourdhui > cours.date_fin_estimee:
                    jours_ecoules = duree_totale_jours 
                else:
                    jours_ecoules = (aujourdhui - cours.date_debut_estimee).days

                cours.progression_theorique = min(100, (jours_ecoules / duree_totale_jours) * 100)
            else:
                cours.progression_theorique = 100 

            # Décalage : progression théorique - progression réelle
            cours.decalage = cours.progression_theorique - cours.progression_reelle
            
            # LOGIQUE D'ALERTE DE RETARD (Basée sur l'Urgence)
            jours_restants = (cours.date_fin_estimee - aujourdhui).days

            if cours.decalage > 0: 
                if jours_restants <= 7 and jours_restants >= 0 and cours.progression_reelle < 75:
                    cours.alerte_retard = True
                elif jours_restants < 0 and cours.progression_reelle < 100:
                    cours.alerte_retard = True 


    context = {
        'annee_active': annee_active,
        'cours_list': cours_list,
    }
    # Ajout des données du tableau de bord AP simple (du premier bloc) pour le template 'home.html' si nécessaire
    context['heures_enseignees'] = Emargement.objects.aggregate(total=Sum('heure_eff'))['total'] or 0
    context['matieres_actives'] = Matiere.objects.count()
    context['professeurs_actifs'] = Professeur.objects.count()

    return render(request, 'gestion_cours/home.html', context)


# L'utilisateur DOIT être connecté pour gérer l'émargement
@login_required
def emargement_view(request, pk):
    """Gère l'affichage et la soumission du formulaire d'émargement, avec contrôle strict de l'heure totale."""
    
    matiere_prog = get_object_or_404(MatiereProgrammee, pk=pk)
    
    annee_active = AnneeAcademique.objects.filter(active=True).first()
    if not annee_active:
        messages.error(request, "Impossible d'émarger : Aucune année académique active trouvée.")
        return redirect('gestion_cours:home')

    if matiere_prog.annee_academique != annee_active:
        messages.error(request, "Erreur : La matière sélectionnée n'est pas programmée pour l'année académique active.")
        return redirect('gestion_cours:home')

    # Initialisation de date_emar (dans le formulaire, ce sera date_emar)
    initial_data = {'date_emar': timezone.now().date()}
    form = EmargementForm(request.POST) if request.method == 'POST' else EmargementForm(initial=initial_data)
    volume_prevu = matiere_prog.nbr_heure
    
    heures_faites_obj = Emargement.objects.filter(matiere_programmer=matiere_prog).aggregate(total_faites=Sum('heure_eff'))
    heures_faites_actuelles = heures_faites_obj['total_faites'] or 0
    heures_restantes = float(volume_prevu) - float(heures_faites_actuelles)
    
    if request.method == 'POST':
        if form.is_valid():
            
            # Les champs sont lus directement du formulaire
            date_emar = form.cleaned_data['date_emar'] 
            heure_eff_saisie = float(form.cleaned_data['duree_saisie'])

            # --- VÉRIFICATION D'UNICITÉ MANUELLE (CORRECTION POUR L'APPROCHE fields=[]) ---
            if Emargement.objects.filter(matiere_programmer=matiere_prog, date_emar=date_emar).exists():
                 messages.error(request, f"Échec de l'émargement : La matière {matiere_prog.matiere.libelle} a déjà été émargée à la date du {date_emar}.")
                 return render(request, 'gestion_cours/emargement_form.html', {'matiere_prog': matiere_prog, 'form': form, 'volume_restant': heures_restantes})
            # -------------------------------------------------------------------------------

            # --- LOGIQUE DE VALIDATION DES HEURES ---
            if heure_eff_saisie <= 0 or heure_eff_saisie > 8:
                messages.error(request, "Erreur: La durée du cours doit être comprise entre 0 et 8 heures.")
                return render(request, 'gestion_cours/emargement_form.html', {'matiere_prog': matiere_prog, 'form': form, 'volume_restant': heures_restantes})

            if heures_restantes <= 0:
                 messages.error(request, f"Échec de l'émargement : Le volume horaire prévu de {volume_prevu}h est déjà atteint ou dépassé ({heures_faites_actuelles:.2f}h).")
                 return render(request, 'gestion_cours/emargement_form.html', {'matiere_prog': matiere_prog, 'form': form, 'volume_restant': heures_restantes})

            if heure_eff_saisie > heures_restantes:
                 messages.error(request, f"Échec de l'émargement : La durée saisie ({heure_eff_saisie:.2f}h) dépasse le volume restant ({heures_restantes:.2f}h). Veuillez ajuster votre saisie.")
                 return render(request, 'gestion_cours/emargement_form.html', {'matiere_prog': matiere_prog, 'form': form, 'volume_restant': heures_restantes})
            
            # --- CRÉATION DE L'OBJET EMERARGEMENT ---
            Emargement.objects.create(
                matiere_programmer=matiere_prog,
                date_emar=date_emar,
                heure_eff=heure_eff_saisie,
            )
            
            messages.success(request, f"Émargement réussi pour {matiere_prog.matiere.libelle} (Durée: {heure_eff_saisie:.2f} heures)!")
            
            return redirect('gestion_cours:home')
            
        else:
            messages.error(request, "Erreur de formulaire. Veuillez vérifier les champs.")

    context = {
        'matiere_prog': matiere_prog,
        'form': form,
        'volume_restant': heures_restantes,
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
            # Enregistre l'utilisateur connecté
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