# Coding Preferences Vector Database

This system allows you to store, search, and learn from your coding preferences using vector embeddings. It's designed to help you build personalized coding assistants that understand your style and preferences.

## Features

### 🎯 Core Functionality
- **Vector Storage**: Store coding preferences with automatic embedding generation
- **Semantic Search**: Find similar preferences using vector similarity
- **Pattern Learning**: Learn from your coding behaviors and signals
- **Preference Categories**: Organize preferences by type (frontend, backend, testing, etc.)
- **Strength Levels**: Rate preferences from weak to absolute

### 🔍 Smart Search
- **Similarity Search**: Find preferences similar to a query using vector embeddings
- **Context-Aware**: Search considers both preference text and context
- **Threshold Control**: Adjust similarity thresholds for search results

### 📊 Analytics
- **Style Summary**: Get overview of your coding preferences by category
- **Pattern Recognition**: Learn patterns from your coding behaviors
- **Signal Tracking**: Track actual coding behaviors to improve suggestions

## Database Schema

### Tables

#### `coding_preferences`
Stores your explicit coding preferences with vector embeddings.

```sql
- id: UUID (primary key)
- user_id: UUID (foreign key to auth.users)
- category: ENUM (frontend_framework, backend_pattern, code_style, etc.)
- preference_text: TEXT (the actual preference)
- context: TEXT (additional context)
- strength: ENUM (weak, moderate, strong, absolute)
- embedding: VECTOR(1536) (OpenAI embedding)
- metadata: JSONB (additional structured data)
- created_at/updated_at: TIMESTAMP
```

#### `coding_signals`
Tracks your actual coding behaviors for pattern learning.

```sql
- id: UUID (primary key)
- user_id: UUID (foreign key to auth.users)
- signal_type: TEXT (file_created, code_pattern_used, etc.)
- signal_data: JSONB (the actual signal data)
- embedding: VECTOR(1536) (embedding of the signal)
- confidence_score: FLOAT (confidence in the signal)
- created_at: TIMESTAMP
```

#### `preference_patterns`
Learned patterns from your coding signals.

```sql
- id: UUID (primary key)
- user_id: UUID (foreign key to auth.users)
- pattern_name: TEXT (name of the learned pattern)
- pattern_description: TEXT (description of the pattern)
- pattern_data: JSONB (structured pattern data)
- embedding: VECTOR(1536) (embedding for pattern matching)
- confidence_score: FLOAT (confidence in the pattern)
- signal_count: INTEGER (number of signals that contributed)
- created_at/updated_at: TIMESTAMP
```

## API Endpoints

### Coding Preferences

#### `POST /api/coding-preferences/`
Create a new coding preference with automatic embedding generation.

```json
{
  "category": "frontend_framework",
  "preference_text": "Use TypeScript for all frontend code",
  "context": "Always prefer TypeScript over JavaScript for type safety",
  "strength": "strong"
}
```

#### `GET /api/coding-preferences/`
Get all coding preferences, optionally filtered by category.

#### `GET /api/coding-preferences/summary`
Get a summary of coding preferences by category.

#### `PUT /api/coding-preferences/{id}`
Update an existing coding preference.

#### `DELETE /api/coding-preferences/{id}`
Delete a coding preference.

#### `POST /api/coding-preferences/search`
Search for similar preferences using vector similarity.

```json
{
  "query_text": "TypeScript frontend development",
  "similarity_threshold": 0.7,
  "max_results": 10
}
```

### Coding Signals

#### `POST /api/coding-preferences/signals`
Track a coding signal (behavioral data).

```json
{
  "signal_type": "file_created",
  "signal_data": {
    "file_path": "src/components/UserProfile.tsx",
    "language": "typescript"
  },
  "confidence_score": 1.0
}
```

## Usage Examples

### Adding Your Coding Preferences

```typescript
import { codingPreferencesService } from './services/codingPreferences';

// Add a frontend preference
await codingPreferencesService.addFrontendPreference(
  "Use TypeScript for all frontend code",
  "Always prefer TypeScript over JavaScript for type safety",
  "strong"
);

// Add a backend preference
await codingPreferencesService.addBackendPreference(
  "Follow Uncle Bob principles - one class should do one thing",
  "Apply Single Responsibility Principle consistently",
  "strong"
);

// Add a code style preference
await codingPreferencesService.addCodeStylePreference(
  "Use meaningful variable names",
  "Avoid abbreviations and use descriptive names",
  "moderate"
);
```

