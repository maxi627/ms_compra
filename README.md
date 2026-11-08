# ms_compra

Microservicio de **compras** del e-commerce basado en microservicios. Registra cada compra realizada (producto, fecha y dirección de envío) y es uno de los pasos que ejecuta la Saga orquestada desde [base_ms](https://github.com/maxi627/base_ms).

- **Stack:** Python 3.10 · Flask 3 · SQLAlchemy · Marshmallow · PostgreSQL · Redis (caché, locks y rate limiting) · Gunicorn · Docker · Traefik
- **Puerto interno:** `5000`
- **Host vía Traefik:** `http://compras.localhost/api/v1`

---

## Ecosistema

Este repositorio forma parte de un conjunto de repos que funcionan juntos:

| Repositorio | Rol | Puerto | Host vía Traefik |
|---|---|---|---|
| [servicios](https://github.com/maxi627/servicios) | Infraestructura: Traefik (API gateway) y Redis | 80 / 443 / 8080 · 6379 | — |
| [base_ms](https://github.com/maxi627/base_ms) | PostgreSQL compartida (`ecomercedb`) + orquestador Saga | 5432 · 5005 | — |
| [ms_producto](https://github.com/maxi627/ms_producto) | Catálogo de productos | 5003 | `producto.localhost` |
| [ms_stock](https://github.com/maxi627/ms_stock) | Movimientos de inventario | 5001 | `stock.localhost` |
| [ms_pagos](https://github.com/maxi627/ms_pagos) | Registro de pagos | 5002 | `pagos.localhost` |
| **[ms_compra](https://github.com/maxi627/ms_compra)** (este repo) | Registro de compras | 5000 | `compras.localhost` |

```mermaid
flowchart LR
    cliente([Cliente / k6]) -->|HTTP :80| traefik
    saga[base_ms<br/>Orquestador Saga] -->|HTTP| traefik
    traefik{{Traefik}} -->|compras.localhost| compra[ms_compra :5000]
    traefik -->|stock.localhost| stock[ms_stock :5001]
    traefik -->|pagos.localhost| pagos[ms_pagos :5002]
    traefik -->|producto.localhost| producto[ms_producto :5003]
    compra & stock & pagos & producto --> pg[(PostgreSQL<br/>ecomercedb)]
    compra & stock & pagos & producto --> redis[(Redis)]
```

Todos los contenedores se comunican por la red Docker externa **`red1`**.

### Levantar todo el ecosistema

```bash
# 1. Red compartida (una sola vez)
docker network create red1

# 2. Infraestructura: Redis y Traefik
cd servicios
docker compose -f docker-compose.redis.yml up -d
docker compose -f docker-compose.traefik.yml up -d

# 3. Base de datos PostgreSQL
cd ../base_ms
docker compose up -d

# 4. Microservicios (cada uno con su propio .env)
cd ../ms_producto && docker compose -f docker-compose.producto.yml up -d --build
cd ../ms_stock    && docker compose -f docker-compose.stock.yml up -d --build
cd ../ms_pagos    && docker compose -f docker-compose.pagos.yml up -d --build
cd ../ms_compra   && docker compose -f docker-compose.compra.yml up -d --build
```

Dashboard de Traefik: <http://localhost:8080>. Si los hosts `*.localhost` no resuelven en tu sistema, agregalos al archivo `hosts` apuntando a `127.0.0.1`.

---

## Modelo de datos

Tabla `Compra`:

| Campo | Tipo | Validación |
|---|---|---|
| `id` | Integer (PK, autoincremental) | solo lectura |
| `producto_id` | Integer | requerido (ID de [ms_producto](https://github.com/maxi627/ms_producto)) |
| `fecha_compra` | DateTime | requerido, ISO 8601 |
| `direccion_envio` | Text | requerido, entre 8 y 40 caracteres |

## API

Base: `http://compras.localhost/api/v1`

| Método | Ruta | Descripción | Rate limit |
|---|---|---|---|
| GET | `/compras` | Lista todas las compras | 50000/min |
| GET | `/compras/<id>` | Obtiene una compra | 50000/min |
| POST | `/compras` | Crea una compra | 50000/min |
| PUT | `/compras/<id>` | Actualiza una compra | 50000/min |
| DELETE | `/compras/<id>` | Elimina una compra (usado como compensación en la Saga) | 30000/min |
| GET | `/ping` | Health check (fuera de `/api/v1`) | 10000/min (default) |

Ejemplo:

```bash
curl -X POST http://compras.localhost/api/v1/compras \
  -H "Content-Type: application/json" \
  -d '{"producto_id": 1, "fecha_compra": "2025-01-23T10:00:00", "direccion_envio": "Calle 123"}'
```

Todas las respuestas siguen el formato común del ecosistema:

```json
{
  "message": "Compra created",
  "status_code": 201,
  "data": { "id": 1, "producto_id": 1, "fecha_compra": "2025-01-23T10:00:00", "direccion_envio": "Calle 123" }
}
```

Códigos: `200` OK · `201` creado · `404` no encontrado · `422` error de validación · `429` límite excedido · `500` error interno.

## Arquitectura interna

Misma estructura en capas que el resto de los microservicios:

```
app/
├── config/        # Configuración por entorno (development / testing / production) y caché
├── models/        # Modelo SQLAlchemy (Compra)
├── mapping/       # Schemas Marshmallow (CompraSchema, ResponseSchema)
├── repositories/  # Acceso a datos con manejo de transacciones (commit / rollback)
├── services/      # Lógica de negocio + caché Redis + locks distribuidos; ResponseBuilder
└── routes/        # Blueprint Flask con los endpoints y rate limiting
main.py            # Crea tablas y arranca Flask (dev) o Gunicorn con 3 workers (production)
```

- **Caché (Flask-Caching + Redis):** `compras` y `compra_<id>` con TTL de 300 s; se invalida al crear, actualizar o borrar.
- **Concurrencia:** `PUT` y `DELETE` toman un lock en Redis (`compra_lock_<id>`, 10 s, `SET NX`) para evitar modificaciones simultáneas.
- **Rate limiting:** Flask-Limiter con Redis como backend, compartido entre réplicas.

## Configuración

Crear un archivo `.env` en la raíz del repo:

```env
FLASK_ENV=development            # development | testing | production

# PostgreSQL (contenedor ecomercedb de base_ms)
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_DB=ecomerce
POSTGRES_PORT=5432
DEV_DATABASE_URI=postgresql://postgres:postgres@ecomercedb:5432/ecomerce
TEST_DB_URI=postgresql://postgres:postgres@localhost:5432/ecomerce_test
PROD_DATABASE_URI=postgresql://postgres:postgres@ecomercedb:5432/ecomerce

# Redis (contenedor redis_service de servicios)
REDIS_HOST=redis_service
REDIS_PORT=6379
REDIS_PASSWORD=cambiar
REDIS_DB=0
```

Con `FLASK_ENV=production` la app corre con Gunicorn (3 workers); en cualquier otro caso con el servidor de desarrollo de Flask.

## Ejecución

**Con Docker** (requiere `red1`, Redis, Traefik y PostgreSQL levantados, ver [Ecosistema](#ecosistema)):

```bash
docker compose -f docker-compose.compra.yml up -d --build
```

La imagen se publica como `ms-compras:v1.2`. Para escalar horizontalmente, ajustar `deploy.replicas` en el compose; Traefik balancea entre las réplicas.

**Local:**

```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python main.py
```

Si Python no encuentra el módulo `app`, agregar la raíz del repo al `PYTHONPATH` (`set PYTHONPATH=<ruta del repo>` en Windows).

## Tests

```bash
# Unitarios (requieren PostgreSQL y Redis accesibles)
python -m unittest discover -s test -p "*_test.py" -v   # los tests usan FLASK_ENV=testing (TEST_DB_URI)
```

| Archivo | Qué prueba |
|---|---|
| `test/app_test.py` | Que la app se crea correctamente |
| `test/db_test.py` | Conexión a la base de datos |
| `test/redis_test.py` | Conexión a Redis y caché después de crear una compra |
| `test/compra_test.py` | Modelo `Compra` |

**Carga con [k6](https://k6.io/):** `testk6.js` sube a 50 usuarios virtuales contra `GET /compras` y verifica status 200 y latencia < 200 ms.

```bash
k6 run testk6.js
```
