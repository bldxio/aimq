# Docker & Kubernetes Deployment

This guide covers deploying AIMQ workers using Docker and Kubernetes for production environments.

## Overview

AIMQ provides two Docker deployment approaches:

1. **Local Development**: Generate project-specific Docker files with `aimq init --docker`
2. **Production**: Use the published AIMQ image with volume mounts or git URLs

## Local Development Setup

### Generate Docker Files

```bash
# Initialize with Docker files
aimq init --docker

# This creates:
# - Dockerfile (optimized for your project)
# - docker-compose.yml (with volume mounts)
# - .dockerignore
```

### Start with Docker Compose

```bash
# Start the worker
docker-compose up -d

# View logs
docker-compose logs -f

# Stop
docker-compose down
```

The generated `docker-compose.yml` mounts your local `tasks.py` and `.env` files, allowing for rapid development iteration.

---

## Production Deployment

### Using the Published Image

AIMQ publishes Docker images that can be used with two patterns:

#### Pattern 1: Volume Mount (Simple)

Mount your local `tasks.py` and `.env` files:

```bash
docker run --rm \
  -v $(pwd)/tasks.py:/app/tasks.py:ro \
  -v $(pwd)/.env:/app/.env:ro \
  aimq:latest
```

#### Pattern 2: Git Repository (Recommended for Production)

Load tasks from a git repository using environment variables:

```bash
# Default branch from GitHub
docker run --rm \
  -e AIMQ_TASKS=git:mycompany/aimq-tasks \
  -e SUPABASE_URL=https://xxx.supabase.co \
  -e SUPABASE_KEY=eyJ... \
  aimq:latest

# Specific branch or tag
docker run --rm \
  -e AIMQ_TASKS=git:mycompany/aimq-tasks@production \
  -e SUPABASE_URL=https://xxx.supabase.co \
  -e SUPABASE_KEY=eyJ... \
  aimq:latest

# Monorepo subdirectory
docker run --rm \
  -e AIMQ_TASKS=git:mycompany/monorepo#services/worker \
  -e SUPABASE_URL=https://xxx.supabase.co \
  -e SUPABASE_KEY=eyJ... \
  aimq:latest
```

### Git URL Patterns

AIMQ supports npm-style git URLs:

- `git:user/repo` - Default branch from GitHub
- `git:user/repo@branch` - Specific branch or tag
- `git:user/repo#path/to/tasks` - Subdirectory in monorepo
- `git:gitlab.com/user/repo@v1.0.0` - Full URL with version tag

### Git Authentication

**For private repositories:**

#### HTTPS with Token (Quick Setup)
```bash
docker run --rm \
  -e AIMQ_TASKS=git:mycompany/private-repo@main \
  -e GIT_USERNAME=myuser \
  -e GIT_PASSWORD=ghp_your_github_token \
  aimq:latest
```

#### SSH (Recommended for Production)
```bash
docker run --rm \
  -v ~/.ssh:/home/aimq/.ssh:ro \
  -e AIMQ_TASKS=git:mycompany/private-repo@main \
  -e AIMQ_USE_SSH=true \
  aimq:latest
```

---

## Docker Compose Examples

### Production with Git Repository

```yaml
version: '3.8'

services:
  aimq-worker:
    image: aimq:latest
    environment:
      - AIMQ_TASKS=git:mycompany/aimq-tasks@production
      - SUPABASE_URL=${SUPABASE_URL}
      - SUPABASE_KEY=${SUPABASE_KEY}
      - WORKER_NAME=aimq-worker
      - WORKER_LOG_LEVEL=info
      - OPENAI_API_KEY=${OPENAI_API_KEY}
    restart: unless-stopped
    # For private repos with SSH:
    # volumes:
    #   - ~/.ssh:/home/aimq/.ssh:ro
```

### Local Development with Volume Mounts

