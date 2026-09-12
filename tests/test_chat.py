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


async def test_chat_query_without_token_returns_401(client):
    resp = await client.post("/api/v1/chat/query", json={"question": "what is in my documents?"})

    assert resp.status_code == 401


async def test_chat_query_empty_question_returns_422(client):
    tenant_id = await _create_tenant(client)
    headers = await _auth_headers(client, tenant_id)

    resp = await client.post("/api/v1/chat/query", headers=headers, json={"question": ""})

    assert resp.status_code == 422


async def test_chat_query_with_no_indexed_documents_returns_fallback(client):
    tenant_id = await _create_tenant(client)
    headers = await _auth_headers(client, tenant_id)

    resp = await client.post(
        "/api/v1/chat/query", headers=headers, json={"question": "what is in my documents?"}
    )

    assert resp.status_code == 200
    body = resp.json()
    assert "couldn't find" in body["data"]["answer"].lower()
    assert body["data"]["citations"] == []


async def test_chat_query_returns_answer_with_citations(client):
    tenant_id = await _create_tenant(client)
    headers = await _auth_headers(client, tenant_id)
    upload = await client.post(
        "/api/v1/documents", headers=headers, files={"file": ("policy.txt", b"content", "text/plain")}
    )
    document_id = upload.json()["data"]["id"]
    client.fake_vector_store.added.append(
        ("employees get 30 days of paid leave per year", {"document_id": document_id, "tenant_id": tenant_id})
    )

    resp = await client.post(
        "/api/v1/chat/query", headers=headers, json={"question": "how much paid leave do I get?"}
    )

    assert resp.status_code == 200
    body = resp.json()
    assert "30 days of paid leave" in body["data"]["answer"]
    assert len(body["data"]["citations"]) == 1
    assert body["data"]["citations"][0]["document_id"] == document_id
    assert body["data"]["citations"][0]["filename"] == "policy.txt"


async def test_chat_query_only_retrieves_own_tenant_chunks(client):
    tenant_a = await _create_tenant(client)
    headers_a = await _auth_headers(client, tenant_a, email="alice@example.com")
    upload_a = await client.post(
        "/api/v1/documents", headers=headers_a, files={"file": ("a.txt", b"a", "text/plain")}
    )
    document_a = upload_a.json()["data"]["id"]
    client.fake_vector_store.added.append(
        ("tenant A's private salary figures", {"document_id": document_a, "tenant_id": tenant_a})
    )

    tenant_b_resp = await client.post("/api/v1/tenants", json={"name": "Globex", "slug": "globex"})
    tenant_b = tenant_b_resp.json()["data"]["id"]
    headers_b = await _auth_headers(client, tenant_b, email="bob@example.com")
    upload_b = await client.post(
        "/api/v1/documents", headers=headers_b, files={"file": ("b.txt", b"b", "text/plain")}
    )
    document_b = upload_b.json()["data"]["id"]
    client.fake_vector_store.added.append(
        ("tenant B's private salary figures", {"document_id": document_b, "tenant_id": tenant_b})
    )

    resp = await client.post(
        "/api/v1/chat/query", headers=headers_b, json={"question": "what are the salary figures?"}
    )

    assert resp.status_code == 200
    body = resp.json()
    assert "tenant A" not in body["data"]["answer"]
    assert all(c["document_id"] != document_a for c in body["data"]["citations"])
