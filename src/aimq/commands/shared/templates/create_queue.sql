-- Create a new queue named {{queue_name}}
select pgmq.create('{{queue_name}}');
alter table pgmq."q_{{queue_name}}" enable row level security;
