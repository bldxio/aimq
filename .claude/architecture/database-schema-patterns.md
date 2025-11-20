# Database Schema Organization Patterns

> **Status**: Active
> **Last Updated**: 2025-11-20
> **Category**: architecture

## Overview

Strategic organization of database objects across multiple schemas provides security, usability, and maintainability benefits. This pattern is especially important when building on top of existing extensions (like pgmq) while adding custom functionality.

## The Three-Schema Pattern

### Schema Separation Strategy

```
┌─────────────────────────────────────────────────────────┐
│                    Database                              │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │   pgmq       │  │ pgmq_public  │  │    aimq      │  │
│  │  (storage)   │  │   (public)   │  │  (private)   │  │
│  ├──────────────┤  ├──────────────┤  ├──────────────┤  │
│  │ Queue tables │  │ RPC functions│  │   Triggers   │  │
│  │ Archive data │  │ Wrappers     │  │   Internal   │  │
│  │ Standard ops │  │ Management   │  │   Helpers    │  │
│  └──────────────┘  └──────────────┘  └──────────────┘  │
│        ▲                  ▲                  ▲          │
│        │                  │                  │          │
│        │                  │                  │          │
│  ┌─────┴──────────────────┴──────────────────┴──────┐  │
│  │              Access Control (RLS)                 │  │
│  └───────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────┘
```

### 1. Storage Schema (`pgmq`)

**Purpose**: Core data storage and standard operations

**Contents**:
- Queue tables (one per queue)
- Archive tables
- Standard pgmq functions (send, pop, archive, etc.)

**Access**: Internal use by other schemas

**Why Separate**:
- Follows extension conventions
- Keeps data in standard locations
- Allows extension upgrades without breaking custom code

```sql
-- Queue tables live here
pgmq.my_queue
pgmq.my_queue_archive

-- Standard operations
pgmq.send(queue_name, message, delay)
pgmq.pop(queue_name)
```

### 2. Public Schema (`pgmq_public`)

**Purpose**: Publicly accessible RPC functions

**Contents**:
- Wrapper functions for standard operations
- Custom management functions (create_queue, list_queues)
- Functions callable via Supabase SDK

**Access**: Exposed to authenticated users via RPC

**Why Separate**:
- Explicit API surface (only what you expose)
- RLS policies can be applied
- Follows Supabase conventions
- No need to configure custom schema access

```sql
-- Public RPC functions
pgmq_public.create_queue(name, with_realtime)
pgmq_public.list_queues()
pgmq_public.enable_queue_realtime(name)
pgmq_public.send(queue_name, message)
pgmq_public.pop(queue_name)
```

### 3. Private Schema (`aimq`)

**Purpose**: Internal implementation details

**Contents**:
- Trigger functions
- Helper functions
- Internal utilities

**Access**: Service role only (not exposed to users)

**Why Separate**:
- Security: Users can't call internal functions
- Clarity: Clear boundary between public and private
- Flexibility: Can change internals without breaking API

```sql
-- Private trigger functions
aimq.notify_job_enqueued()
aimq.setup_queue_trigger(queue_name)
```

## Implementation Example

### Schema Setup

```sql
-- 1. Create schemas
create schema if not exists pgmq;
create schema if not exists pgmq_public;
create schema if not exists aimq;

-- 2. Grant appropriate access
grant usage on schema pgmq_public to postgres, anon, authenticated, service_role;
grant usage on schema aimq to postgres, service_role;  -- service_role only!

-- 3. Enable extension in storage schema
create extension if not exists pgmq with schema pgmq;
```

### Public RPC Function

```sql
-- Wrapper in pgmq_public that calls pgmq
create or replace function pgmq_public.send(
    queue_name text,
    message jsonb,
    sleep_seconds integer default 0
)
  returns setof bigint
  language plpgsql
  set search_path = ''  -- Security: explicit schema references
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

-- Make it callable via RPC
grant execute on function pgmq_public.send to authenticated, service_role;
```

### Private Trigger Function

```sql
-- Internal trigger in aimq schema
create or replace function aimq.notify_job_enqueued()
  returns trigger
  language plpgsql
  security definer  -- Runs with creator's privileges
  set search_path = ''
as $$
begin
    perform pg_notify(
        'aimq:jobs',
        json_build_object(
            'event', 'job_enqueued',
            'queue', TG_TABLE_NAME,
            'msg_id', NEW.msg_id
        )::text
    );
    return NEW;
end;
$$;

-- No grant execute - only used by triggers
```

