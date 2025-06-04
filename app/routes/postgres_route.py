from flask import Blueprint, jsonify
from app.auth import require_api_key
from DB_Connexion import postgres_connexion
from dotenv import load_dotenv
import os
load_dotenv()

pg_bp = Blueprint("pg", __name__, url_prefix="/pg")

@pg_bp.route("/articles", methods=["GET"])
@require_api_key()
def get_articles_pg():
    """
    Récupère les 50 premiers articles de la base PostgreSQL.
    """
    try:
        cur, conn = postgres_connexion()
        cur.execute("SELECT article_id, titre, date_parution FROM article LIMIT 50;")
        rows = cur.fetchall()
        articles = [{"article_id": r[0], "titre": r[1], "date_parution": r[2]} for r in rows]
        return jsonify(articles), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500



@pg_bp.route("/codes", methods=["GET"])
@require_api_key()
def get_codes_pg():
    """
    Récupère tous les codes (code_id et nom) présents dans la base PostgreSQL.
    """
    try:
        cur, conn = postgres_connexion()
        cur.execute("SELECT code_id, name FROM code;")
        rows = cur.fetchall()
        return jsonify([{"code_id": r[0], "name": r[1]} for r in rows]), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@pg_bp.route("/articles/<code_id>", methods=["GET"])
@require_api_key()
def get_articles_by_code_pg(code_id):
    """
    Récupère tous les articles liés à un code donné.
    """
    try:
        cur, conn = postgres_connexion()
        cur.execute("""
            SELECT a.article_id, a.titre, a.date_parution 
            FROM article a 
            JOIN code c ON a.id_code = c.id 
            WHERE c.code_id = %s
        """, (code_id,))
        rows = cur.fetchall()
        return jsonify([{"article_id": r[0], "titre": r[1], "date_parution": r[2]} for r in rows]), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@pg_bp.route("/versions/<article_id>", methods=["GET"])
@require_api_key()
def get_versions_by_article_pg(article_id):
    """
    Récupère toutes les versions d'un article donné.
    """
    try:
        cur, conn = postgres_connexion()
        cur.execute("""
            SELECT version_id, date_version, date_fin 
            FROM article_version 
            WHERE article_id = %s
        """, (article_id,))
        rows = cur.fetchall()
        return jsonify([{
            "version_id": r[0],
            "date_version": r[1],
            "date_fin": r[2]
        } for r in rows]), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500