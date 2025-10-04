const API_BASE = import.meta.env.VITE_API_BASE || 'http://localhost:8000'

export async function postJSON<T>(path: string, body: unknown): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  })
  if (!res.ok) throw new Error(await res.text())
  return res.json()
}

export type CreatePlanReq = { project_id: string; idea: string; pattern_slug?: string }
export function createPlan(body: CreatePlanReq) {
  return postJSON('/api/plan', body)
}

export type AskReq = { plan_id: string; nodePath: string; selection?: string; question: string }
export function ask(body: AskReq) {
  return postJSON('/api/ask', body)
}

export type PatchOp = { op: 'add' | 'remove' | 'replace'; path: string; value?: unknown }
export type PlanPatchReq = { plan_id: string; nodePath: string; patch: PatchOp[] }
export function applyPlanPatch(body: PlanPatchReq) {
  return postJSON('/api/plan/patch', body)
}

export function getCursorLink(plan_id: string) {
  return postJSON<{ link: string }>("/api/cursor-link", { plan_id })
}

