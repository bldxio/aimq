# Database Migration Wrapper Functions

Pattern for wrapping database extensions and functions with cleaner, more secure public APIs.

## The Problem

When integrating database extensions (like pgmq, PostGIS, pg_cron), directly exposing extension functions leads to:

1. **Confusing APIs** - Extension parameter names may be unclear or inconsistent
2. **Security risks** - Overly permissive access to internal functions
3. **Upgrade difficulties** - Direct dependencies on extension internals
4. **Poor documentation** - Extension functions often lack clear descriptions
5. **Inconsistent naming** - Extensions may use different conventions than your app

## The Solution

Create wrapper functions in a public schema that:
- Provide cleaner, more intuitive APIs
- Control permissions granularly
- Add comprehensive documentation
- Isolate extension internals from public API
- Allow for future extension upgrades without breaking changes

## Pattern Structure

```sql
-- 1. Create public schema for wrappers
create schema if not exists <extension>_public;
grant usage on schema <extension>_public to <roles>;

-- 2. Create wrapper function with improved API
create or replace function <extension>_public.<function_name>(
    -- Use clear, descriptive parameter names
    param1 type,
    param2 type default value
)
  returns <return_type>
  language plpgsql
  set search_path = ''  -- Security: explicit schema references
as $$
begin
    -- Call extension function with mapping
    return query
    select * from <extension>.<internal_function>(
        internal_param1 := param1,
        internal_param2 := param2
    );
end;
$$;

-- 3. Add documentation
comment on function <extension>_public.<function_name>(...) is
    'Clear description of what this function does';

-- 4. Grant specific permissions
grant execute on function <extension>_public.<function_name>(...)
    to authenticated;
```

## Real-World Example: pgmq Wrapper

### Before: Direct Extension Access

```sql
-- Users call pgmq functions directly
select * from pgmq.send(
    queue_name := 'my-queue',
    msg := '{"data": "value"}'::jsonb,
    delay := 30  -- Confusing: "delay" could mean many things
);

-- Problems:
-- 1. "delay" is ambiguous (delay what? for how long?)
-- 2. Direct access to pgmq schema
-- 3. No documentation
-- 4. Hard to change later
```

### After: Wrapper Function

```sql
-- Create public schema
create schema if not exists pgmq_public;
grant usage on schema pgmq_public to postgres, anon, authenticated, service_role;

-- Wrapper with improved API
create or replace function pgmq_public.send(
    queue_name text,
    message jsonb,
    sleep_seconds integer default 0  -- Clear: sleep before processing
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
        delay := sleep_seconds  -- Map to extension's parameter
    );
end;
$$;

comment on function pgmq_public.send(queue_name text, message jsonb, sleep_seconds integer) is
    'Sends a message to the specified queue, optionally delaying its availability by a number of seconds.';

grant execute on function pgmq_public.send(text, jsonb, integer)
    to authenticated;

-- Users now call the wrapper
select * from pgmq_public.send(
    queue_name := 'my-queue',
    message := '{"data": "value"}'::jsonb,
    sleep_seconds := 30  -- Much clearer!
);
```

## Benefits

### 1. Clearer APIs

```sql
-- Before: Ambiguous
pgmq.send(queue_name, msg, delay)

-- After: Self-documenting
pgmq_public.send(queue_name, message, sleep_seconds)
```

### 2. Better Security

```sql
-- Revoke direct access to extension
revoke all on schema pgmq from public;

-- Grant only wrapper access
grant usage on schema pgmq_public to authenticated;
grant execute on function pgmq_public.send(...) to authenticated;

-- Users can't access internal functions
-- select * from pgmq.internal_function();  -- ERROR: permission denied
```

### 3. Comprehensive Documentation

```sql
-- Extension functions often lack docs
\df+ pgmq.send
-- Function: pgmq.send
-- Description: (none)

-- Wrapper functions have clear documentation
\df+ pgmq_public.send
-- Function: pgmq_public.send
-- Description: Sends a message to the specified queue,
--              optionally delaying its availability by a number of seconds.
```

### 4. Easier Upgrades

```sql
-- Extension changes internal API
-- Old: pgmq.send(queue, msg, delay)
-- New: pgmq.send(queue, msg, delay_seconds, priority)

-- Update wrapper to handle both versions
create or replace function pgmq_public.send(
    queue_name text,
    message jsonb,
    sleep_seconds integer default 0
)
  returns setof bigint
  language plpgsql
as $$
begin
    -- Adapt to new extension API
    return query
    select *
    from pgmq.send(
        queue := queue_name,
        msg := message,
        delay_seconds := sleep_seconds,
        priority := 5  -- Default priority
    );
end;
$$;

-- User code doesn't change!
```

