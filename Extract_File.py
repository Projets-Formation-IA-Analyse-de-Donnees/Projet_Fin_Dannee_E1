import pandas as pd
import psycopg2
import os
from dotenv import load_dotenv
from DB_Connexion import postgres_connexion, connect_Arrango_db

load_dotenv()

# --- inserssion des datas du ficheir local en bdd ---
def insert_data(csv_path,cur,conn):
    """
    Insere les données du CSV dans la table associée
    """
    df = pd.read_csv(csv_path)

    for _, row in df.iterrows():
        article_id = row['article_id']
        date_fin = row['date_fin']  
        version_id = row['version_id']
        date_debut = row['date_debut']

        try:
            cur.execute("""
                INSERT INTO article_version (article_id, version_id, date_version, date_fin)
                VALUES (%s, %s, %s, %s)
                ON CONFLICT DO NOTHING;
            """, (article_id, version_id,date_debut,date_fin ))

        except Exception as e:
            print(f"Erreur pour {article_id}: {e}")
            conn.rollback()
            continue

    conn.commit()
    print("Données insérées.")

# --- MAIN ---
def main():
    db_postgres,conn = postgres_connexion()
    insert_data(os.getenv("CSV_PATH"),db_postgres,conn)
    db_postgres.close()
    conn.close()

if __name__ == "__main__":
    main()


