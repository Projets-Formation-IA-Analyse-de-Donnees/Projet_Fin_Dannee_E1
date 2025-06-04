# Projet Légifrance - Intégration Multi-Sources & API REST

Ce projet a pour but d'extraire, stocker et exposer des données juridiques issues de différentes sources :
- une API REST externe (Légifrance),
- un fichier local structuré (JSON/CSV/XML),
- un scraping d’un site web (vie-publique.fr),
- une base de données SQL (PostgreSQL),
- une base de données NoSQL orientée graphe (ArangoDB).

Toutes les données sont agrégées et disponibles via une API Flask sécurisée par une clé API.

---

## Table des matières

- [Lancement du projet](docs/setup.md)
- [Endpoints de l’API](docs/api_endpoints.md)
- [Structure des données PostgreSQL (à venir)](docs/schema_pgsql.md)
- [Structure des données ArangoDB (à venir)](docs/schema_arango.md)

##  lancement
- clone
-python -m venv venv
- venv\scripts\activate
-pip install -r requirements.txt
-creer . env avec: 
-docker-compose up -d --build
-python Extract_API.py
python Extract_File.py
python Extract_Scrapping.py
- 

curl -H "x-api-key: Talocka37!!" http://localhost:5000/pg/articles
curl -H "x-api-key: Talocka37!!" http://localhost:5000/pg/codes
curl -H "x-api-key: Talocka37!!" http://localhost:5000/pg/articles/LEGITEXT000006071307
curl -H "x-api-key: Talocka37!!" http://localhost:5000/pg/versions/LEGIARTI000050546251

curl -H "x-api-key: Talocka37!!" http://localhost:5000/arango/article/LEGIARTI000050546251
curl -H "x-api-key: Talocka37!!" http://localhost:5000/arango/structure
curl -H "x-api-key: Talocka37!!" http://localhost:5000/arango/citations
curl -H "x-api-key: Talocka37!!" http://localhost:5000/arango/news
curl -H "x-api-key: Talocka37!!" http://localhost:5000/arango/articles