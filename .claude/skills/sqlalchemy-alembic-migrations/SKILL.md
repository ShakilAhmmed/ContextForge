---
name: sqlalchemy-alembic-migrations
description: Create or modify a SQLAlchemy 2.0 async ORM model and its matching Alembic migration, portable between Postgres (prod) and SQLite (tests). Use when adding a table/model, changing a column, adding a foreign key or index, or writing a migration in this repo.
---

# SQLAlchemy + Alembic Migrations

## Quick start

Reference pair: `app/models/tenant.py` + `alembic/versions/0001_create_tenants.py`.

## Workflow

1. **Model** in `app/models/<name>.py`, using SQLAlchemy 2.0's typed `Mapped[...]`/`mapped_column(...)` style — not the legacy `Column(...)` class-attribute style.
2. **Portable types**: use SQLAlchemy's generic `Uuid(as_uuid=True)` for primary/foreign keys, not `sqlalchemy.dialects.postgresql.UUID`. Models must work against SQLite (test suite) as well as Postgres (prod) — dialect-specific types break that. `DateTime(timezone=True)` + `server_default=func.now()` for `created_at`.
3. Register the model in `app/models/__init__.py` (`alembic/env.py` wildcard-imports this module specifically so `Base.metadata` sees every table before autogenerate/migrate runs).
4. **Migration**: one file per logical change in `alembic/versions/`, numbered sequentially (`0003_...py`), with `down_revision` pointing at the immediately preceding revision — chain must be linear and unbroken.
   - Migrations may use `postgresql.*`-specific types directly (`sqlalchemy.dialects.postgresql.UUID`, etc.) since they only ever execute against the real Postgres database — unlike the ORM model, they aren't shared with the SQLite test path.
   - Always write a working `downgrade()`, not `pass`, unless the change is genuinely irreversible (and say why in a comment if so).
5. Foreign keys: `sa.ForeignKey("parent_table.id")` in both the migration and the model's `mapped_column(..., ForeignKey(...))`.
6. Never hand-edit an already-applied migration. Add a new migration for further changes, even to fix a mistake in a previous one (unless it's still unreleased/unapplied anywhere).

## Local verification

- Real DB path: `docker compose up --build` in `ops/docker` runs `alembic upgrade head` automatically via the container entrypoint before uvicorn starts.
- Test path never touches Alembic — `tests/conftest.py` creates tables directly from `Base.metadata.create_all` against an in-memory SQLite engine, so a portable model is what makes the fast test suite possible at all.

## Checklist

- [ ] Model uses `Mapped[...]`/`mapped_column`, generic `Uuid`, no Postgres-only types
- [ ] Model registered in `app/models/__init__.py`
- [ ] Migration's `down_revision` chains to the actual current head
- [ ] Migration has a real `downgrade()`
- [ ] Verified against real Postgres via the dev compose stack, not just assumed
