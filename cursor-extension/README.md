# Blueprint Snap - VS Code Extension

**Dev DNA Edition**: One-line idea → Plan JSON + style-adapted scaffolds + Ask-Copilot + Cursor deep link

## Features

- **URI Handler**: Handles `vscode://subhrato.blueprint-snap/ingest` deep links
- **HMAC Verification**: Verifies payload signatures for security
- **File Operations**: Safely writes files to your workspace
- **Task Execution**: Automatically runs VS Code tasks after ingestion
- **Payload Validation**: Test payloads before ingestion

## Installation

### From VSIX Package

1. Download the latest `.vsix` file from releases
2. Open VS Code
3. Go to Extensions (Ctrl+Shift+X)
4. Click the "..." menu and select "Install from VSIX..."
5. Select the downloaded `.vsix` file

### From Source

1. Clone this repository
2. Run `npm install` in the `cursor-extension` directory
3. Run `npm run compile` to build the extension
4. Press F5 to run the extension in a new Extension Development Host window

## Configuration

Add these settings to your VS Code `settings.json`:

```json
{
  "blueprintSnap.secret": "your-hmac-secret-here",
  "blueprintSnap.autoOpenFiles": true,
  "blueprintSnap.runTasks": true
}
```

### Settings

- **`blueprintSnap.secret`**: HMAC secret for verifying payload signatures (required)
- **`blueprintSnap.autoOpenFiles`**: Automatically open files after ingestion (default: true)
- **`blueprintSnap.runTasks`**: Automatically run tasks after ingestion (default: true)

## Usage

### Deep Link Integration

The extension automatically handles deep links from the Blueprint Snap web app:

```
vscode://subhrato.blueprint-snap/ingest?data=<base64url-payload>&sig=<hmac-signature>
```

### Manual Commands

#### Validate Payload

1. Open Command Palette (Ctrl+Shift+P)
2. Run "Blueprint: Validate Payload"
3. Paste a base64url-encoded payload to validate its structure

#### Ingest Plan

1. Open Command Palette (Ctrl+Shift+P)
2. Run "Blueprint: Ingest Plan"
3. Paste a base64url-encoded payload to ingest

## Payload Format

The extension expects payloads in this format:

```typescript
interface CursorPayload {
  version: number;
  projectHint?: string;
  plan: {
    title: string;
    prBody: string;
  };
  files: Array<{
    path: string;
    content: string;
  }>;
  postActions?: {
    open?: string[];
    runTask?: string;
  };
}
```

## Security

- All payloads are verified using HMAC-SHA256 signatures
- File paths are validated to prevent directory traversal attacks
- Only files within the current workspace are written

## Development

### Building

```bash
npm install
npm run compile
```

### Packaging

```bash
npm run package
```

This creates a `.vsix` file that can be installed in VS Code.

### Testing

```bash
npm test
```

## Troubleshooting

### "HMAC secret not configured"

Set the `blueprintSnap.secret` setting in VS Code:

1. Open Settings (Ctrl+,)
2. Search for "blueprintSnap.secret"
3. Set it to your HMAC secret

### "Invalid signature"

The payload signature doesn't match. This could be due to:
- Incorrect HMAC secret
- Corrupted payload
- Man-in-the-middle attack

### Files not opening

Check that `blueprintSnap.autoOpenFiles` is set to `true` in your settings.

### Tasks not running

Check that:
- `blueprintSnap.runTasks` is set to `true`
- The task name exists in your workspace's `.vscode/tasks.json`
- The task is properly configured

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

MIT License - see LICENSE file for details.
