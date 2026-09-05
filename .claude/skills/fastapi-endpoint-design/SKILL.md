---
name: fastapi-endpoint-design
description: Add or modify a FastAPI REST endpoint following industry-standard resource-oriented design (thin router, controller-as-handler, typed Pydantic I/O, consistent envelope, pagination). Use when adding a new API resource/endpoint, changing a request/response shape, or reviewing an endpoint's structure in this repo.
---

# FastAPI Endpoint Design

## Quick start

This repo's pattern — router files never contain logic:

```
app/api/routes/<resource>.py       router.add_api_route(path, controller_fn, methods=[...], response_model=...)
app/controllers/<resource>_controller.py   the handler itself: Depends(...) in its own signature, DB calls, raises errors
app/schemas/<resource>.py          Pydantic request/response models
app/models/<resource>.py           SQLAlchemy ORM model
```

Reference pair: `app/api/routes/tenants.py` + `app/controllers/tenant_controller.py`.

## Workflow

1. **Resource URL**: plural noun, no verbs — `/tenants`, `/tenants/{id}`. Version prefix `/api/v1` is applied once in `app/api/v1.py`; don't repeat it per-router.
2. **Schemas first**: a `<Resource>Create`/`<Resource>Read` pair in `app/schemas/`. Validate everything at this boundary (`Field(min_length=...)`, `pattern=...`, `EmailStr`, etc.) — never hand-check input inside the controller.
3. **Controller function** carries the full FastAPI signature, including `Depends(get_db)`/`Depends(get_current_user)`/etc. — it *is* the route handler, registered directly via `router.add_api_route(path, controller_fn, ...)`. Don't write a second function in the route file with the same name that just calls the controller — that's dead duplication.
4. **Response envelope** — every response goes through the standard contract, never a raw model or dict:
   - Single resource: `SuccessResponse[ReadSchema]` → `{"success": true, "code": <status>, "message": str|null, "data": {...}}`
   - List: `PaginatedResponse[ReadSchema]` → adds `"meta": {"page","page_size","total_items","total_pages"}`, built via `app/core/pagination.py`'s `page_params` dependency + `build_meta()`.
   - Never return an unbounded list — every collection endpoint is paginated.
5. **Errors** — raise via `app/core/errors.py` helpers (`not_found`, `conflict`, `unauthorized`, `rate_limited`) so they render through the global exception handler into the standard error contract (`{"success": false, "code", "error": {"type","message","details"}}`). Add a new helper there for a new error type rather than raising `HTTPException` ad hoc.
6. **Status codes**: 200 read, 201 create, 401 missing/bad auth, 403 forbidden, 404 not found, 409 uniqueness conflict, 422 validation (handled automatically by FastAPI/Pydantic), 429 rate limited, 500 unhandled.
7. Wire the router into `app/api/v1.py`.

## Checklist before calling an endpoint done

- [ ] Router has zero logic — only `add_api_route` calls
- [ ] Controller function has full type hints + `Depends(...)` for every collaborator
- [ ] Request/response bodies are Pydantic models, not `dict`
- [ ] Success responses use `SuccessResponse`/`PaginatedResponse`
- [ ] Failure paths use an `app/core/errors.py` helper
- [ ] List endpoints paginate
- [ ] Tests written alongside (see `fastapi-async-testing` skill) asserting the full contract shape, not just status code
