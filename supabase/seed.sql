-- ============================================================================
-- setup standard supabase auth
-- ============================================================================
-- Note: profiles table is now defined in email_processing_schema migration

-- Set up Storage
insert into storage.buckets (id, name)
values ('avatars', 'avatars');

create policy "Avatar images are publicly accessible."
  on storage.objects for select
  using ( bucket_id = 'avatars' );

create policy "Anyone can upload an avatar."
  on storage.objects for insert
  with check ( bucket_id = 'avatars' );

create policy "Anyone can update an avatar."
  on storage.objects for update
  with check ( bucket_id = 'avatars' );

-- ============================================================================
-- Create default queues
-- ============================================================================
select pgmq_public.create_queue('incoming-messages', true, 'aimq:jobs', 'job_enqueued');
select pgmq_public.create_queue('outgoing-messages', true, 'aimq:jobs', 'job_enqueued');
select pgmq_public.create_queue('default-assistant', true, 'aimq:jobs', 'job_enqueued');
select pgmq_public.create_queue('react-assistant', true, 'aimq:jobs', 'job_enqueued');

-- ============================================================================
-- Email Processing Test Data
-- ============================================================================

-- Test workspace: acme
insert into workspaces (id, name, short_name, settings)
values (
    '00000000-0000-0000-0000-000000000001',
    'Acme Corporation',
    'acme',
    '{"timezone": "America/Los_Angeles"}'::jsonb
);

-- Test assistant profile: Mindi
insert into profiles (id, type, name, email, model, queue_name, system_prompt)
values (
    '00000000-0000-0000-0000-000000000010',
    'assistant',
    'Mindi',
    null,
    'gpt-4',
    'default-assistant',
    'You are Mindi, a helpful AI assistant for Acme Corporation. You are professional, concise, and friendly. Always sign your emails with "Best regards, Mindi".'
);

-- Test user profile: John Doe
insert into profiles (id, type, name, email)
values (
    '00000000-0000-0000-0000-000000000011',
    'user',
    'John Doe',
    'john@example.com'
);

-- Test user profile: Jane Smith
insert into profiles (id, type, name, email)
values (
    '00000000-0000-0000-0000-000000000012',
    'user',
    'Jane Smith',
    'jane@example.com'
);

-- Add members to workspace
insert into members (workspace_id, profile_id, role)
values
    ('00000000-0000-0000-0000-000000000001', '00000000-0000-0000-0000-000000000010', 'member'), -- Mindi (assistant)
    ('00000000-0000-0000-0000-000000000001', '00000000-0000-0000-0000-000000000011', 'admin'),  -- John
    ('00000000-0000-0000-0000-000000000001', '00000000-0000-0000-0000-000000000012', 'member'); -- Jane

-- Test channel: support
insert into channels (id, workspace_id, name, short_name, description, primary_assistant_id)
values (
    '00000000-0000-0000-0000-000000000020',
    '00000000-0000-0000-0000-000000000001',
    'Support',
    'support',
    'Customer support channel',
    '00000000-0000-0000-0000-000000000010' -- Mindi as primary assistant
);

-- Test channel: engineering
insert into channels (id, workspace_id, name, short_name, description, primary_assistant_id)
values (
    '00000000-0000-0000-0000-000000000021',
    '00000000-0000-0000-0000-000000000001',
    'Engineering',
    'engineering',
    'Engineering team channel',
    '00000000-0000-0000-0000-000000000010' -- Mindi as primary assistant
);

-- Add participants to channels
insert into participants (workspace_id, channel_id, profile_id)
values
    -- Support channel
    ('00000000-0000-0000-0000-000000000001', '00000000-0000-0000-0000-000000000020', '00000000-0000-0000-0000-000000000010'), -- Mindi
    ('00000000-0000-0000-0000-000000000001', '00000000-0000-0000-0000-000000000020', '00000000-0000-0000-0000-000000000011'), -- John
    ('00000000-0000-0000-0000-000000000001', '00000000-0000-0000-0000-000000000020', '00000000-0000-0000-0000-000000000012'), -- Jane
    -- Engineering channel
    ('00000000-0000-0000-0000-000000000001', '00000000-0000-0000-0000-000000000021', '00000000-0000-0000-0000-000000000010'), -- Mindi
    ('00000000-0000-0000-0000-000000000001', '00000000-0000-0000-0000-000000000021', '00000000-0000-0000-0000-000000000011'); -- John
