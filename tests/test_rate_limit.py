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
    with patch.object(config.settings, "rate_limit_default", 3):
        for _ in range(3):
            resp = await client.get("/api/v1/tenants")
            assert resp.status_code == 200

        resp = await client.get("/api/v1/tenants")

        assert resp.status_code == 429
