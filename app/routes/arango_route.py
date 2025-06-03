from flask import Blueprint, jsonify
from app.auth import require_api_key
from DB_Connexion import postgres_connexion, connect_Arrango_db

arango_bp = Blueprint('arango_bp', __name__)

@arango_bp.route("/api/arango/articles", methods=["GET"])
@require_api_key()
def get_articles_arango():
    db_arrongo = connect_Arrango_db()
    col = db_arrongo.collection("news")
    data = [doc for doc in col]
    return jsonify(data)
