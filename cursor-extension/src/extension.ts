import * as vscode from 'vscode';
import * as crypto from 'crypto';
import * as path from 'path';
import * as fs from 'fs';

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

export function activate(context: vscode.ExtensionContext) {
  console.log('Blueprint Snap extension is now active!');

  // Register URI handler
  const uriHandler = vscode.window.registerUriHandler({
    handleUri: async (uri: vscode.Uri) => {
      if (uri.scheme === 'vscode' && uri.authority === 'subhrato.blueprint-snap') {
        if (uri.path === '/ingest') {
          await handleIngestUri(uri);
        }
      }
    }
  });

  // Register commands
  const validateCommand = vscode.commands.registerCommand('blueprintSnap.validatePayload', async () => {
    await showValidatePayloadInput();
  });

  const ingestCommand = vscode.commands.registerCommand('blueprintSnap.ingest', async () => {
    await showIngestInput();
  });

  context.subscriptions.push(uriHandler, validateCommand, ingestCommand);
}

async function handleIngestUri(uri: vscode.Uri): Promise<void> {
  try {
    const params = new URLSearchParams(uri.query);
    const data = params.get('data');
    const sig = params.get('sig');

    if (!data || !sig) {
      vscode.window.showErrorMessage('Invalid Blueprint Snap payload: missing data or signature');
      return;
    }

    const payload = await decodeAndVerifyPayload(data, sig);
    await ingestPlan(payload);

    vscode.window.showInformationMessage(
      `Blueprint Snap: Successfully ingested plan "${payload.plan.title}"`
    );
  } catch (error) {
    console.error('Error handling ingest URI:', error);
    vscode.window.showErrorMessage(
      `Blueprint Snap: Failed to ingest plan - ${error.message}`
    );
  }
}

async function decodeAndVerifyPayload(data: string, signature: string): Promise<CursorPayload> {
  try {
    // Get HMAC secret from settings
    const config = vscode.workspace.getConfiguration('blueprintSnap');
    const secret = config.get<string>('secret');
    
    if (!secret || secret === 'CHANGE_ME') {
      throw new Error('HMAC secret not configured. Please set blueprintSnap.secret in settings.');
    }

    // Add padding if needed
    const paddedData = data + '='.repeat((4 - data.length % 4) % 4);
    
    // Decode base64url
    const payloadJson = Buffer.from(paddedData, 'base64url').toString('utf-8');
    const payload: CursorPayload = JSON.parse(payloadJson);

    // Verify signature using the same format as backend (sorted keys, compact separators)
    const normalizedJson = JSON.stringify(payload, Object.keys(payload).sort());
    const expectedSignature = crypto
      .createHmac('sha256', secret)
      .update(normalizedJson)
      .digest('base64url')
      .replace(/=/g, '');

    // Add padding for comparison
    const sigPadded = signature + '='.repeat((4 - signature.length % 4) % 4);
    const expectedPadded = expectedSignature + '='.repeat((4 - expectedSignature.length % 4) % 4);

    if (!crypto.timingSafeEqual(
      Buffer.from(sigPadded, 'base64url'),
      Buffer.from(expectedPadded, 'base64url')
    )) {
      throw new Error('Invalid signature');
    }

    return payload;
  } catch (error) {
    throw new Error(`Failed to decode payload: ${error.message}`);
  }
}

