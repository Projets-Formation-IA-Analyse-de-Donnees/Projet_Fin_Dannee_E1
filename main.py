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

# import requests
# from django.http import JsonResponse
# from django.contrib.auth.decorators import login_required

# # Assurez-vous que la vue nécessite une connexion préalable
# @login_required
# def obtenir_prediction(request):
#     # L'URL de l'API du modèle ML
#     url_model_ml = 'http://localhost:8001/api/model/'  # Assurez-vous que l'URL est correcte

#     # Créer une session HTTP qui maintient les cookies d'authentification
#     session = requests.Session()

#     # Copiez les cookies de session de l'utilisateur actuel dans la session
#     cookies = request.COOKIES
#     session.cookies.update(cookies)

#     # Données à envoyer pour la prédiction (par exemple)
#     data = {
#         'feature1': 'value1',
#         'feature2': 'value2',
#     }

#     # Effectuer la requête POST avec authentification
#     response = session.post(url_model_ml, json=data)

#     if response.status_code == 200:
#         result = response.json()  # Récupérer la réponse du modèle
#         return JsonResponse(result)
#     else:
#         return JsonResponse({'error': 'Erreur lors de la récupération de la prédiction'}, status=500)
