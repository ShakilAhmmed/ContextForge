from fastapi import FastAPI

from app.api.v1 import router as api_v1_router
from app.core.config import settings
from app.core.exception_handlers import register_exception_handlers

app = FastAPI(title="ContextForge", version="0.1.0")

register_exception_handlers(app)

app.include_router(api_v1_router)


@app.get("/health")
async def health() -> dict:
    return {"status": "ok", "env": settings.env}
