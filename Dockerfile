# Usar una imagen base oficial de Python
FROM python:3.9-slim

# Establecer el directorio de trabajo en el contenedor
WORKDIR /app

# Copiar el archivo requirements.txt en el directorio de trabajo
COPY requirements.txt .

# Instalar las dependencias del proyecto
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el resto del código de la aplicación en el directorio de trabajo
COPY . .

# Comando para ejecutar la aplicación
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]