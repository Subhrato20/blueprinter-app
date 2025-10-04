-- Row Level Security (RLS) Policies for Blueprint Snap

-- Enable RLS on all tables
ALTER TABLE projects ENABLE ROW LEVEL SECURITY;
ALTER TABLE style_profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE patterns ENABLE ROW LEVEL SECURITY;
ALTER TABLE plans ENABLE ROW LEVEL SECURITY;
ALTER TABLE plan_messages ENABLE ROW LEVEL SECURITY;
ALTER TABLE plan_revisions ENABLE ROW LEVEL SECURITY;
ALTER TABLE dev_events ENABLE ROW LEVEL SECURITY;

-- Projects policies
CREATE POLICY "Users can view their own projects" ON projects
    FOR SELECT USING (auth.uid() = owner);

CREATE POLICY "Users can create their own projects" ON projects
    FOR INSERT WITH CHECK (auth.uid() = owner);

CREATE POLICY "Users can update their own projects" ON projects
    FOR UPDATE USING (auth.uid() = owner);

CREATE POLICY "Users can delete their own projects" ON projects
    FOR DELETE USING (auth.uid() = owner);

-- Style profiles policies
CREATE POLICY "Users can view their own style profile" ON style_profiles
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can create their own style profile" ON style_profiles
    FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update their own style profile" ON style_profiles
    FOR UPDATE USING (auth.uid() = user_id);

CREATE POLICY "Users can delete their own style profile" ON style_profiles
    FOR DELETE USING (auth.uid() = user_id);

-- Patterns policies (public read access)
CREATE POLICY "Anyone can view patterns" ON patterns
    FOR SELECT USING (true);

CREATE POLICY "Only service role can manage patterns" ON patterns
    FOR ALL USING (auth.role() = 'service_role');

-- Plans policies
CREATE POLICY "Users can view their own plans" ON plans
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can create their own plans" ON plans
    FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update their own plans" ON plans
    FOR UPDATE USING (auth.uid() = user_id);

CREATE POLICY "Users can delete their own plans" ON plans
    FOR DELETE USING (auth.uid() = user_id);

-- Plan messages policies
CREATE POLICY "Users can view messages for their plans" ON plan_messages
    FOR SELECT USING (
        EXISTS (
            SELECT 1 FROM plans 
            WHERE plans.id = plan_messages.plan_id 
            AND plans.user_id = auth.uid()
        )
    );

CREATE POLICY "Users can create messages for their plans" ON plan_messages
    FOR INSERT WITH CHECK (
        EXISTS (
            SELECT 1 FROM plans 
            WHERE plans.id = plan_messages.plan_id 
            AND plans.user_id = auth.uid()
        )
    );

CREATE POLICY "Users can update messages for their plans" ON plan_messages
    FOR UPDATE USING (
        EXISTS (
            SELECT 1 FROM plans 
            WHERE plans.id = plan_messages.plan_id 
            AND plans.user_id = auth.uid()
        )
    );

CREATE POLICY "Users can delete messages for their plans" ON plan_messages
    FOR DELETE USING (
        EXISTS (
            SELECT 1 FROM plans 
            WHERE plans.id = plan_messages.plan_id 
            AND plans.user_id = auth.uid()
        )
    );

-- Plan revisions policies
CREATE POLICY "Users can view revisions for their plans" ON plan_revisions
    FOR SELECT USING (
        EXISTS (
            SELECT 1 FROM plans 
            WHERE plans.id = plan_revisions.plan_id 
            AND plans.user_id = auth.uid()
        )
    );

CREATE POLICY "Users can create revisions for their plans" ON plan_revisions
    FOR INSERT WITH CHECK (
        EXISTS (
            SELECT 1 FROM plans 
            WHERE plans.id = plan_revisions.plan_id 
            AND plans.user_id = auth.uid()
        )
    );

-- Dev events policies
CREATE POLICY "Users can view their own dev events" ON dev_events
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can create their own dev events" ON dev_events
    FOR INSERT WITH CHECK (auth.uid() = user_id);

-- Create functions for real-time subscriptions
CREATE OR REPLACE FUNCTION get_user_plans(user_uuid UUID)
RETURNS TABLE(id UUID, project_id UUID, plan_json JSONB, status plan_status, created_at TIMESTAMP WITH TIME ZONE, updated_at TIMESTAMP WITH TIME ZONE)
LANGUAGE sql SECURITY DEFINER
AS $$
    SELECT p.id, p.project_id, p.plan_json, p.status, p.created_at, p.updated_at
    FROM plans p
    WHERE p.user_id = user_uuid;
$$;

CREATE OR REPLACE FUNCTION get_plan_messages(plan_uuid UUID)
RETURNS TABLE(id UUID, user_question TEXT, node_path TEXT, selection_text TEXT, created_at TIMESTAMP WITH TIME ZONE)
LANGUAGE sql SECURITY DEFINER
AS $$
    SELECT pm.id, pm.user_question, pm.node_path, pm.selection_text, pm.created_at
    FROM plan_messages pm
    WHERE pm.plan_id = plan_uuid;
$$;

-- Grant necessary permissions
GRANT USAGE ON SCHEMA public TO authenticated;
GRANT ALL ON ALL TABLES IN SCHEMA public TO authenticated;
GRANT ALL ON ALL SEQUENCES IN SCHEMA public TO authenticated;
GRANT EXECUTE ON ALL FUNCTIONS IN SCHEMA public TO authenticated;

-- Grant permissions to service role
GRANT ALL ON ALL TABLES IN SCHEMA public TO service_role;
GRANT ALL ON ALL SEQUENCES IN SCHEMA public TO service_role;
GRANT EXECUTE ON ALL FUNCTIONS IN SCHEMA public TO service_role;
