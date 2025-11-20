-- Enable required extensions
create schema if not exists "pgmq";
create extension if not exists "pgmq" with schema "pgmq";

create schema if not exists pgmq_public;
grant usage on schema pgmq_public to postgres, anon, authenticated, service_role;

-- Create aimq schema for internal functions
create schema if not exists aimq;
grant usage on schema aimq to postgres, service_role;

create or replace function pgmq_public.pop(
    queue_name text
)
  returns setof pgmq.message_record
  language plpgsql
  set search_path = ''
as $$
begin
    return query
    select *
    from pgmq.pop(
        queue_name := queue_name
    );
end;
$$;

comment on function pgmq_public.pop(queue_name text) is 'Retrieves and locks the next message from the specified queue.';


create or replace function pgmq_public.send(
    queue_name text,
    message jsonb,
    sleep_seconds integer default 0  -- renamed from 'delay'
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

comment on function pgmq_public.send(queue_name text, message jsonb, sleep_seconds integer) is 'Sends a message to the specified queue, optionally delaying its availability by a number of seconds.';


create or replace function pgmq_public.send_batch(
    queue_name text,
    messages jsonb[],
    sleep_seconds integer default 0  -- renamed from 'delay'
)
  returns setof bigint
  language plpgsql
  set search_path = ''
as $$
begin
    return query
    select *
    from pgmq.send_batch(
        queue_name := queue_name,
        msgs := messages,
        delay := sleep_seconds
    );
end;
$$;

comment on function pgmq_public.send_batch(queue_name text, messages jsonb[], sleep_seconds integer) is 'Sends a batch of messages to the specified queue, optionally delaying their availability by a number of seconds.';


create or replace function pgmq_public.archive(
    queue_name text,
    message_id bigint
)
  returns boolean
  language plpgsql
  set search_path = ''
as $$
begin
    return
    pgmq.archive(
        queue_name := queue_name,
        msg_id := message_id
    );
end;
$$;

comment on function pgmq_public.archive(queue_name text, message_id bigint) is 'Archives a message by moving it from the queue to a permanent archive.';


create or replace function pgmq_public.archive(
    queue_name text,
    message_id bigint
)
  returns boolean
  language plpgsql
  set search_path = ''
as $$
begin
    return
    pgmq.archive(
        queue_name := queue_name,
        msg_id := message_id
    );
end;
$$;

comment on function pgmq_public.archive(queue_name text, message_id bigint) is 'Archives a message by moving it from the queue to a permanent archive.';


create or replace function pgmq_public.delete(
    queue_name text,
    message_id bigint
)
  returns boolean
  language plpgsql
  set search_path = ''
as $$
begin
    return
    pgmq.delete(
        queue_name := queue_name,
        msg_id := message_id
    );
end;
$$;

comment on function pgmq_public.delete(queue_name text, message_id bigint) is 'Permanently deletes a message from the specified queue.';

create or replace function pgmq_public.read(
    queue_name text,
    sleep_seconds integer,
    n integer
)
  returns setof pgmq.message_record
  language plpgsql
  set search_path = ''
as $$
begin
    return query
    select *
    from pgmq.read(
        queue_name := queue_name,
        vt := sleep_seconds,
        qty := n
    );
end;
$$;

comment on function pgmq_public.read(queue_name text, sleep_seconds integer, n integer) is 'Reads up to "n" messages from the specified queue with an optional "sleep_seconds" (visibility timeout).';

-- Grant execute permissions on wrapper functions to roles
grant execute on function pgmq_public.pop(text) to postgres, service_role, anon, authenticated;
grant execute on function pgmq.pop(text) to postgres, service_role, anon, authenticated;

grant execute on function pgmq_public.send(text, jsonb, integer) to postgres, service_role, anon, authenticated;
grant execute on function pgmq.send(text, jsonb, integer) to postgres, service_role, anon, authenticated;

grant execute on function pgmq_public.send_batch(text, jsonb[], integer) to postgres, service_role, anon, authenticated;
grant execute on function pgmq.send_batch(text, jsonb[], integer) to postgres, service_role, anon, authenticated;

grant execute on function pgmq_public.archive(text, bigint) to postgres, service_role, anon, authenticated;
grant execute on function pgmq.archive(text, bigint) to postgres, service_role, anon, authenticated;

grant execute on function pgmq_public.delete(text, bigint) to postgres, service_role, anon, authenticated;
grant execute on function pgmq.delete(text, bigint) to postgres, service_role, anon, authenticated;

grant execute on function pgmq_public.read(text, integer, integer) to postgres, service_role, anon, authenticated;
grant execute on function pgmq.read(text, integer, integer) to postgres, service_role, anon, authenticated;

-- For the service role, we want full access
-- Grant permissions on existing tables
grant all privileges on all tables in schema pgmq to postgres, service_role;

-- Ensure service_role has permissions on future tables
alter default privileges in schema pgmq grant all privileges on tables to postgres, service_role;

grant usage on schema pgmq to postgres, anon, authenticated, service_role;


/*
  Grant access to sequences to API roles by default. Existing table permissions
  continue to enforce insert restrictions. This is necessary to accommodate the
  on-backup hook that rebuild queue table primary keys to avoid a pg_dump segfault.
  This can be removed once logical backups are completely retired.
*/
grant usage, select, update
on all sequences in schema pgmq
to anon, authenticated, service_role;

alter default privileges in schema pgmq
grant usage, select, update
on sequences
to anon, authenticated, service_role;

-- ============================================================================
-- AIMQ Realtime Integration
-- ============================================================================

-- Trigger function to emit realtime notifications when jobs are enqueued
-- This function is called by triggers on pgmq queue tables
create or replace function aimq.pgmq_notify_job_enqueued()
returns trigger
language plpgsql
security definer
set search_path = ''
as $$
declare
  channel_name text;
  event_name text;
  queue_name text;
  payload jsonb;
begin
  -- Extract configuration from trigger arguments
  -- TG_ARGV[0] = channel name (e.g., 'worker-wakeup')
  -- TG_ARGV[1] = event name (e.g., 'job_enqueued')
  -- TG_ARGV[2] = queue name (e.g., 'default')
  channel_name := TG_ARGV[0];
  event_name := TG_ARGV[1];
  queue_name := TG_ARGV[2];

  -- Build payload for Supabase Realtime
  payload := jsonb_build_object(
    'type', 'broadcast',
    'event', event_name,
    'payload', jsonb_build_object(
      'queue', queue_name,
      'job_id', NEW.msg_id
    )
  );

  -- Emit notification to Supabase Realtime
  -- Format: realtime:{channel_name}
  perform pg_notify('realtime:' || channel_name, payload::text);

  return NEW;
end;
$$;

comment on function aimq.pgmq_notify_job_enqueued() is
  'Trigger function that emits Supabase Realtime notifications when jobs are enqueued to pgmq queues. Expects 3 trigger arguments: channel_name, event_name, queue_name.';

-- ============================================================================
-- PGMQ Public RPC Functions for Queue Management
-- ============================================================================

-- Create a new queue with optional realtime trigger
create or replace function pgmq_public.create_queue(
  queue_name text,
  with_realtime boolean default true,
  channel_name text default 'worker-wakeup',
  event_name text default 'job_enqueued'
)
returns jsonb
language plpgsql
security definer
set search_path = ''
as $$
declare
  table_schema text := 'pgmq';
  table_name text;
  trigger_name text;
  result jsonb;
begin
  -- Create the pgmq queue (creates table in pgmq schema)
  perform pgmq.create(queue_name);

  -- Build table and trigger names (queue tables are in pgmq schema)
  table_name := 'q_' || queue_name;
  trigger_name := 'aimq_notify_' || queue_name;

  -- Attach realtime trigger if requested
  if with_realtime then
    execute format(
      'create trigger %I
       after insert on %I.%I
       for each row
       execute function aimq.pgmq_notify_job_enqueued(%L, %L, %L)',
      trigger_name,
      table_schema,
      table_name,
      channel_name,
      event_name,
      queue_name
    );
  end if;

  -- Return success result
  result := jsonb_build_object(
    'success', true,
    'queue_name', queue_name,
    'realtime_enabled', with_realtime,
    'channel', channel_name,
    'event', event_name
  );

  return result;
end;
$$;

comment on function pgmq_public.create_queue(text, boolean, text, text) is
  'Creates a new pgmq queue with optional realtime trigger. Returns JSON with queue details and realtime configuration.';

grant execute on function pgmq_public.create_queue(text, boolean, text, text) to postgres, service_role, authenticated;

-- List all pgmq queues with realtime status and metrics
create or replace function pgmq_public.list_queues()
returns jsonb
language plpgsql
security definer
set search_path = ''
as $$
declare
  queue_record record;
  queues jsonb := '[]'::jsonb;
  queue_info jsonb;
  trigger_exists boolean;
  queue_length bigint;
  newest_msg_age_sec integer;
  oldest_msg_age_sec integer;
  total_messages bigint;
  scrape_time timestamptz;
begin
  -- Iterate through all pgmq queues
  for queue_record in
    select queue_name
    from pgmq.list_queues()
  loop
    -- Check if realtime trigger exists (check both pgmq and pgmq_public schemas)
    select exists(
      select 1
      from pg_trigger t
      join pg_class c on t.tgrelid = c.oid
      join pg_namespace n on c.relnamespace = n.oid
      where n.nspname in ('pgmq', 'pgmq_public')
        and c.relname = 'q_' || queue_record.queue_name
        and t.tgname = 'aimq_notify_' || queue_record.queue_name
    ) into trigger_exists;

    -- Get queue metrics from pgmq.metrics
    select
      m.queue_length,
      m.newest_msg_age_sec,
      m.oldest_msg_age_sec,
      m.total_messages,
      m.scrape_time
    into
      queue_length,
      newest_msg_age_sec,
      oldest_msg_age_sec,
      total_messages,
      scrape_time
    from pgmq.metrics(queue_record.queue_name) m;

    -- Build queue info with metrics
    queue_info := jsonb_build_object(
      'queue_name', queue_record.queue_name,
      'realtime_enabled', trigger_exists,
      'queue_length', coalesce(queue_length, 0),
      'newest_msg_age_sec', newest_msg_age_sec,
      'oldest_msg_age_sec', oldest_msg_age_sec,
      'total_messages', coalesce(total_messages, 0),
      'scrape_time', scrape_time
    );

    -- Append to results
    queues := queues || queue_info;
  end loop;

  return jsonb_build_object(
    'success', true,
    'queues', queues
  );
end;
$$;

comment on function pgmq_public.list_queues() is
  'Lists all pgmq queues with their realtime trigger status and metrics. Includes queue_length, message ages, and total_messages from pgmq.metrics(). Returns JSON array of queue objects.';

grant execute on function pgmq_public.list_queues() to postgres, service_role, authenticated;

-- Enable realtime on an existing queue
create or replace function pgmq_public.enable_queue_realtime(
  queue_name text,
  channel_name text default 'worker-wakeup',
  event_name text default 'job_enqueued'
)
returns jsonb
language plpgsql
security definer
set search_path = ''
as $$
declare
  table_name text;
  table_schema text;
  trigger_name text;
  trigger_exists boolean;
  result jsonb;
  queue_exists boolean;
begin
  -- Verify queue exists using pgmq.list_queues()
  select exists(
    select 1
    from pgmq.list_queues() q
    where q.queue_name = enable_queue_realtime.queue_name
  ) into queue_exists;

  if not queue_exists then
    return jsonb_build_object(
      'success', false,
      'error', 'Queue ''' || queue_name || ''' does not exist. Please create the queue before using it.'
    );
  end if;

  -- Find which schema the queue table is in (pgmq or pgmq_public)
  select n.nspname
  into table_schema
  from pg_class c
  join pg_namespace n on c.relnamespace = n.oid
  where c.relname = 'q_' || queue_name
    and n.nspname in ('pgmq', 'pgmq_public')
    and c.relkind = 'r'
  limit 1;

  if table_schema is null then
    return jsonb_build_object(
      'success', false,
      'error', 'Queue table not found for: ' || queue_name
    );
  end if;

  -- Build table and trigger names
  table_name := 'q_' || queue_name;
  trigger_name := 'aimq_notify_' || queue_name;

  -- Check if trigger already exists
  select exists(
    select 1
    from pg_trigger t
    join pg_class c on t.tgrelid = c.oid
    join pg_namespace n on c.relnamespace = n.oid
    where n.nspname = table_schema
      and c.relname = 'q_' || queue_name
      and t.tgname = trigger_name
  ) into trigger_exists;

  if trigger_exists then
    return jsonb_build_object(
      'success', true,
      'queue_name', queue_name,
      'realtime_enabled', true,
      'channel', channel_name,
      'event', event_name
    );
  end if;

  -- Create the trigger
  execute format(
    'create trigger %I
     after insert on %I.%I
     for each row
     execute function aimq.pgmq_notify_job_enqueued(%L, %L, %L)',
    trigger_name,
    table_schema,
    table_name,
    channel_name,
    event_name,
    queue_name
  );

  -- Return success result
  result := jsonb_build_object(
    'success', true,
    'queue_name', queue_name,
    'realtime_enabled', true,
    'channel', channel_name,
    'event', event_name
  );

  return result;
end;
$$;

comment on function pgmq_public.enable_queue_realtime(text, text, text) is
  'Enables realtime trigger on an existing pgmq queue. Upgrades a standard queue to an AIMQ queue with instant worker wake-up. Returns JSON with operation result.';

grant execute on function pgmq_public.enable_queue_realtime(text, text, text) to postgres, service_role, authenticated;
