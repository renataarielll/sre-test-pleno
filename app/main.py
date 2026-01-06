import os
import time
import logging
from fastapi import FastAPI, Request, Response
from prometheus_client import (
    Counter,
    Histogram,
    Gauge,
    generate_latest,
    CONTENT_TYPE_LATEST,
)

# =========================
# Configurações
# =========================
APP_ENV = os.getenv("APP_ENV", "staging")
PORT = int(os.getenv("PORT", "8080"))

# =========================
# Logging estruturado
# =========================
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
)
logger = logging.getLogger(__name__)

# =========================
# Métricas Prometheus
# =========================
REQUEST_COUNT = Counter(
    "app_requests_total",
    "Total de requisições HTTP",
    ["method", "endpoint", "status"],
)

REQUEST_LATENCY = Histogram(
    "app_request_latency_seconds",
    "Latência das requisições HTTP",
    ["endpoint"],
)

ERROR_RATE = Gauge(
    "app_error_rate",
    "Taxa de erro da aplicação (último minuto)",
)

# =========================
# App FastAPI
# =========================
app = FastAPI(title="SRE Pleno Test App")

@app.middleware("http")
async def metrics_middleware(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)

    latency = time.time() - start_time
    endpoint = request.url.path

    REQUEST_LATENCY.labels(endpoint=endpoint).observe(latency)
    REQUEST_COUNT.labels(
        method=request.method,
        endpoint=endpoint,
        status=response.status_code,
    ).inc()

    if response.status_code >= 500:
        ERROR_RATE.set(1)

    logger.info(
        f"endpoint={endpoint} method={request.method} "
        f"status={response.status_code} latency={latency:.3f}s env={APP_ENV}"
    )

    return response

# =========================
# Endpoints obrigatórios
# =========================
@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/ready")
def ready():
    return {"status": "ready"}

@app.get("/metrics")
def metrics():
    return Response(
        generate_latest(),
        media_type=CONTENT_TYPE_LATEST
    )

@app.get("/")
def root():
    return {
        "message": "SRE Pleno Test Application",
        "environment": APP_ENV,
    }
