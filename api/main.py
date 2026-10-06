from fastapi.middleware.cors import CORSMiddleware 
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import numpy as np
import os

# Importación condicional de TensorFlow
try:
    import tensorflow as tf
    from tensorflow import keras
    TF_AVAILABLE = True
except ImportError:
    TF_AVAILABLE = False

app = FastAPI(
    title="Celsius → Fahrenheit API",
    description="API REST que usa un modelo Keras para convertir grados Celsius a Fahrenheit.",
    version="1.0.0",
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Cargar modelo al arrancar
MODEL_PATH = os.getenv("MODEL_PATH", "modelo_GCtoGFV2.keras")
loaded_model = None  # <-- Inicia en None, se carga en startup

@app.on_event("startup")
def load_model():
    global loaded_model
    if not TF_AVAILABLE:
        print("TensorFlow no disponible – modo demo activo.")
        return
    if not os.path.exists(MODEL_PATH):
        print(f"Modelo no encontrado en '{MODEL_PATH}' – modo demo activo.")
        return
    try:
        # safe_mode=False y compile=False para compatibilidad con distintas versiones de Keras
        loaded_model = keras.models.load_model(
            MODEL_PATH,
            custom_objects=None,
            compile=False,
            safe_mode=False
        )
        print(f"Modelo cargado desde '{MODEL_PATH}'")
    except Exception as e:
        print(f"Error al cargar el modelo: {e}")


# Schemas
class CelsiusInput(BaseModel):
    celsius: float
    model_config = {
        "json_schema_extra": {
            "examples": [{"celsius": 21}]
        }
    }

class PredictionOutput(BaseModel):
    celsius: float
    fahrenheit: float
    source: str


# Endpoints
@app.get("/", summary="Health check")
def root():
    model_status = "loaded" if loaded_model is not None else "not loaded (demo mode)"
    return {
        "service": "Celsius → Fahrenheit API",
        "status": "running",
        "model": model_status,
    }


@app.post("/predict", response_model=PredictionOutput, summary="Predice Fahrenheit a partir de Celsius")
def predict(data: CelsiusInput):
    celsius_val = data.celsius

    if loaded_model is not None:
        try:
            celsius_array = np.array([celsius_val])
            prediction = loaded_model.predict(celsius_array)
            fahrenheit_val = float(np.squeeze(prediction))
            return PredictionOutput(
                celsius=celsius_val,
                fahrenheit=round(fahrenheit_val, 4),
                source="model",
            )
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error en predicción: {e}")
    else:
        fahrenheit_val = celsius_val * 9 / 5 + 32
        return PredictionOutput(
            celsius=celsius_val,
            fahrenheit=round(fahrenheit_val, 4),
            source="formula (modelo no cargado)",
        )


@app.get("/predict/{celsius}", response_model=PredictionOutput, summary="Predice vía GET con parámetro de ruta")
def predict_get(celsius: float):
    return predict(CelsiusInput(celsius=celsius))