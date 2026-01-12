# 📑 Relatório Técnico Detalhado – SRE Challenge (Pleno)

## 1. Introdução e Escopo do Projeto

Este documento detalha a implementação do projeto sre-test-pleno, desenvolvido para o desafio técnico de SRE. O foco principal foi a criação de um ecossistema orquestrado que garante observabilidade total, escalabilidade dinâmica e resiliência, utilizando a filosofia de Infrastructure as Code (IaC).

## 2. Arquitetura da Solução e Decisões de Design

### 2.1 Camada de Aplicação (FastAPI)

**Framework:** Optou-se pelo FastAPI pela sua performance assíncrona e suporte nativo a health checks.

**Saúde e Prontidão:** Implementação de endpoints /health (Liveness) e /ready (Readiness) para gestão inteligente do ciclo de vida dos pods.

### 2.2 Estratégia de Containerização (Docker)

**Multi-stage Build:** Técnica aplicada para garantir imagens leves (baseadas em python:3.11-slim) e seguras, eliminando ferramentas de build do ambiente de execução.

**Segurança (Hardening):** Execução com utilizador não-privilegiado (USER appuser), reduzindo a superfície de ataque.

### 2.3 Orquestração e Resiliência (Kubernetes)

**Gestão de Recursos:** Definição rigorosa de requests e limits (CPU/Memória) para evitar o erro de OOMKilled.

**Self-Healing:** Configuração de Probes para reinício automático em caso de falhas críticas.

## 3. Diário de Bordo: Dificuldades Enfrentadas e Debugs Realizados

Demonstrar a capacidade de diagnóstico foi parte fundamental do processo:

### 3.1 Correção do Metrics Server e HPA

**Dificuldade:** O HPA exibia o consumo de CPU como <unknown>.

**Debug:** Através de kubectl logs no namespace kube-system, identifiquei que o Metrics Server não comunicava com os nós devido a certificados auto-assinados.

**Resolução:** Reconfiguração do addon do Minikube com as flags de segurança adequadas para permitir a monitorização de recursos.

### 3.2 Parsing de Logs com Grok (ELK)

**Dificuldade:** Os logs eram ingeridos como texto bruto, impedindo a análise de latência.

**Debug:** Utilizei o Grok Debugger e testes no stdout do Logstash para ajustar o padrão de regex.

**Resolução:** Criação de um pipeline que extrai level, endpoint e latency (convertendo este último para integer), permitindo dashboards de performance reais.

### 3.3 Conetividade do Filebeat

***Dificuldade:** Falha na leitura dos logs no caminho /var/log/pods.

**Debug:** O kubectl describe pod revelou problemas de permissões no mount do volume.

**Resolução:** Ajuste do SecurityContext no DaemonSet do Filebeat para garantir acesso de leitura aos logs do host.

### 3.4 Refinamento de Probes e Readiness

**Dificuldade:** Identifiquei via logs (kubectl logs) que o Kubernetes estava recebendo erros 404 no endpoint /ready.

**Debug:** Percebi uma inconsistência entre o manifesto do Kubernetes e as rotas implementadas na aplicação FastAPI.

**Resolução:** Unifiquei os endpoints de Liveness e Readiness para /health e realizei um novo rollout. O resultado foi uma estabilização imediata dos logs, com 100% das requisições retornando HTTP 200, garantindo que o Load Balancer apenas envie tráfego para Pods totalmente operacionais.

## 4. Observabilidade e Escalabilidade (O que foi entregue)

### 4.1 Métricas (Prometheus & Grafana)

**Service Discovery:** Implementado via Kubernetes Annotations, permitindo que o Prometheus encontre a aplicação automaticamente sem intervenção manual.

### 4.2 Logs (ELK Stack)

**Fluxo:** Filebeat (coleta) -> Logstash (filtro/parsing) -> Elasticsearch (armazenamento) -> Kibana (visualização).

### 4.3 Escalabilidade (HPA)

**Validação:** Teste de carga realizado com load-generator. O sistema escalou de 2 para 5 réplicas ao atingir 70% de CPU, comprovando a eficácia da configuração de auto-scaling.

## 5. Evolução e Melhoria Contínua

O projeto foi desenhado para ser expansível, com os seguintes próximos passos planeados:

### 5.1 Implementação de OpenTelemetry (OTel)

A inclusão do OpenTelemetry será um aditivo de valor à stack atual (Prometheus/ELK):

**Tracing Distribuído:** Adicionar rastreio de ponta a ponta para visualizar o fluxo das requisições entre serviços e base de dados.

**Unificação de Sinais:** Utilizar o OTel Collector como um gateway único para receber métricas e traces, podendo exportar simultaneamente para o Prometheus e para ferramentas de tracing como o Jaeger.

**Contextualização:** Correlacionar um log específico (do ELK) com um trace ID (do OTel), reduzindo drasticamente o tempo de diagnóstico (MTTR).

### 5.2 Eficiência de Recursos e FinOps

**Justificativa de Requests/Limits:** A definição cuidadosa dos recursos (requests de 100m de CPU e 128Mi de memória) não foi apenas para estabilidade, mas para otimização de custos. Ao definir Requests baixos, permitimos uma maior densidade de Pods por Nó no cluster, reduzindo o gasto com infraestrutura.

**HPA como Ferramenta de Economia:** O uso do Autoscaling garante que só pagaremos por 5 réplicas durante picos de tráfego. Em horários de baixa demanda, o sistema retorna para 2 réplicas, evitando o desperdício de recursos ociosos.

### 5.3 Segurança e Automação

**Network Policies:** Implementação de isolamento de rede L3/L4 entre namespaces.

**GitOps:** Integração com ArgoCD para garantir que o cluster reflita sempre o estado do repositório.

## 6. Conclusão

Este projeto reflete o compromisso com a Engenharia de Confiabilidade. Mais do que uma aplicação funcional, entregou-se um ecossistema documentado, resiliente e preparado para a integração de tecnologias modernas como o OpenTelemetry.

Autora: **Renata Delgado**