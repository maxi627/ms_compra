from typing import List

from app import db
from app.models import Compra

from .repository import Repository_delete, Repository_get, Repository_save


class CompraRepository(Repository_save, Repository_get, Repository_delete):
    """
    Repositorio para gestionar compras con manejo seguro de transacciones.
    """
    def save(self, entity: Compra) -> Compra:
        try:
            db.session.add(entity)
            db.session.commit()
            return entity
        except Exception as e:
            db.session.rollback()
            raise e

    def get_all(self) -> List[Compra]:
        """
        Obtiene todas las compras almacenadas en la base de datos.
        """
        return Compra.query.all()

    def get_by_id(self, id: int) -> Compra:
        """
        Obtiene una compra específica por su ID.
        """
        return Compra.query.get(id)

    def delete(self, id: int) -> bool:
        """
        Elimina una compra por su ID con manejo de transacciones.
        """
        try:
            compra = self.get_by_id(id)
            if compra:
                db.session.delete(compra)
                db.session.commit()
                return True
            return False
        except Exception as e:
            db.session.rollback()
            raise e

