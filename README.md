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

