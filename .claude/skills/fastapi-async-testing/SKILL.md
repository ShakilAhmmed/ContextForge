---
name: fastapi-async-testing
description: Write pytest tests for an async FastAPI endpoint using httpx ASGITransport, in-memory SQLite, and fakeredis — no real Docker/Postgres/Redis needed. Use when adding a new endpoint, fixing a bug (write the failing test first), or asked to test/verify API behavior in this repo.
---

# FastAPI Async Testing

## Quick start

```python
async def test_create_widget_returns_success_contract(client):
    resp = await client.post("/api/v1/widgets", json={"name": "thing"})

    assert resp.status_code == 201
    body = resp.json()
    assert body["success"] is True
    assert body["code"] == 201
    assert body["data"]["name"] == "thing"
```

`client` is a fixture from `tests/conftest.py`: a real FastAPI app (`app.main.app`) served over `httpx.AsyncClient` + `ASGITransport` — no running server needed. `get_db` is overridden to an in-memory SQLite engine (tables created from `Base.metadata` fresh per test), `get_redis` is overridden to `fakeredis.FakeAsyncRedis`. Nothing touches the real stack.

## Workflow — write the test before/alongside the endpoint, not after

1. Name the test `test_<action>_<condition>_<expected_outcome>` — e.g. `test_create_tenant_duplicate_slug_returns_409`. The name alone should say what broke.
2. Structure as Arrange / Act / Assert with a blank line between each section — no interleaving.
3. Assert the **full response contract**, not just the status code: `success`, `code`, and either `data` (success) or `error.type`/`error.message`/`error.details` (failure). A 200 with a malformed body is still a bug the status code alone won't catch.
4. One behavior per test — a `..._returns_409` test shouldn't also be checking an unrelated 422 path.
5. Cover: the happy path, each distinct failure path (404/409/422/401/429 as applicable), and pagination boundaries for list endpoints (empty page, page 2, `total_pages` math).
6. For rate-limited routes: `from unittest.mock import patch; from app.core import config; with patch.object(config.settings, "rate_limit_login", 3): ...` — the rate limiter reads `settings` at request time specifically so tests can do this (see `app/core/rate_limit.py`'s docstring).

## Running

```
source .venv/bin/activate      # after: python3 -m venv .venv && pip install -e ".[dev]"
pytest -q
```

CI runs the same command in `.github/workflows/test.yml`, separate from `lint.yml` and `docker-build.yml`.

## When NOT to use fakeredis/SQLite

If a change is specifically about a database- or Redis-server behavior that SQLite/fakeredis can't faithfully emulate (a Postgres-specific constraint, real Redis TTL edge case), verify manually against the real stack (`docker compose up --build` in `ops/docker`) in addition to the fast suite — don't silently trust a fake that can't actually exercise the thing being changed.
