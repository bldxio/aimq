# Database Schema Migration and Testing

> **Status**: Active
> **Last Updated**: 2025-11-20
> **Category**: architecture

## Overview

Strategies for testing database schema organization and migrating existing projects to use the three-schema pattern.

## Testing

### Test Schema Isolation

```python
def test_private_function_not_accessible():
    """Private functions should not be callable via RPC"""
    with pytest.raises(Exception) as exc:
        supabase.rpc('aimq.notify_job_enqueued', {})
    assert "does not exist" in str(exc.value)

def test_public_function_accessible():
    """Public functions should be callable via RPC"""
    result = supabase.rpc('create_queue', {'queue_name': 'test'})
    assert result.data['success'] is True
```

### Test Access Control

```python
def test_schema_permissions():
    """Verify schema access is properly configured"""
    # pgmq_public should be accessible
    result = supabase.rpc('list_queues', {})
    assert isinstance(result.data, list)

    # aimq should not be accessible
    with pytest.raises(Exception):
        supabase.schema('aimq').rpc('setup_queue_trigger', {})
```

### Test Function Behavior

```python
def test_wrapper_function():
    """Test that wrapper functions work correctly"""
    # Send message via public wrapper
    result = supabase.rpc('send', {
        'queue_name': 'test',
        'message': {'data': 'test'}
    })
    assert result.data is not None

    # Verify message in storage schema
    messages = supabase.rpc('pop', {'queue_name': 'test'})
    assert messages.data[0]['message']['data'] == 'test'
```

### Test Trigger Setup

```python
def test_realtime_trigger():
    """Test that realtime triggers are set up correctly"""
    # Enable realtime
    result = supabase.rpc('enable_queue_realtime', {
        'queue_name': 'test'
    })
    assert result.data['success'] is True

    # Verify trigger exists
    triggers = supabase.rpc('list_queues', {})
    test_queue = next(q for q in triggers.data if q['queue_name'] == 'test')
    assert test_queue['realtime_enabled'] is True
```

## Migration Strategy

### Adding Schema Organization to Existing Project

#### Step 1: Create New Schemas

```sql
-- Create new schemas
create schema if not exists pgmq_public;
create schema if not exists aimq;

-- Grant appropriate access
grant usage on schema pgmq_public to postgres, anon, authenticated, service_role;
grant usage on schema aimq to postgres, service_role;
```

#### Step 2: Move Public Functions

Create new functions in `pgmq_public`, keep old ones for compatibility:

```sql
-- New function in pgmq_public
create or replace function pgmq_public.send(
    queue_name text,
    message jsonb,
    sleep_seconds integer default 0
)
  returns setof bigint
  language plpgsql
  set search_path = ''
as $$
begin
    return query
    select *
    from pgmq.send(
        queue_name := queue_name,
        msg := message,
        delay := sleep_seconds
    );
end;
$$;

grant execute on function pgmq_public.send to authenticated, service_role;

-- Keep old function for backward compatibility
create or replace function public.send_message(...)
  -- Calls pgmq_public.send internally
$$;
```

#### Step 3: Move Private Functions

```sql
-- Move internal functions to aimq schema
create or replace function aimq.notify_job_enqueued()
  returns trigger
  language plpgsql
  security definer
  set search_path = ''
as $$
begin
    perform pg_notify(
        'aimq:jobs',
        json_build_object('event', 'job_enqueued')::text
    );
    return NEW;
end;
$$;

-- Update triggers to use new function
drop trigger if exists old_trigger_name on pgmq.my_queue;
create trigger aimq_notify_my_queue
  after insert on pgmq.my_queue
  for each row
  execute function aimq.notify_job_enqueued();
```

#### Step 4: Update References

Update application code to use new schema:

```python
# Old code
result = supabase.rpc('send_message', {...})

# New code
result = supabase.rpc('send', {...})
```

#### Step 5: Deprecate Old Functions

Add deprecation warnings:

```sql
create or replace function public.send_message(...)
  returns setof bigint
  language plpgsql
as $$
begin
    raise warning 'public.send_message is deprecated. Use pgmq_public.send instead.';
    return query select * from pgmq_public.send(...);
end;
$$;
```

Plan removal after migration period:

```sql
-- After migration period (e.g., 3 months)
drop function if exists public.send_message;
```

## Migration Checklist

### Pre-Migration

- [ ] Document current schema structure
- [ ] Identify all public functions
- [ ] Identify all private/internal functions
- [ ] List all triggers and their dependencies
- [ ] Create backup of database

### During Migration

- [ ] Create new schemas (pgmq_public, aimq)
- [ ] Grant appropriate permissions
- [ ] Move public functions to pgmq_public
- [ ] Move private functions to aimq
- [ ] Update trigger definitions
- [ ] Test schema isolation
- [ ] Test function behavior
- [ ] Update application code

### Post-Migration

- [ ] Monitor for deprecation warnings
- [ ] Update documentation
- [ ] Communicate changes to team
- [ ] Plan removal of deprecated functions
- [ ] Remove old functions after migration period

## Rollback Strategy

If migration causes issues:

```sql
-- 1. Keep old functions working
-- (They should still exist during migration)

-- 2. Revert application code
-- (Use old function names)

-- 3. Remove new schemas if needed
drop schema if exists pgmq_public cascade;
drop schema if exists aimq cascade;

-- 4. Restore from backup if necessary
-- (Use pg_restore or similar)
```

## Best Practices

### 1. ✅ Migrate Incrementally

Don't migrate everything at once. Start with one function or feature:

```sql
-- Week 1: Migrate send function
create function pgmq_public.send(...)

-- Week 2: Migrate pop function
create function pgmq_public.pop(...)

-- Week 3: Migrate list_queues
create function pgmq_public.list_queues(...)
```

### 2. ✅ Maintain Backward Compatibility

Keep old functions working during migration:

```sql
-- Old function calls new function
create or replace function public.old_function(...)
as $$
begin
    return pgmq_public.new_function(...);
end;
$$;
```

### 3. ✅ Test Thoroughly

Test each migration step:

```python
def test_migration_step_1():
    """Test that send function works in new schema"""
    result = supabase.rpc('send', {...})
    assert result.data is not None

def test_backward_compatibility():
    """Test that old function still works"""
    result = supabase.rpc('send_message', {...})
    assert result.data is not None
```

### 4. ✅ Document Changes

Update documentation as you migrate:

```markdown
## Migration Status

- [x] send function → pgmq_public.send
- [x] pop function → pgmq_public.pop
- [ ] archive function → pgmq_public.archive (in progress)
- [ ] list_queues → pgmq_public.list_queues (planned)
```

## Related

- [Database Schema Patterns](./database-schema-patterns.md) - Schema organization patterns
- [Progressive Enhancement](../patterns/progressive-enhancement.md) - Phased development
- [Testing Strategy](../patterns/testing-strategy.md) - Testing patterns

## References

- [PostgreSQL Schema Documentation](https://www.postgresql.org/docs/current/ddl-schemas.html)
- [Database Migration Best Practices](https://www.postgresql.org/docs/current/backup.html)
- [Supabase Migrations](https://supabase.com/docs/guides/database/migrations)

---

**Remember**: Migrate incrementally, test thoroughly, maintain compatibility! 🚀✨
