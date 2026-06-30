import random

from locust import HttpUser, between, events, task

SEED_URL_COUNT = 50
_short_codes: list[str] = []


@events.test_start.add_listener
def seed_short_urls(environment, **kwargs):
    """Pre-create a pool of short codes once, before any simulated user
    starts hitting the redirect endpoint. This is deliberate: we want to
    measure the redirect path's own performance (the thing Redis caching
    exists for), not /shorten's DB-insert cost mixed into the same numbers.
    """
    import requests

    base_url = environment.host or "http://localhost:8000"
    with requests.Session() as session:
        for i in range(SEED_URL_COUNT):
            resp = session.post(
                f"{base_url}/shorten",
                json={"url": f"https://example.com/load-test/{i}"},
                timeout=10,
            )
            resp.raise_for_status()
            _short_codes.append(resp.json()["short_code"])
    print(f"Seeded {len(_short_codes)} short codes for load testing.")


class RedirectUser(HttpUser):
    host = "http://localhost:8000"
    wait_time = between(0.1, 0.5)

    @task(19)
    def redirect(self):
        if not _short_codes:
            return
        code = random.choice(_short_codes)
        # Don't follow the 307 - we're timing core-service's own response,
        # not example.com's.
        self.client.get(f"/{code}", allow_redirects=False, name="/{short_code}")

    @task(1)
    def shorten_new_url(self):
        resp = self.client.post(
            "/shorten",
            json={"url": f"https://example.com/load-test/new/{random.randint(0, 10**9)}"},
            name="/shorten",
        )
        if resp.status_code == 201:
            _short_codes.append(resp.json()["short_code"])
