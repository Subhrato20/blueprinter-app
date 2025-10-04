import React, { useState } from 'react'
import { planApi, downloadZip, ApiError } from './services/api'
import { PlanViewer } from './components/PlanViewer'
import { AskCopilotModal } from './components/AskCopilotModal'
import CodingPreferencesManager from './components/CodingPreferencesManager'
import type { PlanJSON, SelectionState, PatchPreview } from './types'
import { 
  Download, 
  Copy, 
  Sparkles,
  Settings
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
      const response = await fetch('/api/cursor-link', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ planId: currentPlanId })
      })

      if (!response.ok) {
        throw new Error('Failed to generate cursor link')
      }

      const data = await response.json()
      
      // Copy to clipboard
      await navigator.clipboard.writeText(data.link)
      
      // Show success message
      setError(null)
      // You could add a toast notification here instead
      alert('Cursor link copied to clipboard!')
    } catch (error) {
      setError(error.message)
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
      const response = await fetch('/api/ask', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('supabase.auth.token')}`
        },
        body: JSON.stringify({
          planId: currentPlanId,
          nodePath: selection.nodePath,
          selectionText: selection.selectionText,
          userQuestion: question
        })
      })

      if (!response.ok) {
        throw new Error('Failed to get copilot response')
      }

      const patchResponse = await response.json()
      
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
    } catch (error) {
      setError(error.message)
    } finally {
      setIsLoading(false)
    }
  }

  const handleApplyPatch = async () => {
    if (!patchPreview || !currentPlanId) return

    try {
      setIsLoading(true)
      const response = await fetch('/api/plan/patch', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('supabase.auth.token')}`
        },
        body: JSON.stringify({
          planId: currentPlanId,
          patch: patchPreview.patch
        })
      })

      if (!response.ok) {
        throw new Error('Failed to apply patch')
      }

      const result = await response.json()
      setCurrentPlan(result.updatedPlan)
      setPatchPreview(null)
      setShowAskModal(false)
    } catch (error) {
      setError(error.message)
    } finally {
      setIsLoading(false)
    }
  }

  // No authentication needed - direct access

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center gap-4">
              <div className="flex items-center gap-2">
                <Sparkles className="h-8 w-8 text-primary-600" />
                <h1 className="text-xl font-bold text-gray-900">Blueprint Snap</h1>
              </div>
              <div className="flex items-center gap-2 text-sm text-gray-600">
                <span>/</span>
                <span>Personal Project</span>
              </div>
            </div>
            <div className="flex items-center gap-4">
              <button
                onClick={() => setShowPreferences(!showPreferences)}
                className="btn-outline flex items-center gap-2"
              >
                <Settings className="h-4 w-4" />
                Coding Preferences
              </button>
              <button
                onClick={() => {
                  setCurrentPlan(null)
                  setCurrentPlanId(null)
                  setIdea('')
                }}
                className="btn-outline flex items-center gap-2"
              >
                <Sparkles className="h-4 w-4" />
                New Plan
              </button>
            </div>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {error && (
          <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-md">
            <p className="text-red-800">{error}</p>
            <button 
              onClick={() => setError(null)}
              className="mt-2 text-sm text-red-600 hover:text-red-800"
            >
              Dismiss
            </button>
          </div>
        )}

        {showPreferences ? (
          <CodingPreferencesManager />
        ) : !currentPlan ? (
          <div className="max-w-2xl mx-auto">
            <div className="card">
              <div className="card-header">
                <h2 className="text-xl font-semibold">Generate a Development Plan</h2>
                <p className="text-gray-600">
                  Describe your idea in one line and get a complete development plan with files, tests, and implementation steps.
                </p>
              </div>
              <div className="card-content">
                <div className="space-y-4">
                  <div>
                    <label htmlFor="idea" className="block text-sm font-medium text-gray-700 mb-2">
                      Your Idea
                    </label>
                    <textarea
                      id="idea"
                      value={idea}
                      onChange={(e) => setIdea(e.target.value)}
                      placeholder="e.g., Add user search with pagination to the admin panel"
                      className="textarea w-full"
                      rows={3}
                    />
                  </div>
                  <button
                    onClick={handleGeneratePlan}
                    disabled={!idea.trim() || isLoading}
                    className="w-full btn-primary py-3 flex items-center justify-center gap-2"
                  >
                    {isLoading ? (
                      <>
                        <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                        Generating Plan...
                      </>
                    ) : (
                      <>
                        <Sparkles className="h-5 w-5" />
                        Generate Plan
                      </>
                    )}
                  </button>
                </div>
              </div>
            </div>
          </div>
        ) : (
          <div className="space-y-6">
            {/* Plan Actions */}
            <div className="flex items-center justify-between">
              <div>
                <h2 className="text-2xl font-bold text-gray-900">{currentPlan.title}</h2>
                <p className="text-gray-600">Generated development plan</p>
              </div>
              <div className="flex items-center gap-3">
                <button
                  onClick={handleDownloadZip}
                  className="btn-outline flex items-center gap-2"
                >
                  <Download className="h-4 w-4" />
                  Download ZIP
                </button>
                <button
                  onClick={handleCopyCursorLink}
                  className="btn-primary flex items-center gap-2"
                >
                  <Copy className="h-4 w-4" />
                  Copy Cursor Link
                </button>
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
