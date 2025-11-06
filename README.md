# 📚 Projet Django CBS (Gestion des Cours)

Ce dépôt contient le code source de l'application web Django utilisée pour la **gestion des cours**. Le projet a été développé initialement sous **Kali Linux** et est configuré pour fonctionner sur Windows (et tout autre environnement Linux/macOS).

---
SuperUser
USER: admin
PWD: AdminCBS

APUser
user:AP
pwd:AdminCBS
## 🚀 Démarrage et Installation

Suivez ces étapes pour cloner le projet, installer les dépendances et lancer l'application.

### 1. Prérequis Logiciels

Assurez-vous d'avoir installé les outils de base :

* **Python 3.x**
* **Git**

### 2. Configuration de l'Environnement

Ouvrez votre terminal (PowerShell sur Windows, ou Bash/Zsh sur Linux/macOS).

#### A. Cloner le Dépôt

```bash
# Cloner le dépôt depuis GitHub (remplacez l'URL par la vôtre)
git clone [https://docs.github.com/fr/repositories/creating-and-managing-repositories/creating-a-new-repository](https://docs.github.com/fr/repositories/creating-and-managing-repositories/creating-a-new-repository)
cd Django_CBS
Créer et Activer l'Environnement Virtuel
L'environnement virtuel (venv) est crucial pour isoler les dépendances :

Bash

# 1. Créer l'environnement virtuel
python -m venv venv

# 2. Activer l'environnement
# Pour Windows (PowerShell):
.\venv\Scripts\activate

# Pour Linux/macOS:
source venv/bin/activate
C. Installer les Dépendances
Installez toutes les bibliothèques requises. Ces dépendances incluent celles que nous avons identifiées (django-filter, crispy-forms, openpyxl, reportlab, etc.) :

Bash

pip install -r requirements.txt
⚠️ Si le fichier requirements.txt manque après le clonage : Vous devrez installer les paquets de base manuellement : pip install django django-filter django-crispy-forms crispy-bootstrap5 openpyxl reportlab Ensuite, créez le fichier de dépendances : pip freeze > requirements.txt

💻 Lancement du Projet
A. Appliquer les Migrations
Mettez à jour la base de données (SQLite par défaut) :

Bash

python manage.py migrate
B. Démarrer le Serveur
Bash

python manage.py runserver
L'application sera accessible dans votre navigateur à l'adresse http://127.0.0.1:8000/.

🔒 Gestion des Utilisateurs
Connexion Admin : Accédez à la page /admin/. Si le fichier de base de données (db.sqlite3) a été cloné, le superutilisateur créé sous Kali fonctionne directement.

Créer un Superutilisateur : Si la base de données est vide ou si l'utilisateur n'existe pas :

Bash

python manage.py createsuperuser
☁️ Synchronisation avec GitHub
1. Mise à Jour des Dépendances
Chaque fois que vous installez un nouveau paquet avec pip install, mettez à jour le fichier requirements.txt :

Bash

pip freeze > requirements.txt
2. Contribuer et Pousser (Push)
Pour enregistrer vos modifications locales et les envoyer vers GitHub :

Bash

git add .
git commit -m "Description concise et explicite de mes changements"
git push origin nom_de_votre_branche
3. Récupérer les Modifications (Pull)
Pour télécharger les dernières mises à jour depuis GitHub :

Bash

git pull origin nom_de_votre_branche
