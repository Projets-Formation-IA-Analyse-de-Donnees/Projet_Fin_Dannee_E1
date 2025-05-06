from dotenv import load_dotenv
from arango import ArangoClient
import requests
import os
import time
import psycopg2
from psycopg2 import sql

load_dotenv()

# --- Connexion à ArangoDB ---
def connect_Arrango_db():
    """
    Se connecte à ArangoDB.
    Crée la base 'legifrance' si elle n'existe pas déjà.
    Crée les collections 'articles', 'cite' et 'contains' dans la base si elles n'existent pas.
    Crée les deux nœuds racines pour le Code de la défense et le Code de la fonction publique.
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
    if not db.has_collection("articles"):
        db.create_collection("articles")
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
    Création des tables si elles n'xistent pas encore.
    """
    create_query = """
    -- Table article
    CREATE TABLE IF NOT EXISTS article (
        id SERIAL PRIMARY KEY,
        titre TEXT NOT NULL,
        date_parution TIMESTAMP,
        CONSTRAINT unique_article UNIQUE(titre, date_parution)
    );

    -- Table texte
    CREATE TABLE IF NOT EXISTS texte (
        id SERIAL PRIMARY KEY,
        id_article INTEGER NOT NULL REFERENCES article(id) ON DELETE CASCADE,
        contenu TEXT
    );

    -- Table version
    CREATE TABLE IF NOT EXISTS version (
        id SERIAL PRIMARY KEY,
        id_article INTEGER NOT NULL REFERENCES article(id) ON DELETE CASCADE,
        id_texte INTEGER NOT NULL REFERENCES texte(id) ON DELETE CASCADE,
        version TEXT
    );
    """ 
    try:
        conn = psycopg2.connect(
            dbname=os.getenv("POSTGRES_DB"),
            user=os.getenv("POSTGRES_USER"),
            password=os.getenv("POSTGRES_PASSWORD"),
            host=os.getenv("POSTGRES_HOST"),
            port=os.getenv("POSTGRES_PORT")
        )
        cur = conn.cursor()  
        conn.autocommit = False 
        cur.execute(create_query)
        print("Tables créées avec succès.")
        return cur ,conn
    except Exception as e:
        print(f"Erreur PostgreSQL : {e}")
        return
    










              