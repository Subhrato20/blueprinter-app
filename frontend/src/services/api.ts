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
  constructor(public status: number, message: string, public detail?: string) {
    super(message)
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
    const response = await fetch(url, config)
    
    if (!response.ok) {
      const errorData: ApiError = await response.json()
      throw new ApiError(response.status, errorData.error, errorData.detail)
    }

    return await response.json()
  } catch (error) {
    if (error instanceof ApiError) {
      throw error
    }
    throw new ApiError(0, 'Network error', error.message)
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
