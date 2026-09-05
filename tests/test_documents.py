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


async def test_upload_document_returns_success_contract_and_queues_it(client):
    tenant_id = await _create_tenant(client)
    headers = await _auth_headers(client, tenant_id)

    resp = await client.post(
        "/api/v1/documents",
        headers=headers,
        files={"file": ("notes.txt", b"hello world", "text/plain")},
    )

    assert resp.status_code == 201
    body = resp.json()
    assert body["success"] is True
    assert body["code"] == 201
    assert body["data"]["filename"] == "notes.txt"
    assert body["data"]["content_type"] == "text/plain"
    assert body["data"]["size_bytes"] == len(b"hello world")
    assert body["data"]["tenant_id"] == tenant_id

    # stored in the (fake) object store
    assert len(client.fake_storage.objects) == 1
    stored_key, stored_content = next(iter(client.fake_storage.objects.items()))
    assert stored_content == b"hello world"

    # enqueued for the (future) ingestion worker
    assert len(client.fake_queue.messages) == 1
    message = client.fake_queue.messages[0]
    assert message["document_id"] == body["data"]["id"]
    assert message["tenant_id"] == tenant_id
    assert message["storage_key"] == stored_key


async def test_upload_document_without_token_returns_401(client):
    resp = await client.post("/api/v1/documents", files={"file": ("notes.txt", b"hi", "text/plain")})

    assert resp.status_code == 401


async def test_upload_document_unsupported_content_type_returns_400(client):
    tenant_id = await _create_tenant(client)
    headers = await _auth_headers(client, tenant_id)

    resp = await client.post(
        "/api/v1/documents",
        headers=headers,
        files={"file": ("script.exe", b"MZ", "application/x-msdownload")},
    )

    assert resp.status_code == 400
    body = resp.json()
    assert body["success"] is False
    assert body["error"]["type"] == "bad_request"
    assert len(client.fake_storage.objects) == 0
    assert len(client.fake_queue.messages) == 0


async def test_upload_document_too_large_returns_413(client, monkeypatch):
    from app.core.config import settings

    monkeypatch.setattr(settings, "max_upload_size_bytes", 5)
    tenant_id = await _create_tenant(client)
    headers = await _auth_headers(client, tenant_id)

    resp = await client.post(
        "/api/v1/documents",
        headers=headers,
        files={"file": ("notes.txt", b"way too big for the limit", "text/plain")},
    )

    assert resp.status_code == 413
    assert resp.json()["error"]["type"] == "payload_too_large"


async def test_get_document_not_found_returns_404(client):
    tenant_id = await _create_tenant(client)
    headers = await _auth_headers(client, tenant_id)

    resp = await client.get("/api/v1/documents/00000000-0000-0000-0000-000000000000", headers=headers)

    assert resp.status_code == 404


async def test_get_other_tenants_document_returns_404(client):
    tenant_a = await _create_tenant(client)
    headers_a = await _auth_headers(client, tenant_a, email="alice@example.com")
    upload = await client.post(
        "/api/v1/documents",
        headers=headers_a,
        files={"file": ("notes.txt", b"secret", "text/plain")},
    )
    document_id = upload.json()["data"]["id"]

    tenant_b_resp = await client.post("/api/v1/tenants", json={"name": "Globex", "slug": "globex"})
    tenant_b = tenant_b_resp.json()["data"]["id"]
    headers_b = await _auth_headers(client, tenant_b, email="bob@example.com")

    resp = await client.get(f"/api/v1/documents/{document_id}", headers=headers_b)

    assert resp.status_code == 404


async def test_get_own_document_returns_it(client):
    tenant_id = await _create_tenant(client)
    headers = await _auth_headers(client, tenant_id)
    upload = await client.post(
        "/api/v1/documents",
        headers=headers,
        files={"file": ("notes.txt", b"hello", "text/plain")},
    )
    document_id = upload.json()["data"]["id"]

    resp = await client.get(f"/api/v1/documents/{document_id}", headers=headers)

    assert resp.status_code == 200
    assert resp.json()["data"]["id"] == document_id


async def test_list_documents_only_returns_own_tenants_documents(client):
    tenant_id = await _create_tenant(client)
    headers = await _auth_headers(client, tenant_id)
    await client.post("/api/v1/documents", headers=headers, files={"file": ("a.txt", b"a", "text/plain")})
    await client.post("/api/v1/documents", headers=headers, files={"file": ("b.txt", b"b", "text/plain")})

    resp = await client.get("/api/v1/documents", headers=headers)

    assert resp.status_code == 200
    body = resp.json()
    assert body["meta"]["total_items"] == 2
    assert {d["filename"] for d in body["data"]} == {"a.txt", "b.txt"}
