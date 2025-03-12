import pandas as pd
from sqlalchemy import create_engine
from models import Titanic, SessionLocal

def load_data_web():
    url = "https://www.openml.org/data/get_csv/16826755/dataset"
    df = pd.read_csv(url)
    engine = create_engine("postgresql://user:password@localhost:5432/mydatabase")
    df.columns = [col.lower().replace(" ", "_") for col in df.columns]
    df.to_sql("titanic", engine, if_exists="replace", index=False)
    messagae = "Données insérées avec succès dans la base de données PostgreSQL !"
