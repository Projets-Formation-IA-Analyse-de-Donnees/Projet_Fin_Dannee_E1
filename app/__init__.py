from flask import Flask
from app.routes.arango_route import pg_bp
from app.routes.postgres_route import arango_bp

def create_app():
    app = Flask(__name__)
    
    # Enregistrement des Blueprints
    app.register_blueprint(pg_bp)
    app.register_blueprint(arango_bp)
    
    return app
