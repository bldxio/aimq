# AIMQ Worker: Docker & Kubernetes Deployment Guide

## Overview

This project provides a Python-based worker for processing jobs from queues, designed for robust deployment in Docker and Kubernetes environments. The worker uses a modular, extensible design and is compatible with modern orchestration and CI/CD workflows.

---

## Project Structure

- `src/aimq/worker.py`: Core worker logic and entrypoint.
- `docker/Dockerfile`: Docker build instructions.
- `.dockerignore`: Keeps your Docker image clean.
- `examples/`: Example task definitions and usage patterns.

---

## Docker Usage

### Build the Image

```bash
cd docker
bash build.sh
```

This will create a Docker image named `aimq:local`.

### Run the Worker Container

```bash
docker run --rm -it aimq:local
```

- The container runs the worker using `python -m aimq.worker`, following Python and Docker best practices.
- All dependencies are installed with Poetry during the build, but Poetry is not required at runtime.

---

## Code Entrypoint

**`src/aimq/worker.py`** defines a `main()` function:
```python
def main():
    worker = Worker()
    # TODO: Register tasks/queues here if needed
    worker.start()

if __name__ == "__main__":
    main()
```
- This allows the worker to be started as a module: `python -m aimq.worker`.

---

## Task Registration

To add processing logic, use the `@worker.task()` decorator:

```python
def main():
    worker = Worker()

    @worker.task()
    def echo_task(data: dict):
        print("Received:", data)
        return data

    worker.start()
```
- See `examples/` for more advanced patterns and integrations (e.g., Supabase).

---

## Kubernetes-Ready

- The container uses a minimal, production-grade Python base image.
- Entrypoint and signal handling are compatible with Kubernetes pod lifecycle.
- For production, add readiness/liveness probes as needed.

---

## Development vs. Production

- **Development:** Use `poetry run python ...` for local testing.
- **Production:** The Docker image runs with `python -m aimq.worker` for reliability and simplicity.

---

## Next Steps

- Register your actual processing tasks in `main()` in `worker.py`.
- Configure environment variables and secrets as needed for your deployment.
- For CI/CD and Kubernetes manifests, see `.github/workflows/` and adapt as required.

---

## Example: Kubernetes Deployment Manifest

Below is a minimal, production-ready Kubernetes manifest for deploying the AIMQ worker. Adjust image, resource requests, and environment variables as needed.

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: aimq-worker
spec:
  replicas: 1
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
          image: aimq:local  # Use your registry/image:tag in production
          imagePullPolicy: IfNotPresent
          env:
            # Example environment variables
            - name: SUPABASE_URL
              value: "https://your-supabase-url"
            - name: SUPABASE_KEY
              valueFrom:
                secretKeyRef:
                  name: supabase-secrets
                  key: service-role-key
          resources:
            requests:
              cpu: "250m"
              memory: "256Mi"
            limits:
              cpu: "1"
              memory: "1Gi"
          # Optional: Graceful shutdown for Kubernetes
          lifecycle:
            preStop:
              exec:
                command: ["/bin/sh", "-c", "sleep 10"]
      restartPolicy: Always
```

**Best Practices:**
- Use secrets for sensitive values (see `env` section above).
- Set resource requests/limits for predictable scheduling.
- Add readiness/liveness probes if your worker exposes an HTTP endpoint.
- Use `imagePullPolicy: Always` if pulling from a remote registry.
- Adjust `replicas` and labels as needed for your workload.

---
