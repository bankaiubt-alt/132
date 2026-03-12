create schema if not exists private;
create schema if not exists extensions;

create extension if not exists pgcrypto with schema extensions;

create or replace function public.set_updated_at()
returns trigger
language plpgsql
as $$
begin
  new.updated_at = now();
  return new;
end;
$$;

create table if not exists private.parent_accounts (
  id uuid primary key default extensions.gen_random_uuid(),
  full_name text not null check (char_length(trim(full_name)) >= 3),
  username text not null,
  password_hash text not null,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create unique index if not exists parent_accounts_username_lower_idx
on private.parent_accounts ((lower(username)));

drop trigger if exists set_parent_accounts_updated_at on private.parent_accounts;
create trigger set_parent_accounts_updated_at
before update on private.parent_accounts
for each row execute function public.set_updated_at();

revoke all on schema private from public;
revoke all on schema private from anon;
revoke all on schema private from authenticated;
revoke all on all tables in schema private from public;
revoke all on all tables in schema private from anon;
revoke all on all tables in schema private from authenticated;

create or replace function public.parent_register(
  p_full_name text,
  p_password text,
  p_username text
)
returns table (
  parent_id uuid,
  full_name text,
  username text
)
language plpgsql
security definer
set search_path = public, private, extensions
as $$
declare
  v_full_name text := trim(coalesce(p_full_name, ''));
  v_username text := lower(trim(coalesce(p_username, '')));
  v_password text := coalesce(p_password, '');
begin
  if char_length(v_full_name) < 3 then
    raise exception 'Full name must be at least 3 characters';
  end if;

  if char_length(v_username) < 3 then
    raise exception 'Username must be at least 3 characters';
  end if;

  if char_length(v_password) < 6 then
    raise exception 'Password must be at least 6 characters';
  end if;

  if exists (
    select 1
    from private.parent_accounts pa
    where lower(pa.username) = v_username
  ) then
    raise exception 'Username already registered';
  end if;

  return query
  insert into private.parent_accounts (
    full_name,
    username,
    password_hash
  )
  values (
    v_full_name,
    v_username,
    crypt(v_password, extensions.gen_salt('bf'))
  )
  returning id, private.parent_accounts.full_name, private.parent_accounts.username;
end;
$$;

create or replace function public.parent_login(
  p_password text,
  p_username text
)
returns table (
  parent_id uuid,
  full_name text,
  username text
)
language sql
security definer
set search_path = public, private, extensions
as $$
  select
    pa.id as parent_id,
    pa.full_name,
    pa.username
  from private.parent_accounts pa
  where lower(pa.username) = lower(trim(p_username))
    and pa.password_hash = crypt(p_password, pa.password_hash)
  limit 1;
$$;

revoke all on function public.parent_register(text, text, text) from public;
revoke all on function public.parent_login(text, text) from public;

grant execute on function public.parent_register(text, text, text) to anon, authenticated;
grant execute on function public.parent_login(text, text) to anon, authenticated;

create table if not exists public.children (
  id uuid primary key default extensions.gen_random_uuid(),
  parent_id uuid not null references private.parent_accounts(id) on delete cascade,
  full_name text not null check (char_length(trim(full_name)) >= 2),
  age integer not null check (age between 1 and 18),
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create index if not exists children_parent_id_idx
on public.children (parent_id);

create table if not exists private.child_accounts (
  child_id uuid primary key references public.children(id) on delete cascade,
  parent_id uuid not null references private.parent_accounts(id) on delete cascade,
  username text not null,
  password_hash text not null,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create unique index if not exists child_accounts_username_lower_idx
on private.child_accounts ((lower(username)));

drop trigger if exists set_children_updated_at on public.children;
create trigger set_children_updated_at
before update on public.children
for each row execute function public.set_updated_at();

drop trigger if exists set_child_accounts_updated_at on private.child_accounts;
create trigger set_child_accounts_updated_at
before update on private.child_accounts
for each row execute function public.set_updated_at();

alter table public.children enable row level security;

revoke all on public.children from public;
revoke all on public.children from anon;
revoke all on public.children from authenticated;
revoke all on private.child_accounts from public;
revoke all on private.child_accounts from anon;
revoke all on private.child_accounts from authenticated;

drop function if exists public.parent_add_child(integer, text, text, text, text, text);
create function public.parent_add_child(
  p_child_age integer,
  p_child_name text,
  p_child_password text,
  p_child_username text,
  p_parent_password text,
  p_parent_username text
)
returns table (
  child_id uuid,
  child_name text,
  age integer,
  username text
)
language plpgsql
security definer
set search_path = public, private, extensions
as $$
declare
  v_parent_id uuid;
  v_child_id uuid;
  v_child_name text := trim(coalesce(p_child_name, ''));
  v_child_username text := lower(trim(coalesce(p_child_username, '')));
  v_child_password text := coalesce(p_child_password, '');
begin
  select pa.id
  into v_parent_id
  from private.parent_accounts pa
  where lower(pa.username) = lower(trim(coalesce(p_parent_username, '')))
    and pa.password_hash = crypt(coalesce(p_parent_password, ''), pa.password_hash)
  limit 1;

  if v_parent_id is null then
    raise exception 'Invalid parent credentials';
  end if;

  if char_length(v_child_name) < 2 then
    raise exception 'Child name must be at least 2 characters';
  end if;

  if p_child_age < 1 or p_child_age > 18 then
    raise exception 'Child age must be between 1 and 18 years';
  end if;

  if char_length(v_child_username) < 3 then
    raise exception 'Child username must be at least 3 characters';
  end if;

  if char_length(v_child_password) < 4 then
    raise exception 'Child password must be at least 4 characters';
  end if;

  if exists (
    select 1
    from private.child_accounts ca
    where lower(ca.username) = v_child_username
  ) then
    raise exception 'Child username already registered';
  end if;

  insert into public.children (
    parent_id,
    full_name,
    age
  )
  values (
    v_parent_id,
    v_child_name,
    p_child_age
  )
  returning id into v_child_id;

  insert into private.child_accounts (
    child_id,
    parent_id,
    username,
    password_hash
  )
  values (
    v_child_id,
    v_parent_id,
    v_child_username,
    crypt(v_child_password, extensions.gen_salt('bf'))
  );

  return query
  select
    c.id as child_id,
    c.full_name as child_name,
    c.age,
    ca.username
  from public.children c
  join private.child_accounts ca on ca.child_id = c.id
  where c.id = v_child_id;
end;
$$;

drop function if exists public.parent_list_children(text, text);
create function public.parent_list_children(
  p_parent_password text,
  p_parent_username text
)
returns table (
  child_id uuid,
  child_name text,
  age integer,
  username text
)
language plpgsql
security definer
set search_path = public, private, extensions
as $$
declare
  v_parent_id uuid;
begin
  select pa.id
  into v_parent_id
  from private.parent_accounts pa
  where lower(pa.username) = lower(trim(coalesce(p_parent_username, '')))
    and pa.password_hash = crypt(coalesce(p_parent_password, ''), pa.password_hash)
  limit 1;

  if v_parent_id is null then
    raise exception 'Invalid parent credentials';
  end if;

  return query
  select
    c.id as child_id,
    c.full_name as child_name,
    c.age,
    ca.username
  from public.children c
  join private.child_accounts ca on ca.child_id = c.id
  where c.parent_id = v_parent_id
  order by c.created_at desc;
end;
$$;

drop function if exists public.parent_update_child(uuid, integer, text, text, text, text, text);
create function public.parent_update_child(
  p_child_id uuid,
  p_child_age integer,
  p_child_name text,
  p_child_password text,
  p_child_username text,
  p_parent_password text,
  p_parent_username text
)
returns table (
  child_id uuid,
  child_name text,
  age integer,
  username text
)
language plpgsql
security definer
set search_path = public, private, extensions
as $$
declare
  v_parent_id uuid;
  v_child_name text := trim(coalesce(p_child_name, ''));
  v_child_username text := lower(trim(coalesce(p_child_username, '')));
  v_child_password text := coalesce(p_child_password, '');
begin
  select pa.id
  into v_parent_id
  from private.parent_accounts pa
  where lower(pa.username) = lower(trim(coalesce(p_parent_username, '')))
    and pa.password_hash = crypt(coalesce(p_parent_password, ''), pa.password_hash)
  limit 1;

  if v_parent_id is null then
    raise exception 'Invalid parent credentials';
  end if;

  if not exists (
    select 1
    from public.children c
    where c.id = p_child_id
      and c.parent_id = v_parent_id
  ) then
    raise exception 'Child not found or access denied';
  end if;

  if char_length(v_child_name) < 2 then
    raise exception 'Child name must be at least 2 characters';
  end if;

  if p_child_age < 1 or p_child_age > 18 then
    raise exception 'Child age must be between 1 and 18 years';
  end if;

  if char_length(v_child_username) < 3 then
    raise exception 'Child username must be at least 3 characters';
  end if;

  if v_child_password <> '' and char_length(v_child_password) < 4 then
    raise exception 'Child password must be at least 4 characters';
  end if;

  if exists (
    select 1
    from private.child_accounts ca
    where lower(ca.username) = v_child_username
      and ca.child_id <> p_child_id
  ) then
    raise exception 'Child username already registered';
  end if;

  update public.children
  set
    full_name = v_child_name,
    age = p_child_age,
    updated_at = now()
  where id = p_child_id
    and parent_id = v_parent_id;

  update private.child_accounts as ca
  set
    username = v_child_username,
    password_hash = case
      when v_child_password = '' then password_hash
      else crypt(v_child_password, extensions.gen_salt('bf'))
    end,
    updated_at = now()
  where ca.child_id = p_child_id
    and ca.parent_id = v_parent_id;

  return query
  select
    c.id as child_id,
    c.full_name as child_name,
    c.age,
    ca.username
  from public.children c
  join private.child_accounts ca on ca.child_id = c.id
  where c.id = p_child_id;
end;
$$;

drop function if exists public.parent_delete_child(uuid, text, text);
create function public.parent_delete_child(
  p_child_id uuid,
  p_parent_password text,
  p_parent_username text
)
returns void
language plpgsql
security definer
set search_path = public, private, extensions
as $$
declare
  v_parent_id uuid;
begin
  select pa.id
  into v_parent_id
  from private.parent_accounts pa
  where lower(pa.username) = lower(trim(coalesce(p_parent_username, '')))
    and pa.password_hash = crypt(coalesce(p_parent_password, ''), pa.password_hash)
  limit 1;

  if v_parent_id is null then
    raise exception 'Invalid parent credentials';
  end if;

  if not exists (
    select 1
    from public.children c
    where c.id = p_child_id
      and c.parent_id = v_parent_id
  ) then
    raise exception 'Child not found or access denied';
  end if;

  delete from private.child_accounts
  where child_id = p_child_id
    and parent_id = v_parent_id;

  delete from public.children
  where id = p_child_id
    and parent_id = v_parent_id;
end;
$$;

drop function if exists public.child_login(text, text);
create function public.child_login(
  p_password text,
  p_username text
)
returns table (
  child_id uuid,
  child_name text,
  age integer,
  username text
)
language sql
security definer
set search_path = public, private, extensions
as $$
  select
    c.id as child_id,
    c.full_name as child_name,
    c.age,
    ca.username
  from private.child_accounts ca
  join public.children c on c.id = ca.child_id
  where lower(ca.username) = lower(trim(coalesce(p_username, '')))
    and ca.password_hash = crypt(coalesce(p_password, ''), ca.password_hash)
  limit 1;
$$;

revoke all on function public.parent_add_child(integer, text, text, text, text, text) from public;
revoke all on function public.parent_list_children(text, text) from public;
revoke all on function public.parent_update_child(uuid, integer, text, text, text, text, text) from public;
revoke all on function public.parent_delete_child(uuid, text, text) from public;
revoke all on function public.child_login(text, text) from public;

grant execute on function public.parent_add_child(integer, text, text, text, text, text) to anon, authenticated;
grant execute on function public.parent_list_children(text, text) to anon, authenticated;
grant execute on function public.parent_update_child(uuid, integer, text, text, text, text, text) to anon, authenticated;
grant execute on function public.parent_delete_child(uuid, text, text) to anon, authenticated;
grant execute on function public.child_login(text, text) to anon, authenticated;

notify pgrst, 'reload schema';
