-- Enable extensions
create extension if not exists vector;

-- Auth note: expects GitHub OAuth configured in Supabase project.

-- Projects
create table if not exists public.projects (
  id uuid primary key default gen_random_uuid(),
  name text not null,
  owner uuid not null references auth.users(id),
  created_at timestamp with time zone default now()
);

-- Style profiles (per user)
create table if not exists public.style_profiles (
  user_id uuid primary key references auth.users(id),
  tokens jsonb not null,
  embedding vector(384),
  updated_at timestamp with time zone default now()
);

-- Patterns (public)
create table if not exists public.patterns (
  slug text primary key,
  template jsonb not null,
  created_at timestamp with time zone default now()
);

-- Plans
create table if not exists public.plans (
  id uuid primary key default gen_random_uuid(),
  project_id uuid not null references public.projects(id) on delete cascade,
  plan_json jsonb not null,
  created_at timestamp with time zone default now()
);

-- Plan messages (Ask Copilot chat)
create table if not exists public.plan_messages (
  id uuid primary key default gen_random_uuid(),
  plan_id uuid not null references public.plans(id) on delete cascade,
  role text not null check (role in ('system','user','assistant')),
  message jsonb not null,
  created_at timestamp with time zone default now()
);

-- Plan revisions (JSON Patch history)
create table if not exists public.plan_revisions (
  id uuid primary key default gen_random_uuid(),
  plan_id uuid not null references public.plans(id) on delete cascade,
  patch jsonb not null,
  rationale text,
  created_at timestamp with time zone default now()
);

-- Dev events (audit/telemetry)
create table if not exists public.dev_events (
  id uuid primary key default gen_random_uuid(),
  project_id uuid references public.projects(id) on delete set null,
  user_id uuid references auth.users(id) on delete set null,
  kind text not null,
  data jsonb,
  created_at timestamp with time zone default now()
);

-- Storage buckets expected: repos (repo zips), artifacts (scaffold zips)

