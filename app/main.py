from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.v1 import router as api_v1_router
from app.core.config import settings
from app.core.exception_handlers import register_exception_handlers
from app.core.storage import get_storage


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    storage = await get_storage()
    await storage.ensure_bucket()
    yield


app = FastAPI(title="ContextForge", version="0.1.0", lifespan=lifespan)

register_exception_handlers(app)

app.include_router(api_v1_router)


@app.get("/health")
async def health() -> dict:
    return {"status": "ok", "env": settings.env}
