export type PlanStep = { kind: string; target: string; summary: string }
export type PlanFile = { path: string; content: string }
export type PlanJSON = {
  title: string
  steps: PlanStep[]
  files: PlanFile[]
  risks: string[]
  tests: string[]
  prBody: string
}

