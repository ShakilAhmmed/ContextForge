# ops

## docker (local dev)

One-time setup — self-signed cert + `/etc/hosts` entry (nginx serves `contextforge.local`, not `localhost`, so the cert's CN matches):

```
cd ops/docker
./certs/gen-certs.sh
echo "127.0.0.1 contextforge.local" | sudo tee -a /etc/hosts
```

Then:

```
cp .env.example .env
docker compose up --build
```

Serves via nginx at `https://contextforge.local:8443/` (port 8080 redirects to 8443 — HTTP_PORT/HTTPS_PORT in `.env`, change if those are taken too). nginx proxies to the FastAPI `api` container; `api`'s entrypoint runs `alembic upgrade head` before starting uvicorn.

The cert is self-signed, so the browser will warn on first visit — expected in dev, click through (or trust `ops/docker/certs/dev.crt` locally). `dev.crt`/`dev.key` are gitignored; regenerate with `gen-certs.sh` after cloning.

## k8s

Manifests in `ops/k8s`, applied in order (numeric prefix):

```
kubectl apply -f ops/k8s/00-namespace.yaml
kubectl apply -f ops/k8s/01-postgres-secret.yaml
kubectl apply -f ops/k8s/02-postgres.yaml
kubectl apply -f ops/k8s/02b-redis.yaml
kubectl apply -f ops/k8s/02c-minio.yaml
kubectl apply -f ops/k8s/02d-elasticmq.yaml
kubectl apply -f ops/k8s/03-api-configmap.yaml
kubectl apply -f ops/k8s/03b-api-secret.yaml
kubectl apply -f ops/k8s/07-migrate-job.yaml
kubectl wait --for=condition=complete job/migrate -n contextforge
kubectl apply -f ops/k8s/04-api.yaml
kubectl apply -f ops/k8s/05-nginx-configmap.yaml
kubectl apply -f ops/k8s/06-nginx.yaml
```

- `01-postgres-secret.yaml`, `02c-minio.yaml`'s `minio-secret`, `03-api-configmap.yaml`, and `03b-api-secret.yaml` ship demo credentials/JWT secret — replace with a real secrets manager before any shared/staging cluster. In production, `S3_ENDPOINT_URL`/`SQS_ENDPOINT_URL` point at real AWS S3/SQS instead of MinIO/ElasticMQ — same client code, just different endpoint + credentials.
- `contextforge-api:latest` must point at an image built from the root `Dockerfile` and pushed to a registry your cluster can pull from.
- `06-nginx.yaml` Service is `LoadBalancer` — swap for `ClusterIP` + Ingress if the cluster doesn't support LB provisioning.
