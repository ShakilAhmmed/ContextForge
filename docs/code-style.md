# Code Style Guide

Applies to all Python code in this repo. Enforced by `ruff` (lint + format) where possible; the rest is convention, checked in review.

## Tooling

- **Formatter + linter**: [Ruff](https://docs.astral.sh/ruff/) — replaces Black/isort/Flake8. Config lives in `pyproject.toml` under `[tool.ruff]`.
- Run before committing:
  ```
  ruff format .
  ruff check . --fix
  ```
- CI runs `ruff check .` and `ruff format --check .` (`.github/workflows/lint.yml`) — a PR with lint or formatting drift fails CI, same as a failing test.

## Formatting

- Line length: 110 (matches this codebase's existing style — dense but readable; Ruff enforces it).
- Double quotes for strings, trailing commas in multi-line collections/calls — Ruff format handles this automatically, don't hand-format against it.
- One blank line between top-level functions/classes in the same module; no blank line at the start of a function body.

## Naming

- `snake_case` for functions, variables, modules. `PascalCase` for classes (models, Pydantic schemas). `UPPER_SNAKE_CASE` for module-level constants.
- Files: singular resource name (`tenant.py`, not `tenants.py`) for models/schemas; the *router* file is the one exception and is plural to match its URL prefix (`app/api/routes/tenants.py` → `/tenants`).
- Test files: `tests/test_<module>.py`. Test functions: `test_<action>_<condition>_<expected_outcome>` (e.g. `test_create_tenant_duplicate_slug_returns_409`) — the name alone should tell you what broke without reading the body.
- Boolean names read as a yes/no question: `is_active`, `has_quota`, not `active_flag`.

## Type hints

- All function signatures are fully typed — parameters and return type. No untyped `def` in `app/`.
- Use built-in generics (`list[str]`, `dict[str, int]`, `X | None`) — this is Python 3.12, don't import from `typing` for these.
- Use `typing.Generic`/`TypeVar` only where it earns its keep (see `app/schemas/common.py`'s `SuccessResponse[T]`) — don't add generics for a single concrete type.

## Imports

- Order: stdlib → third-party → local (`app.*`), each group separated by a blank line, alphabetized within a group. Ruff's isort-equivalent rule enforces this — `ruff check --fix` sorts automatically.
- No wildcard imports except the one documented case: `alembic/env.py` imports `app.models` with `# noqa: F401,F403` specifically to register models on `Base.metadata` — don't copy that pattern elsewhere.
- No unused imports — Ruff flags these; don't suppress without a reason comment.

## Comments and docstrings

- Default to no comments. Code should read clearly from naming and structure alone.
- Write a comment only for the *why*, when it's non-obvious: a hidden constraint, a workaround, a deliberate trade-off. See `app/core/rate_limit.py`'s docstring (explains *why* settings are read at call time, not construction time) as the model to follow.
- No docstrings that restate the signature (`"""Get the user."""` above `get_user()`). If you need a docstring, make it earn its place the same way a comment does.
- Never leave commented-out code, TODOs without an owner/issue, or "removed X" comments — delete cleanly, git history has the rest.

## Error handling

- Never raise bare `HTTPException` in a controller — use `app/core/errors.py` helpers (`not_found()`, `conflict()`, `unauthorized()`, `rate_limited()`) or extend that module with a new helper if a new error type is needed. This keeps every error rendering through the same contract (see `CLAUDE.md`).
- Don't catch exceptions you can't meaningfully handle. Let unexpected errors hit the global `Exception` handler (`app/core/exception_handlers.py`) rather than adding a broad `try/except` "just in case".
- Only catch the specific exception you expect (`IntegrityError` for a unique-constraint race, not bare `Exception`).

## Async

- All I/O (DB, Redis, HTTP) is `async`/`await` — no blocking calls (`time.sleep`, sync `requests`, sync psycopg2 in request paths) inside async route/controller code.
- Controllers take an `AsyncSession`/`Redis` via `Depends(...)` — never open a session/connection manually inside a controller.

## API design

- Resource-oriented URLs, plural nouns: `/tenants`, `/tenants/{id}` — no verbs in the path.
- Every request/response body is a Pydantic model — no raw `dict` in a signature or return type.
- Every response goes through `SuccessResponse[T]` / `PaginatedResponse[T]` / the error contract — see `CLAUDE.md` for the exact shape. Don't return an ORM model or plain schema directly from a controller.
- List endpoints are paginated (`app/core/pagination.py`) — never return an unbounded list.
- Status codes mean what they say: 200 read, 201 create, 204 no body (not currently used but reserved for delete), 401 missing/invalid auth, 403 authenticated-but-forbidden, 404 not found, 409 conflict (uniqueness), 422 validation, 429 rate limited, 500 unhandled.

## Database / ORM

- Primary keys: `Uuid` (SQLAlchemy's generic type, not `postgresql.UUID`) so models work against both Postgres (prod) and SQLite (tests) — see `app/models/tenant.py`.
- Every table has `created_at` with `server_default=func.now()`. Add `updated_at` only when a resource is actually mutable.
- One Alembic migration per logical change, numbered and chained (`down_revision` points at the previous file). Migrations may use `postgresql.*` types directly since they only ever run against Postgres — unlike models, migrations aren't shared with the SQLite test path.
- No raw SQL strings in application code — use SQLAlchemy Core/ORM constructs (`select(...)`, not `text("SELECT ...")`) unless there's a specific, commented reason.

## Testing

- Arrange/Act/Assert, in that order, with a blank line between each — no interleaving setup and assertions.
- Assert on the full response contract (`success`, `code`, `data`/`error.type`), not just the HTTP status code — a 200 with the wrong body shape is still a bug.
- One behavior per test. A test named `..._returns_409` should have exactly one assertion path that can produce a 409, not a grab-bag of unrelated checks.
- No real network/Docker/Postgres/Redis in unit tests — `tests/conftest.py`'s `client` fixture overrides `get_db` (SQLite) and `get_redis` (`fakeredis`). If a future test genuinely needs the real stack, mark and isolate it clearly (e.g. a separate `tests/integration/` directory) rather than mixing it into the fast suite.

## Git

- [Conventional Commits](https://www.conventionalcommits.org/): `feat:`, `fix:`, `refactor:`, `test:`, `chore:`, `docs:` prefix, imperative mood, no trailing period. Body explains *why*, not a restatement of the diff.
- One logical change per commit. Don't bundle an unrelated formatting pass into a feature commit.

## Security

- Secrets (`JWT_SECRET`, DB/Redis credentials) come from environment/config (`app/core/config.py`), never hardcoded — the checked-in defaults are dev-only placeholders, deliberately called out as such in `ops/k8s/*secret.yaml`.
- Passwords are hashed with `bcrypt` (`app/core/security.py`) — never logged, never returned in a response schema (`UserRead` excludes `hashed_password` by construction, not by filtering after the fact).
- All external input is validated at the Pydantic schema boundary (`app/schemas/`), not by hand-checking inside a controller.
