import os

from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, ".env"))  # Carga las variables del entorno

class Config:
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    @staticmethod
    def init_app(app):
        """Método para inicializar configuraciones adicionales si es necesario."""
        pass

    @staticmethod
    def validate_required_env_vars(env_vars):
        """Valida que las variables de entorno críticas estén definidas."""
        missing_vars = [var for var in env_vars if not os.getenv(var)]
        if missing_vars:
            raise ValueError(f"Las siguientes variables de entorno faltan o están vacías: {', '.join(missing_vars)}")

class DevelopmentConfig(Config):
    SQLALCHEMY_TRACK_MODIFICATIONS = True
    SQLALCHEMY_RECORD_QUERIES = True
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.getenv('DEV_DATABASE_URI') 
    CACHE_REDIS_HOST = os.getenv('REDIS_HOST')
    CACHE_REDIS_PORT = os.getenv('REDIS_PORT')
    CACHE_REDIS_DB = os.getenv('REDIS_DB')
    CACHE_REDIS_PASSWORD = os.getenv('REDIS_PASSWORD')

    @staticmethod
    def init_app(app):
        """Valida las variables de entorno críticas para desarrollo."""
        Config.validate_required_env_vars(['DEV_DATABASE_URI', 'REDIS_HOST', 'REDIS_PORT'])

class TestingConfig(Config):
    SQLALCHEMY_TRACK_MODIFICATIONS = True
    SQLALCHEMY_RECORD_QUERIES = True
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.getenv('TEST_DB_URI')
    CACHE_REDIS_HOST = os.getenv('REDIS_HOST')
    CACHE_REDIS_PORT = os.getenv('REDIS_PORT')
    CACHE_REDIS_DB = os.getenv('REDIS_DB')
    CACHE_REDIS_PASSWORD = os.getenv('REDIS_PASSWORD')

    @staticmethod
    def init_app(app):
        """Valida las variables de entorno críticas para pruebas."""
        Config.validate_required_env_vars(['TEST_DB_URI', 'REDIS_HOST', 'REDIS_PORT'])

class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI = os.getenv("PROD_DATABASE_URI")

    @staticmethod
    def init_app(app):
        """Valida las variables de entorno críticas para producción."""
        Config.validate_required_env_vars(['PROD_DATABASE_URI'])

def factory(env):
    """Devuelve la configuración adecuada según el entorno."""
    envs = {
        "development": DevelopmentConfig,
        "production": ProductionConfig,
        "testing": TestingConfig,
        "default": DevelopmentConfig
    }
    return envs.get(env, DevelopmentConfig)
