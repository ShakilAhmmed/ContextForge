---
name: fastapi-endpoint-design
description: Add or modify a FastAPI REST endpoint following industry-standard resource-oriented design (controller owns its router, typed Pydantic I/O, consistent envelope, pagination). Use when adding a new API resource/endpoint, changing a request/response shape, or reviewing an endpoint's structure in this repo.
---

# FastAPI Endpoint Design

## Quick start

This repo's pattern — one file per resource, controller owns its router:

```
app/controllers/<resource>_controller.py   router = APIRouter(prefix=..., tags=[...]); @router.get/post(...) on each handler
app/schemas/<resource>.py                  Pydantic request/response models
app/models/<resource>.py                   SQLAlchemy ORM model
```

Reference: `app/controllers/tenant_controller.py`. Aggregated in `app/api/v1.py` via `router.include_router(tenant_controller.router)`.

## Workflow

1. **Resource URL**: plural noun, no verbs — `/tenants`, `/tenants/{id}`. Version prefix `/api/v1` is applied once in `app/api/v1.py`; don't repeat it per-router.
2. **Schemas first**: a `<Resource>Create`/`<Resource>Read` pair in `app/schemas/`. Validate everything at this boundary (`Field(min_length=...)`, `pattern=...`, `EmailStr`, etc.) — never hand-check input inside the controller.
3. **Handler function** carries the full FastAPI signature, including `Depends(get_db)`/`Depends(get_current_user)`/etc., decorated directly with `@router.get(...)`/`@router.post(...)` — it *is* the route registration, there's no separate routes file wiring it up.
4. **Response envelope** — every response goes through the standard contract, never a raw model or dict:
   - Single resource: `SuccessResponse[ReadSchema]` → `{"success": true, "code": <status>, "message": str|null, "data": {...}}`
   - List: `PaginatedResponse[ReadSchema]` → adds `"meta": {"page","page_size","total_items","total_pages"}`, built via `app/core/pagination.py`'s `page_params` dependency + `build_meta()`.
   - Never return an unbounded list — every collection endpoint is paginated.
5. **Errors** — raise via `app/core/errors.py` helpers (`not_found`, `conflict`, `unauthorized`, `forbidden`, `bad_request`, `payload_too_large`, `rate_limited`) so they render through the global exception handler into the standard error contract (`{"success": false, "code", "error": {"type","message","details"}}`). Add a new helper there for a new error type rather than raising `HTTPException` ad hoc.
6. **Status codes**: 200 read, 201 create, 400 bad request, 401 missing/bad auth, 403 forbidden, 404 not found, 409 uniqueness conflict, 413 payload too large, 422 validation (handled automatically by FastAPI/Pydantic), 429 rate limited, 500 unhandled.
7. **Business logic that touches multiple systems** (DB + storage + queue, say) belongs in `app/services/<resource>_service.py` as a plain async function, called from the handler — see `api-auth-rate-limiting` skill's sibling note and `app/services/document_service.py`. Simple CRUD stays directly in the controller.
8. `router.include_router(<resource>_controller.router)` in `app/api/v1.py`.

## Checklist before calling an endpoint done

- [ ] Handler decorated directly on the controller's own `router` — no separate routes file
- [ ] Handler has full type hints + `Depends(...)` for every collaborator
- [ ] Request/response bodies are Pydantic models, not `dict`
- [ ] Success responses use `SuccessResponse`/`PaginatedResponse`
- [ ] Failure paths use an `app/core/errors.py` helper
- [ ] List endpoints paginate
- [ ] Multi-system side effects (storage/queue) live in a service, not the controller
- [ ] Tests written alongside (see `fastapi-async-testing` skill) asserting the full contract shape, not just status code
