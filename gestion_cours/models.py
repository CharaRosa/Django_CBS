from django.db import models
from django.contrib.auth import get_user_model 

# Récupérer le modèle User actif
User = get_user_model() 

# ----------------------------------------------------------------------
# MODÈLES DE BASE (Référentiels)
# ----------------------------------------------------------------------

# Modèle pour les Professeurs - MISE À JOUR
class Professeur(models.Model):
    # Champs existants
    nom = models.CharField(max_length=100)
    prenoms = models.CharField(max_length=150)
    contact = models.CharField(max_length=50, unique=True)
    email = models.EmailField(unique=True)
    
    # Nouveaux Champs
    grade = models.CharField(
        max_length=100, 
        null=True, 
        blank=True,
        verbose_name="Grade universitaire"
    )
    domaine = models.CharField(
        max_length=100, 
        null=True, 
        blank=True,
        verbose_name="Domaine d'expertise"
    )
    cv = models.FileField(
        upload_to='professeurs/cvs/', 
        null=True, 
        blank=True,
        verbose_name="CV (Fichier)"
    )
    dernier_diplome = models.FileField(
        upload_to='professeurs/diplomes/', 
        null=True, 
        blank=True,
        verbose_name="Dernier Diplôme (Fichier)"
    )
    
    def __str__(self):
        return f"{self.nom} {self.prenoms}"
    
    class Meta:
        verbose_name = "Professeur"
        verbose_name_plural = "Professeurs"
        ordering = ['nom']

# Modèle pour les Filières (Ex: Génie Informatique, Finance)
class Filiere(models.Model):
    code = models.CharField(max_length=10, unique=True)
    libelle = models.CharField(max_length=100)
    
    def __str__(self):
        return self.libelle

    class Meta:
        verbose_name_plural = "Filières"
        
# Modèle pour les Niveaux (Ex: Licence 1, Master 2)
class Niveau(models.Model):
    LIBELLE_CHOICES = [
        ('Licence', 'Licence'),
        ('Master', 'Master'),
    ]
    libelle = models.CharField(max_length=10, choices=LIBELLE_CHOICES)
    niv = models.IntegerField() # 1, 2 ou 3
    filiere = models.ForeignKey(Filiere, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.libelle} {self.niv} - {self.filiere.code}"

    class Meta:
        verbose_name_plural = "Niveaux"
        unique_together = ('libelle', 'filiere', 'niv')

# Modèle pour les Matières (Ex: Algorithmique, Chinois)
class Matiere(models.Model):
    code = models.CharField(max_length=10, unique=True)
    libelle = models.CharField(max_length=100)
    
    def __str__(self):
        return self.libelle

    class Meta:
        verbose_name_plural = "Matières"

# Modèle pour les Années Académiques
class AnneeAcademique(models.Model):
    annee_accademique = models.CharField(max_length=10, unique=True)
    active = models.BooleanField(default=False)
    
    def save(self, *args, **kwargs):
        # Assure qu'une seule année est active à la fois
        if self.active:
            AnneeAcademique.objects.filter(active=True).exclude(pk=self.pk).update(active=False)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.annee_accademique

    class Meta:
        verbose_name_plural = "Années Académiques"
        
# ----------------------------------------------------------------------
# MODÈLES DE GESTION DES COURS
# ----------------------------------------------------------------------

# Modèle pour la programmation d'une matière (Le cours réel)
class MatiereProgrammee(models.Model):
    SEMESTRE_CHOICES = [
        ('S1', 'Semestre 1'),
        ('S2', 'Semestre 2'),
    ]

    matiere = models.ForeignKey(Matiere, on_delete=models.CASCADE)
    filiere = models.ForeignKey(Filiere, on_delete=models.CASCADE)
    niveau = models.ForeignKey(Niveau, on_delete=models.CASCADE)
    professeur = models.ForeignKey(Professeur, on_delete=models.CASCADE)
    annee_academique = models.ForeignKey(AnneeAcademique, on_delete=models.CASCADE)
    
    # Champ Semestre
    semestre = models.CharField(
        max_length=2, 
        choices=SEMESTRE_CHOICES, 
        default='S1' 
    ) 

    nbr_heure = models.DecimalField(max_digits=5, decimal_places=2, verbose_name="Volume horaire prévu")
    date_debut_estimee = models.DateField(null=True, blank=True)
    date_fin_estimee = models.DateField(null=True, blank=True)
    
    def __str__(self):
        return f"{self.matiere.libelle} - {self.niveau.libelle} {self.niveau.niv} ({self.filiere.code}) - {self.semestre}"

    class Meta:
        verbose_name_plural = "Matières Programmées"
        # Mise à jour de unique_together pour inclure le semestre
        unique_together = ('matiere', 'filiere', 'niveau', 'annee_academique', 'semestre') 

# Modèle pour l'Emargement (Feuille de présence)
class Emargement(models.Model):
    matiere_programmer = models.ForeignKey(MatiereProgrammee, on_delete=models.CASCADE)
    date_emar = models.DateField(verbose_name="Date de la séance")
    heure_eff = models.DecimalField(max_digits=4, decimal_places=2, verbose_name="Heures effectuées")
    
    def __str__(self):
        return f"Émargement du {self.date_emar} pour {self.matiere_programmer}"

    class Meta:
        verbose_name_plural = "Émargements"
        unique_together = ('matiere_programmer', 'date_emar')

# Modèle d'Évaluation (Revue Qualitative)
class Evaluation(models.Model):
    # Utilisation de OneToOneField pour s'assurer qu'un cours n'a qu'une seule évaluation
    matiere_programmer = models.OneToOneField(MatiereProgrammee, on_delete=models.CASCADE)
    
    utilisateur_evaluation = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        verbose_name="Évalué par"
    )

    resume_evaluation = models.TextField(verbose_name="Résumé de l'Évaluation du Cours")
    resume_ap = models.TextField(verbose_name="Appréciation de l'Assistant Pédagogique (AP)")
    recommandation = models.TextField(verbose_name="Recommandations et Suggestions")

    def __str__(self):
        return f"Évaluation qualitative de {self.matiere_programmer.matiere.libelle}"
        
    class Meta:
        verbose_name_plural = "Évaluations"