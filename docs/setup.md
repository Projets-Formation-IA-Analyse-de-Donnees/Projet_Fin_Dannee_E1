# Lancement du projet

Voici les étapes nécessaires pour configurer et lancer l’ensemble du projet :

---

## Prérequis

- Python 3.10 ou supérieur
- Docker + Docker Compose

---

## Étapes d'installation

```bash
# 1. Cloner le dépôt
git clone <lien-du-repo>
cd Projet_Fin_Dannee_E1

# 2. Créer l’environnement virtuel
python -m venv venv
venv\Scripts\activate         # Sur Windows
# source venv/bin/activate    # Sur Linux/Mac

# 3. Installer les dépendances Python
pip install -r requirements.txt

# 4. Créer un fichier .env à la racine du projet avec ce contenu :
POSTGRES_DB = <Nom de votre BDD postgres>
POSTGRES_USER = <Nom Utilisateur postgres>
POSTGRES_PASSWORD = <Mot de Passe postgres>
POSTGRES_HOST = <Host de votre BDD postgres>
POSTGRES_PORT = <Port de votre BDD postgres>

ARANGO_HOST = <Host de votre BDD arango>
ARANGO_URL = <URL de votre BDD arango>
ARANGO_USER = <Nom Utilisateur arango>
ARANGO_PASSWORD = <Mot de Passe arango>

API_KEY = <Clef API Légifrance>
URL_API = <URL API Légifrance>

# 5. Lancer les services Docker
docker-compose up -d --build

# 6. Extraire et insérer les données
python Extract_API.py
python Extract_File.py
python Extract_Scrapping.py
'''

## Requetes
