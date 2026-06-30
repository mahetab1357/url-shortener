# Load testing

Locust load test targeting core-service's redirect path. See
[RESULTS.md](RESULTS.md) for the most recent recorded run.

## Run it yourself

The full stack must be running first (`docker compose up -d` from the repo
root), then:

```bash
cd load-tests
python -m venv .venv && source .venv/Scripts/activate   # .venv\Scripts\activate on cmd
pip install -r requirements.txt

# Headless, 100 users, ramp 10/s, 60 seconds:
locust -f locustfile.py --host=http://localhost:8000 --headless \
    -u 100 -r 10 --run-time 60s --csv results --html results.html

# Or with the interactive web UI instead:
locust -f locustfile.py --host=http://localhost:8000
# then open http://localhost:8089
```
