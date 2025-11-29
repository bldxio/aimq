-- ============================================================================
-- Email Processing System Schema
-- ============================================================================
-- This migration creates the core schema for AI-powered email processing
-- with workspace isolation, multi-agent support, and attachment handling.
--
-- Key Features:
-- - Workspace-based multi-tenancy with denormalized workspace_id
-- - STI (Single Table Inheritance) for profiles and messages
-- - Channel-based organization with customizable agents
-- - Email routing via subdomain (workspace) and user (channel)
-- - Attachment storage with OCR/processing pipeline support
-- - Thread support via reply_to_id
-- ============================================================================

-- ============================================================================
-- ENUMS
-- ============================================================================

create type profile_type as enum ('user', 'assistant');
create type message_type as enum ('chat', 'email');
create type message_status as enum ('pending', 'processing', 'processed', 'sent', 'failed');
create type member_role as enum ('owner', 'admin', 'member');
create type attachment_status as enum ('pending', 'downloaded', 'needs_processing', 'processed', 'failed');
create type sentiment_type as enum ('positive', 'neutral', 'negative');

-- ============================================================================
-- WORKSPACES
-- ============================================================================

create table workspaces (
    id uuid primary key default gen_random_uuid(),
    name text not null,
    short_name text not null unique,
    settings jsonb default '{}'::jsonb,
    created_at timestamptz not null default now(),
    updated_at timestamptz not null default now(),

    constraint short_name_format check (short_name ~ '^[a-z0-9-]+$'),
    constraint short_name_length check (char_length(short_name) >= 2 and char_length(short_name) <= 32)
);

comment on table workspaces is 'Multi-tenant workspaces for email processing isolation';
comment on column workspaces.short_name is 'Subdomain for email routing (e.g., "acme" → support@acme.example.com)';

create index idx_workspaces_short_name on workspaces(short_name);

-- ============================================================================
-- PROFILES (STI: users and assistants)
-- ============================================================================

create table profiles (
    id uuid primary key default gen_random_uuid(),
    type profile_type not null default 'user',
    name text not null,
    email text,
    avatar_url text,
    model text,
    queue_name text,
    system_prompt text,
    created_at timestamptz not null default now(),
    updated_at timestamptz not null default now(),

    constraint email_required_for_users check (
        (type = 'user' and email is not null) or
        (type = 'assistant')
    ),
    constraint assistant_fields check (
        (type = 'assistant' and model is not null) or
        (type = 'user')
    )
);

comment on table profiles is 'Users and AI assistants (STI via type column)';
comment on column profiles.type is 'Discriminator: user or assistant';
comment on column profiles.model is 'LLM model for assistants (e.g., "gpt-4", "claude-3")';
comment on column profiles.queue_name is 'Queue name for assistant job processing';
comment on column profiles.system_prompt is 'Base personality/instructions for assistant';

create index idx_profiles_type on profiles(type);
create index idx_profiles_email on profiles(email) where email is not null;

-- ============================================================================
-- MEMBERS (Workspace Memberships)
-- ============================================================================

create table members (
    id uuid primary key default gen_random_uuid(),
    workspace_id uuid not null references workspaces(id) on delete cascade,
    profile_id uuid not null references profiles(id) on delete cascade,
    role member_role not null default 'member',
    custom_prompt text,
    created_at timestamptz not null default now(),
    updated_at timestamptz not null default now(),

    constraint unique_workspace_member unique(workspace_id, profile_id)
);

comment on table members is 'Workspace memberships for users and assistants';
comment on column members.custom_prompt is 'Workspace-level customization for assistant prompts';

create index idx_members_workspace on members(workspace_id);
create index idx_members_profile on members(profile_id);

-- ============================================================================
-- CHANNELS
-- ============================================================================

create table channels (
    id uuid primary key default gen_random_uuid(),
    workspace_id uuid not null references workspaces(id) on delete cascade,
    name text not null,
    short_name text not null,
    description text,
    primary_assistant_id uuid references profiles(id) on delete set null,
    settings jsonb default '{}'::jsonb,
    created_at timestamptz not null default now(),
    updated_at timestamptz not null default now(),

    constraint unique_workspace_channel unique(workspace_id, short_name),
    constraint short_name_format check (short_name ~ '^[a-z0-9-]+$'),
    constraint short_name_length check (char_length(short_name) >= 2 and char_length(short_name) <= 32)
);