### Searching for Similar Preferences

```typescript
// Search for similar preferences
const results = await codingPreferencesService.searchSimilarPreferences({
  query_text: "TypeScript frontend development",
  similarity_threshold: 0.7,
  max_results: 5
});

console.log(results.preferences);
```

### Tracking Coding Signals

```typescript
// Track file creation
await codingPreferencesService.trackFileCreation(
  "src/components/UserProfile.tsx",
  "typescript"
);

// Track code pattern usage
await codingPreferencesService.trackCodePattern(
  "react_hooks",
  "Used useState and useEffect hooks"
);

// Track refactoring
await codingPreferencesService.trackRefactoring(
  "extract_method",
  "Long method detected"
);
```

## Frontend Interface

The system includes a React component `CodingPreferencesManager` that provides:

- **Preference Management**: Add, edit, delete coding preferences
- **Category Organization**: View preferences by category
- **Search Interface**: Search for similar preferences
- **Style Summary**: Overview of your coding style
- **Visual Indicators**: Strength levels and categories

## Setup Instructions

### 1. Database Setup

Run the migration to create the vector database schema:

```bash
# Apply the migration
supabase db push
```

### 2. Backend Setup

The backend API endpoints are automatically included when you start the FastAPI server:

```bash
cd backend
python -m uvicorn app.main:app --reload
```

### 3. Frontend Setup

The coding preferences manager is integrated into the main app. Access it via the "Coding Preferences" button in the header.

### 4. Environment Variables

Make sure you have the required environment variables:

```bash
# Backend
OPENAI_API_KEY=your-openai-api-key
SUPABASE_URL=your-supabase-url
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key

# Frontend
VITE_SUPABASE_URL=your-supabase-url
VITE_SUPABASE_ANON_KEY=your-supabase-anon-key
```

## Example Use Cases

### 1. Personal Coding Assistant
Store your preferences like "Use TypeScript for frontend" and "Follow Uncle Bob principles" so your AI assistant can suggest code that matches your style.

### 2. Team Style Guide
Share coding preferences across team members to maintain consistent coding standards.

### 3. Learning from Behavior
Track your actual coding behaviors to learn patterns and improve suggestions over time.

### 4. Context-Aware Suggestions
Get suggestions based on the current context (e.g., "When working with React, prefer functional components").

## Advanced Features

### Pattern Learning
The system can learn patterns from your coding signals:

- **File Creation Patterns**: Learn which file types you create frequently
- **Code Pattern Usage**: Learn which patterns you prefer
- **Refactoring Patterns**: Learn your refactoring approaches
- **Testing Patterns**: Learn your testing preferences

### Vector Similarity Search
Uses OpenAI embeddings to find semantically similar preferences:

- **Semantic Understanding**: Finds preferences by meaning, not just keywords
- **Context Awareness**: Considers both preference text and context
- **Configurable Thresholds**: Adjust similarity requirements

### Integration with AI
The vector database integrates with your AI coding assistant:

- **Personalized Suggestions**: AI can suggest code that matches your preferences
- **Style Consistency**: Maintain consistent coding style across projects
- **Learning from Feedback**: Improve suggestions based on your actual usage

## Demo Script

Run the demo script to see the system in action:

```bash
cd examples
python coding_preferences_demo.py
```

Make sure to update the configuration variables in the script first.

## Contributing

To add new features to the coding preferences system:

1. **Database**: Add new tables/columns in migrations
2. **Backend**: Add new API endpoints in `coding_preferences.py`
3. **Frontend**: Update the React components
4. **Services**: Add new service methods for complex operations

## Troubleshooting

### Common Issues

1. **Embedding Generation Fails**: Check your OpenAI API key
2. **Vector Search Returns No Results**: Lower the similarity threshold
3. **Authentication Errors**: Verify Supabase configuration
4. **Performance Issues**: Add indexes for large datasets

### Debug Mode

Enable debug logging in the backend:

```python
import structlog
structlog.configure(processors=[structlog.dev.ConsoleRenderer()])
```

This will help you debug embedding generation and vector search issues.
