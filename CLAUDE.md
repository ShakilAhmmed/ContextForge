# CLAUDE.md

Guidance for Claude Code when working in this repo. See also [README.md](README.md), [docs/arch.md](docs/arch.md) (target architecture), [docs/mvp-scope.md](docs/mvp-scope.md) (MVP scope), [docs/code-style.md](docs/code-style.md) (style guide — naming, formatting, error handling, testing, git, security), [ops/README.md](ops/README.md) (deploy).

## Stack

FastAPI (async) + PostgreSQL (async SQLAlchemy 2.0 ORM) + Alembic migrations + Redis (rate limiting) + MinIO (S3-compatible document storage) + ElasticMQ (SQS-compatible ingestion queue). nginx reverse-proxies with TLS in front of uvicorn. Python 3.12.

## Architecture pattern — controller owns its router

Each resource is one file. The controller module defines its own `APIRouter` and decorates its handler functions directly — no separate routes/ file:

```
app/controllers/<resource>_controller.py  — router = APIRouter(...); @router.get/post(...) on each handler (full FastAPI signature: params + Depends), DB calls, raises ApiError
app/schemas/<resource>.py      — Pydantic request/response models
app/models/<resource>.py       — SQLAlchemy ORM model
```

`app/api/v1.py` aggregates: `router.include_router(tenant_controller.router)` etc. See `app/controllers/tenant_controller.py` as the reference example.

**When an operation has real business logic or touches multiple external systems** (storage + DB + queue, say), pull it into `app/services/<resource>_service.py` as a plain async function and have the controller handler just parse the request and call it. Simple CRUD (tenants, reads) stays directly in the controller — don't add a service module for a single DB query. See `app/services/document_service.py` (upload: validates, writes to object storage, commits the DB row, then enqueues an ingestion message — in that order, since a queue message pointing at an uncommitted row is worse than a committed row that never got enqueued) + `app/controllers/document_controller.py` as the reference pair.

## Response contracts — always use these, never return raw dicts/models

Defined in `app/schemas/common.py`:

- **Success**: `SuccessResponse[T]` → `{"success": true, "code": <http status>, "message": str|null, "data": T}`
- **Paginated success**: `PaginatedResponse[T]` → same plus `"meta": {"page","page_size","total_items","total_pages"}`. Use `app/core/pagination.py`'s `page_params` dependency and `build_meta()`.
- **Error**: `ErrorResponse` → `{"success": false, "code": <http status>, "error": {"type": "<slug>", "message": str, "details": [...]}}`. Rendered automatically by the global handlers in `app/core/exception_handlers.py` — don't build error JSON by hand. Raise errors via `app/core/errors.py` helpers (`not_found()`, `conflict()`, `unauthorized()`, `rate_limited()`, or `ApiError(status, type, message)` directly for a new type).

`code` is always the numeric HTTP status on both success and error, mirrored at the top level.

## Auth

JWT bearer tokens (`app/core/security.py`, `PyJWT` + `bcrypt`). `app/api/deps.py:get_current_user` is the dependency to protect a route — add `Depends(get_current_user)` to a controller's signature. `/api/v1/auth/register`, `/login`, `/me` are the reference implementation.

## Rate limiting

`app/core/rate_limit.py:rate_limit(key_prefix, limit_attr, window_attr)` — a dependency factory backed by Redis (fixed-window counter). Pass **attribute names** (strings), not resolved values — the dependency reads `settings` at request time so limits stay tunable and patchable in tests. Global default is applied on the `/api/v1` router in `app/api/v1.py`; stricter per-route limits (e.g. `/auth/login`) are added via `dependencies=[Depends(rate_limit(...))]` on that specific `@router.post(...)` decorator.

## Object storage & queue

