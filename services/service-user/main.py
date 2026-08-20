import os
import uvicorn

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from api.rest.user_router import router as user_router

SERVICE_NAME = "user"

app = FastAPI(title="service-user")

# Middlewares
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Exception handler global
@app.exception_handler(Exception)
def unhandled_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"error": "internal_server_error", "detail": str(exc)},
    )

# helth check endpoint
@app.get("/health")
def health_check():
    return {"status": "ok", "service": SERVICE_NAME}

app.include_router(user_router)

# lancer le serveur uvicorn si ce fichier est exécuté directement
if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)