# MVP Scoping Document — ContextForge

`docs/arch.md` = target-state architecture. This doc = what ships in MVP vs later.

## Goal

Prove core loop: tenant uploads docs → ingested → user chats/searches → grounded, cited answer. Multi-tenant isolation from day one (hard to retrofit). Everything else deferred.

## In Scope (MVP)

| Area | Included |
|---|---|
| Clients | Web App (chat, search, basic admin), Document Upload |
| Edge/Identity | CloudFront+WAF, API Gateway, Cognito, Tenant Authorizer |
| App Services | Chat & Search Service, Ingestion Service, minimal Tenant Admin Service |
| Async Ingestion | S3 Document Lake, SQS, Ingestion Workers (parse→chunk→embed→index), DLQ |
| AI | Titan Embeddings, LLM(s) via Bedrock (Claude + Nova fallback), Bedrock Guardrails |
| Data | PostgreSQL (tenants/users/docs/ACL/jobs), one vector store (pick Qdrant OR OpenSearch, not both), Redis (session+rate-limit+cache) |
| RAG Pipeline | Input Guardrails, Query Router (RAG-only, no tool/direct branch), Query Rewriter, Retrieval (vector+ACL filter), Reranker (Cohere/custom), Context Builder, Model Router (quality/cost/latency), Output Guardrails, Citation Validator |
| Observability | Langfuse (traces/evals), CloudWatch, Prometheus + Grafana, Loki |
| Reliability | Timeouts, Retry+Backoff, Idempotency (ingestion), Circuit Breaker, Bulkheads, Rate Limiting, Model Fallback |
| Multi-tenancy | tenant_id in JWT, service-level authz, DB scoping, vector tenant filter, doc-level ACL, per-tenant quotas/budgets enforced |

## Out of Scope (Phase 2+)

- **Connectors**: SharePoint, Confluence, Google Drive, S3, Jira sync — MVP is manual upload only
- **Direct/tool-call intent branch in Router** — RAG-only responses

## Open Risks

- Single vector store choice (Qdrant vs OpenSearch) blocks ingestion worker + retrieval work — decide before sprint start
- Reranker + Model Router + full reliability suite (circuit breaker/bulkheads) add real build time — biggest scope risk to MVP timeline, watch closely
- No connector sync means demo/pilot tenants must hand-upload docs
- Quota enforcement at MVP adds an extra guard path in Chat/Ingest — verify it doesn't block legit early pilot usage (soft-limit + alert before hard block)

## MVP Architecture (subset of docs/arch.md)

```mermaid
flowchart LR

subgraph CLIENTS["Tenant Users"]
    WEB["Web App<br/>chat, search, admin"]
    UPLOAD["Document Upload"]
end

subgraph EDGE["Edge & Identity"]
    CF["CloudFront + WAF"]
    APIGW["API Gateway"]
    COGNITO["Cognito"]
    AUTHZ["Tenant Authorizer<br/>RBAC + tenant isolation"]
end

WEB --> CF --> APIGW
UPLOAD --> APIGW
APIGW --> COGNITO --> AUTHZ

subgraph APP["Application Services"]
    CHAT["Chat & Search Service"]
    INGEST["Ingestion Service"]
    ADMINSVC["Tenant Admin Service<br/>onboarding, basic audit"]
end

APIGW --> CHAT
APIGW --> INGEST
AUTHZ --> ADMINSVC

subgraph ASYNC["Async Ingestion"]
    S3RAW["S3 Document Lake"]
    QUEUE["SQS"]
    WORKERS["Ingestion Workers<br/>parse→chunk→embed→index"]
    DLQ["Dead Letter Queue"]
end

INGEST --> S3RAW --> QUEUE --> WORKERS
QUEUE -. failed .-> DLQ

subgraph AI["Amazon Bedrock"]
    EMBED["Titan Embeddings"]
    LLM1["Claude"]
    LLM2["Nova / Fallback Model"]
    GUARD["Bedrock Guardrails"]
end

WORKERS --> EMBED

subgraph DATA["Tenant-Isolated Data"]
    PG["PostgreSQL"]
    VECTOR["Vector Store<br/>(Qdrant or OpenSearch)"]
    REDIS["Redis<br/>cache, rate-limit, sessions"]
end

WORKERS --> VECTOR
WORKERS --> PG
ADMINSVC --> PG
CHAT --> PG
CHAT --> REDIS

subgraph RAG["RAG Query Pipeline"]
    INPUTG["Input Guardrails"]
    ROUTER["Query Router (RAG-only)"]
    REWRITE["Query Rewriter"]
    RETRIEVE["Hybrid Retrieval<br/>tenant + ACL filter"]
    RERANK["Reranker<br/>Cohere / custom"]
    CONTEXT["Context Builder"]
    MODELROUTER["Model Router<br/>quality / cost / latency"]
    OUTPUTG["Output Guardrails"]
    CITE["Citation Validator"]
    RESPONSE["Structured Response"]
end

CHAT --> INPUTG --> ROUTER --> REWRITE --> RETRIEVE
RETRIEVE --> VECTOR
RETRIEVE --> RERANK --> CONTEXT --> MODELROUTER --> GUARD
GUARD --> LLM1
GUARD --> LLM2
LLM1 --> OUTPUTG
LLM2 --> OUTPUTG
OUTPUTG --> CITE --> RESPONSE
RESPONSE --> CHAT

subgraph OBS["Observability"]
    LANGFUSE["Langfuse"]
    OTEL["OpenTelemetry"]
    CLOUDWATCH["CloudWatch"]
    PROM["Prometheus"]
    GRAFANA["Grafana"]
    LOKI["Loki"]
end

CHAT -. traces .-> LANGFUSE
RETRIEVE -. spans .-> LANGFUSE
RERANK -. spans .-> LANGFUSE
MODELROUTER -. spans .-> LANGFUSE
CHAT -. telemetry .-> OTEL
OTEL --> CLOUDWATCH
OTEL --> PROM
PROM --> GRAFANA
CHAT -. logs .-> LOKI

subgraph REL["Reliability Patterns"]
    TIMEOUT["Timeouts"]
    RETRY["Retry + Backoff + Jitter"]
    CB["Circuit Breaker"]
    RL["Rate Limiting"]
    IDEM["Idempotency"]
    BULK["Bulkheads"]
    FALLBACK["Model Fallback"]
end

CHAT -.-> TIMEOUT
CHAT -.-> RETRY
CHAT -.-> CB
CHAT -.-> RL
INGEST -.-> IDEM
MODELROUTER -.-> FALLBACK
WORKERS -.-> BULK

subgraph TENANCY["Multi-Tenancy Rules"]
    JWT["tenant_id in JWT"]
    SERVICEISO["Service-level tenant authorization"]
    DBISO["PostgreSQL tenant scoping"]
    VECISO["Vector search mandatory tenant filter"]
    ACL["Document-level ACL"]
    QUOTA["Per-tenant quotas / budgets"]
end

COGNITO --> JWT --> SERVICEISO
SERVICEISO --> DBISO
SERVICEISO --> VECISO
SERVICEISO --> ACL
SERVICEISO --> QUOTA
VECISO --> VECTOR
DBISO --> PG
QUOTA --> PG
```
