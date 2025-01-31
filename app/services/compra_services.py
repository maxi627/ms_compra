from app import cache, redis_client  # Se asume que redis_client está configurado
from app.models import Compra
from app.repositories import CompraRepository
from contextlib import contextmanager
import time

class CompraService:
    """
    Servicio para gestionar compras con soporte de caché y bloqueos en Redis para concurrencia.
    """
    CACHE_TIMEOUT = 300  # Tiempo de expiración de caché en segundos
    REDIS_LOCK_TIMEOUT = 10  # Tiempo de bloqueo en Redis en segundos

    def __init__(self, repository=None):
        self.repository = repository or CompraRepository()

    @contextmanager
    def redis_lock(self, compra_id: int):
        """
        Context manager para gestionar el bloqueo de recursos en Redis.
        """
        lock_key = f"compra_lock_{compra_id}"
        lock_value = str(time.time())

        if redis_client.set(lock_key, lock_value, ex=self.REDIS_LOCK_TIMEOUT, nx=True):
            try:
                yield  # Permite la ejecución del bloque protegido
            finally:
                redis_client.delete(lock_key)
        else:
            raise Exception(f"El recurso está bloqueado para la compra {compra_id}.")

    def all(self) -> list[Compra]:
        """
        Obtiene la lista de todas las compras, con caché.
        """
        cached_compras = cache.get('compras')
        if cached_compras is None:
            compras = self.repository.get_all()
            if compras:
                cache.set('compras', compras, timeout=self.CACHE_TIMEOUT)
            return compras
        return cached_compras

    def add(self, compra: Compra) -> Compra:
        """
        Agrega una nueva compra y actualiza la caché.
        """
        new_compra = self.repository.save(compra)
        cache.set(f'compra_{new_compra.id}', new_compra, timeout=self.CACHE_TIMEOUT)
        cache.delete('compras')
        return new_compra

    def update(self, compra_id: int, updated_compra: Compra) -> Compra:
        """
        Actualiza una compra existente.
        :param compra_id: ID de la compra a actualizar.
        :param updated_compra: Datos de la compra actualizados.
        :return: Objeto Compra actualizado.
        """
        with self.redis_lock(compra_id):
            existing_compra = self.find(compra_id)
            if not existing_compra:
                raise Exception(f"Compra con ID {compra_id} no encontrada.")

            # Actualizar los atributos del objeto existente
            existing_compra.producto_id = updated_compra.producto_id
            existing_compra.fecha_compra = updated_compra.fecha_compra
            existing_compra.direccion_envio = updated_compra.direccion_envio

            saved_compra = self.repository.save(existing_compra)

            # Actualizar la caché
            cache.set(f'compra_{compra_id}', saved_compra, timeout=self.CACHE_TIMEOUT)
            cache.delete('compras')  # Invalida la lista de compras en caché

            return saved_compra

    def delete(self, compra_id: int) -> bool:
        """
        Elimina una compra por su ID y actualiza la caché.
        """
        with self.redis_lock(compra_id):
            deleted = self.repository.delete(compra_id)
            if deleted:
                cache.delete(f'compra_{compra_id}')
                cache.delete('compras')
            return deleted

    def find(self, compra_id: int) -> Compra:
        """
        Busca una compra por su ID, con caché.
        """
        cached_compra = cache.get(f'compra_{compra_id}')
        if cached_compra is None:
            compra = self.repository.get_by_id(compra_id)
            if compra:
                cache.set(f'compra_{compra_id}', compra, timeout=self.CACHE_TIMEOUT)
            return compra
        return cached_compra
