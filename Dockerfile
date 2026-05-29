# 1. Usamos una versión oficial y liviana de Python
FROM python:3.10-slim

# 2. Le decimos al contenedor dónde vamos a trabajar adentro de su memoria
WORKDIR /app

# 3. Copiamos PRIMERO el archivo de requerimientos (esto hace que la construcción sea más rápida)
COPY requirements.txt .

# 4. Instalamos las librerías
RUN pip install --no-cache-dir -r requirements.txt

# 5. Copiamos el resto de tu código (tu main.py y la carpeta /Modelos)
COPY . .

# 6. Exponemos el puerto 8000 para que se pueda acceder desde internet
EXPOSE 8000

# 7. El comando exacto para encender tu API, preparado para un servidor web (0.0.0.0)
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]