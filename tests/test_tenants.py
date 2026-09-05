async def _create_tenant(client) -> str:
    resp = await client.post("/api/v1/tenants", json={"name": "Acme", "slug": "acme"})
    return resp.json()["data"]["id"]


async def _auth_headers(client, tenant_id: str, email: str = "alice@example.com") -> dict:
    await client.post(
        "/api/v1/auth/register",
        json={"tenant_id": tenant_id, "email": email, "password": "hunter22"},
    )
    login = await client.post("/api/v1/auth/login", json={"email": email, "password": "hunter22"})
    token = login.json()["data"]["access_token"]
    return {"Authorization": f"Bearer {token}"}


async def test_create_tenant_returns_success_contract(client):
    resp = await client.post("/api/v1/tenants", json={"name": "Acme", "slug": "acme"})

    assert resp.status_code == 201
    body = resp.json()
    assert body["success"] is True
    assert body["code"] == 201
    assert body["message"] == "tenant created successfully"
    assert body["data"]["slug"] == "acme"
    assert body["data"]["name"] == "Acme"
    assert "id" in body["data"]
    assert "created_at" in body["data"]


async def test_create_tenant_duplicate_slug_returns_409(client):
    await client.post("/api/v1/tenants", json={"name": "Acme", "slug": "acme"})

    resp = await client.post("/api/v1/tenants", json={"name": "Acme 2", "slug": "acme"})

    assert resp.status_code == 409
    body = resp.json()
    assert body["success"] is False
    assert body["code"] == 409
    assert body["error"]["type"] == "conflict"


async def test_create_tenant_invalid_slug_returns_422(client):
    resp = await client.post("/api/v1/tenants", json={"name": "Bad", "slug": "Not Valid!"})

    assert resp.status_code == 422
    body = resp.json()
    assert body["success"] is False
    assert body["code"] == 422
    assert body["error"]["type"] == "validation_error"
    assert body["error"]["details"][0]["field"] == "slug"


async def test_get_tenant_without_token_returns_401(client):
    tenant_id = await _create_tenant(client)

    resp = await client.get(f"/api/v1/tenants/{tenant_id}")

    assert resp.status_code == 401


async def test_get_tenant_with_non_owned_id_returns_403_not_404(client):
    # Ownership is checked before existence, so a random/foreign id never
    # confirms or denies whether that tenant exists - it's just forbidden.
    tenant_id = await _create_tenant(client)
    headers = await _auth_headers(client, tenant_id)

    resp = await client.get("/api/v1/tenants/00000000-0000-0000-0000-000000000000", headers=headers)

    assert resp.status_code == 403
    body = resp.json()
    assert body["success"] is False
    assert body["code"] == 403
    assert body["error"]["type"] == "forbidden"


async def test_get_own_tenant_returns_tenant(client):
    tenant_id = await _create_tenant(client)
    headers = await _auth_headers(client, tenant_id)

    resp = await client.get(f"/api/v1/tenants/{tenant_id}", headers=headers)

    assert resp.status_code == 200
    body = resp.json()
    assert body["code"] == 200
    assert body["data"]["id"] == tenant_id


async def test_get_other_tenant_returns_403(client):
    own_tenant_id = await _create_tenant(client)
    headers = await _auth_headers(client, own_tenant_id)

    other_resp = await client.post("/api/v1/tenants", json={"name": "Globex", "slug": "globex"})
    other_tenant_id = other_resp.json()["data"]["id"]

    resp = await client.get(f"/api/v1/tenants/{other_tenant_id}", headers=headers)

    assert resp.status_code == 403
    assert resp.json()["error"]["type"] == "forbidden"


async def test_list_tenants_without_token_returns_401(client):
    resp = await client.get("/api/v1/tenants")

    assert resp.status_code == 401


async def test_list_tenants_only_returns_own_tenant(client):
    own_tenant_id = await _create_tenant(client)
    headers = await _auth_headers(client, own_tenant_id)
    await client.post("/api/v1/tenants", json={"name": "Globex", "slug": "globex"})

    resp = await client.get("/api/v1/tenants", headers=headers)

    assert resp.status_code == 200
    body = resp.json()
    assert body["success"] is True
    assert [t["id"] for t in body["data"]] == [own_tenant_id]
    assert body["meta"]["total_items"] == 1
