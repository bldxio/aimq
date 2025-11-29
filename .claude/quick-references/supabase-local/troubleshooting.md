# Supabase Local Development - Troubleshooting

Common issues and solutions for Supabase local development.

## Services Won't Start

### Check Port Conflicts

```bash
# Check for port conflicts
lsof -i :64321
lsof -i :64322

# Kill conflicting process
lsof -ti :64321 | xargs kill -9
```

### Check Docker

```bash
# Check Docker is running
docker ps

# Restart Docker if needed
# (Use Docker Desktop or system commands)
```

### Clean Restart

```bash
# View detailed logs
supabase logs

# Clean restart
supabase stop --no-backup
supabase start
```

## Migration Errors

### Check Migration Syntax

```bash
# Check migration syntax
cat supabase/migrations/YYYYMMDDHHMMSS_name.sql

# Test migration in isolation
supabase db reset
supabase migration up

# View migration history
supabase migration list
```

### Rollback Migration

```bash
# Rollback (manual - create new migration to undo)
supabase migration new rollback_feature

# Write SQL to undo changes
# Then apply:
supabase db reset
```

## Connection Issues

### Verify Services

```bash
# Verify services are running
supabase status

# Test database connection
psql postgresql://postgres:postgres@127.0.0.1:64322/postgres -c "SELECT 1"

# Test API connection
curl http://127.0.0.1:64321/rest/v1/

# Check firewall/network settings
```

### Connection Refused

**Symptoms:**
- `Connection refused` errors
- Services show as running but can't connect

**Solutions:**
1. Check ports in `config.toml` match your connection strings
2. Verify Docker containers are running: `docker ps`
3. Check firewall isn't blocking ports
4. Try `127.0.0.1` instead of `localhost`

## Extension Issues

### Check Extensions

```bash
# List installed extensions
supabase db psql -c "SELECT * FROM pg_extension"

# Install extension manually
supabase db psql -c "CREATE EXTENSION IF NOT EXISTS pgmq"

# Check extension schema
supabase db psql -c "\dx+ pgmq"
```

### Extension Not Found

**Symptoms:**
- `extension "pgmq" does not exist`
- Extension fails to install

**Solutions:**
1. Check extension is available in your PostgreSQL version
2. Verify extension name spelling
3. Try installing with schema: `CREATE EXTENSION pgmq WITH SCHEMA pgmq`
4. Check Supabase CLI version: `supabase --version`

## Performance Issues

### Slow Queries

```bash
# Enable query logging
supabase db psql -c "ALTER SYSTEM SET log_statement = 'all'"
supabase db psql -c "SELECT pg_reload_conf()"

# View slow queries
supabase logs postgres | grep "duration:"

# Check indexes
supabase db psql -c "\di"
```

### High Memory Usage

```bash
# Check Docker resource limits
docker stats

# Adjust in Docker Desktop settings
# Or in config.toml:
# [db]
# shared_buffers = "256MB"
# effective_cache_size = "1GB"
```

## Data Issues

### Seed Data Fails

```bash
# Check seed file syntax
cat supabase/seed.sql

# Test seed in isolation
supabase db reset

# Check for foreign key violations
supabase logs postgres | grep "violates foreign key"
```

### Data Not Persisting

**Symptoms:**
- Data disappears after restart
- Seed data not applied

**Solutions:**
1. Use `supabase stop` (not `--no-backup`) to preserve data
2. Check seed.sql is being applied: `supabase db reset`
3. Verify migrations are applied: `supabase migration list`

## Common Error Messages

### "PGRST202"

**Error:** `{"code":"PGRST202","message":"Could not find the public schema"}`

**Solution:**
```bash
# Apply migrations
supabase db reset

# Or create schema manually
supabase db psql -c "CREATE SCHEMA IF NOT EXISTS public"
```

### "relation does not exist"

**Error:** `relation "table_name" does not exist`

**Solution:**
```bash
# Check migrations are applied
supabase migration list

# Apply migrations
supabase db reset

# Verify table exists
supabase db psql -c "\dt"
```

### "permission denied for schema"

**Error:** `permission denied for schema schema_name`

**Solution:**
```sql
-- Add to migration
GRANT USAGE ON SCHEMA schema_name TO authenticated;
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA schema_name TO authenticated;
```

## Best Practices

### 1. Use Migrations for Schema Changes

```bash
# ❌ Don't: Manually edit database via Studio
# ✅ Do: Create migration
supabase migration new add_users_table
```

### 2. Keep Seed Data Idempotent

```sql
-- ❌ Bad: Will fail on second run
insert into users (id, email) values (1, 'test@example.com');

-- ✅ Good: Idempotent
insert into users (id, email) values (1, 'test@example.com')
on conflict (id) do nothing;

-- ✅ Better: Use truncate in seed
truncate users cascade;
insert into users (email) values ('test@example.com');
```

### 3. Document Port Changes

Keep port assignments documented in your README:

```markdown
## Local Development Ports

- API: 64321
- Database: 64322
- Studio: 64323
```

### 4. Regular Cleanup

```bash
# Weekly cleanup
supabase stop --no-backup
supabase start

# Remove unused Docker resources
docker system prune
```

## Getting Help

### Check Logs

```bash
# All logs
supabase logs

# Specific service
supabase logs postgres
supabase logs api
supabase logs realtime
```

### Debug Mode

```bash
# Enable debug logging
export SUPABASE_DEBUG=1
supabase start
```

### Community Resources

- [Supabase Discord](https://discord.supabase.com/)
- [GitHub Issues](https://github.com/supabase/supabase/issues)
- [Stack Overflow](https://stackoverflow.com/questions/tagged/supabase)

## Related

- [@overview.md](./overview.md) - Getting started
- [@configuration.md](./configuration.md) - Configuration
- [@migrations.md](./migrations.md) - Database migrations
- [@../precommit-troubleshooting.md](../precommit-troubleshooting.md) - Pre-commit issues

## Resources

- [Supabase CLI Troubleshooting](https://supabase.com/docs/guides/cli/troubleshooting)
- [PostgreSQL Error Codes](https://www.postgresql.org/docs/current/errcodes-appendix.html)
