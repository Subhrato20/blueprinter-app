// Type definitions for Blueprint Snap Frontend

export interface PlanStep {
  kind: 'code' | 'test' | 'config';
  target: string;
  summary: string;
}

export interface PlanFile {
  path: string;
  content: string;
}

export interface PlanJSON {
  title: string;
  steps: PlanStep[];
  files: PlanFile[];
  risks: string[];
  tests: string[];
  prBody: string;
}

export interface PlanResponse {
  plan: PlanJSON;
  planId: string;
}

export interface AskRequest {
  planId: string;
  nodePath: string;
  selectionText: string;
  userQuestion: string;
}

export interface PatchResponse {
  rationale: string;
  patch: Array<{
    op: 'add' | 'remove' | 'replace' | 'move' | 'copy' | 'test';
    path: string;
    value?: any;
    from?: string;
  }>;
}

export interface PlanPatchRequest {
  planId: string;
  patch: PatchResponse['patch'];
  messageId?: string;
}

export interface CursorLinkResponse {
  link: string;
}

export interface ApiError {
  error: string;
  detail?: string;
}

export interface User {
  id: string;
  email: string;
  name?: string;
}

export interface Project {
  id: string;
  name: string;
  description?: string;
  owner: string;
  created_at: string;
  updated_at: string;
}

export interface StyleProfile {
  user_id: string;
  tokens: {
    quotes: 'single' | 'double';
    semicolons: boolean;
    indent: 'spaces' | 'tabs';
    indent_size: number;
    test_framework: string;
    directories: string[];
    aliases: Record<string, string>;
    language: 'typescript' | 'javascript';
  };
  embedding?: number[];
}

export interface DevEvent {
  id: string;
  event_type: 'plan_created' | 'plan_updated' | 'plan_patched' | 'cursor_link_created' | 'file_downloaded';
  user_id: string;
  project_id?: string;
  metadata: Record<string, any>;
  created_at: string;
}

// UI State types
export interface AppState {
  user: User | null;
  currentProject: Project | null;
  currentPlan: PlanJSON | null;
  currentPlanId: string | null;
  isLoading: boolean;
  error: string | null;
}

export interface SelectionState {
  nodePath: string;
  selectionText: string;
  isActive: boolean;
}

export interface PatchPreview {
  original: PlanJSON;
  modified: PlanJSON;
  patch: PatchResponse['patch'];
  rationale: string;
}

export interface FetchHistoryItem {
  id: string;
  user_id?: string;
  endpoint: string;
  method: string;
  request_data?: Record<string, any>;
  response_data?: Record<string, any>;
  status_code?: number;
  duration_ms?: number;
  error_message?: string;
  created_at: string;
}

export interface FetchHistoryResponse {
  items: FetchHistoryItem[];
  total: number;
  page: number;
  page_size: number;
}

export interface FetchHistoryStats {
  total_requests: number;
  methods: Record<string, number>;
  endpoints: Record<string, number>;
  status_codes: Record<string, number>;
  average_duration_ms: number;
  error_count: number;
  success_rate: number;
}

export interface PlanRequest {
  idea: string;
  projectId: string;
}
