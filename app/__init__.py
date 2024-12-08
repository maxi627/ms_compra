import os

from flask import Flask
from flask_caching import Cache
from flask_sqlalchemy import SQLAlchemy

from app.config import cache_config, factory

db = SQLAlchemy()
cache=Cache()
def create_app():
    app = Flask(__name__)
    app_context = os.getenv('FLASK_ENV', 'development')
    try:
        app.config.from_object(factory(app_context))
    except Exception as e:
        raise RuntimeError(f"Error al cargar la configuración para el entorno {app_context}: {e}")

    try:
        db.init_app(app)
        cache.init_app(app, config=cache_config) 
    except Exception as e:
        raise RuntimeError(f"Error al inicializar extensiones: {e}")

    try:
        from app.routes import compra
        app.register_blueprint(compra, url_prefix='/api/v1')
    except Exception as e:
        raise RuntimeError(f"Error al registrar blueprints: {e}")

    # Ruta de prueba
    @app.route('/ping', methods=['GET'])
    def ping():
        return {"message": "El servicio de compras está en funcionamiento"}

    return app

