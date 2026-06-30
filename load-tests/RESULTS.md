# Load Test Results

Real output from a Locust run against the full `docker-compose` stack (all
6 services: Postgres, Redis, RabbitMQ, core-service, analytics-service,
frontend) running locally. Raw output preserved in this directory:
`results_stats.csv`, `results_stats_history.csv`, `results.html`.

## Test configuration

- Tool: Locust 2.31.5 (`locustfile.py`)
- Target: core-service redirect endpoint (`GET /{short_code}`), with a
  light mix of `POST /shorten` (1 shorten per 19 redirects) to simulate
  realistic traffic without it dominating the numbers
- 50 short codes pre-seeded before the run, picked at random per request
- Load profile: 100 concurrent users, spawn rate 10 users/sec, 60s
  steady-state run
- Run command:
  ```
  locust -f locustfile.py --host=http://localhost:8000 --headless \
      -u 100 -r 10 --run-time 60s --csv results --html results.html
  ```

## A real concurrency bug this test caught

The first run of this exact test exposed a genuine bug: core-service's
`RabbitMQPublisher` reused a single `pika.BlockingConnection`/channel
across requests for efficiency (avoiding a TCP+AMQP handshake per
redirect). `pika.BlockingConnection` is explicitly documented as not
thread-safe, but FastAPI runs sync endpoints - including the redirect
handler that publishes click events - across a real thread pool, so
concurrent requests really did call `publish()` concurrently.

Under 100 concurrent users, **~8,500 of ~8,650 publish attempts failed**
with `pika.exceptions.ChannelWrongStateError`, silently - by design,
`publish()` swallows exceptions so a queue problem can never break a
redirect (see [app/mq/rabbitmq_client.py](../core-service/app/mq/rabbitmq_client.py)).
That design choice was correct (the HTTP layer showed 0% failures both
before and after the fix - redirects never broke), but it also meant the
analytics pipeline was quietly losing ~98% of click events under load,
with nothing in the HTTP-level test results hinting at it.

**Fix:** a `threading.Lock` around the publish critical section, since
pika's own threading model requires single-threaded access to a given
connection/channel. Verified two ways:
1. A new regression test
   (`test_publish_serializes_concurrent_calls_across_threads` in
   `core-service/tests/test_rabbitmq_client.py`) spins up 20 real threads
   calling `publish()` concurrently against a fake channel and asserts
   no two threads are ever inside the critical section simultaneously.
   Confirmed this test reliably fails (3/3 runs) with the lock removed,
   and passes consistently with it.
2. Re-ran the identical Locust load test after the fix and queried
   Postgres directly (`analytics.url_click_stats`) to confirm click
   counts actually landed - going from ~150 successfully-recorded clicks
   out of 8,651 redirects (pre-fix) to effectively all of them post-fix.

This is the kind of bug that's invisible at the HTTP layer and invisible
in low-concurrency manual testing - it only showed up under genuine
concurrent load, which is the whole reason this load test exists rather
than just being a checkbox.

## Environment

- **This was run on a single laptop with Locust, Docker Desktop, and all
  6 containers competing for the same CPU/RAM** - not a dedicated
  load-generator machine hitting a separately-hosted target. Treat these
  as a directional smoke test of the architecture, not a production
  capacity benchmark.
- CPU: AMD Ryzen 5 7530U (6 cores / 12 threads)
- RAM: 7.4 GB total, shared across host OS + all 6 Docker containers +
  the Locust process itself
- No CPU/memory limits set on any container in `docker-compose.yml`

## Results (post-fix)

| Endpoint | Requests | Failures | Median | p95 | p99 | Max | Throughput |
|---|---|---|---|---|---|---|---|
| `GET /{short_code}` | 9,335 | 0 | 230ms | 330ms | 390ms | 585ms | 157 req/s |
| `POST /shorten` | 520 | 0 | 220ms | 320ms | 370ms | 539ms | 8.7 req/s |
| **Aggregated** | **9,855** | **0 (0.00%)** | **230ms** | **330ms** | **390ms** | **590ms** | **166 req/s** |

**Zero failed HTTP requests across all 9,855 requests** - and, post-fix,
the click events behind those redirects were actually being recorded
correctly too (verified via direct Postgres query, not just absent
errors in the logs).

## Interpretation

- The redirect path held up under 100 concurrent users with no HTTP
  errors in both runs - but the first run's silent analytics data loss
  is the more important finding (see above). A load test that only checks
  HTTP status codes would have called that run a clean pass.
- ~230ms median latency is dominated by this being a single under-powered
  shared host running 6 containers plus the load generator itself, not by
  the application logic - the FastAPI/Redis path itself does very little
  work per request. A dedicated load-test environment would show
  meaningfully lower latency at the same request rate.
- This test does not isolate cache-hit vs cache-miss latency. Future
  improvement: a second Locust scenario specifically hammering one single
  short code repeatedly (guaranteed cache hits) vs. always-unique codes
  (guaranteed cache misses), to quantify the cache's actual latency win.
