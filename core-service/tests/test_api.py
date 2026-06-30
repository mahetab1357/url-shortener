from datetime import datetime, timedelta, timezone


def test_shorten_returns_short_url(client):
    resp = client.post("/shorten", json={"url": "https://example.com/some/long/path"})
    assert resp.status_code == 201
    body = resp.json()
    assert body["original_url"] == "https://example.com/some/long/path"
    assert len(body["short_code"]) == 7
    assert body["short_code"] in body["short_url"]


def test_shorten_rejects_malformed_url(client):
    resp = client.post("/shorten", json={"url": "not-a-url"})
    assert resp.status_code == 422


def test_shorten_rejects_missing_scheme(client):
    resp = client.post("/shorten", json={"url": "www.example.com"})
    assert resp.status_code == 422


def test_shorten_accepts_custom_alias(client):
    resp = client.post(
        "/shorten", json={"url": "https://example.com", "custom_alias": "my-cool-link"}
    )
    assert resp.status_code == 201
    assert resp.json()["short_code"] == "my-cool-link"


def test_shorten_rejects_invalid_alias_format(client):
    resp = client.post("/shorten", json={"url": "https://example.com", "custom_alias": "a"})
    assert resp.status_code == 422


def test_shorten_duplicate_alias_returns_409(client):
    client.post("/shorten", json={"url": "https://example.com", "custom_alias": "dup-alias"})
    resp = client.post("/shorten", json={"url": "https://other.com", "custom_alias": "dup-alias"})
    assert resp.status_code == 409


def test_redirect_follows_to_original_url(client):
    create_resp = client.post("/shorten", json={"url": "https://example.com/target"})
    short_code = create_resp.json()["short_code"]

    resp = client.get(f"/{short_code}", follow_redirects=False)
    assert resp.status_code == 307
    assert resp.headers["location"] == "https://example.com/target"


def test_redirect_unknown_code_returns_404(client):
    resp = client.get("/does-not-exist", follow_redirects=False)
    assert resp.status_code == 404


def test_redirect_expired_link_returns_410(client):
    past = (datetime.now(timezone.utc) - timedelta(days=1)).isoformat()
    create_resp = client.post(
        "/shorten", json={"url": "https://example.com/expired", "expires_at": past}
    )
    short_code = create_resp.json()["short_code"]

    resp = client.get(f"/{short_code}", follow_redirects=False)
    assert resp.status_code == 410


def test_health_endpoint(client):
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok"}
