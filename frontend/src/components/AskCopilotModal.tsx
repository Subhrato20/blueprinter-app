import React, { useState } from 'react'

type Props = {
  nodePath: string
  onClose: () => void
  onSubmit: (question: string) => Promise<void>
}

export default function AskCopilotModal({ nodePath, onClose, onSubmit }: Props) {
  const [q, setQ] = useState('Refine this step for cursor-based pagination')
  const [busy, setBusy] = useState(false)

  async function submit() {
    setBusy(true)
    try { await onSubmit(q) } finally { setBusy(false); onClose() }
  }

  return (
    <div style={{ position: 'fixed', inset: 0, background: '#0008' }} onClick={onClose}>
      <div style={{ margin: '10% auto', width: 520, background: 'white', padding: 16 }} onClick={e => e.stopPropagation()}>
        <h3>Ask Copilot</h3>
        <p>Node: <code>{nodePath}</code></p>
        <textarea style={{ width: '100%', height: 120 }} value={q} onChange={e => setQ(e.target.value)} />
        <div style={{ marginTop: 8, display: 'flex', gap: 8, justifyContent: 'flex-end' }}>
          <button onClick={onClose}>Cancel</button>
          <button disabled={busy} onClick={submit}>Ask</button>
        </div>
      </div>
    </div>
  )
}

