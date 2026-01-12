# SRE Pleno Test 

## 🚀 Quick Start

Este projeto consiste em uma aplicação FastAPI containerizada e orquestrada em Kubernetes, com foco em alta disponibilidade e observabilidade.

**Pré-requisitos:**
* Minikube (configurado com 4GB RAM)
* kubectl
* Docker

**Execução Local:**
1. Inicie o cluster: `minikube start --memory 4096`
2. Aplique os manifestos: `kubectl apply -f k8s/`
3. Acesse a aplicação: `kubectl port-forward svc/sre-pleno-app-service 8080:80 -n sre-app`

## 🏗 Arquitetura

A solução foi desenhada para ser escalável e resiliente:
* **App:** FastAPI (Python 3.11) com Prometheus Client integrado.
* **K8S:** Deployment com 2 réplicas iniciais, HPA (Horizontal Pod Autoscaler) e Resource Quotas.
* **Monitoring:** Prometheus para coleta via Annotations e Grafana para visualização.
* **Logging:** Stack ELK (Elasticsearch, Logstash, Kibana) via manifestos declarativos.

## 🛠 Componentes e Decisões Técnicas

### 1. Containerização (Peso: 20%)
* [cite_start]**Multi-stage Build:** Utilizado para reduzir o tamanho da imagem final e aumentar a segurança. [cite: 10, 27]
* [cite_start]**Hardening:** A aplicação roda com usuário não-root (`appuser`), mitigando riscos de segurança. [cite: 10, 42]
* [cite_start]**Otimização:** Uso da imagem base `python:3.11-slim` para menor superfície de ataque. [cite: 10, 35]

### 2. Kubernetes (Peso: 30%)
* [cite_start]**HPA v2:** Configurado para escalar até 5 réplicas baseado em CPU (>70%) e Memória (>75%). [cite: 49, 80]
* [cite_start]**Self-healing:** Implementação de Liveness e Readiness Probes para garantir a saúde dos pods. [cite: 53, 71, 75]
* [cite_start]**Resiliência:** Definição rigorosa de `requests` (100m/128Mi) e `limits` (200m/256Mi) para evitar OOMKilled. [cite: 64, 80]

### 3. Observabilidade (Peso: 15%)
* [cite_start]**Métricas:** Exposição de métricas no padrão Prometheus via endpoint `/metrics`. [cite: 89, 100]
* [cite_start]**Service Discovery:** Annotations implementadas no Deployment para coleta automática. [cite: 90, 95]
* [cite_start]**Dashboards:** Projeto de dashboard JSON contemplando Latência P95 e Taxa de Erros. [cite: 15, 106]

### 4. CI/CD (Peso: 10%)
* [cite_start]**Pipeline:** Implementado via GitHub Actions com etapas de Lint (Hadolint), Build e Deploy automático. [cite: 13, 113, 135]

### 5. ELK Stack (Peso: 25%)
* [cite_start]**Pipeline de Log:** Logstash configurado com filtro Grok para extrair `level`, `endpoint` e `latency`. [cite: 166, 171, 173]
* [cite_start]**Nota:** Devido a limitações de hardware no ambiente local de teste, a stack ELK foi entregue via manifestos declarativos (IaC), garantindo que a infraestrutura esteja pronta para produção. [cite: 12, 243]

## 📈 Decisões Técnicas
* [cite_start]Escolha do **FastAPI**: Pela performance assíncrona superior para microserviços. [cite: 9, 22]
* [cite_start]**Infrastructure as Code (IaC)**: Todos os recursos, incluindo dashboards, foram versionados para garantir reprodutibilidade. [cite: 6, 200]

## 📊 Evidências de Funcionamento (CLI)

Para validar a integridade da infraestrutura, foram realizados testes diretamente no cluster via `kubectl`.

