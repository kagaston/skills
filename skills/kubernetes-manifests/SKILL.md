---
name: kubernetes-manifests
description: Plain YAML Kubernetes manifest patterns including project layout, labeling conventions, Deployments, Services, ConfigMaps, Secrets, probes, resource limits, security contexts, and Namespace isolation. Use when writing Kubernetes manifests, deploying to K8s, structuring a k8s/ directory, or reviewing Kubernetes YAML.
---

# Kubernetes Manifests

Patterns for writing plain YAML Kubernetes manifests without Helm or Kustomize. Use these when you need simple, readable K8s configs that can be applied directly with `kubectl apply -f`.

## Project Layout

```
project-name/
├── k8s/
│   ├── namespace.yaml          # Namespace isolation
│   ├── configmap.yaml          # Non-secret configuration
│   ├── secret.yaml             # Sensitive values (gitignored or sealed)
│   ├── app-deployment.yaml     # Deployment + Service per component
│   ├── worker-deployment.yaml
│   └── ingress.yaml            # External access
├── docker-compose.yml          # Local dev (mirrors K8s topology)
├── justfile                    # k8s-apply, k8s-delete recipes
└── ...
```

Group related resources (Deployment + Service) in the same file separated by `---`. Keep ConfigMaps and Secrets in their own files so they can be updated independently.

## Namespace

Isolate project resources in a dedicated namespace:

```yaml
apiVersion: v1
kind: Namespace
metadata:
  name: my-app
  labels:
    app.kubernetes.io/part-of: my-app
```

All subsequent resources should reference this namespace in `metadata.namespace`.

## Labels

Use the standard `app.kubernetes.io/` label schema on every resource:

```yaml
metadata:
  labels:
    app.kubernetes.io/name: api-server
    app.kubernetes.io/component: backend
    app.kubernetes.io/part-of: my-app
    app.kubernetes.io/version: "1.2.3"
    app.kubernetes.io/managed-by: kubectl
```

| Label | Purpose |
|-------|---------|
| `app.kubernetes.io/name` | Component name (used by selectors) |
| `app.kubernetes.io/component` | Role within the system (frontend, backend, database, worker) |
| `app.kubernetes.io/part-of` | Top-level application name (groups all components) |
| `app.kubernetes.io/version` | Image or release version |
| `app.kubernetes.io/managed-by` | Deployment tool (kubectl, helm, argocd) |

Selectors should match on `app.kubernetes.io/name` at minimum.

## Deployments

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: api-server
  namespace: my-app
  labels:
    app.kubernetes.io/name: api-server
    app.kubernetes.io/part-of: my-app
spec:
  replicas: 2
  selector:
    matchLabels:
      app.kubernetes.io/name: api-server
  template:
    metadata:
      labels:
        app.kubernetes.io/name: api-server
        app.kubernetes.io/part-of: my-app
    spec:
      securityContext:
        runAsNonRoot: true
        runAsUser: 1000
        fsGroup: 1000
      containers:
        - name: api-server
          image: org/api-server:1.2.3
          ports:
            - name: http
              containerPort: 8000
          envFrom:
            - configMapRef:
                name: app-config
          env:
            - name: DATABASE_URL
              valueFrom:
                secretKeyRef:
                  name: app-secrets
                  key: database-url
            - name: POD_IP
              valueFrom:
                fieldRef:
                  fieldPath: status.podIP
          resources:
            requests:
              cpu: 100m
              memory: 128Mi
            limits:
              cpu: 500m
              memory: 512Mi
          readinessProbe:
            httpGet:
              path: /health
              port: http
            initialDelaySeconds: 5
            periodSeconds: 10
          livenessProbe:
            httpGet:
              path: /health
              port: http
            initialDelaySeconds: 15
            periodSeconds: 15
```

### Key Patterns

- **`envFrom` + `configMapRef`** -- inject all ConfigMap keys as env vars (bulk config)
- **`env` + `secretKeyRef`** -- inject individual secrets (selective, explicit)
- **`fieldRef`** -- inject pod metadata like `status.podIP` or `metadata.name`
- **Named ports** -- use `name: http` so probes and services reference the name, not the number

## Services

```yaml
apiVersion: v1
kind: Service
metadata:
  name: api-server
  namespace: my-app
  labels:
    app.kubernetes.io/name: api-server
    app.kubernetes.io/part-of: my-app
spec:
  type: ClusterIP
  selector:
    app.kubernetes.io/name: api-server
  ports:
    - name: http
      port: 8000
      targetPort: http
```

### Service Types

| Type | When to use |
|------|-------------|
| `ClusterIP` | Internal-only services (default). Other pods reach it by DNS name |
| `NodePort` | Expose on a static port on every node. Use for dev/testing or when no ingress controller |
| `LoadBalancer` | Cloud-managed external load balancer. Use in AWS/GCP/Azure for production |

Use `ClusterIP` by default. Expose user-facing services via `Ingress` or `NodePort`.

## ConfigMaps

Centralise non-secret configuration:

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: app-config
  namespace: my-app
  labels:
    app.kubernetes.io/part-of: my-app
data:
  LOG_LEVEL: "INFO"
  WORKER_COUNT: "4"
  CACHE_TTL: "300"
```

Pods reference it via `envFrom: [configMapRef: {name: app-config}]` or mount as a volume for file-based config.

## Secrets

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: app-secrets
  namespace: my-app
