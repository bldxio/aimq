# Example Message Schema Migration

**Status**: 📝 Planned
**Priority**: Low - Nice to have for testing
**Complexity**: Low
**Estimated Effort**: 1-2 hours

---

## What

An optional migration that creates a standard message/profile/channel schema for testing and demos. This provides a foundation for building multi-agent chat systems and gives users a reference implementation.

### Key Features

- **Standard Schema**: Message, profile, and channel tables
- **Optional Setup**: Generated via `aimq init --messages` flag
- **Testing Ready**: Pre-configured for agent testing
- **Reference Implementation**: Shows best practices for schema design

---

## Why

### Business Value
- **Faster Onboarding**: Users can start testing immediately
- **Reference Architecture**: Shows how to structure chat data
- **Demo Ready**: Perfect for showcasing AIMQ capabilities
- **Testing Foundation**: Standard schema for integration tests

### Technical Value
- **Consistent Structure**: All examples use same schema
- **Best Practices**: RLS policies, indexes, foreign keys
- **Extensible**: Easy to customize for specific needs
- **Integration Ready**: Works with default agents

---

## Schema Design

### Tables

#### `profiles`
```sql
create table public.profiles (
  id uuid primary key default gen_random_uuid(),
  email text unique not null,
  display_name text,
  avatar_url text,
  role text default 'user' check (role in ('user', 'agent', 'admin')),
  metadata jsonb default '{}'::jsonb,
  created_at timestamptz default now(),
  updated_at timestamptz default now()
);

comment on table public.profiles is 'User and agent profiles';
```

#### `channels`
```sql
create table public.channels (
  id uuid primary key default gen_random_uuid(),
  workspace_id uuid not null,
  name text not null,
  description text,
  channel_type text default 'public' check (channel_type in ('public', 'private', 'direct')),
  metadata jsonb default '{}'::jsonb,
  created_at timestamptz default now(),
  updated_at timestamptz default now(),

  unique(workspace_id, name)
);

comment on table public.channels is 'Chat channels within workspaces';
```

#### `messages`
```sql
create table public.messages (
  id uuid primary key default gen_random_uuid(),
  channel_id uuid not null references public.channels(id) on delete cascade,
  author_id uuid not null references public.profiles(id) on delete cascade,
  reply_to_id uuid references public.messages(id) on delete set null,
  content text not null,
  role text default 'user' check (role in ('user', 'assistant', 'system')),
  metadata jsonb default '{}'::jsonb,
  created_at timestamptz default now(),
  updated_at timestamptz default now()
);

comment on table public.messages is 'Messages in channels with threading support';

-- Indexes for performance
create index messages_channel_id_idx on public.messages(channel_id);
create index messages_author_id_idx on public.messages(author_id);
create index messages_reply_to_id_idx on public.messages(reply_to_id);
create index messages_created_at_idx on public.messages(created_at desc);
```

#### `channel_members`
```sql
create table public.channel_members (
  channel_id uuid not null references public.channels(id) on delete cascade,
  profile_id uuid not null references public.profiles(id) on delete cascade,
  role text default 'member' check (role in ('owner', 'admin', 'member')),
  joined_at timestamptz default now(),

  primary key (channel_id, profile_id)
);

comment on table public.channel_members is 'Channel membership and roles';
```

### RLS Policies

```sql
-- Enable RLS
alter table public.profiles enable row level security;
alter table public.channels enable row level security;
alter table public.messages enable row level security;
alter table public.channel_members enable row level security;

-- Service role has full access (for AIMQ workers)
create policy "Service role has full access to profiles"
  on public.profiles for all
  to service_role
  using (true)
  with check (true);

create policy "Service role has full access to channels"
  on public.channels for all
  to service_role
  using (true)
  with check (true);

create policy "Service role has full access to messages"
  on public.messages for all
  to service_role
  using (true)
  with check (true);

create policy "Service role has full access to channel_members"
  on public.channel_members for all
  to service_role
  using (true)
  with check (true);

-- Users can read public channels
create policy "Users can read public channels"
  on public.channels for select
  to authenticated
  using (channel_type = 'public');

-- Users can read messages in channels they're members of
create policy "Users can read messages in their channels"
  on public.messages for select
  to authenticated
  using (
    exists (
      select 1 from public.channel_members
      where channel_id = messages.channel_id
        and profile_id = auth.uid()
    )
  );
```