```yaml
version: '3.8'

services:
  aimq-worker:
    image: aimq:latest
    volumes:
      - ./tasks.py:/app/tasks.py:ro
      - ./.env:/app/.env:ro
    restart: unless-stopped
```

---

---

## Kubernetes Deployment

### Basic Deployment with Git URL

Minimal production-ready Kubernetes deployment using git URLs:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: aimq-worker
  namespace: default
spec:
  replicas: 3  # Scale based on workload
  selector:
    matchLabels:
      app: aimq-worker
  template:
    metadata:
      labels:
        app: aimq-worker
    spec:
      containers:
        - name: aimq-worker
          image: aimq:latest
          imagePullPolicy: Always
          env:
            # Load tasks from git repository
            - name: AIMQ_TASKS
              value: "git:mycompany/aimq-tasks@production"

            # Supabase configuration
            - name: SUPABASE_URL
              valueFrom:
                secretKeyRef:
                  name: aimq-secrets
                  key: supabase-url
            - name: SUPABASE_KEY
              valueFrom:
                secretKeyRef:
                  name: aimq-secrets
                  key: supabase-key

            # Worker configuration
            - name: WORKER_NAME
              valueFrom:
                fieldRef:
                  fieldPath: metadata.name
            - name: WORKER_LOG_LEVEL
              value: "info"

            # AI Provider Keys (optional)
            - name: OPENAI_API_KEY
              valueFrom:
                secretKeyRef:
                  name: aimq-secrets
                  key: openai-api-key
                  optional: true

          resources:
            requests:
              cpu: "500m"
              memory: "1Gi"
            limits:
              cpu: "2"
              memory: "4Gi"

          # Graceful shutdown
          lifecycle:
            preStop:
              exec:
                command: ["/bin/sh", "-c", "sleep 15"]

      restartPolicy: Always
```

### Create Kubernetes Secret

```bash
kubectl create secret generic aimq-secrets \
  --from-literal=supabase-url='https://xxx.supabase.co' \
  --from-literal=supabase-key='your-service-key' \
  --from-literal=openai-api-key='sk-...'
```

### For Private Git Repositories

If using private git repositories with SSH:

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: git-ssh-key
type: Opaque
data:
  ssh-privatekey: <base64-encoded-ssh-key>
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: aimq-worker
spec:
  # ... (same as above)
  template:
    spec:
      containers:
        - name: aimq-worker
          # ... (same as above)
          env:
            - name: AIMQ_TASKS
              value: "git:mycompany/private-repo@main"
            - name: AIMQ_USE_SSH
              value: "true"
          volumeMounts:
            - name: ssh-key
              mountPath: /home/aimq/.ssh
              readOnly: true
      volumes:
        - name: ssh-key
          secret:
            secretName: git-ssh-key
            defaultMode: 0400
```

---

## Environment Variables Reference

| Variable | Description | Required | Default |
|----------|-------------|----------|---------|
| `AIMQ_TASKS` | Path or git URL to tasks.py | No | `./tasks.py` |
| `AIMQ_USE_SSH` | Use SSH for git operations | No | `false` |
| `SUPABASE_URL` | Supabase project URL | Yes | - |
| `SUPABASE_KEY` | Supabase API key | Yes | - |
| `WORKER_NAME` | Worker instance name | No | `peon` |
| `WORKER_LOG_LEVEL` | Logging level | No | `info` |
| `WORKER_IDLE_WAIT` | Seconds to wait when idle | No | `10.0` |
| `OPENAI_API_KEY` | OpenAI API key (optional) | No | - |
| `MISTRAL_API_KEY` | Mistral API key (optional) | No | - |
| `LANGCHAIN_TRACING_V2` | Enable LangChain tracing | No | `false` |
| `LANGCHAIN_API_KEY` | LangChain API key | No | - |

---

## Production Best Practices

### Scaling

Run multiple worker instances for parallel processing:

```bash
# Scale deployment
kubectl scale deployment aimq-worker --replicas=5

# Or use HorizontalPodAutoscaler
kubectl autoscale deployment aimq-worker \
  --min=2 --max=10 --cpu-percent=70
```