comment on table channels is 'Communication channels within workspaces';
comment on column channels.short_name is 'Email user part (e.g., "support" → support@acme.example.com)';
comment on column channels.primary_assistant_id is 'Default assistant for responding to emails';

create index idx_channels_workspace on channels(workspace_id);
create index idx_channels_workspace_short_name on channels(workspace_id, short_name);
create index idx_channels_primary_assistant on channels(primary_assistant_id) where primary_assistant_id is not null;

-- ============================================================================
-- PARTICIPANTS (Channel Memberships)
-- ============================================================================

create table participants (
    id uuid primary key default gen_random_uuid(),
    workspace_id uuid not null references workspaces(id) on delete cascade,
    channel_id uuid not null references channels(id) on delete cascade,
    profile_id uuid not null references profiles(id) on delete cascade,
    custom_prompt text,
    created_at timestamptz not null default now(),
    updated_at timestamptz not null default now(),

    constraint unique_channel_participant unique(channel_id, profile_id)
);

comment on table participants is 'Channel memberships for users and assistants';
comment on column participants.custom_prompt is 'Channel-level customization for assistant prompts';

create index idx_participants_workspace on participants(workspace_id);
create index idx_participants_channel on participants(channel_id);
create index idx_participants_profile on participants(profile_id);

-- ============================================================================
-- MESSAGES (STI: chat and email)
-- ============================================================================

create table messages (
    id uuid primary key default gen_random_uuid(),
    workspace_id uuid not null references workspaces(id) on delete cascade,
    channel_id uuid not null references channels(id) on delete cascade,
    type message_type not null default 'chat',
    from_member_id uuid references members(id) on delete set null,
    to_member_id uuid references members(id) on delete set null,
    reply_to_id uuid references messages(id) on delete set null,
    status message_status not null default 'pending',
    processing_stage text,
    email_message_id text,
    email_subject text,
    email_to text[],
    email_cc text[],
    email_bcc text[],
    email_html text,
    content_text text not null,
    content_markdown text,
    content_html text,
    content_parts jsonb,
    sentiment sentiment_type,
    sentiment_score float,
    sentiment_details jsonb,
    metadata jsonb default '{}'::jsonb,
    created_at timestamptz not null default now(),
    updated_at timestamptz not null default now(),

    constraint sentiment_score_range check (sentiment_score is null or (sentiment_score >= -1.0 and sentiment_score <= 1.0)),
    constraint from_or_to_required check (from_member_id is not null or to_member_id is not null)
);

comment on table messages is 'Messages (chat and email) with STI via type column';
comment on column messages.type is 'Discriminator: chat or email';
comment on column messages.status is 'Processing status: pending → processing → processed/sent/failed';
comment on column messages.processing_stage is 'Current processing step (e.g., "downloading_attachments", "generating_response")';
comment on column messages.email_message_id is 'External email message ID from provider';
comment on column messages.content_text is 'Plain text content (always present)';
comment on column messages.content_markdown is 'Markdown representation';
comment on column messages.content_html is 'HTML representation for emails';
comment on column messages.content_parts is 'Rich message parts (AI responses, chat)';
comment on column messages.sentiment is 'Overall sentiment classification';
comment on column messages.sentiment_score is 'Sentiment score (-1.0 to 1.0)';

create index idx_messages_workspace on messages(workspace_id);
create index idx_messages_channel on messages(channel_id);
create index idx_messages_status on messages(status);
create index idx_messages_type on messages(type);
create index idx_messages_created_at on messages(created_at desc);
create index idx_messages_reply_to on messages(reply_to_id) where reply_to_id is not null;
create index idx_messages_email_message_id on messages(email_message_id) where email_message_id is not null;

-- ============================================================================
-- ATTACHMENTS
-- ============================================================================

create table attachments (
    id uuid primary key default gen_random_uuid(),
    workspace_id uuid not null references workspaces(id) on delete cascade,
    message_id uuid not null references messages(id) on delete cascade,
    filename text not null,
    content_type text not null,
    size_bytes bigint not null,
    storage_path text,
    status attachment_status not null default 'pending',
    processing_error text,
    ocr_text text,
    ocr_metadata jsonb,
    metadata jsonb default '{}'::jsonb,
    created_at timestamptz not null default now(),
    updated_at timestamptz not null default now(),

    constraint size_positive check (size_bytes > 0)
);

