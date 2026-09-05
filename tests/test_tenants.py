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


async def test_get_tenant_not_found_returns_404(client):
    resp = await client.get("/api/v1/tenants/00000000-0000-0000-0000-000000000000")

    assert resp.status_code == 404
    body = resp.json()
    assert body["success"] is False
    assert body["code"] == 404
    assert body["error"]["type"] == "not_found"


async def test_get_tenant_returns_created_tenant(client):
    created = (await client.post("/api/v1/tenants", json={"name": "Acme", "slug": "acme"})).json()["data"]

    resp = await client.get(f"/api/v1/tenants/{created['id']}")

    assert resp.status_code == 200
    body = resp.json()
    assert body["code"] == 200
    assert body["data"]["id"] == created["id"]


async def test_list_tenants_paginates(client):
    for slug in ("acme", "globex", "initech"):
        await client.post("/api/v1/tenants", json={"name": slug, "slug": slug})

    resp = await client.get("/api/v1/tenants", params={"page": 2, "page_size": 1})

    assert resp.status_code == 200
    body = resp.json()
    assert body["success"] is True
    assert len(body["data"]) == 1
    assert body["meta"] == {"page": 2, "page_size": 1, "total_items": 3, "total_pages": 3}


async def test_list_tenants_empty_returns_empty_page(client):
    resp = await client.get("/api/v1/tenants")

    assert resp.status_code == 200
    body = resp.json()
    assert body["data"] == []
    assert body["meta"]["total_items"] == 0
    assert body["meta"]["total_pages"] == 0
