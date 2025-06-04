from dotenv import load_dotenv
from arango import ArangoClient
import requests
import os
import time
import psycopg2
from psycopg2 import sql
import socket

load_dotenv()
# --- Gestion du Host Postgres ---
def get_postgres_host():
    """
    Retourne le bon host en fonction de l’environnement.
    """
    env_host = os.getenv("POSTGRES_HOST")
    try:
        socket.gethostbyname(env_host)
        return env_host
    except Exception:
        return "localhost"

# --- Connexion à ArangoDB ---
def connect_Arrango_db():
    """
    Se connecte à ArangoDB.
    Crée la base 'legifrance' si elle n'existe pas déjà.
    Crée les collections 'articles', 'cite' , 'contains', 'news' dans la base si elles n'existent pas.
    Crée les deux nœuds racines pour le Code de la défense et le Code de la fonction publique.
    """
    host_env = os.getenv("ARANGO_HOST")  
    url_env = os.getenv("ARANGO_URL")    

    try:
        requests.get(url_env, timeout=1)  
    except Exception:
        host_env = "localhost:8529"
        url_env = "http://localhost:8529"

    client = ArangoClient(hosts=f"http://{host_env}")

    sys_db = client.db(
        "_system",
        username=os.getenv("ARANGO_USER"),
        password=os.getenv("ARANGO_PASSWORD"))
    
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
    if not db.has_collection("articles"):
        db.create_collection("articles")
    if not db.has_collection("news"):
        db.create_collection("news")
    if not db.has_collection("cite"):
        db.create_collection("cite", edge=True)
    if not db.has_collection("contains"):
        db.create_collection("contains", edge=True)

    articles_collection = db.collection("articles")

    roots = [
        {"_key": "CODE_DEFENSE", "titre": "Code de la défense", "num": None},
        {"_key": "CODE_FONCTION_PUBLIQUE", "titre": "Code de la fonction publique", "num": None}
    ]

    for root in roots:
        if not articles_collection.has(root["_key"]):
            articles_collection.insert(root)
    return db

# --- Connexion à Postgres ---
def postgres_connexion():
    """
    Se connecte à Postgres.
    Création les tables code, article,article_version si elles n'xistent pas encore.
    """
    cur = None
    conn = None
    create_query = """
    -- Table code parent
    CREATE TABLE IF NOT EXISTS code (
        id SERIAL PRIMARY KEY,
        code_id TEXT UNIQUE NOT NULL,
        name TEXT NOT NULL
    );

    -- Table article
    CREATE TABLE IF NOT EXISTS article (
        id SERIAL PRIMARY KEY,
        article_id TEXT UNIQUE,
        titre TEXT NOT NULL,
        date_parution TIMESTAMP,
        id_code INTEGER REFERENCES code(id) ON DELETE SET NULL,
        CONSTRAINT unique_article UNIQUE(titre, date_parution)
    );

    -- Table article_version
    CREATE TABLE IF NOT EXISTS article_version (
        id SERIAL PRIMARY KEY,
        article_id TEXT NOT NULL REFERENCES article(article_id) ON DELETE CASCADE,
        version_id TEXT NOT NULL,
        date_version TIMESTAMP NOT NULL,
        date_fin TIMESTAMP,
        CONSTRAINT unique_article_version UNIQUE(article_id, version_id)
    );
    """

    try:
        host = get_postgres_host()  
        conn = psycopg2.connect(
            dbname=os.getenv("POSTGRES_DB"),
            user=os.getenv("POSTGRES_USER"),
            password=os.getenv("POSTGRES_PASSWORD"),
            host=host,
            port=os.getenv("POSTGRES_PORT")
        )
       
        cur = conn.cursor()
        conn.autocommit = False
        cur.execute(create_query)
        print("Tables créées ou déjà présentes.")
    except Exception as e:
        print("Erreur lors de la connexion à PostgreSQL :", e)
        return None, None

    return cur, conn
  
