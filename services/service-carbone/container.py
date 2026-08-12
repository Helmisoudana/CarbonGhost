"""
Container du service carbone.
Regroupe tout ce qui est commun : app FastAPI, middlewares, exception
handlers, health check, et inclusion des routers. C'est le seul fichier
qui assemble les dépendances : main.py ne fait que le lancer.
"""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse


from api.rest.carbone_router import router as carbone_router

SERVICE_NAME = "carbone"

app = FastAPI(title=f"service-carbone")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)




# --- Health check commun à tous les services -------------------------------


@app.get("/health")
def health():
    return {"status": "ok", "service": SERVICE_NAME}


# --- Router spécifique au service ------------------------------------------

app.include_router(carbone_router)
