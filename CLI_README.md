# Blueprinter CLI

A powerful command-line interface for the Blueprinter development planning tool. The CLI provides access to all Blueprinter features including plan generation, copilot interactions, coding preferences management, and Cursor IDE integration.

## Features

- 🚀 **Plan Management**: Create, view, and manage development plans
- 🤖 **AI Copilot**: Ask questions and get suggestions for your plans
- 🎯 **Coding Preferences**: Manage your coding style preferences with vector search
- 🔗 **Cursor Integration**: Generate deep links to open plans in Cursor IDE
- ⚙️ **Configuration**: Easy setup and configuration management
- 📊 **Rich Output**: Beautiful terminal output with tables and formatting

## Installation

### Quick Setup

Run the automated setup script from the project root:

```bash
python setup_cli.py
```

This will:
- Install the CLI package and dependencies
- Create configuration directory
- Set up initial configuration
- Test the installation

### Manual Installation

1. Install the backend package in development mode:
```bash
cd backend
pip install -e .
```

2. Install CLI dependencies:
```bash
pip install click rich httpx
```

3. Create configuration directory:
```bash
mkdir -p ~/.blueprinter
```

## Configuration

### Interactive Setup

Run the interactive setup to configure your CLI:

```bash
blueprinter config set --base-url http://localhost:8000 --api-key your-api-key
```

### Environment Variables

You can also set configuration via environment variables:

```bash
export BLUEPRINTER_API_URL="http://localhost:8000"
export BLUEPRINTER_API_KEY="your-api-key"
export BLUEPRINTER_PROJECT_ID="your-project-id"
```

### Configuration Commands

```bash
# Show current configuration
blueprinter config show

# Set configuration values
blueprinter config set --base-url http://localhost:8000
blueprinter config set --api-key your-api-key
blueprinter config set --project-id my-project
```

## Usage

### Health Check

Check if the API is running and accessible:

```bash
blueprinter health
```

### Plan Management

#### Create a Plan

Create a new development plan from an idea:

```bash
blueprinter plan create "Build a todo app with React and Node.js"
```

With options:

```bash
blueprinter plan create "Build a todo app" --project-id my-project --output plan.json
```

#### Get a Plan

Retrieve and display a plan by ID:

```bash
blueprinter plan get <plan-id>
```

Save to file:

```bash
blueprinter plan get <plan-id> --output plan.json
```

### Copilot Interactions

Ask the AI copilot for suggestions about your plan:

```bash
blueprinter copilot ask <plan-id> "/steps/0" "How can I improve this step?"
```

With selected text:

```bash
blueprinter copilot ask <plan-id> "/steps/0" "Make this more secure" --selection-text "user authentication"
```

### Cursor Integration

Generate a deep link to open your plan in Cursor IDE:

```bash
blueprinter cursor link <plan-id>
```

This will generate a `vscode://` deep link that opens the plan directly in Cursor.

### Coding Preferences

#### Add Preferences

Add coding style preferences:

```bash
blueprinter preferences add frontend_framework "Use React with TypeScript for all frontend projects"
```

With context and strength:

```bash
blueprinter preferences add code_style "Use 2 spaces for indentation" --context "JavaScript/TypeScript files" --strength strong
```

#### List Preferences

View all your coding preferences:

```bash
blueprinter preferences list
```

Filter by category:

```bash
blueprinter preferences list --category frontend_framework
```

#### Search Similar Preferences

Find similar preferences using vector search:

```bash
blueprinter preferences search "React TypeScript components"
```

With custom threshold:

```bash
blueprinter preferences search "testing patterns" --threshold 0.8 --max-results 5
```

#### Style Summary

Get a summary of your coding style:

```bash
blueprinter preferences summary
```

## Command Reference

### Global Options

- `--base-url`: Override API base URL
- `--api-key`: Override API key
- `--verbose, -v`: Enable verbose logging

### Plan Commands

