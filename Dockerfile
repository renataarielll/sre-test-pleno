# =========================
# Base image
# =========================
FROM python:3.11-slim

WORKDIR /app

# Evita arquivos .pyc e garante logs imediatos
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Variáveis da aplicação
ENV APP_ENV=staging
ENV PORT=8080

# Criar usuário não-root
RUN addgroup --system appgroup \
    && adduser --system --ingroup appgroup appuser

# Copiar dependências
COPY app/requirements.txt .

# Instalar dependências
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# Copiar código da aplicação
COPY app/ app/

# Ajustar permissões
RUN chown -R appuser:appgroup /app

USER appuser

EXPOSE 8080

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]
