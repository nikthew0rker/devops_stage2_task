import os
import time
from contextlib import closing

import psycopg2
from fastapi import FastAPI
from fastapi.responses import PlainTextResponse
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST

app = FastAPI(title="DevOps Test App")

REQUEST_COUNT = Counter("app_requests_total", "Total HTTP requests", ["path"])
REQUEST_LATENCY = Histogram("app_request_duration_seconds", "Request latency", ["path"])


def get_conn():
    return psycopg2.connect(
        host=os.getenv("DB_HOST", "db"),
        port=int(os.getenv("DB_PORT", "5432")),
        dbname=os.getenv("DB_NAME", "appdb"),
        user=os.getenv("DB_USER", "appuser"),
        password=os.getenv("DB_PASSWORD", "appuser"),
    )


@app.on_event("startup")
def startup():
    last_error = None
    for _ in range(20):
        try:
            with closing(get_conn()) as conn:
                with conn, conn.cursor() as cur:
                    cur.execute(
                        """
                        CREATE TABLE IF NOT EXISTS visits (
                            id SERIAL PRIMARY KEY,
                            ts TIMESTAMP DEFAULT NOW()
                        )
                        """
                    )
            return
        except Exception as exc:
            last_error = exc
            time.sleep(2)
    raise RuntimeError(f"Database is not ready: {last_error}")


@app.get("/")
def root():
    start = time.time()
    with closing(get_conn()) as conn:
        with conn, conn.cursor() as cur:
            cur.execute("INSERT INTO visits DEFAULT VALUES")
    REQUEST_COUNT.labels(path="/").inc()
    REQUEST_LATENCY.labels(path="/").observe(time.time() - start)
    return {"status": "ok"}


@app.get("/health")
def health():
    with closing(get_conn()) as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT 1")
    return {"status": "healthy"}


@app.get("/metrics")
def metrics():
    return PlainTextResponse(generate_latest().decode(), media_type=CONTENT_TYPE_LATEST)