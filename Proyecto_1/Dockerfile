# Construir la imagen del servicio

# la imagen base

FROM python:3.12-slim

#la carpeta donde va a vivir todo dentro del contenedor

WORKDIR /servicio

#que los mensajes salgan inmediatamente

ENV PYTHONDONTWRITEBYTECODE-1 \
    PYTHONUNBUFFERED-1

#copiar solo el requirements

COPY requirements.txt .

#INSTALAMOS LAS LIBRERIAS

RUN pip install --no.cache-dir -r requirements.txt

#COPIAMOS TODOS LOS ARCHIVOS
COPY . .

#DOCUMENTACION DE PUERTO

EXPOSE 8080

#CORRER EL DESPLIEGUE

CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port ${PORT}"]