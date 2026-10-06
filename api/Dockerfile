# Stage: runtime
# Se fuerza linux/amd64 porque en Mac M3 el contenedor necesita x86_64
# para TensorFlow. Sin esto, el build falla en Apple Silicon.
FROM --platform=linux/amd64 python:3.12-slim

# Metadatos
LABEL description="API REST FastAPI - Celsius a Fahrenheit con modelo Keras"

# Variables de entorno
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    MODEL_PATH=/app/modelo_GCtoGFV2.keras

WORKDIR /app

# Dependencias del sistema
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

# Dependencias Python
COPY requirements.txt .

# Dentro del contenedor (linux/amd64) se usa tensorflow-cpu.
# En el entorno local Mac M3 (ARM64) se usa tensorflow nativo.
# El requirements.txt de api/ es solo para uso local.
RUN pip install --no-cache-dir \
    fastapi==0.115.0 \
    uvicorn[standard]==0.30.6 \
    numpy==1.26.4 \
    tensorflow-cpu==2.16.1 \
    pydantic==2.7.4

# Código fuente
COPY main.py .

# Modelo
# El archivo debe llamarse exactamente modelo_GCtoGFV2.keras
# (la 'o' de 'to' es minúscula).
COPY modelo_GCtoGFV2.keras /app/modelo_GCtoGFV2.keras

# Puerto expuesto
EXPOSE 8000

# Comando de arranque
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]