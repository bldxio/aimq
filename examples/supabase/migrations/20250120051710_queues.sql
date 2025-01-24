-- Create PGMQ queues for example tasks
select pgmq.create('uppercase_text');
alter table pgmq."q_uppercase_text" enable row level security;

select pgmq.create('text_stats');
alter table pgmq."q_text_stats" enable row level security;

-- Create PGMQ queues for document processing and indexing
select pgmq.create('document_processing');
alter table pgmq."q_document_processing" enable row level security;

select pgmq.create('document_indexing');
alter table pgmq."q_document_indexing" enable row level security;

select pgmq.create('upload_document');
alter table pgmq."q_upload_document" enable row level security;
