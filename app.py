from flask import Flask, jsonify
from datetime import date, timedelta

app = Flask(__name__)

# Liste fixe des cours avec leurs stats déterminées
cours_stats = [
    {"id": 1, "nom": "Python avancé", "date_offset": 3, "participants": 25, "satisfaction": 4.7},
    {"id": 2, "nom": "Initiation Pandas", "date_offset": 7, "participants": 18, "satisfaction": 4.2},
    {"id": 3, "nom": "Django", "date_offset": 10, "participants": 22, "satisfaction": 4.5},
    {"id": 4, "nom": "Scraping", "date_offset": 15, "participants": 16, "satisfaction": 4.0},
    {"id": 5, "nom": "SQL", "date_offset": 20, "participants": 30, "satisfaction": 4.8},
]

@app.route('/api/stats')
def stats():
    today = date.today()
    data = []

    for c in cours_stats:
        stat = {
            "cours_id": c["id"],
            "cours_nom": c["nom"],
            "date": str(today - timedelta(days=c["date_offset"])),
            "nb_participants": c["participants"],
            "satisfaction": c["satisfaction"]
        }
        data.append(stat)

    return jsonify(data)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)
