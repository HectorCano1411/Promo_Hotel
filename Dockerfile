# Usa la imagen base de Python
FROM python:3.10

# Establece el directorio de trabajo
WORKDIR /app

# Copia los archivos de requisitos
COPY requirements.txt .

# Instala las dependencias
RUN pip install --no-cache-dir -r requirements.txt


# Instala django-environ
RUN pip install django-environ

# Copia el resto de los archivos de la aplicación
COPY . .

# Crear un grupo con gid=1000
# RUN addgroup --gid 1000 celerygroup

# # Crear un usuario con uid=1000 y agregarlo al grupo celerygroup
# RUN adduser --disabled-password --gecos '' --uid 1000 --gid 1000 celeryuser && \
#     chown -R celeryuser:celerygroup /app

# # Asignar permisos de escritura a la base de datos SQLite si existe
# RUN touch /app/db.sqlite3 && \
#     chown celeryuser:celerygroup /app/db.sqlite3 && \
#     chmod 664 /app/db.sqlite3

# Asignar permisos de escritura a la carpeta entera por si db.sqlite3 no existe aún
# RUN chown -R celeryuser:celerygroup /app

# Cambiar al usuario no root
# USER celeryuser

# Exponer el puerto que utiliza Django (8000)
EXPOSE 8000


# Comando por defecto para ejecutar el servidor
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
