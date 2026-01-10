from flask import Flask, jsonify
import logging
import os
from prometheus_client import make_wsgi_app, Counter, Histogram
from werkzeug.middleware.dispatcher import DispatcherMiddleware

app = Flask(__name__)

# --- MÉTRICAS PROMETHEUS ---
# O endpoint /metrics será criado automaticamente pelo DispatcherMiddleware
REQUEST_COUNT = Counter('http_requests_total', 'Total Request Count', ['method', 'endpoint', 'status'])
REQUEST_LATENCY = Histogram('http_request_duration_seconds', 'Request Latency')

app.wsgi_app = DispatcherMiddleware(app.wsgi_app, {
    '/metrics': make_wsgi_app()
})

# --- CONFIGURAÇÃO DE LOGS ---
LOG_DIR = "/app/logs"
LOG_FILE = os.path.join(LOG_DIR, "app.log")
os.makedirs(LOG_DIR, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler()
    ]
)

# --- ROTAS ---
@app.route("/")
def index():
    # O bloco 'with' mede o tempo e alimenta o Histogram de latência
    with REQUEST_LATENCY.time():
        app.logger.info("Root endpoint accessed")
        REQUEST_COUNT.labels(method='GET', endpoint='/', status=200).inc()
        return jsonify({
            "app": "sre-pleno-app",
            "message": "Application is running"
        })

@app.route("/health")
def health():
    app.logger.info("Health check accessed")
    return jsonify({"status": "green"})

if __name__ == "__main__":
    # Porta 8080 alinhada com Service e Dockerfile
    app.run(host="0.0.0.0", port=8080)