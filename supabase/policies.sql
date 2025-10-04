-- Enable RLS
alter table public.projects enable row level security;
alter table public.style_profiles enable row level security;
alter table public.patterns enable row level security;
alter table public.plans enable row level security;
alter table public.plan_messages enable row level security;
alter table public.plan_revisions enable row level security;
alter table public.dev_events enable row level security;

-- Projects: owner RW
create policy if not exists projects_owner_read on public.projects
  for select using (auth.uid() = owner);
create policy if not exists projects_owner_write on public.projects
  for all using (auth.uid() = owner);

-- Style profiles: owner RW
create policy if not exists style_owner_read on public.style_profiles
  for select using (auth.uid() = user_id);
create policy if not exists style_owner_write on public.style_profiles
  for all using (auth.uid() = user_id);

-- Patterns: public read
create policy if not exists patterns_public_read on public.patterns
  for select using (true);
revoke all on public.patterns from anon, authenticated;
grant select on public.patterns to anon, authenticated;

-- Plans: project owner RW
create policy if not exists plans_owner_read on public.plans
  for select using (exists (
    select 1 from public.projects p where p.id = plans.project_id and p.owner = auth.uid()
  ));
create policy if not exists plans_owner_write on public.plans
  for all using (exists (
    select 1 from public.projects p where p.id = plans.project_id and p.owner = auth.uid()
  ));

-- Plan messages/revisions inherit via plan
create policy if not exists plan_msgs_owner_read on public.plan_messages
  for select using (exists (
    select 1 from public.plans pl join public.projects pr on pr.id = pl.project_id
    where pl.id = plan_messages.plan_id and pr.owner = auth.uid()
  ));
create policy if not exists plan_msgs_owner_write on public.plan_messages
  for all using (exists (
    select 1 from public.plans pl join public.projects pr on pr.id = pl.project_id
    where pl.id = plan_messages.plan_id and pr.owner = auth.uid()
  ));

create policy if not exists plan_revs_owner_read on public.plan_revisions
  for select using (exists (
    select 1 from public.plans pl join public.projects pr on pr.id = pl.project_id
    where pl.id = plan_revisions.plan_id and pr.owner = auth.uid()
  ));
create policy if not exists plan_revs_owner_write on public.plan_revisions
  for all using (exists (
    select 1 from public.plans pl join public.projects pr on pr.id = pl.project_id
    where pl.id = plan_revisions.plan_id and pr.owner = auth.uid()
  ));

