# 🚀 SRE Challenge - Cloud & Observability

Este repositório contém a solução para o desafio técnico de SRE, focando em containerização, orquestração, monitoramento e análise de logs estruturados em um cluster Kubernetes.

## 🏗️ Arquitetura da Solução

A aplicação consiste em uma API Flask instrumentada, operando em ambiente Kubernetes e integrada a uma stack robusta de observabilidade.

* **Aplicação:** Python Flask com exportador nativo de métricas Prometheus (Prometheus Client).
* **Orquestração:** Kubernetes (Minikube) com isolamento por Namespaces (`sre-app` e `monitoring`).
* **Logs (EFK Stack):**
    * **Filebeat:** Coleta logs do volume compartilhado em `/app/logs`.
    * **Logstash:** Processa logs via filtros Grok para extração de latência e status HTTP.
    * **Elasticsearch & Kibana:** Armazenamento e visualização de dados.
* **Monitoramento:** Stack Prometheus + Grafana via Helm Charts.
* **Escalabilidade:** HPA (Horizontal Pod Autoscaler) baseado em consumo de CPU.
* **CI/CD:** GitHub Actions configurado para Linting e Build de imagem Docker.



---

## 🛠️ Decisões Técnicas e Troubleshooting (SRE Insights)

Durante a fase de implantação, foram realizados os seguintes ajustes críticos para garantir a estabilidade do ambiente:

1.  **Otimização do Runtime Python:** Identificado e corrigido o erro de `ModuleNotFoundError` no container através da reestruturação do Dockerfile, garantindo a instalação das dependências (`flask`, `prometheus-client`) sem dependência de cache volátil.
2.  **Gestão de Recursos (Stability):** Identificado erro `OOMKilled` no Elasticsearch devido às restrições de hardware do nó único. Os limites de recursos (Requests/Limits) foram refinados para permitir a coexistência das stacks de métricas e logs no Minikube.
3.  **Coleta de Logs Estruturados:** Implementado um volume do tipo `emptyDir` para garantir que o Filebeat tenha acesso em tempo real aos logs persistidos pela aplicação Flask.

---

## 🚀 Como Executar

### 1. Preparação do Cluster
```bash
minikube start --memory=6144 --cpus=4
eval $(minikube docker-env)
