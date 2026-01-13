# 📄 Relato Técnico – Linha do Tempo Completa de Implementação

## Projeto: sre-pleno-app

Este documento descreve cronologicamente, de forma detalhada e transparente, todo o processo de construção, correção e validação do projeto sre-pleno-app, desde a escolha da aplicação até a estabilização do cluster Kubernetes com observabilidade, escalabilidade e segurança.

O objetivo foi demonstrar competências práticas de SRE, incluindo troubleshooting real, tomada de decisão sob restrições de hardware e entendimento profundo de Kubernetes, Docker e observabilidade.

## 🕒 T-0 — Escolha da Aplicação e Design Inicial

### Objetivo do Teste

### Construir uma aplicação containerizada capaz de:

* Expor health check
* Expor métricas Prometheus
* Gerar logs estruturados
* Escalar automaticamente em Kubernetes
* Integrar com stack de observabilidade (Prometheus + ELK)

### Escolha Tecnológica

* **Linguagem:** Python
* **Framework:** Flask (simplicidade e previsibilidade)
* **Servidor:** WSGI nativo
* **Métricas:** prometheus-client
* **Logs:** logging nativo com saída para arquivo e stdout

### Estrutura Final da Aplicação

```
app/
 ├── main.py
 ├── requirements.txt
``` 

### Decisão Importante – Logs

* Inicialmente logs seriam apenas em stdout
* Decisão SRE: escrever também em arquivo local
* Motivo: permitir Filebeat sidecar/DaemonSet coletar logs sem depender exclusivamente do runtime

**📌 Caminho definido:**
```
/app/logs/app.log
```

## 🕒 T-1 — Implementação da Aplicação (main.py)

### Funcionalidades Implementadas

* ```/ → endpoint principal```

* ```/health → health check```

* ```/metrics → métricas Prometheus```

* ```Logs em arquivo e stdout```

* ```Métrica de contagem e latência por request```

### Código Final (resumo conceitual)

* Criação automática do diretório ```/app/logs```

* Logs INFO para:

    * start da aplicação

    * acessos ao ```/health```

* DispatcherMiddleware para ```/metrics```

**📌 Confirmação prática:**

```
kubectl exec -it <pod> -- sh
ls /app/logs
cat /app/logs/app.log
```

## 🕒 T-2 — Containerização (Docker)

### Objetivo

Criar uma imagem:
* Imutável
* Simples
* Compatível com Kubernetes local (Minikube)

### Decisões

* Base: ```python:3.11-slim```
* Execução como usuário não-root
* Porta exposta: ```8080```
* Diretório de trabalho: ```/app```

### Build da imagem
```
docker build -t sre-pleno-app:v4 .
```

### Problema Real Encontrado

Pods rodavam como root, mesmo após criar usuário no Dockerfile.

### Diagnóstico

O Minikube estava reutilizando imagem em cache.

### Correção
```
minikube image rm sre-pleno-app:v3
minikube image load sre-pleno-app:v4
kubectl rollout restart deployment sre-pleno-app -n sre-app
```

**📌 Resultado:**
```
kubectl exec -it <pod> -- id
uid=1000(appuser)
```

## 🕒 T-3 — Kubernetes Deployment

### Namespace
```
kubectl create namespace sre-app
```

### Deployment

* Réplicas iniciais: 2
* Probes:
    * ```livenessProbe: /health```
    * ```readinessProbe: /health```
* Resources (essencial para HPA):
```
requests:
  cpu: 100m
  memory: 128Mi
limits:
  cpu: 200m
  memory: 256Mi
```

### Erro Encontrado
Pods em ```CrashLoopBackOff```
### Causa
Probe apontava para endpoint inexistente ```(/ready)```
### Correção
Alteração para ```/health```

## 🕒 T-4 — Service e Acesso
### Service ClusterIP

* Porta externa: 80
* Target: 8080
```
kubectl port-forward svc/sre-pleno-app-service 8081:80 -n sre-app
curl http://localhost:8081/health
```

## 🕒 T-5 — Métricas Prometheus
### Decisão
Usar annotations, evitando ServiceMonitor (menos complexidade)
```
annotations:
  prometheus.io/scrape: "true"
  prometheus.io/port: "8080"
  prometheus.io/path: "/metrics"
```
### Validação
```
kubectl get pods -n sre-app -o jsonpath='{.items[*].metadata.annotations}'
```
## 🕒 T-6 — HPA (Escalabilidade)
### Implementação
* CPU > 70%
* Memória > 75%
* Mínimo: 2 pods
* Máximo: 5 pods

