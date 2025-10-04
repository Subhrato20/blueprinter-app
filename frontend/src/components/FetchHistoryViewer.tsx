import { useState, useEffect } from 'react'
import { fetchHistoryApi } from '../services/fetchHistory'
import type { FetchHistoryItem, FetchHistoryStats } from '../types'

export function FetchHistoryViewer() {
  const [items, setItems] = useState<FetchHistoryItem[]>([])
  const [stats, setStats] = useState<FetchHistoryStats | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [page, setPage] = useState(1)
  const [total, setTotal] = useState(0)
  const [pageSize] = useState(50)
  const [selectedItem, setSelectedItem] = useState<FetchHistoryItem | null>(null)
  const [filters, setFilters] = useState({
    method: '',
    endpoint: '',
  })

  const loadHistory = async () => {
    setLoading(true)
    setError(null)
    try {
      const filterParams = {
        method: filters.method || undefined,
        endpoint: filters.endpoint || undefined,
      }
      const response = await fetchHistoryApi.getHistory(page, pageSize, filterParams)
      setItems(response.items)
      setTotal(response.total)
    } catch (err: any) {
      setError(err.message || 'Failed to load history')
    } finally {
      setLoading(false)
    }
  }

  const loadStats = async () => {
    try {
      const statsData = await fetchHistoryApi.getStats()
      setStats(statsData)
    } catch (err) {
      console.error('Failed to load stats:', err)
    }
  }

  useEffect(() => {
    loadHistory()
    loadStats()
  }, [page, filters])

  const handleClearHistory = async () => {
    if (!confirm('Are you sure you want to clear all history?')) return
    
    try {
      await fetchHistoryApi.clearHistory()
      loadHistory()
      loadStats()
    } catch (err: any) {
      setError(err.message || 'Failed to clear history')
    }
  }

  const handleDeleteItem = async (id: string) => {
    try {
      await fetchHistoryApi.deleteItem(id)
      loadHistory()
      loadStats()
      setSelectedItem(null)
    } catch (err: any) {
      setError(err.message || 'Failed to delete item')
    }
  }

  const getStatusColor = (statusCode?: number) => {
    if (!statusCode) return 'bg-gray-500'
    if (statusCode >= 200 && statusCode < 300) return 'bg-green-500'
    if (statusCode >= 300 && statusCode < 400) return 'bg-blue-500'
    if (statusCode >= 400 && statusCode < 500) return 'bg-yellow-500'
    return 'bg-red-500'
  }

  const getMethodColor = (method: string) => {
    const colors: Record<string, string> = {
      GET: 'bg-blue-100 text-blue-800',
      POST: 'bg-green-100 text-green-800',
      PUT: 'bg-yellow-100 text-yellow-800',
      PATCH: 'bg-purple-100 text-purple-800',
      DELETE: 'bg-red-100 text-red-800',
    }
    return colors[method] || 'bg-gray-100 text-gray-800'
  }

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleString()
  }

  return (
    <div className="w-full h-full flex flex-col bg-white rounded-lg shadow-lg overflow-hidden">
      {/* Header */}
      <div className="bg-gradient-to-r from-blue-600 to-purple-600 text-white p-6">
        <h2 className="text-2xl font-bold mb-2">Fetch History</h2>
        <p className="text-blue-100">Track all API requests and responses</p>
      </div>

      {/* Stats Bar */}
      {stats && (
        <div className="bg-gray-50 border-b border-gray-200 p-4">
          <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
            <div className="text-center">
              <div className="text-2xl font-bold text-gray-900">{stats.total_requests}</div>
              <div className="text-xs text-gray-500">Total Requests</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-green-600">{stats.success_rate.toFixed(1)}%</div>
              <div className="text-xs text-gray-500">Success Rate</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-red-600">{stats.error_count}</div>
              <div className="text-xs text-gray-500">Errors</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-blue-600">{stats.average_duration_ms.toFixed(0)}ms</div>
              <div className="text-xs text-gray-500">Avg Duration</div>
            </div>
            <div className="text-center">
              <button
                onClick={handleClearHistory}
                className="px-4 py-2 bg-red-600 text-white text-sm rounded hover:bg-red-700 transition"
              >
                Clear History
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Filters */}
      <div className="bg-white border-b border-gray-200 p-4">
        <div className="flex gap-4">
          <div className="flex-1">
            <input
              type="text"
              placeholder="Filter by endpoint..."
              value={filters.endpoint}
              onChange={(e) => setFilters({ ...filters, endpoint: e.target.value })}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
          </div>
          <select
            value={filters.method}
            onChange={(e) => setFilters({ ...filters, method: e.target.value })}
            className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          >
            <option value="">All Methods</option>
            <option value="GET">GET</option>
            <option value="POST">POST</option>
            <option value="PUT">PUT</option>
            <option value="PATCH">PATCH</option>
            <option value="DELETE">DELETE</option>
          </select>
        </div>
      </div>

      {/* Content */}
      <div className="flex-1 overflow-hidden flex">
        {/* List */}
        <div className="w-1/2 border-r border-gray-200 overflow-y-auto">
          {loading ? (
            <div className="flex items-center justify-center h-full">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
            </div>
          ) : error ? (
            <div className="flex items-center justify-center h-full">
              <div className="text-center">
                <p className="text-red-600 mb-2">Error: {error}</p>
                <button
                  onClick={loadHistory}
                  className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 transition"
                >
                  Retry
                </button>
              </div>
            </div>
          ) : items.length === 0 ? (
            <div className="flex items-center justify-center h-full text-gray-500">
              No history items found
            </div>
          ) : (
            <div className="divide-y divide-gray-200">
              {items.map((item) => (
                <div
                  key={item.id}
                  onClick={() => setSelectedItem(item)}
                  className={`p-4 cursor-pointer hover:bg-gray-50 transition ${
                    selectedItem?.id === item.id ? 'bg-blue-50 border-l-4 border-blue-600' : ''
                  }`}
                >
                  <div className="flex items-center justify-between mb-2">
                    <span className={`px-2 py-1 rounded text-xs font-semibold ${getMethodColor(item.method)}`}>
                      {item.method}
                    </span>
                    {item.status_code && (
                      <span className={`px-2 py-1 rounded text-white text-xs ${getStatusColor(item.status_code)}`}>
                        {item.status_code}
                      </span>
                    )}
                  </div>
                  <div className="text-sm font-medium text-gray-900 mb-1 truncate">
                    {item.endpoint}
                  </div>
                  <div className="flex items-center justify-between text-xs text-gray-500">
                    <span>{formatDate(item.created_at)}</span>
                    {item.duration_ms && <span>{item.duration_ms}ms</span>}
                  </div>
                  {item.error_message && (
                    <div className="mt-2 text-xs text-red-600 truncate">
                      Error: {item.error_message}
                    </div>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Detail View */}
        <div className="w-1/2 overflow-y-auto bg-gray-50">
          {selectedItem ? (
            <div className="p-6">
              <div className="flex items-center justify-between mb-6">
                <h3 className="text-lg font-semibold text-gray-900">Request Details</h3>
                <button
                  onClick={() => handleDeleteItem(selectedItem.id)}
                  className="px-3 py-1 bg-red-600 text-white text-sm rounded hover:bg-red-700 transition"
                >
                  Delete
                </button>
              </div>

              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Endpoint</label>
                  <div className="bg-white p-3 rounded border border-gray-300 text-sm font-mono">
                    {selectedItem.endpoint}
                  </div>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Method</label>
                  <span className={`inline-block px-3 py-1 rounded text-sm font-semibold ${getMethodColor(selectedItem.method)}`}>
                    {selectedItem.method}
                  </span>
                </div>

                {selectedItem.status_code && (
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Status Code</label>
                    <span className={`inline-block px-3 py-1 rounded text-white text-sm ${getStatusColor(selectedItem.status_code)}`}>
                      {selectedItem.status_code}
                    </span>
                  </div>
                )}

                {selectedItem.duration_ms && (
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Duration</label>
                    <div className="text-sm">{selectedItem.duration_ms}ms</div>
                  </div>
                )}

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Timestamp</label>
                  <div className="text-sm">{formatDate(selectedItem.created_at)}</div>
                </div>

                {selectedItem.request_data && (
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Request Data</label>
                    <pre className="bg-white p-3 rounded border border-gray-300 text-xs overflow-x-auto">
                      {JSON.stringify(selectedItem.request_data, null, 2)}
                    </pre>
                  </div>
                )}

                {selectedItem.response_data && (
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Response Data</label>
                    <pre className="bg-white p-3 rounded border border-gray-300 text-xs overflow-x-auto max-h-96 overflow-y-auto">
                      {JSON.stringify(selectedItem.response_data, null, 2)}
                    </pre>
                  </div>
                )}

                {selectedItem.error_message && (
                  <div>
                    <label className="block text-sm font-medium text-red-700 mb-1">Error Message</label>
                    <div className="bg-red-50 border border-red-300 p-3 rounded text-sm text-red-900">
                      {selectedItem.error_message}
                    </div>
                  </div>
                )}
              </div>
            </div>
          ) : (
            <div className="flex items-center justify-center h-full text-gray-500">
              Select an item to view details
            </div>
          )}
        </div>
      </div>

      {/* Pagination */}
      {total > pageSize && (
        <div className="bg-white border-t border-gray-200 p-4">
          <div className="flex items-center justify-between">
            <div className="text-sm text-gray-700">
              Showing {(page - 1) * pageSize + 1} to {Math.min(page * pageSize, total)} of {total} results
            </div>
            <div className="flex gap-2">
              <button
                onClick={() => setPage(page - 1)}
                disabled={page === 1}
                className="px-4 py-2 border border-gray-300 rounded disabled:opacity-50 disabled:cursor-not-allowed hover:bg-gray-50 transition"
              >
                Previous
              </button>
              <button
                onClick={() => setPage(page + 1)}
                disabled={page * pageSize >= total}
                className="px-4 py-2 border border-gray-300 rounded disabled:opacity-50 disabled:cursor-not-allowed hover:bg-gray-50 transition"
              >
                Next
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
