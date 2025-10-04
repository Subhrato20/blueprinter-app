# Blueprint Snap — Dev DNA Edition

**One-line idea → Plan JSON + style-adapted scaffolds + Ask-Copilot + Cursor deep link**

Blueprint Snap is an AI-powered development planning tool that transforms simple ideas into comprehensive development plans with style-adapted code scaffolds, intelligent copilot assistance, and seamless Cursor integration.

## 🚀 Features

- **AI-Powered Planning**: Generate complete development plans from one-line ideas using GPT-5
- **Style Adaptation**: Automatically adapt code to match your coding style preferences
- **Ask Copilot**: Get intelligent suggestions and modifications for any part of your plan
- **Real-time Collaboration**: Live updates and real-time plan modifications
- **Cursor Integration**: Deep link integration with VS Code/Cursor for seamless workflow
- **Pattern Library**: Pre-built development patterns for common scenarios
- **Secure**: HMAC-signed payloads and comprehensive security measures

## 🏗️ Architecture

### Backend (Python 3.11 + FastAPI)
- **LangGraph Orchestration**: Multi-step plan generation workflow
- **OpenAI Integration**: GPT-5 for intelligent plan generation and copilot responses
- **Supabase Integration**: Database, authentication, and real-time features
- **Security**: HMAC signing, input validation, and secure API endpoints

### Frontend (React 18 + TypeScript)
- **Modern UI**: Clean, responsive interface with Tailwind CSS
- **Real-time Updates**: Live plan modifications and collaboration
- **File Management**: Download ZIP files and manage generated code
- **Copilot Interface**: Interactive AI assistance for plan refinement

### Supabase (PostgreSQL + Edge Functions)
- **Database**: User profiles, projects, plans, and development events
- **Authentication**: GitHub OAuth integration
- **Real-time**: Live updates and collaboration features
- **Edge Functions**: Repository analysis for style profile extraction

### VS Code Extension
- **URI Handler**: Deep link integration with `vscode://` protocol
- **File Operations**: Safe file writing and workspace management
- **Task Execution**: Automatic task running after plan ingestion
- **Security**: HMAC verification and path validation

## 📋 Prerequisites

- **Python 3.11+**
- **Node.js 18+**
- **npm**
- **Supabase Account**
- **OpenAI API Key** (with GPT-5 access)
- **VS Code or Cursor** (for extension)

## 🛠️ Installation

### 1. Clone the Repository

```bash
git clone <repository-url>
cd blueprinter
```

### 2. Run Setup Script

```bash
python3 setup_env.py
```

This script will:
- Check prerequisites
- Create `.env` file with generated secrets
- Install all dependencies
- Set up configuration files

### 3. Configure Environment

Edit the `.env` file with your actual credentials:

```env
# OpenAI Configuration
OPENAI_API_KEY=sk-your-actual-openai-key
GPT5_MODEL=gpt-5-reasoning

# Supabase Configuration
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key
NEXT_PUBLIC_SUPABASE_URL=https://your-project.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=your-anon-key

# Security
HMAC_SECRET=your-generated-secret
```

### 4. Set Up Supabase

1. Create a new Supabase project
2. Run the SQL scripts:
   ```sql
   -- Run these in your Supabase SQL editor
   \i supabase/schema.sql
   \i supabase/policies.sql
   ```
3. Deploy the Edge Function:
   ```bash
   supabase functions deploy analyze_repo
   ```

### 5. Install VS Code Extension

```bash
cd cursor-extension
npm run package
# Install the generated .vsix file in VS Code
```

## 🚀 Usage

### Start Development Servers

```bash
# Start all services
npm run dev

# Or start individually
npm run dev:backend   # Backend only
npm run dev:frontend  # Frontend only
```

### Access the Application

- **Frontend**: http://localhost:5173
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs

### Generate a Plan

1. Sign in with GitHub
2. Create a new project
3. Enter your idea: "Add user search with pagination to the admin panel"
4. Click "Generate Plan"
5. Review the generated plan with steps, files, tests, and risks
6. Use "Ask Copilot" to refine specific parts
7. Download as ZIP or "Add to Cursor" for immediate development

## 🔧 API Endpoints

### Plan Generation
```http
POST /api/plan
Content-Type: application/json

{
  "idea": "Add user search with pagination",
  "projectId": "project-uuid"
}
```

### Ask Copilot
```http
POST /api/ask
Content-Type: application/json

{
  "planId": "plan-uuid",
  "nodePath": "/steps/0/summary",
  "selectionText": "Create API route",
  "userQuestion": "How can I improve this step?"
}
```

### Apply Patch
```http
POST /api/plan/patch
Content-Type: application/json

{
  "planId": "plan-uuid",
  "patch": [
    {
      "op": "replace",
      "path": "/steps/0/summary",
      "value": "Create API route with error handling"
    }
  ]
}
```

### Cursor Deep Link
```http
POST /api/cursor-link
Content-Type: application/json

{
  "planId": "plan-uuid"
}
```

## 🎯 Development Patterns

Blueprint Snap includes pre-built patterns for common development scenarios:

- **API Search with Pagination**: Standard API endpoints with search and pagination
- **CRUD Operations**: Complete CRUD operations for resources
- **Authentication System**: User authentication with JWT
- **Custom Patterns**: Add your own patterns to the database

## 🔒 Security

- **HMAC Signing**: All Cursor deep links are HMAC-signed
- **Input Validation**: Comprehensive validation of all inputs
- **Path Security**: Protection against directory traversal attacks
- **Authentication**: GitHub OAuth with Supabase integration
- **RLS Policies**: Row-level security for all database operations

## 🧪 Testing

```bash
# Backend tests
cd backend
pytest

# Frontend tests
cd frontend
npm test

# Extension tests
cd cursor-extension
npm test
```

## 📦 Building for Production

```bash
# Build frontend
npm run build:frontend

# Package extension
npm run package:extension

# Build backend (already built with pip install -e .)
```

## 🚀 Deployment

### Backend (FastAPI)
- Deploy to any Python hosting service (Railway, Render, Heroku)
- Set environment variables
- Ensure Python 3.11+ runtime

### Frontend (React)
- Build with `npm run build:frontend`
- Deploy to Vercel, Netlify, or any static hosting
- Set environment variables for API endpoints

### Supabase
- Use Supabase hosting for database and Edge Functions
- Configure custom domains if needed

### VS Code Extension
- Package with `npm run package:extension`
- Publish to VS Code Marketplace or distribute `.vsix` files

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

MIT License - see LICENSE file for details.

## 🆘 Troubleshooting

### Common Issues

**"HMAC secret not configured"**
- Set `blueprintSnap.secret` in VS Code settings
- Ensure the secret matches between backend and extension

**"Invalid signature"**
- Check that HMAC secrets match
- Verify payload hasn't been corrupted

**"OpenAI API error"**
- Verify your OpenAI API key has GPT-5 access
- Check API key permissions and billing

**"Supabase connection failed"**
- Verify Supabase URL and keys
- Check network connectivity
- Ensure RLS policies are properly configured

### Getting Help

- Check the [Issues](https://github.com/your-repo/issues) page
- Review the API documentation at `/docs`
- Check Supabase logs for database issues

## 🎉 Acknowledgments

- OpenAI for GPT-5 API
- Supabase for backend infrastructure
- LangGraph for workflow orchestration
- VS Code team for extension platform

---

**Blueprint Snap — Dev DNA Edition**  
*Transforming ideas into code, one plan at a time.*
