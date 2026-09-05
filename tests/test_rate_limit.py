from unittest.mock import patch

from app.core import config


async def test_login_rate_limit_returns_429_after_threshold(client):
    with patch.object(config.settings, "rate_limit_login", 3):
        payload = {"email": "nobody@example.com", "password": "wrong"}

        for _ in range(3):
            resp = await client.post("/api/v1/auth/login", json=payload)
            assert resp.status_code == 401

        resp = await client.post("/api/v1/auth/login", json=payload)

        assert resp.status_code == 429
        body = resp.json()
        assert body["success"] is False
        assert body["error"]["type"] == "rate_limited"
        assert "Retry-After" in resp.headers


async def test_default_rate_limit_returns_429_after_threshold(client):
    # POST /tenants stays unauthenticated (bootstrap endpoint), so it's a
    # convenient route to exercise the router-level default limiter with.
    # The limiter dependency runs regardless of whether the create itself
    # succeeds, so a 409 on repeat slugs doesn't affect the count.
    with patch.object(config.settings, "rate_limit_default", 3):
        for _ in range(3):
            resp = await client.post("/api/v1/tenants", json={"name": "Acme", "slug": "acme"})
            assert resp.status_code in (201, 409)

        resp = await client.post("/api/v1/tenants", json={"name": "Acme", "slug": "acme"})

        assert resp.status_code == 429
