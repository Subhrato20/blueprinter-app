// API service for Blueprint Snap Backend

import type { 
  PlanRequest, 
  PlanResponse, 
  AskRequest, 
  PatchResponse, 
  PlanPatchRequest, 
  CursorLinkResponse,
  ApiError 
} from '../types'

const API_BASE_URL = '/api'

class ApiError extends Error {
  constructor(public status: number, message?: string, public detail?: string) {
    const finalMessage = message || detail || 'Request failed'
    super(finalMessage)
    this.name = 'ApiError'
  }
}

async function apiRequest<T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<T> {
  const url = `${API_BASE_URL}${endpoint}`
  
  const defaultHeaders = {
    'Content-Type': 'application/json',
  }

  const config: RequestInit = {
    ...options,
    headers: {
      ...defaultHeaders,
      ...options.headers,
    },
  }

  try {
    // Add a longer timeout for plan generation (5 minutes)
    const controller = new AbortController()
    const timeoutId = setTimeout(() => controller.abort(), 5 * 60 * 1000) // 5 minutes
    
    const response = await fetch(url, {
      ...config,
      signal: controller.signal
    })
    
    clearTimeout(timeoutId)
    
    if (!response.ok) {
      // Attempt to parse JSON error; fall back to text if empty/non-JSON
      let message: string | undefined
      let detail: string | undefined
      try {
        const raw = await response.text()
        if (raw) {
          try {
            const parsed = JSON.parse(raw) as { detail?: string; error?: string; message?: string }
            detail = parsed.detail || parsed.message
            message = parsed.error || parsed.message || detail
          } catch {
            // Not JSON, use raw text
            detail = raw
            message = raw
          }
        }
      } catch {
        // Ignore body read errors; will use generic message
      }
      throw new ApiError(response.status, message, detail)
    }

    // Safely parse JSON on success; handle empty or non-JSON bodies
    const bodyText = await response.text()
    if (!bodyText || bodyText.trim().length === 0) {
      throw new ApiError(response.status, 'Empty response', 'Server returned no content')
    }
    try {
      return JSON.parse(bodyText) as T
    } catch (e) {
      throw new ApiError(response.status, 'Invalid JSON response', 'Server returned non-JSON content')
    }
  } catch (error) {
    if (error instanceof ApiError) {
      throw error
    }
    if ((error as any).name === 'AbortError') {
      throw new ApiError(0, 'Request timeout', 'The request took too long to complete')
    }
    const message = (error as any)?.message || 'Network error'
    throw new ApiError(0, 'Network error', message)
  }
}

// Plan API
export const planApi = {
  async createPlan(request: PlanRequest): Promise<PlanResponse> {
    return apiRequest<PlanResponse>('/plan', {
      method: 'POST',
      body: JSON.stringify(request),
    })
  },

  async getPlan(planId: string): Promise<PlanResponse> {
    return apiRequest<PlanResponse>(`/plan/${planId}`)
  },
}

// Ask Copilot API
export const askApi = {
  async askCopilot(request: AskRequest): Promise<PatchResponse> {
    return apiRequest<PatchResponse>('/ask', {
      method: 'POST',
      body: JSON.stringify(request),
    })
  },
}

// Plan Patch API
export const patchApi = {
  async applyPatch(request: PlanPatchRequest): Promise<{ success: boolean; planId: string; updatedPlan: any }> {
    return apiRequest('/plan/patch', {
      method: 'POST',
      body: JSON.stringify(request),
    })
  },
}

// Cursor Link API
export const cursorApi = {
  async createLink(planId: string): Promise<CursorLinkResponse> {
    return apiRequest<CursorLinkResponse>('/cursor-link', {
      method: 'POST',
      body: JSON.stringify({ planId }),
    })
  },
}

// Utility functions
export const downloadZip = async (plan: any) => {
  const JSZip = (await import('jszip')).default
  const zip = new JSZip()

  // Add all files to the zip
  plan.files.forEach((file: any) => {
    zip.file(file.path, file.content)
  })

  // Add PR body as a markdown file
  zip.file('.blueprint/PR_BODY.md', plan.prBody)

  // Generate and download the zip
  const blob = await zip.generateAsync({ type: 'blob' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `${plan.title.replace(/[^a-z0-9]/gi, '_').toLowerCase()}.zip`
  document.body.appendChild(a)
  a.click()
  document.body.removeChild(a)
  URL.revokeObjectURL(url)
}

export const openInCursor = async (planId: string) => {
  try {
    const response = await cursorApi.createLink(planId)
    window.location.href = response.link
  } catch (error) {
    console.error('Failed to create Cursor link:', error)
    throw error
  }
}

export { ApiError }
