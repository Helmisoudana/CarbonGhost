from fastapi import FastAPI

from config import settings
from container import container
from api.rest.assistant_router import get_router


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="Service Assistant intelligent du systeme de monitoring carbone.",
)


@app.on_event("startup")
async def startup_event():
    container.start_kafka_consumer()


app.include_router(
    get_router(
        container.ask_use_case,
        container.report_use_case,
    )
)


@app.get("/health")
async def health_check():
    return {
        "status": "UP",
        "service": settings.app_name,
        "version": settings.app_version,
    }
