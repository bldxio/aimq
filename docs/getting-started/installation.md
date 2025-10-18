# Installation

AIMQ provides multiple installation options to suit different workflows, from zero-installation quick start to traditional package management.

## Option 1: Using uvx (Recommended for Quick Start)

The fastest way to get started with AIMQ requires no installation:

```bash
# Run any AIMQ command directly
uvx aimq init my-project
uvx aimq start
uvx aimq send my-queue '{"message": "hello"}'
```

**Pros:** No installation, no virtual environments, no dependency conflicts
**Cons:** Slower first run (packages are cached for subsequent runs)

## Option 2: Install as a Tool (Recommended for Regular Use)

Install AIMQ as a persistent tool using uv:

```bash
# Install uv if you haven't already
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install aimq as a tool
uv tool install aimq

# Now you can use aimq directly
aimq init my-project
aimq start
```

**Pros:** Fast, isolated from other Python projects, easy to upgrade
**Cons:** Requires uv installation

## Option 3: Traditional pip Install

```bash
pip install aimq
```

**Pros:** Works with any Python environment
**Cons:** May conflict with other package versions

## Option 4: Development Setup

For contributing to AIMQ or building from source:

```bash
# Clone the repository
git clone https://github.com/bldxio/aimq.git
cd aimq

# Install dependencies from lockfile (production)
uv sync

# For development (includes test/dev tools)
uv sync --group dev

# Run from source
uv run aimq start
```

### Key uv Commands for Development

```bash
# Add a new dependency
uv add requests

# Add to dev dependency group
uv add --group dev pytest

# Remove a dependency
uv remove requests

# Update dependencies
uv lock --upgrade

# Run commands in the uv environment
uv run python -m aimq.worker
uv run pytest
```

## Requirements

- **Python:** 3.11, 3.12, or 3.13
- **Operating System:** Linux, macOS, or Windows

## Main Dependencies

AIMQ has the following main dependencies (automatically installed):

- **easyocr**: For OCR capabilities
- **supabase**: For queue and storage management
- **langchain**: For AI model integration
- **pydantic**: For data validation and settings management
- **torch**: For machine learning models

## Configuration

After installation, you'll need to configure your Supabase credentials. The easiest way is to use `aimq init`:

```bash
# Initialize a new project (creates .env.example)
aimq init my-project
cd my-project

# Copy and configure
cp .env.example .env
# Edit .env with your Supabase credentials
```

Or create a `.env` file manually:

```bash
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-service-role-key
```

## Verifying Installation

You can verify your installation by running:

```bash
# Using uvx
uvx aimq --version

# Using uv tool install
aimq --version

# Using pip
aimq --version
```

This should display the version number of your AIMQ installation.
