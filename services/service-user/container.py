"""
Container du service user.
Regroupe tout ce qui est commun : app FastAPI, middlewares, exception
handlers, health check, et inclusion des routers. C'est le seul fichier
qui assemble les dépendances : main.py ne fait que le lancer.
"""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse


from api.rest.user_router import router as user_router

SERVICE_NAME = "user"

app = FastAPI(title=f"service-user")

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

app.include_router(user_router)
