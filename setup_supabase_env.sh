#!/bin/bash

# Setup Supabase environment variables

echo "Setting up Supabase environment variables..."

# Frontend environment
cat > frontend/.env << EOF
VITE_SUPABASE_URL=https://ztpshxxkgoqmnutmcvpp.supabase.co
VITE_SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Inp0cHNoeHhrZ29xbW51dG1jdnBwIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTk1OTk3NTcsImV4cCI6MjA3NTE3NTc1N30.fbsl93-XAOO_U_zT09Oq-SaEW2A-VVebRKlPu-zbYz4
EOF

# Backend environment
cat > backend/.env << EOF
SUPABASE_URL=https://ztpshxxkgoqmnutmcvpp.supabase.co
SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Inp0cHNoeHhrZ29xbW51dG1jdnBwIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTk1OTk3NTcsImV4cCI6MjA3NTE3NTc1N30.fbsl93-XAOO_U_zT09Oq-SaEW2A-VVebRKlPu-zbYz4
SUPABASE_SERVICE_ROLE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Inp0cHNoeHhrZ29xbW51dG1jdnBwIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1OTU5OTc1NywiZXhwIjoyMDc1MTc1NzU3fQ.8Q8Q8Q8Q8Q8Q8Q8Q8Q8Q8Q8Q8Q8Q8Q8Q8Q8Q8Q8Q8Q
OPENAI_API_KEY=your-openai-api-key-here
DEBUG=true
EOF

echo "Environment files created successfully!"
echo ""
echo "Next steps:"
echo "1. Add your OpenAI API key to backend/.env"
echo "2. Restart the backend server"
echo "3. Refresh the frontend"
echo ""
echo "Your Supabase project is configured and ready!"
