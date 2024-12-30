#TODO:  //LISTO// Usar otro servidor para pasar a produccion en cada micro servicio


# Imagen base de Python
FROM python:3.10-slim-bullseye

# Variables de entorno
ENV FLASK_ENV=development \
    PYTHONUNBUFFERED=1 \
    PATH=$PATH:/home/flaskapp/.local/bin

# Crear un usuario no root y establecer el directorio de trabajo
RUN useradd --create-home --home-dir /home/flaskapp flaskapp
WORKDIR /home/flaskapp

# Instalar dependencias del sistema necesarias (libpq-dev para PostgreSQL)
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

# Copiar el archivo de dependencias primero y luego instalar
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar los archivos del proyecto al contenedor
COPY . /home/flaskapp/

# Cambiar a usuario flaskapp
USER flaskapp

# Exponer el puerto de Flask
EXPOSE 5000

# Comando de entrada
ENTRYPOINT ["python", "main.py"]