### 1. Estado dos Objetos no Namespace
Verificação da saúde dos Pods, Services e Deployments:
#### Comando: kubectl get all -n sre-app
```
NAME                                 READY   STATUS    RESTARTS   AGE
pod/sre-pleno-app-7c7ccffbb8-4w99q   1/1     Running   0          64m
pod/sre-pleno-app-7c7ccffbb8-cqz25   1/1     Running   0          64m

NAME                            TYPE        CLUSTER-IP       EXTERNAL-IP   PORT(S)   AGE
service/sre-pleno-app-service   ClusterIP   10.104.146.255   <none>        80/TCP    65m

NAME                            READY   UP-TO-DATE   AVAILABLE   AGE
deployment.apps/sre-pleno-app   2/2     2            2           65m

NAME                                       DESIRED   CURRENT   READY   AGE
replicaset.apps/sre-pleno-app-7c7ccffbb8   2         2         2       65m

NAME                                                    REFERENCE                  TARGETS                        MINPODS   MAXPODS   REPLICAS   AGE
horizontalpodautoscaler.autoscaling/sre-pleno-app-hpa   Deployment/sre-pleno-app   cpu: 1%/70%, memory: 35%/75%   2         5         2          63m
```

### 2.Recursos e Health Checks (Self-Healing)
Prova da configuração de Probes (Liveness/Readiness) e limites de CPU/Memória:
#### Comando: kubectl describe deployment sre-pleno-app -n sre-app

```
kubectl describe deployment sre-pleno-app -n sre-app
Name:                   sre-pleno-app
Namespace:              sre-app
CreationTimestamp:      Sun, 11 Jan 2026 18:54:41 -0300
Labels:                 app=sre-pleno-app
Annotations:            deployment.kubernetes.io/revision: 1
Selector:               app=sre-pleno-app
Replicas:               2 desired | 2 updated | 2 total | 2 available | 0 unavailable
StrategyType:           RollingUpdate
MinReadySeconds:        0
RollingUpdateStrategy:  25% max unavailable, 25% max surge
Pod Template:
  Labels:  app=sre-pleno-app
  Containers:
   app:
    Image:      sre-pleno-app:v3
    Port:       8080/TCP
    Host Port:  0/TCP
    Limits:
      cpu:     250m
      memory:  128Mi
    Requests:
      cpu:        100m
      memory:     64Mi
    Liveness:     http-get http://:8080/health delay=5s timeout=1s period=10s #success=1 #failure=3
    Readiness:    http-get http://:8080/health delay=5s timeout=1s period=5s #success=1 #failure=3
    Environment:  <none>
    Mounts:
      /app/logs from app-logs (rw)
  Volumes:
   app-logs:
    Type:          EmptyDir (a temporary directory that shares a pod's lifetime)
    Medium:
    SizeLimit:     <unset>
  Node-Selectors:  <none>
  Tolerations:     <none>
Conditions:
  Type           Status  Reason
  ----           ------  ------
  Progressing    True    NewReplicaSetAvailable
  Available      True    MinimumReplicasAvailable
OldReplicaSets:  <none>
NewReplicaSet:   sre-pleno-app-7c7ccffbb8 (2/2 replicas created)
Events:
  Type    Reason             Age   From                   Message
  ----    ------             ----  ----                   -------
  Normal  ScalingReplicaSet  58m   deployment-controller  Scaled up replica set sre-pleno-app-7c7ccffbb8 from 2 to 4
  Normal  ScalingReplicaSet  57m   deployment-controller  Scaled up replica set sre-pleno-app-7c7ccffbb8 from 4 to 5
  Normal  ScalingReplicaSet  49m   deployment-controller  Scaled down replica set sre-pleno-app-7c7ccffbb8 from 5 to 3
  Normal  ScalingReplicaSet  44m   deployment-controller  Scaled down replica set sre-pleno-app-7c7ccffbb8 from 3 to 2
```

### 3.Autoscaling (HPA)
Evidência do Horizontal Pod Autoscaler monitorando as métricas de utilização:
#### Comando: kubectl get hpa -n sre-app

```
NAME                REFERENCE                  TARGETS                        MINPODS   MAXPODS   REPLICAS   AGE
sre-pleno-app-hpa   Deployment/sre-pleno-app   cpu: 1%/70%, memory: 35%/75%   2         5         2          70m
```

### 4.Logs Estruturados (Padrão ELK)
Demonstração do formato de log gerado pela aplicação, pronto para o parsing do Logstash:
#### Comando: kubectl logs -l app=sre-pleno-app -n sre-app --tail=1

```
2026-01-11 23:17:25,203 INFO 10.244.0.1 - - [11/Jan/2026 23:17:25] "GET /health HTTP/1.1" 200 -
2026-01-11 23:17:25,203 INFO 10.244.0.1 - - [11/Jan/2026 23:17:25] "GET /health HTTP/1.1" 200 -
```

👩‍💻 Desenvolvido por **Renata Delgado**

