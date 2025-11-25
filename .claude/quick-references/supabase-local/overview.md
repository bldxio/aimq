# Supabase Local Development - Overview

Quick reference for getting started with Supabase local development.

## What is Supabase Local Development?

Supabase CLI provides a complete local development environment that mirrors your production setup:

- **PostgreSQL database** - Full-featured database with extensions
- **PostgREST API** - Auto-generated REST API from your schema
- **Realtime server** - WebSocket connections for live updates
- **Storage server** - File storage and management
- **Auth server** - Authentication and authorization
- **Studio** - Web UI for database management

## Initial Setup

### 1. Install Supabase CLI

```bash
# macOS
brew install supabase/tap/supabase

# Linux/WSL
curl -fsSL https://raw.githubusercontent.com/supabase/cli/main/install.sh | sh

# Verify installation
supabase --version
```

### 2. Initialize Project

```bash
# Initialize Supabase in your project
supabase init

# This creates:
# - supabase/config.toml
# - supabase/seed.sql
# - supabase/.gitignore
```

### 3. Start Local Services

```bash
# Start all Supabase services
supabase start

# Services started:
# - PostgreSQL database
# - PostgREST API
# - Realtime server
# - Storage server
# - Auth server
# - Studio (web UI)
```

### 4. Access Services

```bash
# View service URLs and credentials
supabase status

# Example output:
# API URL: http://127.0.0.1:54321
# DB URL: postgresql://postgres:postgres@127.0.0.1:54322/postgres
# Studio URL: http://127.0.0.1:54323
# anon key: eyJhbGc...
# service_role key: eyJhbGc...
```

## Common Commands

```bash
# Start services
supabase start

# Stop services
supabase stop

# Restart services
supabase stop && supabase start

# View status
supabase status

# View logs
supabase logs

# Reset database (destructive!)
supabase db reset

# Access database shell
supabase db shell
```

## Quick Links

- [@configuration.md](./configuration.md) - Port configuration and settings
- [@migrations.md](./migrations.md) - Database migrations
- [@troubleshooting.md](./troubleshooting.md) - Common issues
- [@integration.md](./integration.md) - AIMQ integration

## Related

- [@../supabase-local-setup.md](../supabase-local-setup.md) - Original comprehensive guide (archived)
- [@../../patterns/database-migration-wrappers.md](../../patterns/database-migration-wrappers.md) - Migration patterns
- [@../precommit-troubleshooting.md](../precommit-troubleshooting.md) - Pre-commit hooks

## Resources

- [Supabase CLI Docs](https://supabase.com/docs/guides/cli)
- [Local Development Guide](https://supabase.com/docs/guides/cli/local-development)
- [Supabase GitHub](https://github.com/supabase/supabase)
