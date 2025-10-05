-- Fetch History Migration
-- Track all API fetch operations for audit and history purposes

-- Create fetch history table
CREATE TABLE IF NOT EXISTS fetch_history (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    endpoint TEXT NOT NULL,
    method TEXT NOT NULL,
    request_data JSONB,
    response_data JSONB,
    status_code INTEGER,
    duration_ms INTEGER,
    error_message TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for efficient querying
CREATE INDEX idx_fetch_history_user_id ON fetch_history(user_id);
CREATE INDEX idx_fetch_history_endpoint ON fetch_history(endpoint);
CREATE INDEX idx_fetch_history_created_at ON fetch_history(created_at DESC);
CREATE INDEX idx_fetch_history_method ON fetch_history(method);
CREATE INDEX idx_fetch_history_status_code ON fetch_history(status_code);

-- Add comment for documentation
COMMENT ON TABLE fetch_history IS 'Tracks all API fetch operations including requests, responses, and performance metrics';
