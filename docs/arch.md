> Target-state architecture. MVP subset: see [mvp-scope.md](./mvp-scope.md).

flowchart LR

%% =========================
%% CLIENTS
%% =========================
subgraph CLIENTS["Tenant Users & Sources"]
    WEB["Tenant Web App<br/>chat, search, admin UI"]
    UPLOAD["Document Upload<br/>PDF, TXT, Markdown"]
    CONNECTORS["External Connectors<br/>SharePoint, Confluence,<br/>Google Drive, S3, Jira"]
    ADMIN["Tenant Admin<br/>users, roles, quotas"]
end

%% =========================
%% EDGE & IDENTITY
%% =========================
subgraph EDGE["Edge & Identity"]
    CF["CloudFront + WAF"]
    APIGW["API Gateway<br/>tenant-scoped REST"]
    COGNITO["Cognito<br/>SSO / OIDC / JWT"]
    AUTHZ["Tenant Authorizer<br/>RBAC + tenant isolation"]
end

WEB --> CF --> APIGW
UPLOAD --> APIGW
ADMIN --> AUTHZ
CONNECTORS --> AUTHZ
APIGW --> COGNITO --> AUTHZ

%% =========================
%% APPLICATION SERVICES
%% =========================
subgraph APP["Application Services - ECS Fargate"]
    CHAT["Chat & Search Service<br/>Python + FastAPI"]
    INGEST["Ingestion Service<br/>parse, chunk, embed, index"]
    CONNSVC["Connector Sync Service<br/>scheduled crawl + delta sync"]
    ADMINSVC["Tenant Admin Service<br/>onboarding, quotas, audit"]
end

APIGW --> CHAT
APIGW --> INGEST
AUTHZ --> CONNSVC
AUTHZ --> ADMINSVC
CONNSVC --> INGEST

%% =========================
%% ASYNC INGESTION
%% =========================
subgraph ASYNC["Async Ingestion Pipeline"]
    S3RAW["S3 Document Lake<br/>original docs + versions"]
    QUEUE["SQS / EventBridge"]
    WORKERS["Ingestion Workers<br/>parse → normalize → chunk → embed → index"]
    DLQ["Dead Letter Queue"]
end

INGEST --> S3RAW
S3RAW --> QUEUE
QUEUE --> WORKERS
QUEUE -. failed .-> DLQ

%% =========================
%% AI / BEDROCK
%% =========================
subgraph AI["Amazon Bedrock"]
    EMBED["Titan Embeddings"]
    LLM1["Claude"]
    LLM2["Nova / Fallback Model"]
    GUARD["Bedrock Guardrails<br/>PII / safety filters"]
end

WORKERS --> EMBED

%% =========================
%% DATA
%% =========================
subgraph DATA["Tenant-Isolated Data Layer"]
    PG["PostgreSQL / RDS<br/>tenants, users, documents,<br/>ACLs, quotas, jobs, audit"]
    VECTOR["Qdrant / OpenSearch<br/>tenant_id + document_id + ACL metadata"]
    REDIS["Redis / ElastiCache<br/>cache, rate limit, sessions"]
end

WORKERS --> VECTOR
WORKERS --> PG
ADMINSVC --> PG
CHAT --> PG
CHAT --> REDIS

%% =========================
%% RAG PIPELINE
%% =========================
subgraph RAG["RAG Query Pipeline"]
    INPUTG["Input Guardrails<br/>PII / prompt injection"]
    ROUTER["Intent / Query Router<br/>RAG / direct / tool"]
    REWRITE["Query Rewriter"]
    RETRIEVE["Hybrid Retrieval<br/>vector + keyword<br/>tenant + ACL filter"]
    RERANK["Reranker<br/>Cohere / custom"]
    CONTEXT["Context Builder<br/>trim / dedupe / citations"]
    MODELROUTER["Model Router<br/>quality / cost / latency"]
    OUTPUTG["Output Guardrails"]
    CITE["Citation Validator"]
    RESPONSE["Structured Response<br/>Pydantic"]
end

CHAT --> INPUTG --> ROUTER
ROUTER --> REWRITE --> RETRIEVE
RETRIEVE --> VECTOR
RETRIEVE --> RERANK --> CONTEXT --> MODELROUTER
MODELROUTER --> GUARD
GUARD --> LLM1
GUARD --> LLM2
LLM1 --> OUTPUTG
LLM2 --> OUTPUTG
OUTPUTG --> CITE --> RESPONSE
RESPONSE --> CHAT

%% =========================
%% OBSERVABILITY
%% =========================
subgraph OBS["Observability & Evaluation"]
    LANGFUSE["Langfuse<br/>traces, evals, prompts,<br/>cost, latency"]
    OTEL["OpenTelemetry"]
    CLOUDWATCH["CloudWatch"]
    PROM["Prometheus"]
    GRAFANA["Grafana"]
    LOKI["Loki"]
end

CHAT -. traces .-> LANGFUSE
RETRIEVE -. retrieval spans .-> LANGFUSE
RERANK -. rerank spans .-> LANGFUSE
MODELROUTER -. generation spans .-> LANGFUSE
CHAT -. telemetry .-> OTEL
OTEL --> CLOUDWATCH
OTEL --> PROM
PROM --> GRAFANA
CHAT -. logs .-> LOKI

%% =========================
%% RELIABILITY
%% =========================
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

%% =========================
%% MULTI TENANCY
%% =========================
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