---
name: api-auth-rate-limiting
description: Protect a FastAPI route with JWT bearer auth and/or Redis-backed rate limiting, following OWASP API security basics (brute-force throttling, no secrets in code, bcrypt password hashing). Use when adding a route that needs authentication, adding a login/credential endpoint, or when a route is a plausible brute-force/abuse target.
---

# API Auth & Rate Limiting

## Protecting a route with JWT

```python
from app.api.deps import get_current_user
from app.models.user import User


async def my_controller(current_user: User = Depends(get_current_user)) -> SuccessResponse[...]: ...
```

`get_current_user` (`app/api/deps.py`) validates the `Authorization: Bearer <token>` header, decodes it (`app/core/security.py`, PyJWT + `HS256`), and loads the `User`. Missing/expired/invalid token → `401 unauthorized` through the standard error contract automatically. Reference: `app/controllers/auth_controller.py::me`.

Never hand-roll token parsing in a controller — always go through this dependency.

## Rate limiting a route

```python
from app.core.rate_limit import rate_limit


@router.post(
    "/login",
    response_model=SuccessResponse[TokenData],
    dependencies=[Depends(rate_limit("login", "rate_limit_login", "rate_limit_login_window_seconds"))],
)
async def login(...): ...
```

`rate_limit(key_prefix, limit_attr, window_attr)` takes **attribute names** (strings into `app/core/config.py:Settings`), not resolved numbers — it reads `settings` live at request time, so limits are tunable without a redeploy and patchable in tests. It's a Redis fixed-window counter, keyed by `ratelimit:<key_prefix>:<client_ip>`. Exceeding the limit raises `429` with a `Retry-After` header via `app/core/errors.py:rate_limited()`.

A global default (`rate_limit_default` / `rate_limit_default_window_seconds`) is already applied to every `/api/v1` route in `app/api/v1.py`. Add a **stricter** route-specific limit on top for anything that's a plausible abuse target:

- Credential endpoints (login, password reset, OTP verify) — low limit, short window, to blunt brute-force/credential-stuffing.
- Any endpoint that triggers an expensive downstream call (LLM inference, external API, email send).
- Write endpoints on unauthenticated routes (e.g. public registration).

## Security basics (OWASP API Top 10, applied here)

- **Broken auth**: password hashing is `bcrypt` (`app/core/security.py`) — never store or log plaintext, never return `hashed_password` in a response schema (exclude it at the schema level, don't filter after the fact).
- **Secrets**: `JWT_SECRET`, DB/Redis credentials come from `app/core/config.py` (env-driven) — never hardcode a real secret; checked-in defaults in `ops/*` are explicitly-labeled dev placeholders only.
- **Excessive data exposure**: response schemas (`app/schemas/`) are explicit allow-lists of fields — never serialize an ORM model directly.
- **Injection**: no raw SQL string interpolation — SQLAlchemy Core/ORM constructs only.
- **Lack of rate limiting**: covered above — don't ship an unauthenticated write or credential endpoint without one.
