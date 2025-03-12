from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from models import SessionLocal, Titanic
from sqlalchemy import create_engine
import pandas as pd

app = FastAPI()

# Fonction pour obtenir une session de base de données
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Endpoint pour récupérer toutes les données Titanic
@app.get("/titanic/")
def get_titanic_data(db: Session = Depends(get_db)):
    titanic_data = db.query(Titanic).all()  
    return titanic_data