### Functions

```sql
-- Function to get thread tree
create or replace function public.get_message_thread(message_id uuid)
returns table (
  id uuid,
  channel_id uuid,
  author_id uuid,
  reply_to_id uuid,
  content text,
  role text,
  depth int,
  created_at timestamptz
)
language sql
stable
as $$
  with recursive thread as (
    -- Base case: the root message
    select
      m.id,
      m.channel_id,
      m.author_id,
      m.reply_to_id,
      m.content,
      m.role,
      0 as depth,
      m.created_at
    from public.messages m
    where m.id = message_id

    union all

    -- Recursive case: replies to messages in the thread
    select
      m.id,
      m.channel_id,
      m.author_id,
      m.reply_to_id,
      m.content,
      m.role,
      t.depth + 1,
      m.created_at
    from public.messages m
    inner join thread t on m.reply_to_id = t.id
  )
  select * from thread
  order by depth, created_at;
$$;

comment on function public.get_message_thread(uuid) is
  'Returns all messages in a thread, starting from the given message';
```

---

## Implementation

### Migration Template

Create `setup_example_messages.sql` template:

```sql
-- Enable UUID extension
create extension if not exists "uuid-ossp";

-- Create tables
-- (tables from above)

-- Create indexes
-- (indexes from above)

-- Enable RLS
-- (RLS policies from above)

-- Create functions
-- (functions from above)

-- Grant permissions
grant usage on schema public to postgres, anon, authenticated, service_role;
grant all on all tables in schema public to postgres, service_role;
grant select on all tables in schema public to authenticated;
```

### Python Integration

Add to `aimq init` command:

```python
def init(
    directory: Optional[str] = None,
    supabase: bool = None,
    docker: bool = None,
    langgraph: bool = None,
    messages: bool = None,  # NEW FLAG
    all_components: bool = False,
    minimal: bool = False,
) -> None:
    """Initialize a new AIMQ project."""

    # ... existing code ...

    # Setup message schema if requested
    if setup_messages_flag:
        task = progress.add_task("Creating message schema...", total=None)
        project_path = ProjectPath(project_dir)
        migrations = SupabaseMigrations(project_path)
        migration_path = migrations.setup_example_messages_migration()
        console.print(f"✓ Created {migration_path.name}", style="green")
        progress.update(task, completed=True)
```

Add to `SupabaseMigrations` class:

```python
def setup_example_messages_migration(self) -> Path:
    """Create the example message schema migration.

    This migration creates standard message/profile/channel tables
    for testing and demos.

    Returns:
        Path: Path to the created migration file
    """
    return self.create_migration(
        name="setup_example_messages",
        template_name="setup_example_messages.sql"
    )
```

---

## Usage

### Setup

```bash
# Initialize with message schema
aimq init --supabase --messages

# Or add to existing project
aimq init --messages
```

### Testing

```python
from supabase import create_client

client = create_client(url, key)

# Create a test channel
channel = client.table("channels").insert({
    "workspace_id": workspace_id,
    "name": "general",
    "channel_type": "public"
}).execute()

# Create a test message
message = client.table("messages").insert({
    "channel_id": channel.data[0]["id"],
    "author_id": user_id,
    "content": "Hello, world!",
    "role": "user"
}).execute()

# Get thread
thread = client.rpc("get_message_thread", {
    "message_id": message.data[0]["id"]
}).execute()
```

---

## Benefits

1. **Faster Testing**: No need to design schema from scratch
2. **Reference Implementation**: Shows best practices
3. **Demo Ready**: Perfect for showcasing features
4. **Extensible**: Easy to customize for specific needs
5. **Integration Tests**: Standard schema for testing

---

## Future Enhancements

- **Seed Data**: Optional seed data for testing
- **Workspaces Table**: Multi-tenant support
- **Reactions**: Message reactions/emoji
- **Attachments**: File attachments support
- **Read Receipts**: Track message read status
- **Typing Indicators**: Real-time typing status

---

## Related

- [ideas/thread-tree-system.md](./thread-tree-system.md) - Thread tree implementation
- [ideas/message-ingestion-pipeline.md](./message-ingestion-pipeline.md) - Message processing
- [ideas/multi-agent-group-chat.md](./multi-agent-group-chat.md) - Multi-agent chat system
