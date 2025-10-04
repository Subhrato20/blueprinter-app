Blueprinter

A webapp that converts a one-line feature idea into a deterministic plan, scaffold, and PR body in the developer’s own code style.

- Backend: FastAPI + LangGraph (Python)
- Frontend: React + TypeScript (Vite)
- Database: Supabase (DB, RLS, Storage, Realtime)
- Edge Functions: Deno (repo analysis to style tokens)
- Cursor Extension: VS Code URI handler for scaffold handoff

Quick Start (dev)

- Backend: set env, run FastAPI
  - Copy `.env.example` to `.env` and fill values
  - `cd backend` then `uvicorn app.main:app --reload`
- Frontend: `cd frontend` then `npm i` and `npm run dev`
- Supabase:
  - Apply `supabase/schema.sql` then `supabase/policies.sql`
  - Create Storage buckets `repos` and `artifacts`
  - Deploy Edge Function `analyze_repo`
- Cursor extension: `cd cursor-extension` then `npm i` and `F5` to debug

See inline TODOs for hooking real Supabase + LLMs.
