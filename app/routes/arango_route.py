from flask import Blueprint, jsonify
from app.auth import require_api_key
from DB_Connexion import connect_Arrango_db
from dotenv import load_dotenv
load_dotenv()

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

@arango_bp.route("/graph", methods=["GET"])
@require_api_key()
def get_graph_data():
    db = connect_Arrango_db()
    query = """
    FOR edge IN UNION(
        FOR e IN cite RETURN e,
        FOR e IN contains RETURN e
    )
    LET sourceNode = DOCUMENT(edge._from)
    LET targetNode = DOCUMENT(edge._to)
    RETURN {edge, sourceNode, targetNode}
    """
    cursor = db.aql.execute(query)

    nodes = {}
    edges = []

    for result in cursor:
        edge = result["edge"]
        source = result["sourceNode"]
        target = result["targetNode"]

        def extract_label(node):
            return node.get("num") or node.get("titre") or "???"

        if source["_key"] not in nodes:
            nodes[source["_key"]] = {
                "id": source["_key"],
                "label": extract_label(source)
            }

        if target["_key"] not in nodes:
            nodes[target["_key"]] = {
                "id": target["_key"],
                "label": extract_label(target)
            }

        edges.append({
            "from": edge["_from"].split("/")[-1],
            "to": edge["_to"].split("/")[-1]
        })

    return jsonify({
        "nodes": list(nodes.values()),
        "edges": edges
    }),200