`app/core/storage.py` (`ObjectStorage` protocol, `S3ObjectStorage` impl) and `app/core/queue.py` (`QueueClient` protocol, `SQSQueueClient` impl) both follow the same shape: a `Protocol` interface + one real implementation using `aioboto3`, targeting MinIO/ElasticMQ in dev and real AWS S3/SQS in prod via `app/core/config.py` settings (endpoint URL + credentials only differ). Get them via `Depends(get_storage)` / `Depends(get_queue)`, never instantiate directly. `app/main.py`'s `lifespan` calls `storage.ensure_bucket()` on startup.

## API versioning

Everything lives under `/api/v1` — routers are aggregated in `app/api/v1.py` and mounted once in `app/main.py`. New resource routers get included there, not directly in `main.py`.

## Adding a new resource — checklist

1. Model in `app/models/`, register in `app/models/__init__.py`.
2. Alembic migration in `alembic/versions/` (numbered, `down_revision` chained to the previous one). Model uses SQLAlchemy's generic `Uuid`/portable types where possible (works on both SQLite-for-tests and Postgres); migrations target Postgres directly and can use `postgresql.UUID` etc.
3. Pydantic schemas in `app/schemas/`.
4. Controller module in `app/controllers/<resource>_controller.py`: `router = APIRouter(prefix=..., tags=[...])`, handler functions with full `Depends(...)` signatures decorated with `@router.get/post/...(...)`, returning `SuccessResponse[T]` / `PaginatedResponse[T]`, raising `app/core/errors.py` helpers on failure.
5. `router.include_router(<resource>_controller.router)` in `app/api/v1.py`.
6. **Tests first** (see below) in `tests/test_<resource>.py`.

## Testing — write tests before/alongside the endpoint, not after

```
python3 -m venv .venv && source .venv/bin/activate   # once
pip install -e ".[dev]"
pytest -q
```

`tests/conftest.py` provides a `client` fixture: in-memory SQLite (no Docker needed) with `get_db` overridden, `fakeredis` with `get_redis` overridden, and `tests/fakes.py`'s `FakeObjectStorage`/`FakeQueueClient` with `get_storage`/`get_queue` overridden (exposed as `client.fake_storage`/`client.fake_queue` for assertions). Tests hit the real FastAPI app via `httpx.AsyncClient` + `ASGITransport` — no mocking of controllers. Assert on the full response contract shape (`success`/`code`/`data`/`error.type`), not just status code. This is the pattern used throughout `tests/test_tenants.py`, `tests/test_auth.py`, `tests/test_rate_limit.py`, `tests/test_documents.py` — follow it for new tests.

CI runs this in `.github/workflows/test.yml`, separate from `lint.yml` (`ruff check` + `ruff format --check`) and `docker-build.yml` (builds the root `Dockerfile`) — three independent workflow files so any one can fail without blocking the others. Run `ruff format . && ruff check . --fix` locally before committing.

## Local dev stack (Docker)

```
cd ops/docker
./certs/gen-certs.sh                                            # once
echo '127.0.0.1 contextforge.local' | sudo tee -a /etc/hosts    # once
cp .env.example .env
docker compose up --build
```

Serves at `https://contextforge.local:8443/` (self-signed cert — expect a browser warning; use `curl -k`). `api`'s container entrypoint runs `alembic upgrade head` automatically before starting uvicorn — don't run migrations manually against the dev stack unless debugging.

When testing against this stack with curl, quote the `--resolve` flag correctly (`--resolve contextforge.local:8443:127.0.0.1` as literal args, or an array `"${R[@]}"` — a quoted string variable containing spaces breaks curl's option parsing).

Full K8s manifests and apply order: [ops/README.md](ops/README.md).

## Conventions

- No comments explaining *what* code does — only *why*, for non-obvious constraints (see the rate-limit dependency's docstring for an example of a justified one).
- Don't add abstractions, config knobs, or error handling for cases that can't occur here.
- `docs/mvp-scope.md` is the source of truth for what's in/out of scope right now — check it before assuming a target-architecture piece (connectors, reranker, model router, etc.) should be built.
