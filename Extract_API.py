from dotenv import load_dotenv
from DB_Connexion import *
import requests
import os
import time
import psycopg2
from psycopg2 import sql

load_dotenv()

# --- Récupération du token OAuth ---
def get_token():
    """
    Obtient un token OAuth pour l'authentification aux services de l'API.
    """
    data = {
        "grant_type": "client_credentials",
        "client_id": os.getenv("CLIENT_ID"),
        "client_secret": os.getenv("CLIENT_SECRET"),
        "scope": "openid"
    }
    resp = requests.post(os.getenv("TOKEN_URL"), data=data)
    resp.raise_for_status()
    return resp.json()["access_token"]

# --- Construction des headers HTTP ---
def get_headers(token):
    """
    Construit l'en-tête HTTP pour les requêtes API.
    """
    return {
        "Authorization": f"Bearer {token}",
        "Accept": "application/json",
        "Content-Type": "application/json"
    }

# --- Récupération des codes législatifs ---
def get_codes(headers):
    """
    Récupère les codes filtrés 'défense' et 'fonction publique'.
    """
    payload = {"pageSize": 1000, "pageNumber": 1}
    resp = requests.post(f"{os.getenv('URL_API')}/list/code", json=payload, headers=headers)
    resp.raise_for_status()
    codes = resp.json().get("results", [])
    return [c["id"] for c in codes if "défense" in c["titre"].lower() or "fonction publique" in c["titre"].lower()]

# --- Récupération du texte d'un article ---
def get_article_text(article_id, headers):
    """
    Récupère le texte, la date de publication et la version d'un article par son identifiant.
    """
    resp = requests.post(
        f"{os.getenv('URL_API')}/consult/getArticle",
        json={"id": article_id},
        headers=headers)
    
    if not resp.ok:
        return {"texte": "", "date_parution": None, "version": None}
    else:
        data = resp.json().get("article", {})
        version = data.get("versionArticle", None)
        date_debut = data.get("dateDebut", None)    
        if date_debut:
            try:
                if isinstance(date_debut, int) and date_debut > 1000000000000:
                    date_debut = date_debut / 1000 
                date_debut = time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(date_debut))  
            except Exception as e:
                print(f"Error during date conversion: {e}")
                date_debut = None
        return {"texte": data.get("texte", ""),
                "date_parution": date_debut,  
                "version": version}

# --- Récupération des liens associés ---
def get_related_links(article_id, headers):
    """
    Récupère les articles cités et citant.
    """
    resp = requests.post(
        f"{os.getenv('URL_API')}/consult/relatedLinksArticle",
        json={"articleId": article_id},
        headers=headers
    )
    resp.raise_for_status()
    data = resp.json()
    return [l.get("id") for l in data.get("liensCite", [])], [l.get("id") for l in data.get("liensCitePar", [])]

# --- Extraction récursive des articles ---
def extract_article_infos_from_code(code_obj):
    """
    Récupère tous les articles d'un code.
    """
    results = []
    def recurse(sec):
        for articles in sec.get("articles", []):
            results.append({"id": articles["id"], "num": articles.get("num")})
        for section in sec.get("sections", []):
            recurse(section)
    for top in code_obj.get("sections", []):
        recurse(top)
    return results

# --- Verification du type des données à insérer ---
def assert_valid_types(date_parution, titre, texte, version):
    if date_parution is not None and not isinstance(date_parution, str):
        raise TypeError(f"date_parution doit être une str ou None, reçu: {type(date_parution)}")
    if titre is not None and not isinstance(titre, str):
        raise TypeError(f"titre doit être une str ou None, reçu: {type(titre)}")
    if texte is not None:
        if not isinstance(texte, str):
            raise TypeError(f"texte doit être une str ou None, reçu: {type(texte)}")
        if texte.strip() == "":
            raise ValueError("texte ne doit pas être une chaîne vide")
    if version is not None:
        if not isinstance(version, str):
            raise TypeError(f"version doit être une str ou None, reçu: {type(version)}")
        if version.strip() == "":
            raise ValueError("version ne doit pas être une chaîne vide")
        
