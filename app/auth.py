from flask import request, abort
import os

API_KEY = os.getenv("API_KEY")

def require_api_key():
    def wrapper(fn):
        def decorated(*args, **kwargs):
            if request.headers.get('x-api-key') != API_KEY:
                abort(403, "Clé API invalide ou manquante.")
            return fn(*args, **kwargs)
        decorated.__name__ = fn.__name__
        return decorated
    return wrapper
