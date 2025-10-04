import React from 'react'
import type { PlanJSON } from '@/types'

type Props = {
  plan: PlanJSON | null
  onAsk: (nodePath: string) => void
}

export default function PlanViewer({ plan, onAsk }: Props) {
  if (!plan) return <div>No plan yet.</div>
  return (
    <div style={{ display: 'grid', gap: 16 }}>
      <section data-node-path="/title">
        <h2>{plan.title}</h2>
      </section>

      <section data-node-path="/steps">
        <h3>Steps</h3>
        <ol>
          {plan.steps.map((s, i) => (
            <li key={i} data-node-path={`/steps/${i}`}>
              <b>{s.kind}</b> → {s.target}: {s.summary}
              <button style={{ marginLeft: 8 }} onClick={() => onAsk(`/steps/${i}`)}>Ask</button>
            </li>
          ))}
        </ol>
      </section>

      <section data-node-path="/files">
        <h3>Files</h3>
        <ul>
          {plan.files.map((f, i) => (
            <li key={i} data-node-path={`/files/${i}`}>{f.path}</li>
          ))}
        </ul>
      </section>

      <section data-node-path="/risks">
        <h3>Risks</h3>
        <ul>
          {plan.risks.map((r, i) => (<li key={i}>{r}</li>))}
        </ul>
      </section>

      <section data-node-path="/tests">
        <h3>Tests</h3>
        <ul>
          {plan.tests.map((t, i) => (<li key={i}>{t}</li>))}
        </ul>
      </section>

      <section data-node-path="/prBody">
        <h3>PR Body</h3>
        <pre style={{ whiteSpace: 'pre-wrap' }}>{plan.prBody}</pre>
      </section>
    </div>
  )
}

