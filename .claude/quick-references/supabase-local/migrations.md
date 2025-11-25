# Supabase Local Development - Migrations

Database migration workflows for Supabase local development.

## Creating Migrations

### Create Migration File

```bash
# Create new migration file
supabase migration new setup_aimq

# This creates:
# supabase/migrations/YYYYMMDDHHMMSS_setup_aimq.sql
```

### Write Migration

```sql
-- supabase/migrations/20251123021000_setup_aimq.sql

-- Enable extensions
create extension if not exists "pgmq" with schema "pgmq";

-- Create schemas
create schema if not exists pgmq_public;
grant usage on schema pgmq_public to authenticated;

-- Create functions
create or replace function pgmq_public.send(
    queue_name text,
    message jsonb,
    sleep_seconds integer default 0
)
  returns setof bigint
  language plpgsql
as $$
begin
    return query
    select * from pgmq.send(
        queue_name := queue_name,
        msg := message,
        delay := sleep_seconds
    );
end;
$$;
```

## Applying Migrations

### Apply All Migrations

```bash
# Apply all pending migrations
supabase db reset

# Or apply specific migration
supabase migration up

# Check migration status
supabase migration list
```

### Rollback Migrations

```bash
# Rollback last migration
supabase migration down

# Rollback to specific migration
supabase migration down --version 20251123021000
```

## Seed Data

### Create Seed File

Edit `supabase/seed.sql`:

```sql
-- Insert test data
insert into users (email, name) values
    ('test@example.com', 'Test User'),
    ('admin@example.com', 'Admin User');

-- Create test queues
select pgmq_public.create_queue('test-queue');
select pgmq_public.send('test-queue', '{"test": true}'::jsonb);
```

### Apply Seed Data

```bash
# Reset database and apply seed
supabase db reset

# Or apply seed only
psql $DATABASE_URL -f supabase/seed.sql
```

## Common Tasks

### Reset Database

```bash
# Reset to clean state and apply all migrations + seed
supabase db reset

# Confirm with 'y' when prompted
```

### Access Database

```bash
# Connect with psql
supabase db psql

# Or use connection string
psql postgresql://postgres:postgres@127.0.0.1:64322/postgres

# Run SQL file
supabase db psql -f script.sql
```

### Generate Types

```bash
# Generate TypeScript types from database schema
supabase gen types typescript --local > types/supabase.ts

# Generate Python types (if using supabase-py)
# (Manual process - inspect schema and create models)
```

## Migration Best Practices

### Writing Migrations

1. **Use idempotent operations** - `CREATE IF NOT EXISTS`, `DROP IF EXISTS`
2. **Test locally first** - Always test migrations before pushing
3. **Keep migrations small** - One logical change per migration
4. **Add comments** - Explain why, not just what
5. **Handle data carefully** - Backup before destructive changes

### Migration Workflow

1. **Create migration** - `supabase migration new <name>`
2. **Write SQL** - Add your schema changes
3. **Test locally** - `supabase db reset`
4. **Verify changes** - Check Studio or psql
5. **Commit migration** - Add to version control
6. **Deploy** - Push to remote when ready

### Common Patterns

```sql
-- Enable extension
create extension if not exists "extension_name" with schema "schema_name";

-- Create schema
create schema if not exists schema_name;
grant usage on schema schema_name to authenticated;

-- Create table
create table if not exists table_name (
    id bigint primary key generated always as identity,
    created_at timestamptz default now()
);

-- Create function
create or replace function function_name()
  returns void
  language plpgsql
as $$
begin
    -- function body
end;
$$;

-- Create index
create index if not exists idx_name on table_name (column_name);

-- Grant permissions
grant select, insert, update, delete on table_name to authenticated;
```

## Troubleshooting

### Migration Fails

```bash
# Check migration status
supabase migration list

# View error details
supabase logs postgres

# Reset and try again
supabase db reset
```

### Schema Conflicts

```bash
# Check current schema
supabase db psql -c "\dn"

# Check tables
supabase db psql -c "\dt schema_name.*"

# Drop and recreate
supabase stop --no-backup
supabase start
```

## Related

- [@overview.md](./overview.md) - Getting started
- [@configuration.md](./configuration.md) - Configuration
- [@troubleshooting.md](./troubleshooting.md) - Common issues
- [@../../patterns/database-migration-wrappers.md](../../patterns/database-migration-wrappers.md) - Migration patterns
- [@../../architecture/database-schema-migration.md](../../architecture/database-schema-migration.md) - Migration strategies

## Resources

- [Supabase Migrations Guide](https://supabase.com/docs/guides/cli/local-development#database-migrations)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
