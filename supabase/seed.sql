-- ============================================================================
-- setup standard supabase auth
-- ============================================================================

create table profiles (
  id uuid references auth.users not null,
  updated_at timestamp with time zone,
  username text unique,
  avatar_url text,
  website text,

  primary key (id),
  unique(username),
  constraint username_length check (char_length(username) >= 3)
);

alter table profiles enable row level security;

create policy "Public profiles are viewable by the owner."
  on profiles for select
  using ( (select auth.uid()) = id );

create policy "Users can insert their own profile."
  on profiles for insert
  with check ( (select auth.uid()) = id );

create policy "Users can update own profile."
  on profiles for update
  using ( (select auth.uid()) = id );

-- Set up Realtime
begin;
  drop publication if exists supabase_realtime;
  create publication supabase_realtime;
commit;
alter publication supabase_realtime add table profiles;

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
