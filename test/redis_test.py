import os
import unittest
from redis import Redis
from app import create_app, cache, db
from app.models import Compra
from app.services import CompraService

service = CompraService()

class RedisTestCase(unittest.TestCase):
    def setUp(self):
        os.environ['FLASK_CONTEXT'] = 'testing'
        self.app = create_app()
        self.app_context = self.app.app_context()
        
        self.app_context.push()
        db.create_all()
        
    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()
    # test connection to Redis
    def test_redis_connection(self):
        redis = Redis(
            host=self.app.config['CACHE_REDIS_HOST'],
            port=self.app.config['CACHE_REDIS_PORT'],
            db=self.app.config['CACHE_REDIS_DB'],
            password=self.app.config['CACHE_REDIS_PASSWORD']
        )
        self.assertTrue(redis.ping())
    
    def test_cache_after_adding_compra(self):
        compra = Compra(producto_id=1, fecha_compra='2024-09-13T15:30:00', direccion_envio='Calle 1')
        compra1 = service.add(compra)
        

        cached_compra = cache.get(f'compra_{compra1.id}')
        
        self.assertIsNotNone(cached_compra)
        self.assertEqual(cached_compra.id, compra1.id)
        self.assertEqual(cached_compra.producto_id, compra1.producto_id)
        self.assertEqual(cached_compra.fecha_compra, compra1.fecha_compra)
        self.assertEqual(cached_compra.direccion_envio, compra1.direccion_envio)

if __name__ == '__main__':
    unittest.main()