# Estágio 1: Builder (Compilação e Dependências)
FROM python:3.11-slim AS builder

WORKDIR /app

# Instalamos as dependências em um diretório temporário
RUN pip install --no-cache-dir --prefix=/install flask prometheus-client werkzeug

# Estágio 2: Runtime (Imagem Final e Segura)
FROM python:3.11-slim

WORKDIR /app

# Copiamos apenas as dependências instaladas do estágio anterior
COPY --from=builder /install /usr/local

# Copiamos o código da aplicação
COPY app/ .

# SEGURANÇA: Criamos um usuário comum para não rodar como root
RUN adduser --disabled-password --gecos '' appuser && \
    chown -R appuser:appuser /app

USER appuser

EXPOSE 8080

CMD ["python", "main.py"]