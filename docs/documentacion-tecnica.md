# REPORTE TÉCNICO

Proyecto GCtoGF API

Conversión Celsius → Fahrenheit con Modelo Keras en Docker

**Angel de Jesús Canela Figueroa**

22 de Abril de 2026

Mac M3 (Apple Silicon) — macOS

## 1. Problemas Encontrados

Al intentar ejecutar el proyecto por primera vez, se identificaron cuatro problemas que impedían la construcción y ejecución correcta de la API:

### 1.1. Estructura de Carpetas Incorrecta

El comando docker build se ejecutaba desde la carpeta raíz tempcross/, pero el Dockerfile se encontraba dentro de api/. Docker no podía encontrarlo y fallaba con el siguiente error:

```
ERROR: failed to read dockerfile: open Dockerfile: no such file or directory
```

Solución: Identificar el directorio correcto y ejecutar el build desde dentro de api/.

### 1.2. Nombre del Modelo Incorrecto

El archivo físico del modelo Keras se llamaba modelo_GCTogFV2.keras (con 'T' mayúscula y 'o' minúscula), pero el Dockerfile buscaba modelo_GCtoGFV2.keras (con 't' minúscula y 'G' mayúscula). macOS distingue entre mayúsculas y minúsculas en nombres de archivo, lo que causó:

```
ERROR: "/modelo_GCtoGFV2.keras": not found
```

Solución: Renombrar el archivo para que coincidiera exactamente con lo definido en el Dockerfile.

### 1.3. TensorFlow Incompatible con Mac M3

El archivo requirements.txt original contenía tensorflow-cpu==2.16.1, paquete que no existe para la arquitectura ARM (Apple Silicon M1/M2/M3). Solo está disponible para x86/Intel:

```
ERROR: No matching distribution found for tensorflow-cpu==2.16.1
```

Solución: Usar el paquete oficial para Apple Silicon:

```
tensorflow==2.16.1
```

### 1.4. Docker sin Plataforma Definida

El Dockerfile original no especificaba la plataforma de destino. En Mac M3, Docker corre en ARM64 pero TensorFlow dentro del contenedor requiere AMD64. Sin especificarlo, la imagen podía ser incompatible.

Solución: Agregar la plataforma explícita en el Dockerfile y en el comando de build.

## 2. Cambios Realizados

### 2.1. Archivo requirements.txt

**Antes:**

```
tensorflow-cpu==2.16.1
```

**Después:**

```
tensorflow==2.16.1
```

### 2.2. Archivo Dockerfile

**Antes:**

```
FROM python:3.11-slim
```

**Después:**

```
FROM --platform=linux/amd64 python:3.11-slim
```

Nota: La advertencia amarilla en VSCode sobre esta línea es informativa, no es un error. El comando es válido y necesario para Mac M3.

### 2.3. Nombre del Modelo

**Antes:**

```
modelo_GCTogFV2.keras
```

**Después:**

```
modelo_GCtoGFV2.keras
```

## 3. Comandos Ejecutados — Paso a Paso

### Paso 1. Ubicar el directorio de trabajo

```
pwd

# Resultado: /Users/angelescuela/Documents/tempcross
```

La carpeta estaba en Documents (inglés), no en Documentos (español). Por eso fallaban todos los cd anteriores.

### Paso 2. Renombrar el modelo

```
mv api/modelo_GCTogFV2.keras api/modelo_GCtoGFV2.keras
```

Corrige la diferencia de mayúsculas/minúsculas en el nombre del archivo.

### Paso 3. Entrar a la carpeta api/

```
cd api
```

El Dockerfile debe estar en el mismo directorio donde se ejecuta docker build.

### Paso 4. Crear el entorno virtual

```
python3 -m venv venv
```

Crea un entorno Python aislado para que las dependencias no conflictúen con el sistema global.

### Paso 5. Activar el entorno virtual

```
source venv/bin/activate
```

