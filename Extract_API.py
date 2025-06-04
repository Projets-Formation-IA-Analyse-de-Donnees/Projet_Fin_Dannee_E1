import os
import time
import requests
import logging
from tqdm import tqdm
from dotenv import load_dotenv
from DB_Connexion import postgres_connexion, connect_Arrango_db

load_dotenv()

# --- Configuration Logging ---
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(levelname)s - %(message)s',
                     handlers=[
                    logging.FileHandler("insert.log"),
                    logging.StreamHandler()
                    ])

# --- Constantes Globales ---
CODE_TO_ROOT = {
    "LEGITEXT000006071307": "CODE_DEFENSE",
    "LEGITEXT000044416551": "CODE_FONCTION_PUBLIQUE"
}

# --- Token OAuth ---
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

# --- Récupération des codes ---
def get_codes(headers):
    """
    Récupère les codes filtrés 'défense' et 'fonction publique'.
    """
    payload = {"pageSize": 1000, "pageNumber": 1}
    resp = requests.post(f"{os.getenv('URL_API')}/list/code", json=payload, headers=headers)
    resp.raise_for_status()
    codes = resp.json().get("results", [])
    return [c["id"] for c in codes if "défense" in c["titre"].lower() or "fonction publique" in c["titre"].lower()]

# --- Texte d'un article ---
def get_article_text(article_id, headers):
    resp = requests.post(f"{os.getenv('URL_API')}/consult/getArticle", json={"id": article_id}, headers=headers)
    if not resp.ok:
        return {"texte": "", "date_parution": None, "version": None}
    data = resp.json().get("article", {})
    version = data.get("versionArticle")
    date_debut = data.get("dateDebut")
    if date_debut:
        try:
            if isinstance(date_debut, int) and date_debut > 1e12:
                date_debut /= 1000
            date_debut = time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(date_debut))
        except Exception as e:
            logging.warning(f"Erreur conversion date: {e}")
            date_debut = None
    return {"texte": data.get("texte", ""), "date_parution": date_debut, "version": version}

# --- Liens articles ---
def get_related_links(article_id, headers):
    resp = requests.post(f"{os.getenv('URL_API')}/consult/relatedLinksArticle", json={"articleId": article_id}, headers=headers)
    resp.raise_for_status()
    data = resp.json()
    return [l.get("id") for l in data.get("liensCite", [])], [l.get("id") for l in data.get("liensCitePar", [])]

# --- Extraction des articles ---
def extract_article_infos_from_code(code_obj):
    """
    Récupère tous les articles d'un code.
    """
    results = []
    def recurse(sec):
        for art in sec.get("articles", []):
            results.append({"id": art["id"], "num": art.get("num")})
        for section in sec.get("sections", []):
            recurse(section)
    for top in code_obj.get("sections", []):
        recurse(top)
    return results

# --- Validation types ---
def assert_valid_types(date_parution, titre, texte, version):
    if date_parution and not isinstance(date_parution, str):
        raise TypeError(f"date_parution doit être str ou None, reçu {type(date_parution)}")
    if titre and not isinstance(titre, str):
        raise TypeError(f"titre doit être str ou None, reçu {type(titre)}")
    if texte:
        if not isinstance(texte, str) or texte.strip() == "":
            raise ValueError("texte ne doit pas être vide ou invalide")
    if version:
        if not isinstance(version, str) or version.strip() == "":
            raise ValueError("version ne doit pas être vide ou invalide")

# --- Get/Create Code ---
def get_or_create_code(cur, conn, code_id):
    try:
        cur.execute("SELECT id FROM code WHERE code_id = %s", (code_id,))
        result = cur.fetchone()
        if result:
            return result[0]
        name_code = CODE_TO_ROOT.get(code_id, code_id)
        cur.execute("INSERT INTO code (code_id, name) VALUES (%s, %s) RETURNING id;", (code_id, name_code))
        conn.commit()
        return cur.fetchone()[0]
    except Exception as e:
        logging.error(f"Erreur insertion code {code_id}: {e}")
        conn.rollback()
        return None