comment on table attachments is 'Email and chat attachments with OCR/processing support';
comment on column attachments.storage_path is 'Path in Supabase Storage';
comment on column attachments.status is 'Processing status: pending → downloaded → needs_processing → processed/failed';
comment on column attachments.processing_error is 'Error message if processing failed';
comment on column attachments.ocr_text is 'Extracted text from OCR';
comment on column attachments.ocr_metadata is 'OCR processing metadata';

create index idx_attachments_workspace on attachments(workspace_id);
create index idx_attachments_message on attachments(message_id);
create index idx_attachments_status on attachments(status);

-- ============================================================================
-- STORAGE BUCKETS
-- ============================================================================

insert into storage.buckets (id, name, public)
values ('attachments', 'attachments', false)
on conflict (id) do nothing;

-- ============================================================================
-- ROW LEVEL SECURITY (RLS)
-- ============================================================================

alter table workspaces enable row level security;
alter table profiles enable row level security;
alter table members enable row level security;
alter table channels enable row level security;
alter table participants enable row level security;
alter table messages enable row level security;
alter table attachments enable row level security;

-- Service role has full access (for edge functions and workers)
create policy "Service role has full access to workspaces"
    on workspaces for all
    to service_role
    using (true)
    with check (true);

create policy "Service role has full access to profiles"
    on profiles for all
    to service_role
    using (true)
    with check (true);

create policy "Service role has full access to members"
    on members for all
    to service_role
    using (true)
    with check (true);

create policy "Service role has full access to channels"
    on channels for all
    to service_role
    using (true)
    with check (true);

create policy "Service role has full access to participants"
    on participants for all
    to service_role
    using (true)
    with check (true);

create policy "Service role has full access to messages"
    on messages for all
    to service_role
    using (true)
    with check (true);

create policy "Service role has full access to attachments"
    on attachments for all
    to service_role
    using (true)
    with check (true);

-- Storage policies for attachments bucket
create policy "Service role can manage attachments"
    on storage.objects for all
    to service_role
    using (bucket_id = 'attachments')
    with check (bucket_id = 'attachments');

-- ============================================================================
-- UPDATED_AT TRIGGERS
-- ============================================================================

create or replace function update_updated_at_column()
returns trigger as $$
begin
    new.updated_at = now();
    return new;
end;
$$ language plpgsql;

create trigger update_workspaces_updated_at
    before update on workspaces
    for each row
    execute function update_updated_at_column();

create trigger update_profiles_updated_at
    before update on profiles
    for each row
    execute function update_updated_at_column();

create trigger update_members_updated_at
    before update on members
    for each row
    execute function update_updated_at_column();

create trigger update_channels_updated_at
    before update on channels
    for each row
    execute function update_updated_at_column();

create trigger update_participants_updated_at
    before update on participants
    for each row
    execute function update_updated_at_column();

create trigger update_messages_updated_at
    before update on messages
    for each row
    execute function update_updated_at_column();

create trigger update_attachments_updated_at
    before update on attachments
    for each row
    execute function update_updated_at_column();

-- ============================================================================
-- HELPER FUNCTIONS
-- ============================================================================

create or replace function get_workspace_by_subdomain(subdomain text)
returns uuid as $$
    select id from workspaces where short_name = subdomain limit 1;
$$ language sql stable;

comment on function get_workspace_by_subdomain is 'Look up workspace ID by subdomain (short_name)';

create or replace function get_channel_by_user(workspace_id_param uuid, user_part text)
returns uuid as $$
    select id from channels
    where workspace_id = workspace_id_param
    and short_name = user_part
    limit 1;
$$ language sql stable;

comment on function get_channel_by_user is 'Look up channel ID by workspace and email user part (short_name)';

create or replace function is_workspace_member(workspace_id_param uuid, email_param text)
returns boolean as $$
    select exists(
        select 1
        from members m
        join profiles p on p.id = m.profile_id
        where m.workspace_id = workspace_id_param
        and p.email = email_param
        and p.type = 'user'
    );
$$ language sql stable;

comment on function is_workspace_member is 'Check if email belongs to a workspace member';