# --- Extraction et insertion des articles ---
def extract_and_store_articles(db, db_postgres,conn, headers):
    """
    Extrait les articles et les insère dans la collection 'articles'.
    """
    articles_col = db.collection("articles")
    list_code_id = get_codes(headers)
    for code_id in list_code_id:
        print(f"Traitement du code {code_id}")
        resp = requests.post(
            f"{os.getenv('URL_API')}/consult/legiPart",
            json={"textId": code_id, "date": int(time.time() * 1000)},
            headers=headers
        )
        if not resp.ok:
            print(f"Erreur pour le code {code_id}: {resp.status_code}")
            continue

        code_data = resp.json()
        articles = extract_article_infos_from_code(code_data)
        print(f"{len(articles)} articles extraits.")

        for article in articles[:50]:
            aid = article["id"]
            meta = get_article_text(aid, headers)
            cite, cite_par = get_related_links(aid, headers)
            doc = {
                "_key": aid,
                "num": article.get("num"),
                "cite": cite,
                "cite_par": cite_par,
                "code_parent": code_id
            }
            if not articles_col.has(aid):
                try:
                    articles_col.insert(doc)
                except Exception as e:
                    print(f"Erreur lors de l'insertion dans ArangoDB pour l'article {aid}:{e}")
                    continue
                try:
                    assert_valid_types(meta["date_parution"], article.get("num"), meta['texte'], meta["version"])
                
                    db_postgres.execute("""
                        INSERT INTO article (article_id,date_parution, titre)
                        VALUES (%s, %s, %s) RETURNING id;
                    """, (aid,meta["date_parution"], article.get("num")))
                    
                    article_id = db_postgres.fetchone()[0]  # Récupère l'ID de l'article inséré

                    # 2. Insertion dans la table texte
                    db_postgres.execute("""
                        INSERT INTO texte (id_article, contenu)
                        VALUES (%s, %s) RETURNING id;
                    """, (article_id, meta['texte']))

                    conn.commit()
                except Exception as e:
                    print(f"Erreur PostgreSQL pour l'article {aid}: {e}")


        print(f"Code {code_id} traité.")

# --- Insertion d'une arête cite ---
def insert_citation_edge(cite_collection, articles_collection, from_article_id, to_article_id):
    """
    Insère une arête de citation.
    """
    if not to_article_id.startswith("LEGIARTI"):
        print(f"Ignoré car ID non reconnu : {to_article_id}")
        return
    
    edge_key = f"cite_{from_article_id}_{to_article_id}"
    if not articles_collection.has(from_article_id):
        print(f"Source {from_article_id} absente de la base")
        return
    if not articles_collection.has(to_article_id):
        print(f"Cible {to_article_id} absente de la base")
        return

    if articles_collection.has(from_article_id) and articles_collection.has(to_article_id):
        if not cite_collection.has(edge_key):
            cite_collection.insert({
                "_key": edge_key,
                "_from": f"articles/{from_article_id}",
                "_to": f"articles/{to_article_id}"
            })
            print(f"Arête insérée : {from_article_id} -> {to_article_id}")

# --- Insérer les arêtes de citation ---
def insert_edges(db):
    """
    Insère toutes les arêtes de citation.
    """
    articles_collection = db.collection("articles")
    cite_collection = db.collection("cite")

    for article in articles_collection:
        article_id = article["_key"]
        for cited_article_id in article.get("cite", []):
            insert_citation_edge(cite_collection, articles_collection, article_id, cited_article_id)
        for citing_article_id in article.get("cite_par", []):
            insert_citation_edge(cite_collection, articles_collection, citing_article_id, article_id)

    print("Insertion des arêtes de citation terminée.")

# --- Insérer les arêtes contains ---
def insert_contains_edges(db):
    """
    Insère les arêtes 'contains' entre les racines et leurs articles.
    """
    articles_collection = db.collection("articles")
    contains_collection = db.collection("contains")

    code_to_root = {
        "LEGITEXT000006071307": "CODE_DEFENSE",
        "LEGITEXT000044416551": "CODE_FONCTION_PUBLIQUE"
    }

    for article in articles_collection:
        code_parent = article.get("code_parent")
        if code_parent in code_to_root:
            root_key = code_to_root[code_parent]
            article_id = article["_key"]
            edge_key = f"contains_{root_key}_{article_id}"
            if not contains_collection.has(edge_key):
                contains_collection.insert({
                    "_key": edge_key,
                    "_from": f"articles/{root_key}",
                    "_to": f"articles/{article_id}"
                })

# --- MAIN ---
def main():
    """
    Fonction principale : connecte à la base, extrait les données, insère articles + arêtes + organisation.
    """
    db_arrango = connect_Arrango_db()
    db_postgres,conn = postgres_connexion()
    token = get_token()
    headers = get_headers(token)
    extract_and_store_articles(db_arrango, db_postgres,conn, headers)
    insert_edges(db_arrango)
    insert_contains_edges(db_arrango)
    print("Extraction, population et organisation terminées.")
    db_postgres.close()
    conn.close()

if __name__ == "__main__":
    main()
