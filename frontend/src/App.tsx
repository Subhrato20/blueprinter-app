import React, { useState } from 'react'
import PlanViewer from './components/PlanViewer'
import type { PlanJSON } from './types'
import { applyPlanPatch, ask, createPlan, getCursorLink } from './services/api'

export default function App() {
  const [idea, setIdea] = useState('Add paginated search to /users')
  const [project, setProject] = useState('proj_dev')
  const [plan, setPlan] = useState<PlanJSON | null>(null)
  const [showAsk, setShowAsk] = useState<{ path: string } | null>(null)

  async function generatePlan() {
    const res: PlanJSON = await createPlan({ project_id: project, idea })
    setPlan(res)
  }

  async function runAsk(path: string, q: string) {
    const resp = await ask({ plan_id: 'dev', nodePath: path, question: q })
    if (!plan) return
    const updated = await applyPlanPatch({ plan_id: 'dev', nodePath: path, patch: resp.patch })
    setPlan(updated)
  }

  async function addToCursor() {
    const { link } = await getCursorLink('dev')
    window.location.href = link
  }

  return (
    <div style={{ padding: 16, display: 'grid', gap: 12 }}>
      <h1>Blueprinter</h1>

      <div>
        <label>Project ID: <input value={project} onChange={e => setProject(e.target.value)} /></label>
      </div>
      <div>
        <textarea style={{ width: 600, height: 80 }} value={idea} onChange={e => setIdea(e.target.value)} />
      </div>
      <div style={{ display: 'flex', gap: 8 }}>
        <button onClick={generatePlan}>Generate Plan</button>
        <button onClick={addToCursor} disabled={!plan}>Add to Cursor</button>
      </div>

      <PlanViewer plan={plan} onAsk={(nodePath) => setShowAsk({ path: nodePath })} />

      {showAsk && (
        <div>
          {/* Inline modal to avoid extra imports */}
          <div style={{ position: 'fixed', inset: 0, background: '#0008' }} onClick={() => setShowAsk(null)}>
            <div style={{ margin: '10% auto', width: 520, background: 'white', padding: 16 }} onClick={e => e.stopPropagation()}>
              <h3>Ask Copilot</h3>
              <Ask nodePath={showAsk.path} onClose={() => setShowAsk(null)} onSubmit={(q) => runAsk(showAsk.path, q)} />
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

function Ask({ nodePath, onClose, onSubmit }: { nodePath: string; onClose: () => void; onSubmit: (q: string) => Promise<void> }) {
  const [q, setQ] = useState('Refine this step for cursor-based pagination')
  const [busy, setBusy] = useState(false)
  return (
    <div>
      <p>Node: <code>{nodePath}</code></p>
      <textarea style={{ width: '100%', height: 120 }} value={q} onChange={e => setQ(e.target.value)} />
      <div style={{ display: 'flex', justifyContent: 'flex-end', gap: 8 }}>
        <button onClick={onClose}>Cancel</button>
        <button disabled={busy} onClick={async () => { setBusy(true); try { await onSubmit(q) } finally { setBusy(false); onClose() } }}>Ask</button>
      </div>
    </div>
  )
}

