async def _create_tenant(client) -> str:
    resp = await client.post("/api/v1/tenants", json={"name": "Acme", "slug": "acme"})
    return resp.json()["data"]["id"]


async def test_register_returns_success_contract(client):
    tenant_id = await _create_tenant(client)

    resp = await client.post(
        "/api/v1/auth/register",
        json={"tenant_id": tenant_id, "email": "alice@example.com", "password": "hunter22"},
    )

    assert resp.status_code == 201
    body = resp.json()
    assert body["success"] is True
    assert body["data"]["email"] == "alice@example.com"
    assert body["data"]["tenant_id"] == tenant_id
    assert "hashed_password" not in body["data"]


async def test_register_duplicate_email_returns_409(client):
    tenant_id = await _create_tenant(client)
    payload = {"tenant_id": tenant_id, "email": "alice@example.com", "password": "hunter22"}
    await client.post("/api/v1/auth/register", json=payload)

    resp = await client.post("/api/v1/auth/register", json=payload)

    assert resp.status_code == 409
    assert resp.json()["error"]["type"] == "conflict"


async def test_register_unknown_tenant_returns_409(client):
    resp = await client.post(
        "/api/v1/auth/register",
        json={
            "tenant_id": "00000000-0000-0000-0000-000000000000",
            "email": "alice@example.com",
            "password": "hunter22",
        },
    )

    assert resp.status_code == 409


async def test_login_returns_access_token(client):
    tenant_id = await _create_tenant(client)
    await client.post(
        "/api/v1/auth/register",
        json={"tenant_id": tenant_id, "email": "alice@example.com", "password": "hunter22"},
    )

    resp = await client.post(
        "/api/v1/auth/login", json={"email": "alice@example.com", "password": "hunter22"}
    )

    assert resp.status_code == 200
    body = resp.json()
    assert body["success"] is True
    assert body["data"]["token_type"] == "bearer"
    assert body["data"]["expires_in"] > 0
    assert len(body["data"]["access_token"]) > 0


async def test_login_wrong_password_returns_401(client):
    tenant_id = await _create_tenant(client)
    await client.post(
        "/api/v1/auth/register",
        json={"tenant_id": tenant_id, "email": "alice@example.com", "password": "hunter22"},
    )

    resp = await client.post("/api/v1/auth/login", json={"email": "alice@example.com", "password": "wrong"})

    assert resp.status_code == 401
    assert resp.json()["error"]["type"] == "unauthorized"


async def test_login_unknown_email_returns_401(client):
    resp = await client.post(
        "/api/v1/auth/login", json={"email": "nobody@example.com", "password": "hunter22"}
    )

    assert resp.status_code == 401


async def test_me_without_token_returns_401(client):
    resp = await client.get("/api/v1/auth/me")

    assert resp.status_code == 401


async def test_me_with_valid_token_returns_current_user(client):
    tenant_id = await _create_tenant(client)
    await client.post(
        "/api/v1/auth/register",
        json={"tenant_id": tenant_id, "email": "alice@example.com", "password": "hunter22"},
    )
    login_resp = await client.post(
        "/api/v1/auth/login", json={"email": "alice@example.com", "password": "hunter22"}
    )
    token = login_resp.json()["data"]["access_token"]

    resp = await client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"})

    assert resp.status_code == 200
    assert resp.json()["data"]["email"] == "alice@example.com"


async def test_me_with_invalid_token_returns_401(client):
    resp = await client.get("/api/v1/auth/me", headers={"Authorization": "Bearer garbage"})

    assert resp.status_code == 401


async def _login_via_cookie(client) -> None:
    """Registers + logs in, relying on httpx's cookie jar (no Authorization
    header) - mirrors how a real browser authenticates."""
    tenant_id = await _create_tenant(client)
    await client.post(
        "/api/v1/auth/register",
        json={"tenant_id": tenant_id, "email": "alice@example.com", "password": "hunter22"},
    )
    await client.post("/api/v1/auth/login", json={"email": "alice@example.com", "password": "hunter22"})


async def test_login_sets_httponly_access_token_cookie(client):
    tenant_id = await _create_tenant(client)
    await client.post(
        "/api/v1/auth/register",
        json={"tenant_id": tenant_id, "email": "alice@example.com", "password": "hunter22"},
    )

    resp = await client.post(
        "/api/v1/auth/login", json={"email": "alice@example.com", "password": "hunter22"}
    )

    set_cookie_headers = resp.headers.get_list("set-cookie")
    access_token_header = next(h for h in set_cookie_headers if h.startswith("access_token="))

    assert "HttpOnly" in access_token_header
    assert "samesite=none" in access_token_header.lower()
    assert resp.cookies["access_token"]


async def test_me_authenticates_via_cookie_alone(client):
    await _login_via_cookie(client)

    resp = await client.get("/api/v1/auth/me")

    assert resp.status_code == 200
    assert resp.json()["data"]["email"] == "alice@example.com"


async def test_mutating_request_via_cookie_without_csrf_header_returns_403(client):
    await _login_via_cookie(client)

    resp = await client.post("/api/v1/documents", files={"file": ("notes.txt", b"hello", "text/plain")})

    assert resp.status_code == 403
    assert resp.json()["error"]["type"] == "forbidden"


async def test_mutating_request_via_cookie_with_csrf_header_succeeds(client):
    await _login_via_cookie(client)

    resp = await client.post(
        "/api/v1/documents",
        files={"file": ("notes.txt", b"hello", "text/plain")},
        headers={"X-CSRF-Token": "1"},
    )

    assert resp.status_code == 201


async def test_mutating_request_via_header_auth_skips_csrf_check(client):
    tenant_id = await _create_tenant(client)
    await client.post(
        "/api/v1/auth/register",
        json={"tenant_id": tenant_id, "email": "alice@example.com", "password": "hunter22"},
    )
    login_resp = await client.post(
        "/api/v1/auth/login", json={"email": "alice@example.com", "password": "hunter22"}
    )
    token = login_resp.json()["data"]["access_token"]
    client.cookies.clear()  # only the Authorization header authenticates this request

    resp = await client.post(
        "/api/v1/documents",
        files={"file": ("notes.txt", b"hello", "text/plain")},
        headers={"Authorization": f"Bearer {token}"},
    )

    assert resp.status_code == 201


async def test_logout_clears_cookies(client):
    await _login_via_cookie(client)

    resp = await client.post("/api/v1/auth/logout")

    set_cookie_headers = resp.headers.get_list("set-cookie")
    access_token_header = next(h for h in set_cookie_headers if h.startswith("access_token="))
    assert 'access_token=""' in access_token_header or "Max-Age=0" in access_token_header
