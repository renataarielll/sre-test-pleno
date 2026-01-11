# =================================================================
# ESTÁGIO 1: BUILDER (Otimização e Eficiência)
# =================================================================
# Justificativa SRE: Utilizamos Multi-stage build para separar o ambiente de 
# compilação do ambiente de execução, garantindo uma imagem final mais leve.
FROM python:3.11-slim AS builder

WORKDIR /app

# Copiamos apenas o arquivo de dependências para aproveitar o cache de camadas do Docker.
# Se o requirements.txt não mudar, o Docker pula esta instalação em builds futuros.
COPY app/requirements.txt .

# Instalamos as dependências em um diretório isolado (/install).
# O uso do --no-cache-dir reduz o tamanho da camada ao não salvar arquivos temporários do pip.
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

# =================================================================
# ESTÁGIO 2: RUNTIME (Segurança e Hardening)
# =================================================================
# Justificativa SRE: Imagem final baseada em 'slim' para reduzir a superfície de ataque.
FROM python:3.11-slim

# Definição de variáveis de ambiente conforme requisitos do desafio (Tarefa 1).
ENV APP_ENV=staging
ENV PORT=8080
# Garante que o output do Python seja enviado direto para o terminal (logs) sem buffer.
ENV PYTHONUNBUFFERED=1 

WORKDIR /app

# SEGURANÇA (Peso 40%): Implementação de usuário não-root.
# Por padrão, containers rodam como root. Aqui criamos um usuário limitado para 
# mitigar riscos de segurança e escalação de privilégio no cluster Kubernetes.
RUN addgroup --system appgroup && adduser --system --group appuser

# Otimização: Copiamos apenas o necessário do estágio de build.
# Isso remove compiladores e ferramentas de build da imagem final.
COPY --from=builder /install /usr/local
COPY --chown=appuser:appgroup app/ .

# Mudamos para o usuário não-privilegiado antes da execução.
USER appuser

# Porta configurada conforme o Service e HPA do Kubernetes.
EXPOSE 8080

# EXECUÇÃO: Utilizamos o Uvicorn (servidor ASGI) para rodar o FastAPI.
# O host 0.0.0.0 é fundamental para que o Kubernetes consiga rotear o tráfego para o pod.
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]