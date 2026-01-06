# SRE Test – Aplicação com Kubernetes, HPA e Observabilidade

## 📌 Visão Geral

Este projeto demonstra a implementação completa de uma aplicação containerizada com **Docker**, orquestrada em **Kubernetes**, com **autoscaling (HPA)** e **observabilidade usando Prometheus e Grafana**.

O objetivo é simular um ambiente próximo de produção, aplicando boas práticas esperadas de um **SRE Pleno**: confiabilidade, escalabilidade, monitoramento e troubleshooting.

---

## 🧰 Stack Utilizada

* **Python 3.11**
* **FastAPI**
* **Uvicorn**
* **Docker**
* **Kubernetes (Minikube)**
* **Helm**
* **Prometheus**
* **Grafana**

---

## 📂 Estrutura do Projeto

```
sre-test-pleno/
├── app/
│   ├── main.py
│   ├── requirements.txt
├── k8s/
│   ├── deployment.yaml
│   ├── service.yaml
│   ├── hpa.yaml
├── Dockerfile
└── README.md
```

---

## 🚀 Como Executar Localmente (Docker)

```bash
docker build -t sre-pleno-app .
docker run -p 8080:8080 sre-pleno-app
```

Acesse:

* [http://localhost:8080/health](http://localhost:8080/health)

---

## ☸️ Kubernetes (Minikube)

### 1️⃣ Subir o cluster

```bash
minikube start --driver=docker --memory=6000 --cpus=4
```

### 2️⃣ Usar o Docker do Minikube

```bash
eval $(minikube docker-env)
docker build -t sre-pleno-app:latest .
```

### 3️⃣ Aplicar manifests

```bash
kubectl apply -f k8s/
```

### 4️⃣ Acessar a aplicação

```bash
kubectl port-forward svc/sre-pleno-app 8080:80
```

---

## ❤️ Healthchecks

* **/health** → Liveness Probe
* **/ready** → Readiness Probe

Esses endpoints garantem que o Kubernetes só direcione tráfego para pods saudáveis.

---

## 📈 Autoscaling (HPA)

### Habilitar Metrics Server

```bash
minikube addons enable metrics-server
```

### Aplicar HPA

```bash
kubectl apply -f k8s/hpa.yaml
```

### Testar escalabilidade

```bash
kubectl run load-generator \
  --image=busybox \
  --restart=Never \
  --command -- sh -c "while true; do wget -q -O- http://sre-pleno-app.default.svc.cluster.local; done"
```

Verifique:

```bash
kubectl get hpa
kubectl get pods
```

---

## 📊 Observabilidade (Prometheus + Grafana)

### Instalação via Helm

```bash
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo update

kubectl create namespace monitoring

helm install monitoring prometheus-community/kube-prometheus-stack \
  --namespace monitoring
```

### Acessar Grafana

```bash
kubectl port-forward -n monitoring svc/monitoring-grafana 3000:80
```

Acesse: [http://localhost:3000](http://localhost:3000)

Credenciais:

```bash
kubectl get secret monitoring-grafana -n monitoring \
  -o jsonpath="{.data.admin-user}" | base64 --decode

kubectl get secret monitoring-grafana -n monitoring \
  -o jsonpath="{.data.admin-password}" | base64 --decode
```

---

## 📊 Dashboards Recomendados

* Kubernetes / Compute Resources / Pod
* Kubernetes / Deployment
* Kubernetes / Horizontal Pod Autoscaler

---

## 🧠 Decisões Técnicas

* **ClusterIP** para comunicação interna
* **Requests e Limits** para previsibilidade de recursos
* **HPA baseado em CPU** para escalabilidade automática
* **Prometheus + Grafana** para observabilidade completa

---

## ✅ Conclusão

Este projeto demonstra a construção de uma aplicação resiliente, escalável e observável em Kubernetes, seguindo práticas modernas de SRE.

---

👩‍💻 Desenvolvido por **Renata Delgado**
