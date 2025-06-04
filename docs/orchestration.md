# Orchestration et modularité

Le projet repose sur trois sources de données distinctes :

- une API publique (Légifrance),

- un fichier local structuré,

- et un scraping de contenu web.

Chacune de ces sources est traitée par un script d’extraction dédié :

- Extract_API.py

- Extract_File.py

- Extract_Scrapping.py

Cette structure modulaire permet d’exécuter les scripts indépendamment selon les besoins.
Néanmoins, certaines dépendances logiques existent entre les données. Par exemple, les versions d’articles font référence à des articles qui doivent préexister dans la base.
Ainsi, un ordre d’exécution est à respecter pour éviter les erreurs d’intégrité.

## Ordre conseillé d'exécution :

- 1: Extract_API.py

- 2: Extract_File.py

- 3: Extract_Scrapping.py




Tu peux maintenant consulter la liste complète des points de terminaison disponibles, ainsi que des exemples de requêtes et de réponses, dans le fichier suivant : [Voir la documentation des endpoints](api_endpoints.md)
