import csv
import os
from dotenv import load_dotenv
from DB_Connexion import *

load_dotenv()

def insert_data_from_csv(csv_path, conn):
    cur = conn.cursor()
    with open(csv_path, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            try:
                # Exemple : si vos colonnes s'appellent 'titre', 'date_parution', 'texte', 'version'
                titre = row['titre']
                date_parution = row['date_parution']  # Assurez-vous que le format est correct (ex: 'YYYY-MM-DD HH:MM:SS')
                texte = row['texte']
                version = row['version']
                print("cas 1:",titre,date_parution,texte,version )
            except Exception as e:
                print(f"Erreur lors de la récupérations des informations du fichier:{e}")
       





def main():
    csv_file = os.getenv("CSV_Path") 
    db_postgres,conn = postgres_connexion()
    insert_data_from_csv(csv_file, conn)
    conn.close()
    print("Import terminé.")

if __name__ == "__main__":
    main()