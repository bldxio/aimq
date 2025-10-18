# AIMQ Docker Deployment Guide

This directory contains the Dockerfile and build scripts for publishing the AIMQ worker image. The published image is designed for flexible deployment where users provide their own `tasks.py` via volume mount or git repository.

---

## 📦 Using the Published Image

The AIMQ image is published to support two deployment patterns:

### 1️⃣ Volume Mount (Local Development)

Mount your local `tasks.py` and `.env` files:

```bash
docker run --rm \
  -v $(pwd)/tasks.py:/app/tasks.py:ro \
  -v $(pwd)/.env:/app/.env:ro \
  aimq:latest
```

### 2️⃣ Git Repository (Production)

Load tasks from a git repository using environment variables:

```bash
# Default branch
docker run --rm \
  -e AIMQ_TASKS=git:mycompany/aimq-tasks \
  -e SUPABASE_URL=https://... \
  -e SUPABASE_KEY=... \
  aimq:latest

# Specific branch
docker run --rm \
  -e AIMQ_TASKS=git:mycompany/aimq-tasks@production \
  -e SUPABASE_URL=https://... \
  -e SUPABASE_KEY=... \
  aimq:latest

# Monorepo subdirectory
docker run --rm \
  -e AIMQ_TASKS=git:mycompany/monorepo#services/worker \
  -e SUPABASE_URL=https://... \
  -e SUPABASE_KEY=... \
  aimq:latest
```

### 🔐 Git Authentication

For private repositories:

**HTTPS with token:**
```bash
# GitHub Personal Access Token
docker run --rm \
  -e AIMQ_TASKS=git:mycompany/private-repo@main \
  -e GIT_ASKPASS=/bin/echo \
  -e GIT_USERNAME=myuser \
  -e GIT_PASSWORD=ghp_... \
  aimq:latest
```

**SSH (recommended for production):**
```bash
docker run --rm \
  -v ~/.ssh:/home/aimq/.ssh:ro \
  -e AIMQ_TASKS=git:mycompany/private-repo@main \
  -e AIMQ_USE_SSH=true \
  aimq:latest
```

---

## 🏗️ Building the Image Locally

### Prerequisites
- [Docker](https://docs.docker.com/get-docker/) installed and running

### Build Script

Use the provided `build.sh` script:

```bash
cd docker
./build.sh [TAG]
```

- Default tag: `local` → builds `aimq:local`
- Custom tag: `./build.sh dev` → builds `aimq:dev`

### Script Help

```bash
./build.sh --help
```

---

## 🤖 CI/CD Workflow (GitHub Actions)

Automated builds are handled by GitHub Actions.

### Tagging Strategy

| Environment      | Tag Format                      | Published | Use Case        |
|------------------|---------------------------------|-----------|-----------------|
| Local            | `aimq:local`                    | No        | Local dev       |
| Feature Branch   | `aimq:feature-<branch>-<sha>`   | Optional  | Ephemeral/QA    |
| Development      | `aimq:dev-<sha>`                | Yes       | Dev/Staging     |
| Production       | `aimq:latest`, `aimq:<version>` | Yes       | Production      |

### Example Workflow

The CI/CD workflow:
1. Authenticates with the container registry
2. Determines the tag based on branch/tag
3. Builds and pushes using `docker-build-push.sh`

```yaml
- name: Set image tag
  run: |
    if [[ "$GITHUB_REF" == refs/tags/* ]]; then
      TAG="${GITHUB_REF##*/}"
    else
      BRANCH=$(echo "${GITHUB_REF#refs/heads/}" | tr '/' '-')
      SHORT_SHA="${GITHUB_SHA::7}"
      TAG="${BRANCH}-${SHORT_SHA}"
    fi
    echo "TAG=$TAG" >> $GITHUB_ENV
```

---

## 🔧 Development vs Published Image

**This directory (`/docker/`)** builds the **published image**:
- Builds AIMQ from source during CI/CD (ensures version consistency)
- Uses `uv sync --frozen` for reproducible builds from lockfile
- Designed for users deploying AIMQ workers
- Supports volume mount and git URL patterns

**Why build from source in CI/CD?**
The Docker image is built alongside the package release in the CI/CD pipeline. Building from source ensures the Docker image contains the exact same code version being published to PyPI, avoiding version mismatch issues.

**For local development** (contributing to AIMQ itself):
- Use `aimq init --docker` to generate deployment files in your project
- Or use `uv run aimq start` directly without Docker

---

## 📝 Environment Variables

The published image supports these environment variables:

| Variable              | Description                                  | Example                           |
|-----------------------|----------------------------------------------|-----------------------------------|
| `AIMQ_TASKS`          | Path or git URL to tasks.py                  | `git:user/repo@branch`            |
| `AIMQ_USE_SSH`        | Use SSH for git operations (default: false)  | `true`                            |
| `SUPABASE_URL`        | Supabase project URL                         | `https://xxx.supabase.co`         |
| `SUPABASE_KEY`        | Supabase anon/service key                    | `eyJ...`                          |
| `WORKER_NAME`         | Worker instance name                         | `aimq-worker-1`                   |
| `WORKER_LOG_LEVEL`    | Logging level                                | `info`, `debug`, `warning`        |
| `OPENAI_API_KEY`      | OpenAI API key (optional)                    | `sk-...`                          |
| `MISTRAL_API_KEY`     | Mistral API key (optional)                   | `...`                             |

---

## 🐳 Docker Compose Example

For production deployments with git repositories:

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
      - OPENAI_API_KEY=${OPENAI_API_KEY}
    restart: unless-stopped
    # For SSH git access:
    # volumes:
    #   - ~/.ssh:/home/aimq/.ssh:ro
```

For local development with volume mounts:

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

## 🚨 Troubleshooting

### Git clone fails
- Check git URL format: `git:user/repo[@branch][#subdir]`
- For private repos, ensure authentication is configured
- Enable verbose logging: `-e WORKER_LOG_LEVEL=debug`

### tasks.py not found
- With volume mount: ensure path is correct `$(pwd)/tasks.py`
- With git URL: check subdirectory path `git:user/repo#correct/path`

### Supabase connection errors
- Verify `SUPABASE_URL` and `SUPABASE_KEY` are set
- Check network connectivity from container

---

For questions or improvements, feel free to open an issue or PR!
