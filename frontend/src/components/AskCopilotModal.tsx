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
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg shadow-xl max-w-2xl w-full max-h-[90vh] overflow-hidden">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-gray-200">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-primary-100 rounded-lg">
              <Sparkles className="h-5 w-5 text-primary-600" />
            </div>
            <div>
              <h2 className="text-lg font-semibold text-gray-900">Ask Copilot</h2>
              <p className="text-sm text-gray-600">Get AI suggestions for your plan</p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
          >
            <X className="h-5 w-5 text-gray-500" />
          </button>
        </div>

        {/* Content */}
        <div className="p-6 space-y-6 overflow-y-auto max-h-[calc(90vh-140px)]">
          {/* Selection Context */}
          <div className="bg-gray-50 rounded-lg p-4">
            <h3 className="text-sm font-medium text-gray-900 mb-2">Selected Context</h3>
            <div className="space-y-2">
              <div>
                <span className="text-xs font-medium text-gray-600">Path:</span>
                <code className="ml-2 text-xs bg-white px-2 py-1 rounded border">
                  {selection.nodePath}
                </code>
              </div>
              <div>
                <span className="text-xs font-medium text-gray-600">Text:</span>
                <p className="mt-1 text-sm text-gray-800 bg-white p-2 rounded border font-mono">
                  {selection.selectionText}
                </p>
              </div>
            </div>
          </div>

          {/* Question Input */}
          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label htmlFor="question" className="block text-sm font-medium text-gray-700 mb-2">
                What would you like to ask about this selection?
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
              className="btn-primary flex items-center gap-2"
            >
              {isLoading ? (
                <>
                  <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                  Asking Copilot...
                </>
              ) : (
                <>
                  <Send className="h-4 w-4" />
                  Ask Copilot
                </>
              )}
            </button>
          </form>

          {/* Patch Preview */}
          {patchPreview && (
            <div className="border border-gray-200 rounded-lg overflow-hidden">
              <div className="bg-gray-50 px-4 py-3 border-b border-gray-200">
                <div className="flex items-center justify-between">
                  <h3 className="text-sm font-medium text-gray-900">Copilot Response</h3>
                  <button
                    onClick={() => setShowPreview(!showPreview)}
                    className="text-sm text-primary-600 hover:text-primary-700"
                  >
                    {showPreview ? 'Hide' : 'Show'} Details
                  </button>
                </div>
              </div>
              
              <div className="p-4">
                <div className="mb-4">
                  <h4 className="text-sm font-medium text-gray-900 mb-2">Rationale</h4>
                  <p className="text-sm text-gray-700 bg-blue-50 p-3 rounded border">
                    {patchPreview.rationale}
                  </p>
                </div>

                {showPreview && (
                  <div className="space-y-4">
                    <div>
                      <h4 className="text-sm font-medium text-gray-900 mb-2">Proposed Changes</h4>
                      <div className="bg-gray-50 p-3 rounded border">
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
                    className="btn-primary flex items-center gap-2"
                  >
                    <Check className="h-4 w-4" />
                    Apply Changes
                  </button>
                  <button
                    onClick={() => setShowPreview(false)}
                    className="btn-outline flex items-center gap-2"
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
            <h3 className="text-sm font-medium text-gray-900 mb-3">Quick Questions</h3>
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
                  className="text-left p-3 text-sm text-gray-700 bg-gray-50 hover:bg-gray-100 rounded-lg border transition-colors"
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
