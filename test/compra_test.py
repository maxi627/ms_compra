import unittest, os
from app import create_app, db
from app.models import Compra
class CompraTestCase(unittest.TestCase):
    
    def setUp(self):
        # User
        self.IDPRODUCTO_PRUEBA = 1
        self.FECHA_COMPRA_PRUEBA = '2020-01-01:00:00:00'
        self.DIRECCION_ENVIO_PRUEBA = "Calle falsa 123"
    
        os.environ['FLASK_CONTEXT'] = 'testing'
        self.app = create_app()
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()
    def test_compra(self):
        compra = self.__get_compra()

        self.assertEqual(compra.producto_id, self.IDPRODUCTO_PRUEBA)
        self.assertEqual(compra.direccion_envio, self.DIRECCION_ENVIO_PRUEBA)
        self.assertEqual(compra.fecha_compra, self.FECHA_COMPRA_PRUEBA)

    def __get_compra(self):
        compra = Compra()
        compra.producto_id = self.IDPRODUCTO_PRUEBA
        compra.fecha_compra = self.FECHA_COMPRA_PRUEBA
        compra.direccion_envio = self.DIRECCION_ENVIO_PRUEBA

        return compra
    
if __name__ == '__main__':
    unittest.main()