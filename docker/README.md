# Docker Build & CI/CD Workflow

This directory contains scripts and documentation for building and publishing Docker images for the `aimq` project. This guide covers both local development and automated CI/CD workflows, following industry best practices for tagging and promoting images from feature branches to production.

---

## 🚀 Local Development

### Prerequisites
- [Docker](https://docs.docker.com/get-docker/) installed and running.

### Local Build Script
Use the provided `build.sh` script to build the Docker image for your local machine. This does **not** push the image to any registry.

```sh
cd docker
./build.sh [tag]
```
- If you omit `[tag]`, it defaults to `local` (image will be tagged as `aimq:local`).
- Example: `./build.sh dev`

---

## 🤖 CI/CD Workflow (GitHub Actions)

Automated builds and pushes are handled by GitHub Actions in `.github/workflows/docker-build-push.yml`.

### Tagging Strategy
| Stage            | Tag Format                      | Registry Publish | Use Case                |
|------------------|---------------------------------|------------------|-------------------------|
| Local            | `aimq:local`                    | No               | Local dev/testing       |
| Feature Branch   | `aimq:feature-<branch>-<sha>`   | Optional         | Ephemeral/QA            |
| Dev              | `aimq:dev-<sha>`                | Yes              | Dev/Staging             |
| Production       | `aimq:latest`, `aimq:<version>` | Yes              | Prod                    |

- **Feature branches**: Images are tagged with the branch name and commit SHA. Optionally pushed for review apps.
- **Dev branch**: Images are tagged as `dev-<sha>`, always pushed to the registry.
- **Main/production**: Images are tagged as `latest` and/or with a semantic version.

### Example Workflow Steps

The workflow:
- Sets up Docker authentication (using secrets for registry login)
- Determines the correct tag based on branch or tag
- Builds and pushes the image using `docker-build-push.sh`

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

- name: Build and push Docker image
  run: |
    chmod +x ./docker/docker-build-push.sh
    ./docker/docker-build-push.sh "$REGISTRY" "$REPOSITORY" "$IMAGE_NAME" "$TAG"
```

---

## 🛠️ What the Scripts Do
- **build.sh**: Builds the Docker image locally for development/testing.
- **docker-build-push.sh**: Used in CI/CD to build and push images to your container registry.

---

## 📝 Notes
- If you see an authentication error, make sure you have logged into your registry and that `~/.docker/config.json` exists.
- For DigitalOcean, use [`doctl`](https://docs.digitalocean.com/reference/doctl/) for authentication.
- The scripts are safe to run locally or in CI/CD pipelines.

---

For questions or improvements, feel free to open an issue or PR!
