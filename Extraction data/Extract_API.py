from dotenv import load_dotenv
from arango import ArangoClient
import requests
import os
import time
import psycopg2
from psycopg2 import sql

load_dotenv()

# --- Connexion à ArangoDB ---
def connect_db():
    """
    Se connecte à ArangoDB.
    Crée la base 'legifrance' si elle n'existe pas déjà.
    """
    client = ArangoClient()
    sys_db = client.db(
        "_system",
        username=os.getenv("ARANGO_USER"),
        password=os.getenv("ARANGO_PASSWORD")
    )
    db_name = "legifrance"
    if not sys_db.has_database(db_name):
        sys_db.create_database(db_name)
        print(f"Base '{db_name}' créée.")
    else:
        print(f"Base '{db_name}' déjà existante.")

    db = client.db(
        db_name,
        username=os.getenv("ARANGO_USER"),
        password=os.getenv("ARANGO_PASSWORD")
    )
    return db

def postgres_connexion():
    try:
        conn = psycopg2.connect(
            dbname=os.getenv("POSTGRES_DB"),
            user=os.getenv("POSTGRES_USER"),
            password=os.getenv("POSTGRES_PASSWORD"),
            host=os.getenv("POSTGRES_HOST"),
            port=os.getenv("POSTGRES_PORT")
        )
        cur = conn.cursor()
        return cur
    except Exception as e:
        print(f"Erreur PostgreSQL : {e}")
        return

# --- Création des collections ---
def create_collections(db):
    """
    Crée les collections 'articles', 'cite' et 'contains' dans la base si elles n'existent pas.
    """
    if not db.has_collection("articles"):
        db.create_collection("articles")
    if not db.has_collection("cite"):
        db.create_collection("cite", edge=True)
    if not db.has_collection("contains"):
        db.create_collection("contains", edge=True)

# --- Création des nœuds racines ---
def create_root_nodes(db):
    """
    Crée les deux nœuds racines pour le Code de la défense et le Code de la fonction publique.
    """
    articles_collection = db.collection("articles")

    roots = [
        {"_key": "CODE_DEFENSE", "titre": "Code de la défense", "num": None},
        {"_key": "CODE_FONCTION_PUBLIQUE", "titre": "Code de la fonction publique", "num": None}
    ]

    for root in roots:
        if not articles_collection.has(root["_key"]):
            articles_collection.insert(root)

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

# --- Extraction et insertion des articles ---
def extract_and_store_articles(db, headers):
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

        for article in articles[:1]:
            aid = article["id"]
            meta = get_article_text(aid, headers)
            cite, cite_par = get_related_links(aid, headers)
            doc = {
                "_key": aid,
                "num": article.get("num"),
                "texte": meta['texte'],
                "date_parution": meta["date_parution"],  
                "version": meta["version"],  
                "cite": cite,
                "cite_par": cite_par,
                "code_parent": code_id
            }
            if not articles_col.has(aid):
                articles_col.insert(doc)
            else:
                articles_col.update_match({"_key": aid}, doc)
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
    db_arrango = connect_db()
    db_postgres = postgres_connexion()
    create_collections(db_arrango)
    create_root_nodes(db_arrango)
    token = get_token()
    headers = get_headers(token)
    extract_and_store_articles(db_arrango, headers)
    insert_edges(db_arrango)
    insert_contains_edges(db_arrango)
    print("Extraction, population et organisation terminées.")

if __name__ == "__main__":
    main()
