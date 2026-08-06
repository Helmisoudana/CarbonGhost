#!/usr/bin/env python3
"""
generate_service.py — génère le squelette strict minimum d'un microservice
en architecture hexagonale (domain / application / infrastructure / api).

Principe :
    - main.py est FIXE et IDENTIQUE pour tous les services. On n'y touche jamais.
      Il se contente de lancer uvicorn sur l'app définie dans container.py.
    - container.py regroupe tout ce qui est commun à un service : création de
      l'app FastAPI, middlewares, exception handlers, health check, et
      inclusion du router. C'est le seul fichier "d'assemblage".
    - domain/exceptions/base_exceptions.py est généré à l'identique dans
      chaque service : ce sont les exceptions communes que tous les services
      doivent utiliser (NotFoundException, ValidationException, etc.).

Usage:
    python generate_service.py user     --port 8001
    python generate_service.py mesures  --port 8003 --with-mqtt
    python generate_service.py carbone  --port 8002
"""

import argparse
from pathlib import Path

ROOT = Path("services")

# ---------------------------------------------------------------------------
# Contenu FIXE et commun à tous les services (ne dépend jamais de `name`)
# ---------------------------------------------------------------------------

MAIN_PY = '''import os
import uvicorn

from container import app

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=int(os.getenv("PORT", 8000)), reload=True)
'''

BASE_EXCEPTIONS_PY = '''"""
Exceptions de base communes à TOUS les services.
Ne pas mettre de logique spécifique à un service ici.
"""


class DomainException(Exception):
    """Exception racine du domaine. Toute exception métier en hérite."""


class NotFoundException(DomainException):
    """Ressource introuvable (-> 404)."""


class ValidationException(DomainException):
    """Donnée invalide (-> 422)."""


class ConflictException(DomainException):
    """Conflit d'état, ex: ressource déjà existante (-> 409)."""


class UnauthorizedException(DomainException):
    """Accès non autorisé (-> 401)."""
'''


def w(path: Path, content: str = ""):
    """Crée le fichier (et ses dossiers parents) avec le contenu donné."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def generate(name: str, port: int, with_mqtt: bool):
    base = ROOT / f"service-{name}"

    if base.exists():
        print(f"⚠️  {base} existe déjà, génération annulée.")
        return

    # --- structure hexagonale minimale -----------------------------------
    dirs = [
        base / "domain" / "entities",
        base / "domain" / "exceptions",
        base / "domain" / "ports" / "repositories",
        base / "application" / "use_cases",
        base / "infrastructure" / "persistence" / "postgres",
        base / "api" / "rest",
    ]
    for d in dirs:
        d.mkdir(parents=True, exist_ok=True)
        w(d / "__init__.py")

    w(base / "__init__.py")
    w(base / "domain" / "__init__.py")
    w(base / "application" / "__init__.py")
    w(base / "infrastructure" / "__init__.py")
    w(base / "api" / "__init__.py")

    # --- exceptions de base, identiques dans tous les services ------------
    w(base / "domain" / "exceptions" / "base_exceptions.py", BASE_EXCEPTIONS_PY)

    # --- main.py : FIXE, identique partout, ne jamais éditer ---------------
    w(base / "main.py", MAIN_PY)

    # --- container.py : tout ce qui est commun à un service (app, --------
    # middlewares, exception handlers, health check, inclusion du router)
    w(base / "container.py", f'''"""
Container du service {name}.
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
from api.rest.{name}_router import router as {name}_router

SERVICE_NAME = "{name}"

app = FastAPI(title=f"service-{name}")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Exception handlers communs (basés sur domain/exceptions) -------------


@app.exception_handler(NotFoundException)
async def not_found_handler(request: Request, exc: NotFoundException):
    return JSONResponse(status_code=404, content={{"error": str(exc)}})


@app.exception_handler(ValidationException)
async def validation_handler(request: Request, exc: ValidationException):
    return JSONResponse(status_code=422, content={{"error": str(exc)}})


@app.exception_handler(ConflictException)
async def conflict_handler(request: Request, exc: ConflictException):
    return JSONResponse(status_code=409, content={{"error": str(exc)}})


@app.exception_handler(UnauthorizedException)
async def unauthorized_handler(request: Request, exc: UnauthorizedException):
    return JSONResponse(status_code=401, content={{"error": str(exc)}})


@app.exception_handler(DomainException)
async def domain_exception_handler(request: Request, exc: DomainException):
    return JSONResponse(status_code=400, content={{"error": str(exc)}})


# --- Health check commun à tous les services -------------------------------


@app.get("/health")
def health():
    return {{"status": "ok", "service": SERVICE_NAME}}


# --- Router spécifique au service ------------------------------------------

app.include_router({name}_router)
''')

    # --- exemple de router vide, à remplir au fil du dev -------------------
    w(base / "api" / "rest" / f"{name}_router.py", f'''from fastapi import APIRouter

router = APIRouter(prefix="/{name}", tags=["{name}"])

# TODO: brancher les routes sur les use cases de application/use_cases/
# En cas d'erreur métier, lever une exception de domain/exceptions/base_exceptions.py
# (NotFoundException, ValidationException, ...), le container s'occupe du reste.
''')

    # --- requirements minimales --------------------------------------------
    reqs = ["fastapi", "uvicorn[standard]", "pydantic"]
    if with_mqtt:
        reqs.append("paho-mqtt")
    w(base / "requirements.txt", "\n".join(reqs) + "\n")

    # --- Dockerfile minimal --------------------------------------------------
    w(base / "Dockerfile", f'''FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE {port}
CMD ["python", "main.py"]
''')

    # --- .env.example ----------------------------------------------------
    w(base / ".env.example", f"PORT={port}\n")

    if with_mqtt:
        w(base / "infrastructure" / "mqtt" / "__init__.py")
        w(base / "infrastructure" / "mqtt" / "mqtt_client.py", '''# TODO: client MQTT (paho-mqtt) branché sur shared/contracts/mqtt_messages.py
''')

    print(f"✅ service-{name} généré sur le port {port}"
          f"{' (avec MQTT)' if with_mqtt else ''}")


def main():
    parser = argparse.ArgumentParser(description="Générateur de microservice minimal")
    parser.add_argument("name", help="nom du service (ex: user, mesures, carbone)")
    parser.add_argument("--port", type=int, required=True, help="port d'écoute")
    parser.add_argument("--with-mqtt", action="store_true", help="ajoute un client MQTT vide")
    args = parser.parse_args()

    generate(args.name, args.port, args.with_mqtt)


if __name__ == "__main__":
    main()