## Benefits

### Security

**Principle of Least Privilege**:
- Users only access what they need (pgmq_public)
- Internal functions stay private (aimq)
- RLS policies can be applied per schema

**Example**:
```sql
-- RLS on public functions
alter table pgmq_public.* enable row level security;

-- Private functions not accessible to users
-- (no RLS needed - they can't call them)
```

### Usability

**No Custom Configuration**:
- `pgmq_public` follows Supabase conventions
- Users don't need to configure schema access
- Works out of the box with Supabase SDK

**Example**:
```python
# Just works - no schema configuration needed
supabase.rpc('create_queue', {'queue_name': 'my-queue'})
```

### Maintainability

**Clear Boundaries**:
- Public API is explicit (pgmq_public)
- Internal changes don't break users (aimq)
- Extension upgrades are isolated (pgmq)

**Example**:
```sql
-- Can change internal implementation
-- without breaking public API
create or replace function aimq.notify_job_enqueued()
  -- New implementation
  -- Users never called this directly
```

## Common Patterns

### Pattern 1: Wrapper Functions

Wrap extension functions to expose them via RPC:

```sql
create or replace function pgmq_public.archive(
    queue_name text,
    message_id bigint
)
  returns boolean
  language plpgsql
  set search_path = ''
as $$
begin
    return pgmq.archive(
        queue_name := queue_name,
        msg_id := message_id
    );
end;
$$;
```

### Pattern 2: Management Functions

Add custom management operations:

```sql
create or replace function pgmq_public.list_queues()
  returns table(
    queue_name text,
    queue_length bigint,
    realtime_enabled boolean
  )
  language plpgsql
  set search_path = ''
as $$
begin
    return query
    select
        q.queue_name,
        q.queue_length,
        exists(
            select 1 from pg_trigger
            where tgname = 'aimq_notify_' || q.queue_name
        ) as realtime_enabled
    from pgmq.list_queues() q;
end;
$$;
```

### Pattern 3: Trigger Setup

Use private functions for trigger logic:

```sql
-- Private helper to set up triggers
create or replace function aimq.setup_queue_trigger(
    p_queue_name text,
    p_channel text default 'aimq:jobs',
    p_event text default 'job_enqueued'
)
  returns void
  language plpgsql
  security definer
  set search_path = ''
as $$
declare
    v_trigger_name text;
begin
    v_trigger_name := 'aimq_notify_' || p_queue_name;

    execute format(
        'create trigger %I
         after insert on pgmq.%I
         for each row
         execute function aimq.notify_job_enqueued()',
        v_trigger_name,
        p_queue_name
    );
end;
$$;

-- Public function calls private helper
create or replace function pgmq_public.enable_queue_realtime(
    queue_name text
)
  returns jsonb
  language plpgsql
  set search_path = ''
as $$
begin
    perform aimq.setup_queue_trigger(queue_name);
    return jsonb_build_object('success', true);
end;
$$;
```

## Anti-Patterns

### ❌ Everything in One Schema

```sql
-- Bad: All functions in public schema
create function public.send_message(...)
create function public.internal_helper(...)  -- Exposed!
create function public.trigger_function(...)  -- Exposed!
```

**Problems**:
- No security boundary
- Users can call internal functions
- Hard to apply RLS selectively

### ❌ Custom Schema Names

```sql
-- Bad: Non-standard schema names
create schema my_custom_queue_schema;
```

**Problems**:
- Users must configure schema access
- Doesn't follow Supabase conventions
- More setup friction

### ❌ Mixing Concerns

```sql
-- Bad: Public API and triggers in same schema
create schema api;
create function api.send_message(...)  -- Public
create function api.trigger_helper(...)  -- Should be private
```

**Problems**:
- Unclear boundaries
- Hard to secure properly
- Maintenance confusion

## Related

- [Database Schema Migration](./database-schema-migration.md) - Migration strategies and testing
- [Progressive Enhancement](../patterns/progressive-enhancement.md) - Phased development
- [LangGraph AIMQ](./langgraph-aimq.md) - AIMQ architecture

## References

- [PostgreSQL Schema Documentation](https://www.postgresql.org/docs/current/ddl-schemas.html)
- [Supabase Schema Conventions](https://supabase.com/docs/guides/database/extensions)
- [pgmq Extension](https://github.com/tembo-io/pgmq)

---

**Remember**: Good schema organization is security by design! 🔒✨
