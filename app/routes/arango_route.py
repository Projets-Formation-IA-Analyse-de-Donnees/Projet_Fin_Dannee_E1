from flask import Blueprint, jsonify
from app.auth import require_api_key
from DB_Connexion import connect_Arrango_db

arango_bp = Blueprint("arango", __name__, url_prefix="/arango")

@arango_bp.route("/articles", methods=["GET"])
@require_api_key()
def get_articles_arango():
    """
    Récupère tous les documents de la collection 'articles' dans ArangoDB.
    """
    db = connect_Arrango_db()
    collection = db.collection("articles")
    data = [doc for doc in collection]
    return jsonify(data), 200

@arango_bp.route("/news", methods=["GET"])
@require_api_key()
def get_news_arango():
    """
    Récupère tous les documents de la collection 'news' dans ArangoDB.
    """
    db = connect_Arrango_db()
    collection = db.collection("news")
    data = [doc for doc in collection]
    return jsonify(data), 200


@arango_bp.route("/article/<article_id>", methods=["GET"])
@require_api_key()
def get_article_arango(article_id):
    """
    Récupère un article spécifique dans ArangoDB.
    """
    db = connect_Arrango_db()
    col = db.collection("articles")
    if col.has(article_id):
        return jsonify(col.get(article_id)), 200
    return jsonify({"error": f"Article {article_id} non trouvé"}), 404


@arango_bp.route("/citations", methods=["GET"])
@require_api_key()
def get_all_citations():
    """
    Récupère toutes les relations de citation depuis la collection 'cite'.
    """
    db = connect_Arrango_db()
    cite_col = db.collection("cite")
    data = [doc for doc in cite_col]
    return jsonify(data), 200


@arango_bp.route("/structure", methods=["GET"])
@require_api_key()
def get_structure_relations():
    """
    Récupère les relations structurelles (contains) entre codes et articles.
    """
    db = connect_Arrango_db()
    contains = db.collection("contains")
    return jsonify([doc for doc in contains]), 200
