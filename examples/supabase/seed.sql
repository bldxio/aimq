-- Create a test user
insert into auth.users (id, email)
values 
    ('00000000-0000-0000-0000-000000000000', 'test@example.com')
on conflict do nothing;
