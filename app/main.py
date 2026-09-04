from fastapi import FastAPI

from app.api.routes.tenants import router as tenants_router
from app.core.config import settings

app = FastAPI(title="ContextForge", version="0.1.0")

app.include_router(tenants_router)


@app.get("/health")
async def health() -> dict:
    return {"status": "ok", "env": settings.env}