### GitOps Workflow

1. Store tasks in version-controlled git repositories
2. Use git tags/branches for versioning (e.g., `@v1.0.0`, `@production`)
3. Update deployment by changing the git reference
4. Workers automatically pull latest code on restart

### Monitoring

Add health checks using file-based probes (no additional dependencies required):

```yaml
# In container spec
livenessProbe:
  exec:
    command:
      - python3
      - -c
      - |
        import os, time
        probe_file = '/tmp/aimq-health'
        if not os.path.exists(probe_file):
            exit(1)
        age = time.time() - os.path.getmtime(probe_file)
        exit(0 if age < 60 else 1)  # Fail if file not updated in 60s
  initialDelaySeconds: 30
  periodSeconds: 10
  timeoutSeconds: 5
  failureThreshold: 3

readinessProbe:
  exec:
    command:
      - python3
      - -c
      - |
        import os
        exit(0 if os.path.exists('/tmp/aimq-health') else 1)
  initialDelaySeconds: 5
  periodSeconds: 5
  timeoutSeconds: 3
  failureThreshold: 2
```

**Important**: Your application must manage the health probe file. Add this to your worker code:

```python
# In your tasks.py or worker setup
import threading
import time
from pathlib import Path

def health_check_writer():
    """Update health check file periodically."""
    probe_file = Path("/tmp/aimq-health")
    while True:
        probe_file.touch()
        time.sleep(10)  # Update every 10 seconds

# Start health check thread
health_thread = threading.Thread(target=health_check_writer, daemon=True)
health_thread.start()
```

**Alternative: Install procps for pgrep-based probes**

If you prefer process-based checks, add to your Dockerfile:

```dockerfile
FROM python:3.12-slim
RUN apt-get update && apt-get install -y --no-install-recommends procps && rm -rf /var/lib/apt/lists/*
# ... rest of Dockerfile
```

Then use:

```yaml
livenessProbe:
  exec:
    command: ["pgrep", "-f", "aimq"]
  initialDelaySeconds: 30
  periodSeconds: 10
```

**Note**: The file-based probe is recommended as it's lightweight, doesn't require additional packages, and provides more granular health status.

### Resource Limits

Set appropriate limits based on AI model requirements:

- **Light tasks** (text processing): 500m CPU, 1Gi memory
- **OCR processing**: 1 CPU, 2Gi memory
- **Heavy AI models**: 2+ CPU, 4Gi+ memory

### Security

1. **Use Secrets**: Never hardcode credentials in manifests
2. **SSH Keys**: Use volume mounts for private git repos
3. **Read-only mounts**: Mount tasks.py and SSH keys as read-only
4. **Network Policies**: Restrict traffic to Supabase only
5. **Service Accounts**: Use Kubernetes service accounts for cloud provider auth

---

## Troubleshooting

### Git Clone Fails
```bash
# Check git URL format
echo $AIMQ_TASKS
# Should be: git:user/repo[@branch][#subdir]

# Enable debug logging
kubectl set env deployment/aimq-worker WORKER_LOG_LEVEL=debug

# View logs
kubectl logs -f deployment/aimq-worker
```

### Tasks Not Found
```bash
# For volume mounts, ensure path is correct
kubectl exec -it deployment/aimq-worker -- ls -la /app/tasks.py

# For git URLs, check subdirectory path
# git:user/repo#correct/path/to/tasks.py
```

### Supabase Connection Errors
```bash
# Verify environment variables
kubectl exec -it deployment/aimq-worker -- env | grep SUPABASE

# Test connectivity
kubectl exec -it deployment/aimq-worker -- curl $SUPABASE_URL
```

---

## Next Steps

- Review the [Configuration Guide](../getting-started/configuration.md) for all options
- See the [Quick Start Guide](../getting-started/quickstart.md) for local testing
