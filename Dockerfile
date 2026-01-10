FROM python:3.11-slim

WORKDIR /app

# Forçamos a instalação das dependências essenciais aqui
RUN pip install --no-cache-dir flask prometheus-client werkzeug

# Copiamos o conteúdo da pasta app para dentro de /app no container
COPY app/ .

EXPOSE 8080

# O seu log mostrou que o arquivo se chama main.py, então vamos rodar ele:
CMD ["python", "main.py"]