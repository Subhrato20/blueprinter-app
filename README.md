# Blueprinter

A webapp that converts a one-line feature idea into a deterministic plan, scaffold, and PR body in the developer's own code style.

- Backend: FastAPI + LangGraph (Python) + OpenAI GPT-5
- Frontend: React + TypeScript (Vite)
- Database: Supabase (DB, RLS, Storage, Realtime)
- Edge Functions: Deno (repo analysis to style tokens)
- Cursor Extension: VS Code URI handler for scaffold handoff

## Quick Start (dev)

### 1. Backend Setup
```bash
# Set up environment
python3 setup_env.py  # Creates .env file
# Edit backend/.env and add your OpenAI API key

# Install dependencies and run
cd backend
source venv/bin/activate  # or create new venv
uvicorn app.main:app --reload
```

### 2. Frontend Setup
```bash
cd frontend
npm install
npm run dev
```

### 3. OpenAI Integration (Optional)
- Get OpenAI API key from https://platform.openai.com/
- Add to `backend/.env`: `OPENAI_API_KEY=your_key_here`
- Set model: `OPENAI_MODEL=gpt-5` (or gpt-4, gpt-3.5-turbo)
- Restart backend server

### 4. Supabase (Optional)
- Apply `supabase/schema.sql` then `supabase/policies.sql`
- Create Storage buckets `repos` and `artifacts`
- Deploy Edge Function `analyze_repo`

### 5. Cursor Extension (Optional)
```bash
cd cursor-extension
npm install
# Press F5 in VS Code to debug
```

## Features

- **AI-Powered Plan Generation**: Uses GPT-5 to create intelligent development plans
- **Style-Aware Code Generation**: Adapts to your coding preferences
- **Interactive Copilot**: Ask questions and get AI-powered suggestions
- **Fallback Mode**: Works without OpenAI (deterministic responses)
