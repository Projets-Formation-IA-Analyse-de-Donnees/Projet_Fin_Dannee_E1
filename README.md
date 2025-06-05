# Projet Légifrance - Intégration Multi-Sources & API REST

Ce projet a pour objectif de mettre à disposition des données juridiques via une API REST sécurisée.
Les données sont collectées à partir de trois sources distinctes :

- Une API publique (données officielles issues de Légifrance)

- Un fichier local (versions historiques d’articles)

- Du web scraping (actualités juridiques)

Ces données, principalement composées d’articles juridiques issus de plusieurs codes (notamment le Code de la Défense et le Code de la Fonction Publique), sont ensuite agrégées et stockées dans deux bases de données complémentaires :

- PostgreSQL — pour la structure relationnelle des articles et de leurs versions

- ArangoDB — pour la modélisation orientée graphe des relations (citations, hiérarchie, appartenance)

Une API Flask permet ensuite d’exposer ces données à travers plusieurs points de terminaison, en assurant un accès sécurisé et un format unifié.

L’objectif à long terme est de construire un graphe de connaissance (Knowledge Graph) couvrant l’ensemble des articles afin de représenter les liens de citation, de structure et d’évolution entre eux de manière claire et navigable.

Ce projet constitue une brique technique réutilisable dans un site web destiné à la recherche et à l’analyse juridique, avec à terme des fonctionnalités avancées comme :

- l’exploration graphique des articles,

- la recherche intelligente par mots-clés ou concepts,

- et l’enrichissement automatique via des sources tierces.





## Table des matières

- [Lancement du projet](docs/setup.md)
- [Orchestration](docs/orchestration.md)
- [Authentification](docs/auth.md)
- [Endpoints de l’API](docs/api_endpoints.md)