# --- Stockage articles ---ze
def extract_and_store_articles(db, db_postgres, conn, headers):
    articles_col = db.collection("articles")
    for code_id in get_codes(headers):
        logging.info(f"Traitement code {code_id}")
        resp = requests.post(f"{os.getenv('URL_API')}/consult/legiPart", json={"textId": code_id, "date": int(time.time() * 1000)}, headers=headers)
        if not resp.ok:
            logging.warning(f"Erreur code {code_id}: {resp.status_code}")
            continue
        articles = extract_article_infos_from_code(resp.json())
        logging.info(f"{len(articles)} articles extraits")
        id_code = get_or_create_code(db_postgres, conn, code_id)
        for article in tqdm(articles[:50], desc=f"Insertion articles pour {code_id}"):
            aid = article["id"]
            meta = get_article_text(aid, headers)
            cite, cite_par = get_related_links(aid, headers)
            doc = {
                "_key": aid,
                "num": article.get("num"),
                "cite": cite,
                "cite_par": cite_par,
                "code_parent": code_id,
                "content": meta['texte']
            }
            if not articles_col.has(aid):
                try:
                    articles_col.insert(doc)
                except Exception as e:
                    logging.error(f"Erreur ArangoDB {aid}: {e}")
                    continue
            db_postgres.execute("SELECT 1 FROM article WHERE article_id = %s", (aid,))
            if db_postgres.fetchone() is None:
                try:
                    assert_valid_types(meta["date_parution"], article.get("num"), meta['texte'], meta["version"])
                    db_postgres.execute("""
                        INSERT INTO article (article_id, titre, date_parution, id_code)
                        VALUES (%s, %s, %s, %s)
                        ON CONFLICT (article_id) DO NOTHING;
                    """, (aid, article.get("num"), meta["date_parution"], id_code))
                    conn.commit()
                except Exception as e:
                    logging.error(f"Erreur PostgreSQL {aid}: {e}")
                    conn.rollback()
            else:
                logging.info(f"Article {aid} deja present.")
        logging.info(f"Code {code_id} traite.")

# --- Arêtes cite ---
def insert_citation_edge(cite_col, art_col, from_id, to_id):
    if not to_id.startswith("LEGIARTI"):
        logging.debug(f"ID cible non conforme: {to_id}")
        return
    if not art_col.has(from_id) or not art_col.has(to_id):
        logging.warning(f"Article absent (from: {from_id}, to: {to_id})")
        return
    edge_key = f"cite_{from_id}_{to_id}"
    if not cite_col.has(edge_key):
        cite_col.insert({"_key": edge_key, "_from": f"articles/{from_id}", "_to": f"articles/{to_id}"})
        logging.info(f"Arête insérée: {from_id} -> {to_id}")

# --- Toutes arêtes cite ---
def insert_edges(db):
    art_col = db.collection("articles")
    cite_col = db.collection("cite")
    for article in art_col:
        for cid in article.get("cite", []):
            insert_citation_edge(cite_col, art_col, article["_key"], cid)
        for cid in article.get("cite_par", []):
            insert_citation_edge(cite_col, art_col, cid, article["_key"])
    logging.info("Arêtes de citation terminées")

# --- Arêtes contains ---
def insert_contains_edges(db):
    art_col = db.collection("articles")
    cont_col = db.collection("contains")
    for article in art_col:
        code_parent = article.get("code_parent")
        if code_parent in CODE_TO_ROOT:
            root_key = CODE_TO_ROOT[code_parent]
            edge_key = f"contains_{root_key}_{article['_key']}"
            if not cont_col.has(edge_key):
                cont_col.insert({
                    "_key": edge_key,
                    "_from": f"articles/{root_key}",
                    "_to": f"articles/{article['_key']}"
                })

# --- MAIN ---
def main():
    """
    Fonction principale : connecte à la base, extrait les données, insère articles + arêtes + organisation.
    """
    db_arrango = connect_Arrango_db()
    db_postgres, conn = postgres_connexion()
    token = get_token()
    headers = get_headers(token)
    extract_and_store_articles(db_arrango, db_postgres, conn, headers)
    insert_edges(db_arrango)
    insert_contains_edges(db_arrango)
    logging.info("Traitement complet.")
    db_postgres.close()
    conn.close()

if __name__ == "__main__":
    main()
