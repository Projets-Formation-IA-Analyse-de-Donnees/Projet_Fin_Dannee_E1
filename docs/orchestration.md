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

## Monitoring :

Après l'exécution des scripts d'extraction, des fichiers de logs dédiés sont automatiquement générés et enrichis à chaque lancement. Ces logs permettent de suivre en détail le déroulement des insertions dans les bases de données.

- Extract_API.py -> insert_articles.log

- Extract_File.py -> insert_versions.log

- Extract_Scrapping.py -> insert_scrapping.log

 Les logs contiennent des horodatages, les statuts des opérations (INFO/WARNING), et permettent de diagnostiquer facilement les éventuelles erreurs.

Attention: 

Lors de la création de la collection d'arêtes de citation dans ArangoDB, certaines relations peuvent ne pas être établies correctement. Cela s'explique par le fait que, par souci de performance, j’ai volontairement limité le nombre d’articles récupérés à 50 par code.
Par conséquent, il est normal que certains articles ne soient pas reliés, même s’ils possèdent des références vers d'autres articles.

Vous pouvez changer cette valeur ligne 143 du scripts Extract_API.py  `[:50]`


Tu peux maintenant consulter la liste complète des points de terminaison disponibles, ainsi que des exemples de requêtes et de réponses, dans le fichier suivant : [Voir la documentation des endpoints](api_endpoints.md)
