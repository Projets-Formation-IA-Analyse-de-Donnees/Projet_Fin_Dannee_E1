# Utiliser l'image Python officielle
FROM python:3.9-slim

# Définir le répertoire de travail dans le container
WORKDIR /app

# Copier le code du projet dans le container
COPY . /app/

# Installer les dépendances
RUN pip install --no-cache-dir -r requirements.txt

# Exposer le port 80 (ou tout autre port que vous utilisez)
EXPOSE 80

# Démarrer l'application FastAPI avec Uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "80"]
