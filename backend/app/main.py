# Gestión de inventario (Gestivoryx)
# Autores: Alexander Sinisterra
# Tecnologías: Python, FastAPI

from fastapi import FastAPI

app = FastAPI(title="Gestivoryx - Gestión de Inventario")

@app.get("/")
def root():
    return {
        "status": "ok",
        "message": "API de Gestión de Inventario funcionando"
    }
