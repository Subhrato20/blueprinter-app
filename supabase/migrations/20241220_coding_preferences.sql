-- Enhanced Coding Preferences Vector Database
-- This migration adds comprehensive coding preference tracking with vector embeddings

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS "vector";

-- Create enum types for coding preferences
CREATE TYPE preference_category AS ENUM (
    'frontend_framework', 
    'backend_pattern', 
    'code_style', 
    'architecture', 
    'testing', 
    'deployment',
    'documentation',
    'naming_convention'
);

CREATE TYPE preference_strength AS ENUM ('weak', 'moderate', 'strong', 'absolute');

-- Enhanced coding preferences table
CREATE TABLE coding_preferences (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    category preference_category NOT NULL,
    preference_text TEXT NOT NULL, -- The actual preference description
    context TEXT, -- Additional context about when this preference applies
    strength preference_strength DEFAULT 'moderate',
    embedding VECTOR(1536), -- OpenAI embedding for semantic search
    metadata JSONB DEFAULT '{}', -- Additional structured data
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(user_id, category, preference_text)
);

-- Coding signals table - tracks actual coding behaviors
CREATE TABLE coding_signals (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    signal_type TEXT NOT NULL, -- e.g., 'file_created', 'code_pattern_used', 'refactor_applied'
    signal_data JSONB NOT NULL, -- The actual signal data
    embedding VECTOR(1536), -- Embedding of the signal for similarity matching
    confidence_score FLOAT DEFAULT 1.0, -- How confident we are in this signal
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Preference patterns table - learned patterns from signals
CREATE TABLE preference_patterns (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    pattern_name TEXT NOT NULL,
    pattern_description TEXT,
    pattern_data JSONB NOT NULL, -- The learned pattern structure
    embedding VECTOR(1536), -- Embedding for pattern matching
    confidence_score FLOAT DEFAULT 0.0, -- How confident we are in this pattern
    signal_count INTEGER DEFAULT 0, -- Number of signals that contributed to this pattern
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for better performance
CREATE INDEX idx_coding_preferences_user_id ON coding_preferences(user_id);
CREATE INDEX idx_coding_preferences_category ON coding_preferences(category);
CREATE INDEX idx_coding_preferences_embedding ON coding_preferences USING hnsw (embedding vector_cosine_ops);

CREATE INDEX idx_coding_signals_user_id ON coding_signals(user_id);
CREATE INDEX idx_coding_signals_type ON coding_signals(signal_type);
CREATE INDEX idx_coding_signals_embedding ON coding_signals USING hnsw (embedding vector_cosine_ops);
CREATE INDEX idx_coding_signals_created_at ON coding_signals(created_at);

CREATE INDEX idx_preference_patterns_user_id ON preference_patterns(user_id);
CREATE INDEX idx_preference_patterns_embedding ON preference_patterns USING hnsw (embedding vector_cosine_ops);

-- Function to find similar coding preferences
CREATE OR REPLACE FUNCTION find_similar_preferences(
    user_id_param UUID,
    query_embedding VECTOR(1536),
    similarity_threshold FLOAT DEFAULT 0.7,
    max_results INTEGER DEFAULT 10
)
RETURNS TABLE (
    id UUID,
    category preference_category,
    preference_text TEXT,
    context TEXT,
    strength preference_strength,
    similarity FLOAT,
    metadata JSONB
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT 
        cp.id,
        cp.category,
        cp.preference_text,
        cp.context,
        cp.strength,
        1 - (cp.embedding <=> query_embedding) as similarity,
        cp.metadata
    FROM coding_preferences cp
    WHERE cp.user_id = user_id_param
        AND cp.embedding IS NOT NULL
        AND 1 - (cp.embedding <=> query_embedding) > similarity_threshold
    ORDER BY cp.embedding <=> query_embedding
    LIMIT max_results;
END;
$$;

-- Function to find similar coding signals
CREATE OR REPLACE FUNCTION find_similar_signals(
    user_id_param UUID,
    query_embedding VECTOR(1536),
    similarity_threshold FLOAT DEFAULT 0.7,
    max_results INTEGER DEFAULT 10
)
RETURNS TABLE (
    id UUID,
    signal_type TEXT,
    signal_data JSONB,
    similarity FLOAT,
    confidence_score FLOAT,
    created_at TIMESTAMP WITH TIME ZONE
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT 
        cs.id,
        cs.signal_type,
        cs.signal_data,
        1 - (cs.embedding <=> query_embedding) as similarity,
        cs.confidence_score,
        cs.created_at
    FROM coding_signals cs
    WHERE cs.user_id = user_id_param
        AND cs.embedding IS NOT NULL
        AND 1 - (cs.embedding <=> query_embedding) > similarity_threshold
    ORDER BY cs.embedding <=> query_embedding
    LIMIT max_results;
END;
$$;

-- Function to get user's coding style summary
CREATE OR REPLACE FUNCTION get_coding_style_summary(user_id_param UUID)
RETURNS TABLE (
    category preference_category,
    preference_count BIGINT,
    top_preferences TEXT[]
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT 
        cp.category,
        COUNT(*) as preference_count,
        ARRAY_AGG(cp.preference_text ORDER BY cp.strength DESC, cp.created_at DESC) as top_preferences
    FROM coding_preferences cp
    WHERE cp.user_id = user_id_param
    GROUP BY cp.category
    ORDER BY preference_count DESC;
END;
$$;

-- Add updated_at triggers
CREATE TRIGGER update_coding_preferences_updated_at 
    BEFORE UPDATE ON coding_preferences
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_preference_patterns_updated_at 
    BEFORE UPDATE ON preference_patterns
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Insert some example coding preferences
INSERT INTO coding_preferences (user_id, category, preference_text, context, strength, metadata) VALUES
-- You'll need to replace this with actual user_id from your auth.users table
-- (SELECT id FROM auth.users LIMIT 1), 'frontend_framework', 'Use TypeScript for all frontend code', 'Always prefer TypeScript over JavaScript for type safety', 'strong', '{"frameworks": ["typescript"], "reasons": ["type_safety", "better_ide_support"]}'),
-- (SELECT id FROM auth.users LIMIT 1), 'backend_pattern', 'Follow Uncle Bob principles - one class should do one thing', 'Apply Single Responsibility Principle consistently', 'strong', '{"principles": ["SOLID", "clean_code"], "author": "uncle_bob"}'),
-- (SELECT id FROM auth.users LIMIT 1), 'code_style', 'Use meaningful variable names', 'Avoid abbreviations and use descriptive names', 'moderate', '{"naming_convention": "descriptive", "avoid": ["abbreviations", "single_letters"]}'),
-- (SELECT id FROM auth.users LIMIT 1), 'architecture', 'Prefer composition over inheritance', 'Use composition patterns for better flexibility', 'moderate', '{"pattern": "composition", "benefits": ["flexibility", "testability"]}'),
-- (SELECT id FROM auth.users LIMIT 1), 'testing', 'Write tests before implementation (TDD)', 'Follow Test-Driven Development approach', 'strong', '{"methodology": "TDD", "order": ["red", "green", "refactor"]}');

-- Enable Row Level Security
ALTER TABLE coding_preferences ENABLE ROW LEVEL SECURITY;
ALTER TABLE coding_signals ENABLE ROW LEVEL SECURITY;
ALTER TABLE preference_patterns ENABLE ROW LEVEL SECURITY;

-- Create RLS policies
CREATE POLICY "Users can view their own coding preferences" ON coding_preferences
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can insert their own coding preferences" ON coding_preferences
    FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update their own coding preferences" ON coding_preferences
    FOR UPDATE USING (auth.uid() = user_id);

CREATE POLICY "Users can delete their own coding preferences" ON coding_preferences
    FOR DELETE USING (auth.uid() = user_id);

CREATE POLICY "Users can view their own coding signals" ON coding_signals
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can insert their own coding signals" ON coding_signals
    FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can view their own preference patterns" ON preference_patterns
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can insert their own preference patterns" ON preference_patterns
    FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update their own preference patterns" ON preference_patterns
    FOR UPDATE USING (auth.uid() = user_id);
