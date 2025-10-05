// Fetch History API service

import type { FetchHistoryResponse, FetchHistoryStats, ApiError } from '../types'

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
    const response = await fetch(url, config)
    
    if (!response.ok) {
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
            detail = raw
            message = raw
          }
        }
      } catch {
        // Ignore body read errors
      }
      throw new ApiError(response.status, message, detail)
    }

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
    const message = (error as any)?.message || 'Network error'
    throw new ApiError(0, 'Network error', message)
  }
}

// Fetch History API
export const fetchHistoryApi = {
  async getHistory(
    page: number = 1,
    pageSize: number = 50,
    filters?: {
      endpoint?: string
      method?: string
      status_code?: number
    }
  ): Promise<FetchHistoryResponse> {
    const params = new URLSearchParams({
      page: page.toString(),
      page_size: pageSize.toString(),
    })
    
    if (filters?.endpoint) params.append('endpoint', filters.endpoint)
    if (filters?.method) params.append('method', filters.method)
    if (filters?.status_code) params.append('status_code', filters.status_code.toString())
    
    return apiRequest<FetchHistoryResponse>(`/fetch-history?${params}`)
  },

  async getStats(): Promise<FetchHistoryStats> {
    return apiRequest<FetchHistoryStats>('/fetch-history/stats')
  },

  async deleteItem(historyId: string): Promise<{ success: boolean }> {
    return apiRequest(`/fetch-history/${historyId}`, {
      method: 'DELETE',
    })
  },

  async clearHistory(): Promise<{ success: boolean; deleted_count: number }> {
    return apiRequest('/fetch-history', {
      method: 'DELETE',
    })
  },
}

export { ApiError }