### Erros Reais Encontrados

1. HPA criado no namespace default
2. Métricas apareciam como <unknown>

### Correções

* Adição explícita de namespace: sre-app
* Inclusão de resources.requests

### Validação
```
kubectl get hpa -n sre-app
```

## 🕒 T-7 — Teste de Carga
### Execução
```
kubectl run load-generator \
  --rm -it \
  --image=busybox \
  -n sre-app -- \
  sh -c "while true; do wget -q -O- http://sre-pleno-app-service; done"
```
### Resultado
* Escala automática para até 5 pods
* Logs intensificados
* Métricas refletidas corretamente

## 🕒 T-8 — Stack ELK (Observabilidade de Logs)
### Decisão Crítica – Limitação de Hardware

O ambiente local não suportava:
* Elasticsearch (2Gi)
* Kibana (1Gi)
* Prometheus
* Aplicação
* Minikube

### Ajustes Necessários
* Redução do Minikube:
```
minikube start --memory=4096 --cpus=2
```
### Impacto

❗ Dashboards prontos do Kibana não puderam ser criados, pois:
* Kibana frequentemente entrava em Pending ou Timeout
* Consumo de memória tornava o cluster instável

**📌 Decisão consciente documentada: priorizar ingestão e visibilidade de logs em vez de dashboards visuais.**

## 🕒 T-9 — Elasticsearch
### Implementação
* Operador Elastic (ECK)
* 1 nó
* mmap desativado
```
node.store.allow_mmap: false
```
## 🕒 T-10 — Kibana
* 1 instância
* Conectada ao Elasticsearch via elasticsearchRef
* Recursos reduzidos

## 🕒 T-11 — Filebeat (Coleta de Logs)
### Estratégia
* DaemonSet
* Coleta logs de:
```
/var/log/containers/*.log
```
### Configuração
* Envio para Logstash (conceitual)
* Enriquecimento com metadata Kubernetes
### Erros Encontrados
* YAML inválido (containers duplicados)
* ```containers: Required value```
* Namespace incorreto
### Correções
* Reescrita completa do manifesto
* Validação com:
```
kubectl apply -f filebeat.yaml --dry-run=client
```
### Estado Final
```
kubectl get pods -n sre-app | grep filebeat
filebeat-xxxxx   1/1 Running
```
### 🔐 Segurança — Ajustes Implementados
* Execução non-root (UID 1000)
* Resource limits definidos
* Namespace isolado
* Superfície mínima de imagem
* Sem exposição externa desnecessária
* TLS do Elasticsearch mantido (verification_mode none apenas em ambiente local)

### 🔄 CI/CD — Decisão Consciente

#### Por que não implementar pipeline completo?
* Escopo local
* Ambiente sem registry privado
* Foco em SRE runtime
#### O que foi entregue
* Estrutura ```/ci```
* Docker build reproduzível
* Manifests declarativos
* Projeto pronto para CI GitHub Actions (documentado)

#### 🤖 Uso de IA, Documentação e Comunidade
Durante o projeto foram utilizados:
* IA como auxílio de debug, não geração cega
* Documentação oficial:
    * Kubernetes
    * Docker
    * Elastic
* Fóruns e issues reais (timeouts, HPA unknown, Filebeat crashes)

**📌 Todas as decisões foram validadas manualmente no cluster.**

#### 🏁 Estado Final do Projeto
| Pilar | Status |
| ----- | ------ |
| Aplicação | ✅ Estável |
| Kubernetes | ✅ Funcional |
| HPA | ✅ Escalando |
| Métricas | ✅ Prometheus |
| Logs | ✅ Filebeat |
| Segurança | ✅ Adequada |
| Observabilidade | ✅ Funcional |
| Documentação | ✅ Completa |

### ✔️ Conclusão

Este projeto demonstra capacidade prática de SRE, domínio de troubleshooting, tomada de decisão sob restrições reais e entendimento profundo de infraestrutura moderna.

Nada foi “teórico”.
Tudo foi **construído, quebrado, analisado e corrigido.**
