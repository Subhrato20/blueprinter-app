-- Blueprint Snap Database Schema
-- Dev DNA Edition

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "vector";

-- Create custom types
CREATE TYPE plan_status AS ENUM ('draft', 'active', 'completed', 'archived');
CREATE TYPE event_type AS ENUM ('plan_created', 'plan_updated', 'plan_patched', 'cursor_link_created', 'file_downloaded');

-- Projects table
CREATE TABLE projects (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    owner UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    name TEXT NOT NULL,
    description TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Style profiles table for user coding preferences
CREATE TABLE style_profiles (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    tokens JSONB NOT NULL DEFAULT '{}',
    embedding VECTOR(1536), -- OpenAI embedding dimension
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(user_id)
);

-- Development patterns table
CREATE TABLE patterns (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    slug TEXT UNIQUE NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    template JSONB NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Plans table
CREATE TABLE plans (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    project_id UUID NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    plan_json JSONB NOT NULL,
    status plan_status DEFAULT 'draft',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Plan messages table for Ask Copilot interactions
CREATE TABLE plan_messages (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    plan_id UUID NOT NULL REFERENCES plans(id) ON DELETE CASCADE,
    user_question TEXT NOT NULL,
    node_path TEXT NOT NULL,
    selection_text TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Plan revisions table for tracking changes
CREATE TABLE plan_revisions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    plan_id UUID NOT NULL REFERENCES plans(id) ON DELETE CASCADE,
    message_id UUID REFERENCES plan_messages(id) ON DELETE SET NULL,
    patch JSONB NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Development events table for analytics
CREATE TABLE dev_events (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    event_type event_type NOT NULL,
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    project_id UUID REFERENCES projects(id) ON DELETE CASCADE,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for better performance
CREATE INDEX idx_projects_owner ON projects(owner);
CREATE INDEX idx_style_profiles_user_id ON style_profiles(user_id);
CREATE INDEX idx_patterns_slug ON patterns(slug);
CREATE INDEX idx_plans_project_id ON plans(project_id);
CREATE INDEX idx_plans_user_id ON plans(user_id);
CREATE INDEX idx_plans_status ON plans(status);
CREATE INDEX idx_plan_messages_plan_id ON plan_messages(plan_id);
CREATE INDEX idx_plan_revisions_plan_id ON plan_revisions(plan_id);
CREATE INDEX idx_dev_events_user_id ON dev_events(user_id);
CREATE INDEX idx_dev_events_event_type ON dev_events(event_type);
CREATE INDEX idx_dev_events_created_at ON dev_events(created_at);

-- Create updated_at trigger function
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Add updated_at triggers
CREATE TRIGGER update_projects_updated_at BEFORE UPDATE ON projects
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_style_profiles_updated_at BEFORE UPDATE ON style_profiles
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_patterns_updated_at BEFORE UPDATE ON patterns
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_plans_updated_at BEFORE UPDATE ON plans
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Insert default patterns
INSERT INTO patterns (slug, name, description, template) VALUES
('api-search-pagination', 'API Search with Pagination', 'Standard API endpoint with search and pagination', '{
    "steps": [
        {"kind": "code", "target": "routes/api.ts", "summary": "Create API route with search and pagination"},
        {"kind": "code", "target": "services/search.ts", "summary": "Implement search service"},
        {"kind": "test", "target": "tests/api.test.ts", "summary": "Add API tests"},
        {"kind": "test", "target": "tests/search.test.ts", "summary": "Add search service tests"},
        {"kind": "config", "target": "config/database.ts", "summary": "Update database configuration"}
    ],
    "files": [],
    "risks": ["SQL injection", "Performance with large datasets", "Rate limiting"],
    "tests": ["Search functionality", "Pagination", "Error handling", "Performance"],
    "prBody": "Implement API search with pagination functionality"
}'),
('crud-operations', 'CRUD Operations', 'Complete CRUD operations for a resource', '{
    "steps": [
        {"kind": "code", "target": "models/resource.ts", "summary": "Create resource model"},
        {"kind": "code", "target": "routes/resource.ts", "summary": "Create CRUD routes"},
        {"kind": "code", "target": "services/resource.ts", "summary": "Implement business logic"},
        {"kind": "test", "target": "tests/resource.test.ts", "summary": "Add comprehensive tests"},
        {"kind": "config", "target": "middleware/validation.ts", "summary": "Add validation middleware"}
    ],
    "files": [],
    "risks": ["Data validation", "Authorization", "Concurrent updates"],
    "tests": ["Create operation", "Read operation", "Update operation", "Delete operation", "Validation"],
    "prBody": "Implement complete CRUD operations for resource"
}'),
('authentication', 'Authentication System', 'User authentication with JWT', '{
    "steps": [
        {"kind": "code", "target": "auth/jwt.ts", "summary": "Implement JWT utilities"},
        {"kind": "code", "target": "auth/middleware.ts", "summary": "Create auth middleware"},
        {"kind": "code", "target": "routes/auth.ts", "summary": "Create auth routes"},
        {"kind": "test", "target": "tests/auth.test.ts", "summary": "Add authentication tests"},
        {"kind": "config", "target": "config/auth.ts", "summary": "Configure authentication"}
    ],
    "files": [],
    "risks": ["Token security", "Password hashing", "Session management"],
    "tests": ["Login", "Logout", "Token validation", "Password reset"],
    "prBody": "Implement secure authentication system"
}');
