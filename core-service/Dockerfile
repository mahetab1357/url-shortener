FROM python:3.13-slim AS base
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

FROM base AS dev
COPY requirements-dev.txt .
RUN pip install --no-cache-dir -r requirements-dev.txt
# app/ is bind-mounted over this in docker-compose.dev.yml for live reload;
# copying it here too so `docker run` against this stage works standalone.
COPY app ./app
CMD ["sh", "-c", "python -m app.db.init_db && uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload"]

FROM base AS production
COPY app ./app
CMD ["sh", "-c", "python -m app.db.init_db && uvicorn app.main:app --host 0.0.0.0 --port 8000"]
