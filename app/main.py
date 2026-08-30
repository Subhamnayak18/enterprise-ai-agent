from fastapi import FastAPI

from app.api.routes import router
from app.core.config import get_settings
from app.core.logging import configure_logging

configure_logging()
settings = get_settings()
app = FastAPI(title=settings.app_name, version=settings.app_version, description="Grounded procurement assistant combining enterprise policy retrieval, operational SQL and deterministic business tools.")
app.include_router(router)
