import * as vscode from 'vscode'
import * as crypto from 'crypto'
import * as fs from 'fs'
import * as path from 'path'

function b64urlToBuf(s: string): Buffer {
  s = s.replace(/-/g, '+').replace(/_/g, '/')
  while (s.length % 4 !== 0) s += '='
  return Buffer.from(s, 'base64')
}

export function activate(context: vscode.ExtensionContext) {
  const handler: vscode.UriHandler = {
    async handleUri(uri: vscode.Uri) {
      try {
        if (uri.path !== '/ingest') return
        const qs = new URLSearchParams(uri.query)
        const payloadB64 = qs.get('payload') || ''
        const sigB64 = qs.get('sig') || ''
        const payloadBuf = b64urlToBuf(payloadB64)
        const payload = JSON.parse(payloadBuf.toString('utf8')) as { planId: string, files: { path: string, content: string }[], prBody: string }

        const secret = vscode.workspace.getConfiguration().get<string>('blueprintSnap.secret') || ''
        if (secret) {
          const expected = crypto.createHmac('sha256', secret).update(payloadBuf).digest()
          const provided = b64urlToBuf(sigB64)
          if (!crypto.timingSafeEqual(expected, provided)) {
            vscode.window.showErrorMessage('Blueprint Snap: invalid signature')
            return
          }
        }

        const ws = vscode.workspace.workspaceFolders?.[0]
        if (!ws) { vscode.window.showErrorMessage('Open a workspace first'); return }

        for (const f of payload.files || []) {
          const abs = path.join(ws.uri.fsPath, f.path)
          await fs.promises.mkdir(path.dirname(abs), { recursive: true })
          await fs.promises.writeFile(abs, f.content, 'utf8')
          const doc = await vscode.workspace.openTextDocument(abs)
          await vscode.window.showTextDocument(doc, { preview: false })
        }

        const prPath = path.join(ws.uri.fsPath, '.blueprint', 'PR_BODY.md')
        await fs.promises.mkdir(path.dirname(prPath), { recursive: true })
        await fs.promises.writeFile(prPath, payload.prBody || '', 'utf8')
        const prDoc = await vscode.workspace.openTextDocument(prPath)
        await vscode.window.showTextDocument(prDoc, { preview: false })

        vscode.window.showInformationMessage(`Blueprint Snap: Ingested plan ${payload.planId}`)
      } catch (e: any) {
        vscode.window.showErrorMessage('Blueprint Snap: ' + String(e?.message || e))
      }
    }
  }
  context.subscriptions.push(vscode.window.registerUriHandler(handler))
}

export function deactivate() {}