```bash
blueprinter plan create <idea> [OPTIONS]
  --project-id TEXT    Project ID
  --output PATH        Output file for plan JSON

blueprinter plan get <plan-id> [OPTIONS]
  --output PATH        Output file for plan JSON
```

### Copilot Commands

```bash
blueprinter copilot ask <plan-id> <node-path> <user-question> [OPTIONS]
  --selection-text TEXT    Selected text from the plan
```

### Cursor Commands

```bash
blueprinter cursor link <plan-id>
```

### Preferences Commands

```bash
blueprinter preferences add <category> <preference-text> [OPTIONS]
  --context TEXT       Additional context
  --strength [weak|moderate|strong|absolute]  Preference strength

blueprinter preferences list [OPTIONS]
  --category TEXT      Filter by category

blueprinter preferences search <query-text> [OPTIONS]
  --threshold FLOAT    Similarity threshold (0.0-1.0)
  --max-results INT    Maximum number of results

blueprinter preferences summary
```

### Configuration Commands

```bash
blueprinter config set [OPTIONS]
  --base-url TEXT      Set API base URL
  --api-key TEXT       Set API key
  --project-id TEXT    Set default project ID

blueprinter config show
```

## Examples

### Complete Workflow

1. **Start the backend server**:
```bash
cd backend
python app/main.py
```

2. **Check API health**:
```bash
blueprinter health
```

3. **Create a development plan**:
```bash
blueprinter plan create "Build a REST API with FastAPI and PostgreSQL"
```

4. **Get the plan ID and view details**:
```bash
blueprinter plan get <plan-id>
```

5. **Ask the copilot for improvements**:
```bash
blueprinter copilot ask <plan-id> "/steps/0" "How can I add authentication to this API?"
```

6. **Generate Cursor link**:
```bash
blueprinter cursor link <plan-id>
```

7. **Add coding preferences**:
```bash
blueprinter preferences add backend_pattern "Use dependency injection for all services"
blueprinter preferences add code_style "Use async/await instead of callbacks"
```

8. **Search for similar preferences**:
```bash
blueprinter preferences search "async programming patterns"
```

### Advanced Usage

#### Batch Operations

Create multiple plans from a file:

```bash
# Create plans.txt with one idea per line
echo "Build a todo app" > plans.txt
echo "Create a blog platform" >> plans.txt

# Create plans (requires custom script)
while read idea; do
  blueprinter plan create "$idea" --project-id batch-project
done < plans.txt
```

#### Integration with Git

Add plan creation to your git workflow:

```bash
# Create a plan for a new feature
blueprinter plan create "Add user authentication" --project-id $(git rev-parse --abbrev-ref HEAD)

# Generate Cursor link for the plan
PLAN_ID=$(blueprinter plan create "Add user authentication" --project-id $(git rev-parse --abbrev-ref HEAD) | grep "Plan ID" | cut -d: -f2 | tr -d ' ')
blueprinter cursor link $PLAN_ID
```

## Troubleshooting

### Common Issues

1. **"API not reachable" error**:
   - Ensure the backend server is running
   - Check the API URL in configuration
   - Verify network connectivity

2. **"Authentication failed" error**:
   - Check your API key
   - Ensure the key has proper permissions

3. **"Plan not found" error**:
   - Verify the plan ID is correct
   - Check if the plan exists in the database

4. **CLI not found**:
   - Ensure the package is installed: `pip install -e .`
   - Check your PATH includes the installation directory

### Debug Mode

Enable verbose logging for debugging:

```bash
blueprinter --verbose health
```

### Configuration Issues

Reset configuration:

```bash
rm -rf ~/.blueprinter
blueprinter config set --base-url http://localhost:8000
```

## Development

### Adding New Commands

1. Add the command function to `cli/main.py`
2. Register it with the appropriate command group
3. Update this README with documentation

### Testing

Test the CLI with the backend running:

```bash
# Start backend
cd backend && python app/main.py &

# Test CLI
blueprinter health
blueprinter plan create "Test plan"
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Add your CLI improvements
4. Test thoroughly
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.
