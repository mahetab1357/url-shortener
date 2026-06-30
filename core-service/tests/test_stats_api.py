def test_stats_returns_404_for_unknown_short_code(client, fake_analytics_client):
    resp = client.get("/api/urls/does-not-exist/stats")
    assert resp.status_code == 404
    # Analytics shouldn't even be asked about a code core-service doesn't know.
    assert fake_analytics_client.requested_codes == []


def test_stats_returns_zeroed_analytics_when_unavailable(client, fake_analytics_client):
    create_resp = client.post("/shorten", json={"url": "https://example.com/tracked"})
    short_code = create_resp.json()["short_code"]

    fake_analytics_client.response = None  # simulates analytics-service being down

    resp = client.get(f"/api/urls/{short_code}/stats")
    assert resp.status_code == 200
    body = resp.json()
    assert body["analytics_available"] is False
    assert body["total_clicks"] == 0
    assert body["original_url"] == "https://example.com/tracked"


def test_stats_merges_analytics_payload_when_available(client, fake_analytics_client):
    create_resp = client.post("/shorten", json={"url": "https://example.com/tracked"})
    short_code = create_resp.json()["short_code"]

    fake_analytics_client.response = {
        "shortCode": short_code,
        "totalClicks": 12,
        "lastClickedAt": "2026-06-29T12:00:00Z",
        "hourlyClicks": [{"hourStart": "2026-06-29T11:00:00Z", "count": 12}],
        "dailyClicks": [{"date": "2026-06-29", "count": 12}],
        "deviceBreakdown": [{"deviceType": "Mobile", "browser": "Safari", "count": 12}],
        "referrerBreakdown": [{"referrerDomain": "direct", "count": 12}],
    }

    resp = client.get(f"/api/urls/{short_code}/stats")
    assert resp.status_code == 200
    body = resp.json()
    assert body["analytics_available"] is True
    assert body["total_clicks"] == 12
    assert body["short_code"] == short_code
    assert body["device_breakdown"][0]["device_type"] == "Mobile"
    assert fake_analytics_client.requested_codes == [short_code]
