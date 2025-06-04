# Documentation des Endpoints de l'API Flask

> Tous les endpoints nécessitent une clé API envoyée dans l'en-tête `x-api-key`.
> Vous pouvez la définir dans votre .env 

---

## PostgreSQL : 

### `GET /pg/articles`

**Description :**  
Récupère les 50 premiers articles enregistrés dans la base de données PostgreSQL.

**Exemple de réponse :**

```json
[
  {
    "article_id": "LEGIARTI000028342870",
    "date_parution": "Fri, 20 Dec 2013 00:00:00 GMT",
    "titre": "L1332-6-3"
  },
  ...
]
```


### `GET /pg/codes`

**Description :**  
Retourne l’ensemble des codes juridiques enregistrés avec leur code_id et leur nom.

**Exemple de réponse :**

```json
[
   {
    "code_id": "LEGITEXT000006071307",
    "name": "CODE_DEFENSE"
  },
  ...
]
```

### `GET /pg/articles/<code_id>`

**Description :**  
Retourne tous les articles associés à un code donné.

**Paramètres :**
code_id : identifiant du code (ex. LEGITEXT000044416551)

**Exemple de réponse :**

```json
[
  {
    "article_id": "LEGIARTI000006539681",
    "date_parution": "Tue, 21 Dec 2004 00:00:00 GMT",
    "titre": "L1322-3"
  },
  ...
]
```


### `GET /pg/versions/<article_id>`


**Description :**  
Retourne toutes les versions disponibles pour un article donné.

**Paramètres :**
article_id : identifiant de l'article (ex. LEGITEXT000044416551)

**Exemple de réponse :**

```json
[
  {
    "date_fin": "Tue, 01 Jan 2999 00:00:00 GMT",
    "date_version": "Sat, 01 Feb 2025 00:00:00 GMT",
    "version_id": "LEGIARTI000050546251"
  },
  ...
]
```


## ArrangoDB : 

### `GET /arango/articles`

**Description :**  
Récupère tous les documents de la collection 'articles' dans ArangoDB.

**Exemple de réponse :**

```json
[
  {
    "_id": "articles/LEGIARTI000050546343",
    "_key": "LEGIARTI000050546343",
    "_rev": "_jxozoHK---",
    "cite": [...],
    "cite_par": [...],
    "code_parent": "LEGITEXT000044416551",
    "content": ...,
    "num": "R122-34"
  },
  ...
]
```

### `GET /arango/news`

**Description :**  
Récupère tous les documents de la collection 'news' dans ArangoDB.

**Exemple de réponse :**

```json
[
  {
    "_id": "news/conseil_des_ministres_du_19_mars_2008_dispositions_rglementaires_du_code_de_la_dfense_",
    "_key": "conseil_des_ministres_du_19_mars_2008_dispositions_rglementaires_du_code_de_la_dfense_",
    "_rev": "_jxo1Smu---",
    "auteur": "...",
    "code": "CODE_DEFENSE",
    "contenu": "...",
    "date_scraping": "2025-06-04T11:33:02.164989+00:00",
    "titre": "...",
    "url": "https://www.vie-publique.fr/discours/170127-conseil-des-ministres-du-19-mars-2008-dispositions-reglementaires-du-co"
  },
  ...
]
```

### `GET /arango/article/<article_id>`

**Description :**  
Récupère un article spécifique dans ArangoDB.

**Exemple de réponse :**

```json
[
  {
  "_id": "articles/LEGIARTI000050546251",
  "_key": "LEGIARTI000050546251",
  "_rev": "_jxozYZm---",
  "cite": [],
  "cite_par": [],
  "code_parent": "LEGITEXT000044416551",
  "content": "...",
  "num": "R120-1"
}
]
```


### `GET /arango/citations`

**Description :**  
Récupère toutes les relations de citation depuis la collection 'cite'.

**Exemple de réponse :**

```json
[
  {
    "_from": "articles/LEGIARTI000050546271",
    "_id": "cite/cite_LEGIARTI000050546271_LEGIARTI000050546269",
    "_key": "cite_LEGIARTI000050546271_LEGIARTI000050546269",
    "_rev": "_jxozs5a---",
    "_to": "articles/LEGIARTI000050546269"
  },
  ...
]
```


### `GET /arango/structure`

**Description :**  
Récupère les relations structurelles (contains) entre codes et articles.

**Exemple de réponse :**

```json
[
  {
    "_from": "articles/CODE_FONCTION_PUBLIQUE",
    "_id": "contains/contains_CODE_FONCTION_PUBLIQUE_LEGIARTI000050546343",
    "_key": "contains_CODE_FONCTION_PUBLIQUE_LEGIARTI000050546343",
    "_rev": "_jxozx6q---",
    "_to": "articles/LEGIARTI000050546343"
  },
  ...
]
```
