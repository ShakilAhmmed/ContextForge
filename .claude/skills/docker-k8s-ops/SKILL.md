---
name: docker-k8s-ops
description: Run, verify, and tear down this repo's Docker Compose dev stack or Kubernetes manifests (nginx TLS termination, FastAPI api, Postgres, Redis). Use when starting/testing the local stack, adding a new service/env var to compose or k8s, changing the Dockerfile, or deploying to Kubernetes.
---

# Docker & Kubernetes Ops

## Local dev stack (Docker Compose)

One-time setup:
```
cd ops/docker
./certs/gen-certs.sh
echo '127.0.0.1 contextforge.local' | sudo tee -a /etc/hosts
cp .env.example .env
```

Run:
```
docker compose up --build -d
```

Serves at `https://contextforge.local:${HTTPS_PORT:-8443}/` (HTTP port redirects to HTTPS). Self-signed cert — use `curl -k` or accept the browser warning. `api`'s container entrypoint (`ops/docker/entrypoint.sh`) runs `alembic upgrade head` automatically before `uvicorn` starts — don't run migrations manually against this stack.

Services: `postgres`, `redis`, `api` (built from the root `Dockerfile`), `nginx` (reverse proxy + TLS, config in `ops/nginx/nginx.conf`).

**Always verify with real requests, not just "containers are Up".** Standard check sequence:
```
curl -sk --resolve contextforge.local:8443:127.0.0.1 https://contextforge.local:8443/health
```
Build an array for `--resolve`/other multi-word flags (`R=(--resolve host:port:ip)`, then `"${R[@]}"`) — a quoted string variable containing spaces breaks curl's option parsing silently.

**Always tear down after verifying**, unless the user asked you to leave it running:
```
docker compose down -v
```

## Adding a new service or env var

1. New service → add to `ops/docker/docker-compose.yml` with a `healthcheck`, and gate `api`'s `depends_on` on `condition: service_healthy` if `api` needs it at startup.
2. New env var → add to `ops/docker/.env.example` (compose auto-loads `.env` from its own directory) **and** the corresponding K8s `ConfigMap` (`ops/k8s/03-api-configmap.yaml`) or, if sensitive, a `Secret` (`ops/k8s/03b-api-secret.yaml`) — never put a credential/token in the ConfigMap.
3. Rebuild and re-verify with real curl checks before considering it done.

## Kubernetes

Manifests in `ops/k8s/`, numerically prefixed for apply order (`kubectl apply -f` on a whole directory sorts alphabetically, so the prefix enforces the real dependency order — namespace → secrets → postgres/redis → api → nginx). Full apply sequence and notes on swapping `nginx`'s `LoadBalancer` Service for `ClusterIP`+Ingress: [ops/README.md](../../ops/README.md).

Migrations in K8s run via the one-shot `ops/k8s/07-migrate-job.yaml` `Job` — apply it and `kubectl wait --for=condition=complete job/migrate` **before** rolling out `04-api.yaml`, rather than relying on every API replica racing the same `alembic upgrade head` in its entrypoint.

`contextforge-api:latest` in the manifests must point at an image actually pushed to a registry the cluster can pull — the manifests don't build it.

## Dockerfile changes

Root `Dockerfile` is multi-stage (`builder` compiles wheels with build deps, `runtime` is slim, non-root `appuser`). Add a new Python dependency to `pyproject.toml`, not directly to the Dockerfile — the `builder` stage installs from `pyproject.toml`. Rebuild and hit `/health` (and any new/changed endpoint) through the full compose stack before calling a Dockerfile change done — a build succeeding is not the same as the app actually serving traffic correctly.
