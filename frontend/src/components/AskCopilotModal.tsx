import React, { useState } from 'react'
import { X, Send, Check, XCircle, MessageSquare, Sparkles } from 'lucide-react'
import type { SelectionState, PatchPreview } from '../types'

interface AskCopilotModalProps {
  isOpen: boolean
  onClose: () => void
  selection: SelectionState
  onAsk: (question: string) => void
  patchPreview?: PatchPreview | null
  onApplyPatch?: () => void
  isLoading: boolean
}

export function AskCopilotModal({
  isOpen,
  onClose,
  selection,
  onAsk,
  patchPreview,
  onApplyPatch,
  isLoading
}: AskCopilotModalProps) {
  const [question, setQuestion] = useState('')
  const [showPreview, setShowPreview] = useState(false)

  if (!isOpen) return null

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (question.trim()) {
      onAsk(question.trim())
      setQuestion('')
    }
  }

  const handleApplyPatch = () => {
    if (onApplyPatch) {
      onApplyPatch()
    }
  }

  return (
    <div className="fixed inset-0 bg-black/60 backdrop-blur-sm flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-2xl shadow-lg max-w-2xl w-full max-h-[90vh] overflow-hidden">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-gray-100 bg-gradient-to-r from-primary-50 to-accent-50">
          <div className="flex items-center gap-3">
            <div className="relative">
              <div className="absolute inset-0 bg-gradient-to-r from-primary-500 to-accent-500 blur opacity-40 rounded-lg"></div>
              <div className="relative p-2 bg-gradient-to-r from-primary-600 to-accent-600 rounded-lg">
                <Sparkles className="h-5 w-5 text-white" />
              </div>
            </div>
            <div>
              <h2 className="text-lg font-semibold bg-gradient-to-r from-primary-600 to-accent-600 bg-clip-text text-transparent">Ask AI Copilot</h2>
              <p className="text-sm text-gray-600">Get intelligent suggestions for your plan</p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-2 hover:bg-white rounded-lg transition-all duration-200 hover:shadow-sm"
          >
            <X className="h-5 w-5 text-gray-500" />
          </button>
        </div>

        {/* Content */}
        <div className="p-6 space-y-6 overflow-y-auto max-h-[calc(90vh-140px)]">
          {/* Selection Context */}
          <div className="bg-gradient-to-br from-gray-50 to-blue-50/30 rounded-xl p-4 border border-gray-200">
            <h3 className="text-sm font-semibold text-gray-900 mb-3 flex items-center gap-2">
              <MessageSquare className="h-4 w-4 text-primary-600" />
              Selected Context
            </h3>
            <div className="space-y-3">
              <div>
                <span className="text-xs font-semibold text-gray-600 mb-1 block">Path:</span>
                <code className="text-xs bg-white px-3 py-2 rounded-lg border border-gray-200 block">
                  {selection.nodePath}
                </code>
              </div>
              <div>
                <span className="text-xs font-semibold text-gray-600 mb-1 block">Text:</span>
                <p className="text-sm text-gray-800 bg-white p-3 rounded-lg border border-gray-200 font-mono">
                  {selection.selectionText}
                </p>
              </div>
            </div>
          </div>

          {/* Question Input */}
          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label htmlFor="question" className="block text-sm font-semibold text-gray-700 mb-3">
                🤔 What would you like to ask about this selection?
              </label>
              <textarea
                id="question"
                value={question}
                onChange={(e) => setQuestion(e.target.value)}
                placeholder="e.g., How can I improve this step? What are the potential issues? Can you suggest a better approach?"
                className="textarea w-full"
                rows={3}
                disabled={isLoading}
              />
            </div>
            <button
              type="submit"
              disabled={!question.trim() || isLoading}
              className="btn-primary flex items-center gap-2 w-full justify-center"
            >
              {isLoading ? (
                <>
                  <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                  <span>Asking AI Copilot...</span>
                </>
              ) : (
                <>
                  <Send className="h-4 w-4" />
                  <span>Ask AI Copilot</span>
                </>
              )}
            </button>
          </form>

          {/* Patch Preview */}
          {patchPreview && (
            <div className="border border-primary-200 rounded-xl overflow-hidden shadow-sm animate-pulse">
              <div className="bg-gradient-to-r from-primary-50 to-blue-50 px-4 py-3 border-b border-primary-100">
                <div className="flex items-center justify-between">
                  <h3 className="text-sm font-semibold text-primary-900 flex items-center gap-2">
                    <Sparkles className="h-4 w-4 text-primary-600" />
                    AI Copilot Response
                  </h3>
                  <button
                    onClick={() => setShowPreview(!showPreview)}
                    className="text-sm text-primary-600 hover:text-primary-700 font-medium"
                  >
                    {showPreview ? 'Hide' : 'Show'} Details
                  </button>
                </div>
              </div>
              
              <div className="p-4">
                <div className="mb-4">
                  <h4 className="text-sm font-semibold text-gray-900 mb-2 flex items-center gap-2">
                    <MessageSquare className="h-4 w-4 text-blue-600" />
                    Rationale
                  </h4>
                  <p className="text-sm text-gray-700 bg-gradient-to-br from-blue-50 to-primary-50 p-4 rounded-lg border border-blue-200">
                    {patchPreview.rationale}
                  </p>
                </div>

                {showPreview && (
                  <div className="space-y-4">
                    <div>
                      <h4 className="text-sm font-semibold text-gray-900 mb-2">🔧 Proposed Changes</h4>
                      <div className="bg-gray-50 p-4 rounded-lg border border-gray-200">
                        <pre className="text-xs text-gray-800 font-mono overflow-x-auto">
                          {JSON.stringify(patchPreview.patch, null, 2)}
                        </pre>
                      </div>
                    </div>
                  </div>
                )}

                <div className="flex items-center gap-3 mt-4">
                  <button
                    onClick={handleApplyPatch}
                    className="btn-success flex items-center gap-2"
                  >
                    <Check className="h-4 w-4" />
                    Apply Changes
                  </button>
                  <button
                    onClick={() => setShowPreview(false)}
                    className="btn-secondary flex items-center gap-2"
                  >
                    <XCircle className="h-4 w-4" />
                    Dismiss
                  </button>
                </div>
              </div>
            </div>
          )}

          {/* Quick Questions */}
          <div className="border-t border-gray-200 pt-4">
            <h3 className="text-sm font-semibold text-gray-900 mb-3">⚡ Quick Questions</h3>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
              {[
                "How can I improve this?",
                "What are potential issues?",
                "Suggest a better approach",
                "Add more detail",
                "Simplify this step",
                "Add error handling"
              ].map((quickQuestion) => (
                <button
                  key={quickQuestion}
                  onClick={() => setQuestion(quickQuestion)}
                  className="text-left p-3 text-sm text-gray-700 bg-gradient-to-br from-gray-50 to-blue-50/30 hover:from-primary-50 hover:to-accent-50 rounded-lg border border-gray-200 hover:border-primary-300 transition-all duration-200 hover:shadow-sm"
                  disabled={isLoading}
                >
                  {quickQuestion}
                </button>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
