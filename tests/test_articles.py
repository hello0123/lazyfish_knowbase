def test_create_article_url(client):
    resp = client.post("/articles", json={"source_type": "url", "source_url": "https://example.com"})
    assert resp.status_code == 201
    body = resp.json()
    assert body["status"] == "pending"
    assert body["source_url"] == "https://example.com"


def test_create_article_note(client):
    resp = client.post("/articles", json={"source_type": "note", "raw_content": "hello"})
    assert resp.status_code == 201
    assert resp.json()["raw_content"] == "hello"


def test_create_article_missing_field(client):
    resp = client.post("/articles", json={"source_type": "url"})
    assert resp.status_code == 400


def test_create_article_invalid_source_type(client):
    resp = client.post("/articles", json={"source_type": "bogus"})
    assert resp.status_code == 422


def test_get_article(client):
    create = client.post("/articles", json={"source_type": "note", "raw_content": "test note"})
    article_id = create.json()["id"]
    resp = client.get(f"/articles/{article_id}")
    assert resp.status_code == 200
    assert resp.json()["id"] == article_id


def test_get_article_not_found(client):
    resp = client.get("/articles/9999")
    assert resp.status_code == 404
