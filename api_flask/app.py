from flask import Flask, jsonify
from datetime import date, timedelta
import random

app = Flask(__name__)

# Simuler une base de données locale fictive (remplaçable par vraie BDD plus tard)
cours = [
    {"nom": "Python avancé", "id": 1},
    {"nom": "Initiation Pandas", "id": 2},
    {"nom": "Django", "id": 3},
    {"nom": "Scraping web", "id": 4},
    {"nom": "SQL et bases de données", "id": 5}
]

@app.route('/api/stats')
def stats():
    data = []
    today = date.today()

    for c in cours:
        session_date = today - timedelta(days=random.randint(0, 30))
        stat = {
            "cours_id": c["id"],
            "cours_nom": c["nom"],
            "date": str(session_date),
            "nb_participants": random.randint(8, 30),
            "satisfaction": round(random.uniform(3.0, 5.0), 2)
        }
        data.append(stat)

    return jsonify(data)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)
