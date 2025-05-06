import psycopg2
import os
from Extract_API import postgres_connexion 



def create_tables(conn):
    """
    Crée les tables dans la base de données.
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
        cursor = conn.cursor()
        cursor.execute(create_query)
        print("Tables créées avec succès.")
    except Exception as e:
        print(f"Erreur lors de la création des tables : {e}")
    finally:
        if cursor:
            cursor.close()  

def main():
    """
    Fonction principale pour gérer les tables PostgreSQL : suppression et création.
    """
    
    cur, conn = postgres_connexion()  

    if conn:
        # Créer les nouvelles tables
        create_tables(conn)

        # Fermer la connexion
        conn.close()
        print("Connexion fermée.")

if __name__ == "__main__":
    main()
