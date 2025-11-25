# Supabase Local Development - Configuration

Configuration guide for Supabase local development environment.

## Port Configuration

### Default Ports

Supabase uses these default ports:

| Service | Default Port | Purpose |
|---------|--------------|---------|
| API (PostgREST) | 54321 | REST API endpoint |
| Database | 54322 | PostgreSQL connection |
| Studio | 54323 | Web UI dashboard |
| Shadow DB | 54320 | Migration testing |
| Pooler | 54329 | Connection pooling |

### Changing Ports

**Why change ports?**
- Avoid conflicts with other Supabase projects
- Avoid conflicts with other services
- Run multiple projects simultaneously
- Team conventions

**How to change:**

Edit `supabase/config.toml`:

```toml
[api]
port = 64321  # Changed from 54321

[db]
port = 64322  # Changed from 54322
shadow_port = 64320  # Changed from 54320

[db.pooler]
port = 64329  # Changed from 54329

[studio]
port = 64323  # Changed from 54323
```

**Port selection strategy:**
- Use a consistent range (e.g., 64xxx for project A, 65xxx for project B)
- Document port assignments in README
- Check for conflicts before starting

### Check for Port Conflicts

```bash
# Check if port is in use (macOS/Linux)
lsof -i :64321

# Check all Supabase ports
for port in 64320 64321 64322 64323 64329; do
    echo "Port $port:"
    lsof -i :$port
done

# Kill process using a port
lsof -ti :64321 | xargs kill -9
```

## Project Settings

### config.toml Configuration

Edit `supabase/config.toml`:

```toml
# Project identifier (used for local development)
project_id = "aimq"  # Change from default "examples"

[api]
enabled = true
port = 64321
# Expose custom schemas in API
schemas = ["public", "graphql_public", "pgmq_public"]
# Additional schemas for custom extensions
extra_search_path = ["public", "extensions"]

[db]
port = 64322
major_version = 15  # PostgreSQL version

[studio]
enabled = true
port = 64323
api_url = "http://127.0.0.1"
# Optional: OpenAI API key for Supabase AI features
openai_api_key = "env(OPENAI_API_KEY)"

[auth]
enabled = true
# Configure auth providers, email templates, etc.
```

### Environment Variables

Create `.env.local`:

```bash
# Supabase connection
SUPABASE_URL=http://127.0.0.1:64321
SUPABASE_ANON_KEY=eyJhbGc...
SUPABASE_SERVICE_ROLE_KEY=eyJhbGc...

# Database connection
DATABASE_URL=postgresql://postgres:postgres@127.0.0.1:64322/postgres

# Optional: OpenAI for Supabase AI
OPENAI_API_KEY=sk-...
```

**Get keys from:**
```bash
supabase status
```

## Best Practices

### Configuration Management

1. **Use environment variables** for sensitive data
2. **Document custom ports** in project README
3. **Keep config.toml in version control** (no secrets!)
4. **Use .env.local for local overrides** (gitignored)
5. **Validate configuration** after changes

### Port Management

1. **Choose consistent port ranges** per project
2. **Document port assignments** for team
3. **Check for conflicts** before starting
4. **Use higher ports** (60000+) to avoid system conflicts

### Schema Configuration

1. **Expose only necessary schemas** in API
2. **Use extra_search_path** for extensions
3. **Keep public schema clean** for API
4. **Use custom schemas** for internal functions

## Related

- [@overview.md](./overview.md) - Getting started
- [@migrations.md](./migrations.md) - Database migrations
- [@troubleshooting.md](./troubleshooting.md) - Common issues
- [@../../architecture/database-schema-patterns.md](../../architecture/database-schema-patterns.md) - Schema design

## Resources

- [Supabase Config Reference](https://supabase.com/docs/guides/cli/config)
- [Local Development Guide](https://supabase.com/docs/guides/cli/local-development)