type: Opaque
stringData:
  database-url: "postgres://user:pass@db:5432/app"
  api-key: "sk-example"
```

NEVER commit Secrets with real values. Options:
- Use `stringData` with placeholder values and apply real values out-of-band
- Use Sealed Secrets or External Secrets Operator in production
- Add `k8s/secret.yaml` to `.gitignore` and provide a `k8s/secret.yaml.example`

## Health Probes

Three probe types prevent traffic to broken pods and restart stuck ones:

| Probe | Purpose | When it fails |
|-------|---------|---------------|
| `readinessProbe` | Should this pod receive traffic? | Pod removed from Service endpoints |
| `livenessProbe` | Is this pod alive? | Pod restarted |
| `startupProbe` | Has the app finished starting? | Liveness/readiness suspended until passes |

```yaml
startupProbe:
  httpGet:
    path: /health
    port: http
  failureThreshold: 30
  periodSeconds: 2

readinessProbe:
  httpGet:
    path: /health
    port: http
  initialDelaySeconds: 5
  periodSeconds: 10

livenessProbe:
  httpGet:
    path: /health
    port: http
  initialDelaySeconds: 15
  periodSeconds: 15
```

### Probe Methods

```yaml
# HTTP (most common for web services)
httpGet:
  path: /health
  port: 8000

# TCP (databases, message brokers)
tcpSocket:
  port: 5432

# Command (custom checks)
exec:
  command: ["pg_isready", "-U", "postgres"]
```

Use `startupProbe` for containers that take >15 seconds to start. This prevents the liveness probe from killing a slow-starting app.

## Resource Requests and Limits

Always set both. Requests guarantee minimum resources; limits prevent runaway consumption.

```yaml
resources:
  requests:
    cpu: 100m      # 0.1 CPU core
    memory: 128Mi  # 128 MiB
  limits:
    cpu: 500m      # 0.5 CPU core
    memory: 512Mi  # 512 MiB
```

| Guideline | Rule of thumb |
|-----------|---------------|
| CPU requests | Set to average usage |
| CPU limits | Set to 2-5x requests (or omit to avoid throttling) |
| Memory requests | Set to average usage |
| Memory limits | Set to peak usage. Exceeding this triggers OOMKilled |

### QoS Classes

| Class | When | Behaviour |
|-------|------|-----------|
| Guaranteed | requests == limits for all containers | Highest priority, last to be evicted |
| Burstable | requests < limits | Medium priority |
| BestEffort | No requests or limits set | First to be evicted under pressure |

## Security Context

Harden pods by restricting privileges:

```yaml
spec:
  securityContext:
    runAsNonRoot: true
    runAsUser: 1000
    fsGroup: 1000
  containers:
    - name: app
      securityContext:
        allowPrivilegeEscalation: false
        readOnlyRootFilesystem: true
        capabilities:
          drop: ["ALL"]
```

| Setting | What it does |
|---------|-------------|
| `runAsNonRoot: true` | Prevents running as root (fails if image USER is 0) |
| `readOnlyRootFilesystem: true` | Blocks writes to container filesystem (use volumes for writable paths) |
| `allowPrivilegeEscalation: false` | Prevents gaining more privileges than the parent process |
| `capabilities.drop: ["ALL"]` | Removes all Linux capabilities |

## Ingress

Expose services externally via an Ingress controller:

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: my-app
  namespace: my-app
  annotations:
    cert-manager.io/cluster-issuer: letsencrypt-prod
spec:
  ingressClassName: nginx
  tls:
    - hosts:
        - app.example.com
      secretName: app-tls
  rules:
    - host: app.example.com
      http:
        paths:
          - path: /
            pathType: Prefix
            backend:
              service:
                name: api-server
                port:
                  name: http
```

## justfile Recipes

```just
k8s-apply:
    kubectl apply -f k8s/

k8s-delete:
    kubectl delete -f k8s/

k8s-status:
    kubectl get all -n my-app

k8s-logs service="api-server":
    kubectl logs -f -l app.kubernetes.io/name={{service}} -n my-app

k8s-shell service="api-server":
    kubectl exec -it deploy/{{service}} -n my-app -- /bin/sh
```

## CI Validation

Lint and validate manifests in CI before applying:

```yaml
# GitHub Actions
jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Lint YAML
        run: pip install yamllint && yamllint k8s/

      - name: Validate manifests
        run: kubectl apply --dry-run=client -f k8s/

      - name: Scan for misconfigurations
        uses: aquasecurity/trivy-action@master
        with:
          scan-type: config
          scan-ref: k8s/
          severity: CRITICAL,HIGH
```

## Verification Checklist

- [ ] All resources in a dedicated Namespace
- [ ] `app.kubernetes.io/` labels on every resource
- [ ] Selectors match on `app.kubernetes.io/name`
- [ ] Deployments have readinessProbe and livenessProbe
- [ ] Resource requests and limits set on all containers
- [ ] Security context: `runAsNonRoot`, `readOnlyRootFilesystem`, drop ALL capabilities
- [ ] Secrets use `stringData` with placeholders (real values applied out-of-band)
- [ ] Services default to ClusterIP; NodePort/Ingress only for external access
- [ ] ConfigMaps separate from Secrets
- [ ] `just k8s-apply` and `just k8s-delete` recipes in justfile
- [ ] CI validates manifests with `kubectl apply --dry-run=client`
- [ ] YAML linted with yamllint
