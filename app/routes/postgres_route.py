from flask import Blueprint, jsonify
from app.auth import require_api_key
from DB_Connexion import postgres_connexion

pg_bp = Blueprint("pg", __name__, url_prefix="/pg")

cur, conn = postgres_connexion()

@pg_bp.route("/articles", methods=["GET"])
@require_api_key()
def get_articles():
    try:
        cur.execute("SELECT article_id, titre, date_parution FROM article LIMIT 50;")
        rows = cur.fetchall()
        articles = [{"article_id": r[0], "titre": r[1], "date_parution": r[2]} for r in rows]
        return jsonify(articles), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
