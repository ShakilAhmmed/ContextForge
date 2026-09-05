# ContextForge

Multi-tenant RAG platform API — FastAPI + PostgreSQL, async SQLAlchemy ORM, Alembic migrations.

See [docs/arch.md](docs/arch.md) for the target-state architecture and [docs/mvp-scope.md](docs/mvp-scope.md) for what's in/out of the MVP.

## Stack

- **API**: FastAPI (async), Python 3.12
- **DB**: PostgreSQL, SQLAlchemy 2.0 (async ORM), Alembic migrations
- **Serving**: nginx (TLS termination, reverse proxy) in front of uvicorn
- **Ops**: Docker Compose (local dev) and Kubernetes manifests — see [ops/README.md](ops/README.md)

## Project layout

```
app/
├── api/v1.py            aggregates each controller's router under /api/v1
├── api/deps.py          shared dependencies (e.g. get_current_user)
├── controllers/         each owns its APIRouter + request handlers (validation, DB calls, HTTP errors)
├── services/            business logic touching multiple systems (storage, queue), called from controllers
├── models/              SQLAlchemy ORM models
├── schemas/             Pydantic request/response models
├── core/config.py       settings (env-driven)
├── db.py                engine, session, Base
└── main.py              app instance, router registration

alembic/                 migrations
ops/                      Docker + Kubernetes + nginx configs
docs/                     architecture + scoping docs
```

## Local development

Requires Docker.

```
cd ops/docker
./certs/gen-certs.sh                          # one-time: self-signed dev cert
echo '127.0.0.1 contextforge.local' | sudo tee -a /etc/hosts   # one-time
cp .env.example .env
docker compose up --build
```

API is served at `https://contextforge.local:8443/` (nginx redirects `:8080` → `:8443`). Browser will warn on the self-signed cert — expected in dev.

- Swagger UI: `https://contextforge.local:8443/docs`
- Health check: `https://contextforge.local:8443/health`

`api`'s container entrypoint runs `alembic upgrade head` automatically before starting uvicorn.

Full details, including Kubernetes deployment, in [ops/README.md](ops/README.md).

## Migrations

```
alembic revision --autogenerate -m "description"
alembic upgrade head
```

Run these against a Python env with `DATABASE_URL` pointed at your target DB (see `app/core/config.py`), or `docker compose exec api alembic ...` against the running dev stack.
