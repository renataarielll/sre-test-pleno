🚀 SRE Challenge - Cloud & Observability
Este repositório contém a solução para o desafio técnico de SRE, focando em containerização, orquestração, monitoramento e análise de logs estruturados.

🏗️ Arquitetura da Solução
A aplicação consiste em uma API Flask operando em ambiente Kubernetes, integrada a uma stack completa de observabilidade.

Aplicação: Python Flask com exportador nativo de métricas Prometheus.

Orquestração: Kubernetes (Minikube) com separação por Namespaces (sre-app e monitoring).

Logs (EFK Stack):

Filebeat: Coleta logs do volume compartilhado em /app/logs.

Logstash: Processa logs via filtros Grok para estruturar latência e status HTTP.

Elasticsearch: Armazenamento e indexação.

Kibana: Visualização e análise.

Métricas: Prometheus + Grafana (via Helm).

Escalabilidade: HPA (Horizontal Pod Autoscaler) baseado em consumo de CPU.

CI/CD: GitHub Actions configurado para Lint, Build e Push de imagem.

🛠️ Decisões Técnicas e Troubleshooting (SRE Insights)
Durante a implementação, foram aplicadas as seguintes correções críticas:

Otimização de Imagem Docker: Corrigido erro de ModuleNotFoundError através de um build multi-stage que garante a presença de dependências como flask e prometheus-client.

Gestão de Recursos (FinOps/Stability): Identificado e mitigado erro OOMKilled no Elasticsearch. Os limites de memória (Requests/Limits) foram refinados para operar dentro das restrições de um nó único do Minikube (6GB RAM).

Métricas Customizadas: A aplicação foi instrumentada para reportar latência (Histogram) e contagem de requisições (Counter), permitindo a criação de dashboards de Golden Signals.

🚀 Como Executar
1. Preparação do Ambiente
Bash

minikube start --memory=6144 --cpus=4
eval $(minikube docker-env)
2. Build da Aplicação
Bash

docker build -t sre-pleno-app:v3 .
3. Deploy da Infraestrutura
Bash

# Aplicação e Logs
kubectl apply -f k8s/configmap.yaml -n sre-app
kubectl apply -f k8s/deployment.yaml -n sre-app
kubectl apply -f k8s/elk/ -n sre-app

# Monitoramento
kubectl create namespace monitoring
helm install prometheus-stack prometheus-community/kube-prometheus-stack -n monitoring
4. Acessando a Aplicação
Bash

minikube service sre-pleno-app-service -n sre-app --url
📈 Observabilidade
Endpoint de Métricas: /metrics

Health Check: /health

Logs Estruturados: Gerados em /app/logs/app.log no formato: 2026-01-10 00:45:12 INFO Root endpoint accessed

🤖 CI/CD Pipeline
O arquivo .github/workflows/main.yml executa automaticamente:

Linting: Verificação de boas práticas no código Python.

Build: Geração da imagem Docker.

Security Check: (Opcional) Scan de vulnerabilidades na imagem.

O que você pode fazer agora:
Copie o conteúdo acima para o seu arquivo README.md.

Garanta que todos os arquivos .yaml que usamos estão nas pastas mencionadas.

Faça o commit final:

Bash

git add .
git commit -m "docs: final update with architecture and troubleshooting notes"
git push origin main