async function ingestPlan(payload: CursorPayload): Promise<void> {
  const workspaceFolder = vscode.workspace.workspaceFolders?.[0];
  if (!workspaceFolder) {
    throw new Error('No workspace folder open');
  }

  const workspacePath = workspaceFolder.uri.fsPath;
  const config = vscode.workspace.getConfiguration('blueprintSnap');

  // Create .blueprint directory
  const blueprintDir = path.join(workspacePath, '.blueprint');
  if (!fs.existsSync(blueprintDir)) {
    fs.mkdirSync(blueprintDir, { recursive: true });
  }

  // Write PR body
  const prBodyPath = path.join(blueprintDir, 'PR_BODY.md');
  fs.writeFileSync(prBodyPath, payload.plan.prBody);

  // Write files
  const filesToOpen: vscode.Uri[] = [];
  
  for (const file of payload.files) {
    const filePath = path.join(workspacePath, file.path);
    
    // Guard against path traversal
    if (!filePath.startsWith(workspacePath)) {
      console.warn(`Skipping file outside workspace: ${file.path}`);
      continue;
    }

    // Create directory if it doesn't exist
    const dir = path.dirname(filePath);
    if (!fs.existsSync(dir)) {
      fs.mkdirSync(dir, { recursive: true });
    }

    // Write file
    fs.writeFileSync(filePath, file.content);
    
    // Add to files to open
    filesToOpen.push(vscode.Uri.file(filePath));
  }

  // Open files if configured
  if (config.get<boolean>('autoOpenFiles', true)) {
    const filesToOpenLimited = filesToOpen.slice(0, 10); // Limit to first 10 files
    
    // Open PR body first
    await vscode.window.showTextDocument(vscode.Uri.file(prBodyPath));
    
    // Open other files
    for (const fileUri of filesToOpenLimited) {
      try {
        await vscode.window.showTextDocument(fileUri);
      } catch (error) {
        console.warn(`Failed to open file ${fileUri.fsPath}:`, error);
      }
    }
  }

  // Run task if configured and specified
  if (config.get<boolean>('runTasks', true) && payload.postActions?.runTask) {
    try {
      await vscode.commands.executeCommand('workbench.action.tasks.runTask', payload.postActions.runTask);
    } catch (error) {
      console.warn(`Failed to run task ${payload.postActions.runTask}:`, error);
    }
  }

  // Show summary
  const summary = `Ingested plan "${payload.plan.title}":
- ${payload.files.length} files created
- PR body written to .blueprint/PR_BODY.md
- ${filesToOpen.length} files available`;

  vscode.window.showInformationMessage(summary);
}

async function showValidatePayloadInput(): Promise<void> {
  const input = await vscode.window.showInputBox({
    prompt: 'Enter Blueprint Snap payload for validation (base64url encoded)',
    placeHolder: 'eyJ2ZXJzaW9uIjoxLCJwbGFuIjp7InRpdGxlIjoiVGVzdCJ9fQ...',
    validateInput: (value) => {
      if (!value.trim()) {
        return 'Payload cannot be empty';
      }
      return null;
    }
  });

  if (!input) {
    return;
  }

  try {
    // Try to decode as base64url
    const paddedData = input + '='.repeat((4 - input.length % 4) % 4);
    const payloadJson = Buffer.from(paddedData, 'base64url').toString('utf-8');
    const payload = JSON.parse(payloadJson);

    // Validate structure
    if (!payload.version || !payload.plan || !payload.files) {
      throw new Error('Invalid payload structure');
    }

    vscode.window.showInformationMessage(
      `Payload validation successful:
- Version: ${payload.version}
- Plan: ${payload.plan.title}
- Files: ${payload.files.length}`
    );
  } catch (error) {
    vscode.window.showErrorMessage(`Payload validation failed: ${error.message}`);
  }
}

async function showIngestInput(): Promise<void> {
  const input = await vscode.window.showInputBox({
    prompt: 'Enter Blueprint Snap payload to ingest (base64url encoded)',
    placeHolder: 'eyJ2ZXJzaW9uIjoxLCJwbGFuIjp7InRpdGxlIjoiVGVzdCJ9fQ...',
    validateInput: (value) => {
      if (!value.trim()) {
        return 'Payload cannot be empty';
      }
      return null;
    }
  });

  if (!input) {
    return;
  }

  try {
    // For manual input, we'll skip signature verification
    const paddedData = input + '='.repeat((4 - input.length % 4) % 4);
    const payloadJson = Buffer.from(paddedData, 'base64url').toString('utf-8');
    const payload: CursorPayload = JSON.parse(payloadJson);

    await ingestPlan(payload);
  } catch (error) {
    vscode.window.showErrorMessage(`Failed to ingest payload: ${error.message}`);
  }
}

export function deactivate() {
  console.log('Blueprint Snap extension is now deactivated');
}