Se confirma que está activo cuando el prompt muestra (venv) al inicio. Sin activarlo, pip instala en el Python global.

### Paso 6. Modificar requirements.txt

Se editó directamente en VSCode reemplazando tensorflow-cpu por tensorflow nativo.

### Paso 7. Modificar Dockerfile

Se agregó --platform linux/amd64 en la línea FROM del Dockerfile.

### Paso 8. Instalar dependencias localmente

```
pip install -r requirements.txt
```

Instala en el entorno virtual las librerías necesarias para correr la API localmente fuera de Docker.

### Paso 9. Construir la imagen Docker

```
docker buildx build --platform linux/amd64 -t img-api .
```

buildx: Constructor extendido con soporte multiplataforma.

--platform linux/amd64: Fuerza la imagen a AMD64 aunque el Mac sea ARM.

-t img-api: Nombre de la imagen.

.: Usa el directorio actual como contexto (donde está el Dockerfile).

### Paso 10. Correr el contenedor

```
docker run --name srv-api -p 8000:8000 img-api:latest
```

--name srv-api: Nombre del contenedor.

-p 8000:8000: Mapea el puerto 8000 del contenedor al puerto 8000 del Mac.

img-api:latest: Imagen a usar.

### Paso 11. Verificar funcionamiento

```
http://localhost:8000 # Health check

http://localhost:8000/docs # Swagger UI

http://localhost:8000/predict/100 # 100°C → 212°F
```

## 4. Tabla Resumen de Comandos

| **Paso** | **Comando** | **Resultado** |
|----|----|----|
| 1 | pwd | Ubicó la carpeta real en Documents/ |
| 2 | mv modelo_GCTogFV2.keras ... | Corrigió el nombre del modelo |
| 3 | cd api | Entró al directorio correcto |
| 4 | python3 -m venv venv | Creó entorno Python aislado |
| 5 | source venv/bin/activate | Activó el entorno (venv) |
| 6 | Editar requirements.txt | Compatibilidad con Mac M3 |
| 7 | Editar Dockerfile | Plataforma linux/amd64 |
| 8 | pip install -r requirements.txt | Instaló dependencias locales |
| 9 | docker buildx build ... | Construyó imagen Docker |
| 10 | docker run ... | Levantó el contenedor |
| 11 | Navegador localhost:8000 | API funcionando  |

## 5. Resultado Final

| **Componente**                  | **Estado**                        |
|---------------------------------|-----------------------------------|
| Entorno virtual Python (venv)   |  Creado y activo                |
| Dependencias locales instaladas |  Con tensorflow nativo (ARM64)   |
| Imagen Docker construida        |  img-api:latest                 |
| Contenedor corriendo            |  srv-api en puerto 8000         |
| Modelo Keras cargado            |  modelo_GCtoGFV2.keras          |
| API respondiendo                |  http://localhost:8000          |
| Documentación Swagger           |  http://localhost:8000/docs     |
| Predicción funcionando          |  100°C → 212°F vía modelo Keras |

## 6. Arquitectura Final del Proyecto

### Estructura de carpetas

```
tempcross/

├── venv/ # Entorno virtual Python (local Mac)

└── api/

├── Dockerfile # Con --platform linux/amd64

├── main.py # API FastAPI con 3 endpoints

├── modelo_GCtoGFV2.keras # Modelo entrenado Keras

└── requirements.txt # tensorflow nativo para Mac M3
```

### Flujo de funcionamiento

- Cliente (navegador/app) envía petición HTTP

- Docker recibe en puerto 8000 y redirige al contenedor

- FastAPI + Uvicorn procesan la petición

- El modelo Keras (TensorFlow) realiza la predicción

- La API devuelve: { celsius, fahrenheit, source: 'model' }

### Endpoints disponibles

- GET / → Health check del servicio

- POST /predict → Predicción por JSON body

- GET /predict/{n} → Predicción por parámetro en URL
