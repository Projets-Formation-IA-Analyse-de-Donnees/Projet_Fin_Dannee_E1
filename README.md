# Projet Légifrance - Intégration Multi-Sources & API REST

Ce projet a pour objectif de mettre à disposition des données via une API REST sécurisée.
Pour cela, les données sont collectées à partir de trois sources distinctes :

- Une API publique
- Un fichier local
- Du web scraping


Ces données sont ensuite agrégées et stockées dans deux bases de données complémentaires :

- PostgreSQL — une base relationnelle classique

- ArangoDB — une base multi-modèle orientée graphe

Enfin, l’ensemble des données est exposé à travers différents points de terminaison d’une API développée avec Flask.











## Table des matières

- [Lancement du projet](docs/setup.md)
- [Endpoints de l’API](docs/api_endpoints.md)
- [Authentification](docs/auth.md)
- [Orchestration](docs/orchestration.md)


