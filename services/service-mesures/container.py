"""
Container du service mesures.
Regroupe tout ce qui est commun : app FastAPI, middlewares, exception
handlers, health check, et inclusion des routers. C'est le seul fichier
qui assemble les dépendances : main.py ne fait que le lancer.
"""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from domain.exceptions.base_exceptions import (
    DomainException,
    NotFoundException,
    ValidationException,
    ConflictException,
    UnauthorizedException,
)
from api.rest.mesures_router import router as mesures_router

SERVICE_NAME = "mesures"

app = FastAPI(title=f"service-mesures")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Exception handlers communs (basés sur domain/exceptions) -------------


@app.exception_handler(NotFoundException)
async def not_found_handler(request: Request, exc: NotFoundException):
    return JSONResponse(status_code=404, content={"error": str(exc)})


@app.exception_handler(ValidationException)
async def validation_handler(request: Request, exc: ValidationException):
    return JSONResponse(status_code=422, content={"error": str(exc)})


@app.exception_handler(ConflictException)
async def conflict_handler(request: Request, exc: ConflictException):
    return JSONResponse(status_code=409, content={"error": str(exc)})


@app.exception_handler(UnauthorizedException)
async def unauthorized_handler(request: Request, exc: UnauthorizedException):
    return JSONResponse(status_code=401, content={"error": str(exc)})


@app.exception_handler(DomainException)
async def domain_exception_handler(request: Request, exc: DomainException):
    return JSONResponse(status_code=400, content={"error": str(exc)})


# --- Health check commun à tous les services -------------------------------


@app.get("/health")
def health():
    return {"status": "ok", "service": SERVICE_NAME}


# --- Router spécifique au service ------------------------------------------

app.include_router(mesures_router)
