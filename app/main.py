import logging
import os
from fastapi import FastAPI
from datetime import datetime

# ============================
# Caminho de logs (alinhado com o volume)
# ============================

LOG_DIR = "/app/logs"
LOG_FILE = f"{LOG_DIR}/app.log"

os.makedirs(LOG_DIR, exist_ok=True)

# ============================
# Configuração de logging
# ============================

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler()
    ],
)

logger = logging.getLogger(__name__)
logger.info("Aplicação FastAPI iniciada")

# ============================
# Aplicação FastAPI
# ============================

app = FastAPI(
    title="SRE Pleno App",
    description="Aplicação de teste para desafio SRE",
    version="1.0.0",
)

# ============================
# Endpoints
# ============================

@app.get("/")
def root():
    logger.info("Endpoint / acessado")
    return {
        "message": "Aplicação SRE Pleno rodando",
        "timestamp": datetime.utcnow().isoformat()
    }

@app.get("/health")
def health():
    logger.info("Health check realizado")
    return {
        "status": "green",
        "service": "sre-pleno-app"
    }

@app.get("/error")
def error():
    logger.error("Erro simulado acionado")
    return {
        "error": "Erro simulado para testes de observabilidade"
    }
