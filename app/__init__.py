import os
from flask import Flask
from flask_caching import Cache
from flask_sqlalchemy import SQLAlchemy
from app.config import cache_config, factory
import redis
import logging
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

# Configuración de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Instancia global de extensiones
db = SQLAlchemy()
cache = Cache()

# Obtener las variables de entorno
redis_host = os.getenv('REDIS_HOST', 'localhost')
redis_port = int(os.getenv('REDIS_PORT', 6379))
redis_password = os.getenv('REDIS_PASSWORD', '')
redis_db = int(os.getenv('REDIS_DB', 0))


# URI de Redis para Flask-Limiter
redis_uri = f"redis://:{redis_password}@{redis_host}:{redis_port}/{redis_db}"

# Crear una instancia de Redis
redis_client = redis.StrictRedis(
    host=redis_host,
    port=redis_port,
    db=redis_db,
    password=redis_password,
    decode_responses=True
)
# Inicializar el limitador con Redis como backend
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["10 per minute"],
    storage_uri=redis_uri  # ✅ Pasar la URI en lugar de la instancia de Redis
)
# Verificar la conexión
try:
    redis_client.ping()
    logger.info("Conexión a Redis exitosa.")
except redis.ConnectionError as e:
    logger.error(f"Error al conectar con Redis: {e}")

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
        limiter.init_app(app)
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