## Implementation Checklist

- [ ] Create public schema for wrappers
- [ ] Grant appropriate permissions on schema
- [ ] Create wrapper functions with clear parameter names
- [ ] Use `set search_path = ''` for security
- [ ] Add comprehensive comments/documentation
- [ ] Grant execute permissions to specific roles
- [ ] Revoke direct access to extension schema (if appropriate)
- [ ] Test wrapper functions
- [ ] Update application code to use wrappers
- [ ] Document wrapper API in application docs

## Common Patterns

### 1. Parameter Renaming

```sql
-- Extension uses technical names
extension.function(msg, vt, qty)

-- Wrapper uses descriptive names
public.function(message, visibility_timeout, max_messages)
```

### 2. Default Values

```sql
-- Extension requires all parameters
extension.function(queue, msg, delay, retries, timeout)

-- Wrapper provides sensible defaults
public.function(
    queue text,
    message jsonb,
    sleep_seconds integer default 0,
    max_retries integer default 3,
    timeout_seconds integer default 30
)
```

### 3. Type Conversion

```sql
-- Extension uses internal types
extension.function(msg pgmq.message_record)

-- Wrapper uses standard types
public.function(message jsonb) as $$
begin
    return extension.function(
        msg := row(message)::pgmq.message_record
    );
end;
$$;
```

### 4. Error Handling

```sql
create or replace function public.safe_send(
    queue_name text,
    message jsonb
)
  returns bigint
  language plpgsql
as $$
declare
    msg_id bigint;
begin
    -- Validate inputs
    if queue_name is null or queue_name = '' then
        raise exception 'queue_name cannot be empty';
    end if;

    if message is null then
        raise exception 'message cannot be null';
    end if;

    -- Call extension with error handling
    begin
        select * into msg_id
        from extension.send(queue_name, message);

        return msg_id;
    exception
        when others then
            raise exception 'Failed to send message: %', sqlerrm;
    end;
end;
$$;
```

## Migration Strategy

### Phase 1: Create Wrappers

```sql
-- Create wrappers alongside existing direct access
create schema if not exists pgmq_public;
create or replace function pgmq_public.send(...) ...;
```

### Phase 2: Update Application Code

```python
# Before
result = supabase.rpc("pgmq.send", {
    "queue_name": "my-queue",
    "msg": message,
    "delay": 30
})

# After
result = supabase.rpc("pgmq_public.send", {
    "queue_name": "my-queue",
    "message": message,
    "sleep_seconds": 30
})
```

### Phase 3: Deprecate Direct Access

```sql
-- Add deprecation notice
comment on schema pgmq is
    'DEPRECATED: Use pgmq_public schema instead. Direct access will be removed in v2.0';

-- Optionally revoke permissions
revoke all on schema pgmq from authenticated;
```

### Phase 4: Remove Direct Access

```sql
-- After all code is migrated
revoke all on schema pgmq from public;
grant usage on schema pgmq to postgres only;
```

## Testing Wrappers

```sql
-- Test basic functionality
select pgmq_public.send('test-queue', '{"test": true}'::jsonb);

-- Test default parameters
select pgmq_public.send('test-queue', '{"test": true}'::jsonb);

-- Test with explicit parameters
select pgmq_public.send('test-queue', '{"test": true}'::jsonb, 60);

-- Test error handling
select pgmq_public.send(null, '{"test": true}'::jsonb);  -- Should error

-- Test permissions
set role authenticated;
select pgmq_public.send('test-queue', '{"test": true}'::jsonb);  -- Should work
select pgmq.send('test-queue', '{"test": true}'::jsonb);  -- Should fail
```

## Real-World Example: Complete pgmq Wrapper

See `supabase/migrations/20251123021000_setup_aimq.sql` for a complete implementation:

- Wraps 10+ pgmq functions
- Provides clear parameter names
- Adds comprehensive documentation
- Controls permissions granularly
- Includes error handling
- Supports batch operations

Key functions wrapped:
- `send()` - Send single message
- `send_batch()` - Send multiple messages
- `pop()` - Retrieve and lock message
- `archive()` - Archive processed message
- `delete()` - Delete message
- `read()` - Read without locking

## Related

- [@.claude/architecture/database-schema-patterns.md](../architecture/database-schema-patterns.md) - Schema organization
- [@.claude/architecture/database-schema-migration.md](../architecture/database-schema-migration.md) - Migration strategies
- [@.claude/patterns/error-handling.md](./error-handling.md) - Error handling patterns
- [@.claude/quick-references/supabase-local-setup.md](../quick-references/supabase-local-setup.md) - Local setup
