from django.db import models

# --- MODÈLES INCHANGÉS ---

# Modèle pour les Professeurs
class Professeur(models.Model):
    STATUS_CHOICES = [
        ('PERMANENT', 'Permanent'),
        ('CONTRACTUEL', 'Contractuel'),
        ('VACATAIRE', 'Vacataire'),
    ]
    
    nom = models.CharField(max_length=100)
    prenoms = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    telephone = models.CharField(max_length=20, blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PERMANENT')
    domaine_enseignement = models.CharField(max_length=150, blank=True, null=True)

    def __str__(self):
        return f"{self.nom} {self.prenoms}"
    
    class Meta:
        verbose_name_plural = "Professeurs"
        ordering = ['nom']

# Modèle pour les Filières (Ex: Génie Informatique, Finance)
class Filiere(models.Model):
    code = models.CharField(max_length=10, unique=True)
    libelle = models.CharField(max_length=150)

    def __str__(self):
        return self.libelle

    class Meta:
        verbose_name_plural = "Filières"
        
# Modèle pour les Niveaux (Ex: Licence 1, Master 2)
class Niveau(models.Model):
    libelle = models.CharField(max_length=50) # Ex: Licence, Master
    filiere = models.ForeignKey(Filiere, on_delete=models.CASCADE)
    niv = models.IntegerField(default=1) # Le numéro du niveau (1, 2, 3...)
    
    def __str__(self):
        return f"{self.libelle} {self.niv} - {self.filiere.code}"

    class Meta:
        verbose_name_plural = "Niveaux"
        unique_together = ('libelle', 'filiere', 'niv') # Un niveau unique par filière

# Modèle pour les Matières (Ex: Algorithmique, Chinois)
class Matiere(models.Model):
    libelle = models.CharField(max_length=150, unique=True)
    
    def __str__(self):
        return self.libelle

    class Meta:
        verbose_name_plural = "Matières"

# Modèle pour les Années Académiques
class AnneeAcademique(models.Model):
    annee_accademique = models.CharField(max_length=20, unique=True) # Ex: 2024-2025
    active = models.BooleanField(default=False) # Indique si c'est l'année en cours pour l'émargement
    annee_encours = models.BooleanField(default=False) # Permet de marquer l'année en cours (statistiques)

    # Logique pour garantir une seule année active à la fois
    def save(self, *args, **kwargs):
        if self.active:
            # Désactive toutes les autres années si celle-ci devient active
            AnneeAcademique.objects.filter(active=True).exclude(pk=self.pk).update(active=False)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.annee_accademique

    class Meta:
        verbose_name_plural = "Années Académiques"
        
# Modèle pour la programmation d'une matière (Le cours réel)
class MatiereProgrammee(models.Model):
    matiere = models.ForeignKey(Matiere, on_delete=models.CASCADE)
    professeur = models.ForeignKey(Professeur, on_delete=models.CASCADE)
    filiere = models.ForeignKey(Filiere, on_delete=models.CASCADE)
    niveau = models.ForeignKey(Niveau, on_delete=models.CASCADE)
    annee_academique = models.ForeignKey(AnneeAcademique, on_delete=models.CASCADE)
    
    # Nombre d'heures prévues pour ce cours dans l'année
    nbr_heure = models.DecimalField(max_digits=5, decimal_places=2) 
    date_debut_estimee = models.DateField(blank=True, null=True)
    # NOUVEAU CHAMP pour le calcul de la progression théorique
    date_fin_estimee = models.DateField(blank=True, null=True) 

    def __str__(self):
        return f"{self.matiere.libelle} - {self.niveau.libelle} {self.niveau.niv} ({self.filiere.code})"

    class Meta:
        verbose_name_plural = "Matières Programmées"
        unique_together = ('matiere', 'filiere', 'niveau', 'annee_academique')

# Modèle pour l'Emargement (Feuille de présence)
class Emargement(models.Model):
    matiere_programmer = models.ForeignKey(MatiereProgrammee, on_delete=models.CASCADE)
    date_emar = models.DateField()
    
    # Heure effective (Saisie directement par l'utilisateur comme une durée)
    heure_eff = models.DecimalField(max_digits=4, decimal_places=2)
    

    def __str__(self):
        return f"Émargement du {self.date_emar} pour {self.matiere_programmer}"

    class Meta:
        verbose_name_plural = "Émargements"
        unique_together = ('matiere_programmer', 'date_emar')

# --- NOUVEAU MODÈLE D'ÉVALUATION (Revue Qualitative) ---
class Evaluation(models.Model):
    # La contrainte unique=True garantit qu'il n'y a qu'une seule évaluation par MatiereProgrammee
    matiere_programmer = models.ForeignKey(MatiereProgrammee, on_delete=models.CASCADE, unique=True) 
    
    # CHAMPS DE TEXTE POUR L'ÉVALUATION QUALITATIVE
    resume_evaluation = models.TextField(verbose_name="Résumé de l'Évaluation du Cours")
    resume_ap = models.TextField(verbose_name="Appréciation de l'Assistant Pédagogique (AP)")
    recommandation = models.TextField(verbose_name="Recommandations et Suggestions")
    
    # Les anciens champs type_evaluation, note, coefficient sont supprimés.

    def __str__(self):
        return f"Évaluation qualitative de {self.matiere_programmer.matiere.libelle}"
        
    class Meta:
        verbose_name_plural = "Évaluations"

