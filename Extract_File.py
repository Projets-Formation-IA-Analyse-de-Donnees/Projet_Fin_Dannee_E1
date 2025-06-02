import pandas as pd
import psycopg2
import os
import logging
from tqdm import tqdm
from dotenv import load_dotenv
from DB_Connexion import postgres_connexion

# --- Chargement des variables d'environnement ---
load_dotenv()

# --- Configuration du logger ---
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("insert_versions.log"),
        logging.StreamHandler()
    ]
)

# --- Insertion des données du fichier CSV dans PostgreSQL ---
def insert_data(csv_path, cur, conn):
    """
    Insère les données du fichier CSV dans la table article_version
    """
    if not os.path.exists(csv_path):
        logging.error(f"Fichier CSV non trouvé : {csv_path}")
        return

    try:
        df = pd.read_csv(csv_path)
    except Exception as e:
        logging.error(f"Erreur lors de la lecture du fichier CSV : {e}")
        return

    # Vérification des colonnes
    required_columns = {'article_id', 'version_id', 'date_debut', 'date_fin'}
    if not required_columns.issubset(df.columns):
        logging.error(f"Colonnes manquantes dans le fichier CSV. Requises : {required_columns}")
        return

    inserted, failed = 0, 0

    for _, row in tqdm(df.iterrows(), total=len(df), desc="Insertion des versions"):
        article_id = row['article_id']
        version_id = row['version_id']
        date_debut = row['date_debut']
        date_fin = row['date_fin']

        try:
            cur.execute("""
                INSERT INTO article_version (article_id, version_id, date_version, date_fin)
                VALUES (%s, %s, %s, %s)
                ON CONFLICT DO NOTHING;
            """, (article_id, version_id, date_debut, date_fin))
            inserted += 1
        except Exception as e:
            logging.warning(f"Échec insertion {article_id} : {e}")
            conn.rollback()
            failed += 1
            continue

    conn.commit()
    logging.info(f"Insertion terminée. Succès : {inserted}, Échecs : {failed}")

# --- Main ---
def main():
    try:
        cur, conn = postgres_connexion()
        csv_path = os.getenv("CSV_PATH")
        if not csv_path:
            logging.error("Variable d'environnement CSV_PATH manquante.")
            return

        insert_data(csv_path, cur, conn)
    except Exception as e:
        logging.critical(f"Erreur lors de la connexion à la base de données : {e}")
    finally:
        try:
            cur.close()
            conn.close()
        except:
            pass

if __name__ == "__main__":
    main()
