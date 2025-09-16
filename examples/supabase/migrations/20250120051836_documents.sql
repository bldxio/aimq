-- Create storage bucket for documents
insert into storage.buckets (id, name)
values ('documents', 'documents')
on conflict do nothing;

-- Create policy to allow authenticated users to upload documents
create policy "Allow authenticated users to upload documents"
on storage.objects for insert
to authenticated
with check (
    bucket_id = 'documents'
    and (storage.foldername(name))[1] = auth.uid()::text
);

-- Create policy to allow users to read their own documents
create policy "Allow users to read their own documents"
on storage.objects for select
to authenticated
using (
    bucket_id = 'documents'
    and (storage.foldername(name))[1] = auth.uid()::text
);

-- Create table for document metadata
create table if not exists public.documents (
    id uuid primary key default gen_random_uuid(),
    user_id uuid references auth.users not null,
    storage_path text not null,
    original_name text not null,
    mime_type text not null,
    size_bytes bigint not null,
    created_at timestamptz not null default now(),
    processed_at timestamptz,
    error text,
    metadata jsonb
);

-- Set up RLS for documents table
alter table public.documents enable row level security;

create policy "Users can insert their own documents"
    on public.documents for insert
    to authenticated
    with check (user_id = auth.uid());

create policy "Users can view their own documents"
    on public.documents for select
    to authenticated
    using (user_id = auth.uid());
