import React, { useState } from 'react'
import { planApi, downloadZip, ApiError, askApi, patchApi, cursorApi } from './services/api'
import { PlanViewer } from './components/PlanViewer'
import { AskCopilotModal } from './components/AskCopilotModal'
import { ToastContainer } from './components/Toast'
import CodingPreferencesManager from './components/CodingPreferencesManager'
import { FetchHistoryViewer } from './components/FetchHistoryViewer'
import type { PlanJSON, SelectionState, PatchPreview } from './types'
import { 
  Download, 
  Copy, 
  Sparkles,
  Settings,
  History
} from 'lucide-react'

function App() {
  const [currentPlan, setCurrentPlan] = useState<PlanJSON | null>(null)
  const [currentPlanId, setCurrentPlanId] = useState<string | null>(null)
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [idea, setIdea] = useState('')
  const [showAskModal, setShowAskModal] = useState(false)
  const [selection, setSelection] = useState<SelectionState>({
    nodePath: '',
    selectionText: '',
    isActive: false
  })
  const [patchPreview, setPatchPreview] = useState<PatchPreview | null>(null)
  const [showPreferences, setShowPreferences] = useState(false)
  const [showHistory, setShowHistory] = useState(false)

  const handleGeneratePlan = async () => {
    if (!idea.trim()) return

    try {
      setIsLoading(true)
      setError(null)

      const response = await planApi.createPlan({
        idea: idea.trim(),
        projectId: 'default-project' // Use a default project ID
      })

      setCurrentPlan(response.plan)
      setCurrentPlanId(response.planId)
      setIdea('')
    } catch (error) {
      if (error instanceof ApiError) {
        const message = error.detail || error.message || 'Failed to generate plan'
        setError(message)
        console.error('Plan generation failed:', error.status, message)
      } else {
        console.error('Unexpected error generating plan:', error)
        setError('Failed to generate plan')
      }
    } finally {
      setIsLoading(false)
    }
  }

  const handleDownloadZip = async () => {
    if (!currentPlan) return
    
    try {
      await downloadZip(currentPlan)
    } catch (error) {
      setError(error.message)
    }
  }

  const handleCopyCursorLink = async () => {
    if (!currentPlanId) return
    
    try {
      const data = await cursorApi.createLink(currentPlanId)
      
      // Copy to clipboard
      await navigator.clipboard.writeText(data.link)
      
      // Show success message
      setError(null)
      addToast('Cursor link copied to clipboard!', 'success')
    } catch (error: any) {
      const message = error?.detail || error?.message || 'Failed to create Cursor link'
      setError(message)
    }
  }

  const handleSelection = (nodePath: string, selectionText: string) => {
    setSelection({
      nodePath,
      selectionText,
      isActive: true
    })
    setShowAskModal(true)
  }

  const handleAskCopilot = async (question: string) => {
    if (!currentPlanId || !selection.isActive) return

    try {
      setIsLoading(true)
      const patchResponse = await askApi.askCopilot({
        planId: currentPlanId,
        nodePath: selection.nodePath,
        selectionText: selection.selectionText,
        userQuestion: question
      })
      
      // Create patch preview
      if (currentPlan) {
        const { applyPatch } = await import('fast-json-patch')
        const modified = applyPatch(currentPlan, patchResponse.patch)
        
        setPatchPreview({
          original: currentPlan,
          modified: modified.newDocument,
          patch: patchResponse.patch,
          rationale: patchResponse.rationale
        })
      }
    } catch (error: any) {
      const message = error?.detail || error?.message || 'Failed to get copilot response'
      setError(message)
    } finally {
      setIsLoading(false)
    }
  }

  const handleApplyPatch = async () => {
    if (!patchPreview || !currentPlanId) return

    try {
      setIsLoading(true)
      const result = await patchApi.applyPatch({
        planId: currentPlanId,
        patch: patchPreview.patch
      })
      setCurrentPlan(result.updatedPlan)
      setPatchPreview(null)
      setShowAskModal(false)
    } catch (error: any) {
      const message = error?.detail || error?.message || 'Failed to apply patch'
      setError(message)
    } finally {
      setIsLoading(false)
    }
  }

  // No authentication needed - direct access

  return (
    <div className="min-h-screen">
      {/* Header */}
      <header className="glass sticky top-0 z-40 border-b border-gray-200/50 backdrop-blur-lg">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center gap-4">
              <div className="flex items-center gap-3">
                <div className="relative">
                  <div className="absolute inset-0 bg-gradient-to-r from-primary-500 to-accent-500 blur-lg opacity-30 rounded-full"></div>
                  <div className="relative bg-gradient-to-r from-primary-600 to-accent-600 p-2 rounded-xl">
                    <Zap className="h-6 w-6 text-white" />
                  </div>
                </div>
                <div>
                  <h1 className="text-xl font-bold bg-gradient-to-r from-primary-600 to-accent-600 bg-clip-text text-transparent">Blueprint Snap</h1>
                  <p className="text-xs text-gray-500">Dev DNA Edition</p>
                </div>
              </div>
            </div>
            <div className="flex items-center gap-3">
              <button
                onClick={() => {
                  setShowHistory(!showHistory)
                  setShowPreferences(false)
                }}
                className="btn-outline flex items-center gap-2"
              >
                <History className="h-4 w-4" />
                Fetch History
              </button>
              <button
                onClick={() => {
                  setShowPreferences(!showPreferences)
                  setShowHistory(false)
                }}
                className="btn-outline flex items-center gap-2"
              >
                <Settings className="h-4 w-4" />
                <span className="hidden sm:inline">Preferences</span>
              </button>
              <button
                onClick={() => {
                  setCurrentPlan(null)
                  setCurrentPlanId(null)
                  setIdea('')
                  setShowHistory(false)
                  setShowPreferences(false)
                }}
                className="btn-primary flex items-center gap-2"
              >
                <Sparkles className="h-4 w-4" />
                <span className="hidden sm:inline">New Plan</span>
              </button>
            </div>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {error && (
          <div className="mb-6 p-4 bg-red-50 border-l-4 border-red-500 rounded-lg shadow-soft animate-slide-down">
            <div className="flex items-start gap-3">
              <XCircle className="h-5 w-5 text-red-600 mt-0.5 flex-shrink-0" />
              <div className="flex-1">
                <p className="text-red-800 font-medium">{error}</p>
                <button 
                  onClick={() => setError(null)}
                  className="mt-2 text-sm text-red-600 hover:text-red-800 underline"
                >
                  Dismiss
                </button>
              </div>
            </div>
          </div>
        )}

        {showHistory ? (
          <div className="h-[calc(100vh-12rem)]">
            <FetchHistoryViewer />
          </div>
        ) : showPreferences ? (
          <CodingPreferencesManager />
        ) : !currentPlan ? (
          <div className="max-w-3xl mx-auto">
            <div className="text-center mb-8 animate-fade-in">
              <div className="inline-flex items-center justify-center w-16 h-16 rounded-full bg-gradient-to-r from-primary-500 to-accent-500 mb-4">
                <Sparkles className="h-8 w-8 text-white" />
              </div>
              <h2 className="text-3xl font-bold text-gray-900 mb-3">Create Your Development Plan</h2>
              <p className="text-lg text-gray-600">
                Describe your idea and get a complete plan with files, tests, and implementation steps.
              </p>
            </div>
            <div className="card animate-scale-up">
              <div className="card-content">
                <div className="space-y-6">
                  <div>
                    <label htmlFor="idea" className="block text-sm font-semibold text-gray-700 mb-3">
                      💡 What would you like to build?
                    </label>
                    <textarea
                      id="idea"
                      value={idea}
                      onChange={(e) => setIdea(e.target.value)}
                      placeholder="e.g., Build a user authentication system with email verification and password reset"
                      className="textarea w-full text-base"
                      rows={4}
                    />
                  </div>
                  <button
                    onClick={handleGeneratePlan}
                    disabled={!idea.trim() || isLoading}
                    className="w-full btn-primary py-4 flex items-center justify-center gap-3 text-base"
                  >
                    {isLoading ? (
                      <>
                        <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white"></div>
                        <span>Generating your plan...</span>
                      </>
                    ) : (
                      <>
                        <Sparkles className="h-5 w-5" />
                        <span>Generate Development Plan</span>
                      </>
                    )}
                  </button>
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4 pt-4 border-t border-gray-200">
                    <div className="text-center p-3">
                      <div className="text-2xl mb-1">📝</div>
                      <div className="text-sm font-medium text-gray-900">Step-by-Step</div>
                      <div className="text-xs text-gray-500">Clear implementation steps</div>
                    </div>
                    <div className="text-center p-3">
                      <div className="text-2xl mb-1">📁</div>
                      <div className="text-sm font-medium text-gray-900">File Structure</div>
                      <div className="text-xs text-gray-500">Complete file templates</div>
                    </div>
                    <div className="text-center p-3">
                      <div className="text-2xl mb-1">🧪</div>
                      <div className="text-sm font-medium text-gray-900">Test Coverage</div>
                      <div className="text-xs text-gray-500">Comprehensive testing</div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        ) : (
          <div className="space-y-6 animate-fade-in">
            {/* Plan Actions */}
            <div className="card">
              <div className="card-content">
                <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
                  <div>
                    <h2 className="text-2xl font-bold bg-gradient-to-r from-gray-900 to-gray-700 bg-clip-text text-transparent mb-1">{currentPlan.title}</h2>
                    <p className="text-gray-600">✨ Your development plan is ready!</p>
                  </div>
                  <div className="flex items-center gap-3">
                    <button
                      onClick={handleDownloadZip}
                      className="btn-outline flex items-center gap-2"
                    >
                      <Download className="h-4 w-4" />
                      <span className="hidden sm:inline">Download ZIP</span>
                    </button>
                    <button
                      onClick={handleCopyCursorLink}
                      className="btn-primary flex items-center gap-2"
                    >
                      <Copy className="h-4 w-4" />
                      <span className="hidden sm:inline">Copy Link</span>
                    </button>
                  </div>
                </div>
              </div>
            </div>

            {/* Plan Viewer */}
            <PlanViewer
              plan={currentPlan}
              onSelection={handleSelection}
              patchPreview={patchPreview}
            />
          </div>
        )}
      </main>

      {/* Toast Notifications */}
      <ToastContainer toasts={toasts} onRemove={removeToast} />

      {/* Ask Copilot Modal */}
      {showAskModal && (
        <AskCopilotModal
          isOpen={showAskModal}
          onClose={() => {
            setShowAskModal(false)
            setSelection({ nodePath: '', selectionText: '', isActive: false })
            setPatchPreview(null)
          }}
          selection={selection}
          onAsk={handleAskCopilot}
          patchPreview={patchPreview}
          onApplyPatch={handleApplyPatch}
          isLoading={isLoading}
        />
      )}
    </div>
  )
}

export default App
