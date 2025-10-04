import React, { useState, useEffect } from 'react'
import { supabase, getCurrentUser } from './lib/supabase'
import { planApi, downloadZip, openInCursor } from './services/api'
import { PlanViewer } from './components/PlanViewer'
import { AskCopilotModal } from './components/AskCopilotModal'
import type { User, Project, PlanJSON, SelectionState, PatchPreview } from './types'
import { 
  Plus, 
  Download, 
  ExternalLink, 
  Github, 
  LogOut, 
  Settings,
  Sparkles,
  FileText,
  Code,
  TestTube,
  Settings as ConfigIcon
} from 'lucide-react'

function App() {
  const [user, setUser] = useState<User | null>(null)
  const [currentProject, setCurrentProject] = useState<Project | null>(null)
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

  useEffect(() => {
    // Check for existing session
    getCurrentUser().then(({ user }) => {
      if (user) {
        setUser({
          id: user.id,
          email: user.email || '',
          name: user.user_metadata?.full_name || user.user_metadata?.name
        })
      }
    })

    // Listen for auth changes
    const { data: { subscription } } = supabase.auth.onAuthStateChange(
      async (event, session) => {
        if (session?.user) {
          setUser({
            id: session.user.id,
            email: session.user.email || '',
            name: session.user.user_metadata?.full_name || session.user.user_metadata?.name
          })
        } else {
          setUser(null)
          setCurrentProject(null)
          setCurrentPlan(null)
          setCurrentPlanId(null)
        }
      }
    )

    return () => subscription.unsubscribe()
  }, [])

  const handleSignIn = async () => {
    try {
      const { error } = await supabase.auth.signInWithOAuth({
        provider: 'github',
        options: {
          redirectTo: `${window.location.origin}/auth/callback`
        }
      })
      if (error) throw error
    } catch (error) {
      setError(error.message)
    }
  }

  const handleSignOut = async () => {
    try {
      const { error } = await supabase.auth.signOut()
      if (error) throw error
    } catch (error) {
      setError(error.message)
    }
  }

  const handleCreateProject = async () => {
    if (!user) return
    
    try {
      setIsLoading(true)
      const { data, error } = await supabase
        .from('projects')
        .insert({
          name: 'New Project',
          description: 'A new Blueprint Snap project',
          owner: user.id
        })
        .select()
        .single()

      if (error) throw error
      setCurrentProject(data)
    } catch (error) {
      setError(error.message)
    } finally {
      setIsLoading(false)
    }
  }

  const handleGeneratePlan = async () => {
    if (!idea.trim() || !currentProject) return

    try {
      setIsLoading(true)
      setError(null)

      const response = await planApi.createPlan({
        idea: idea.trim(),
        projectId: currentProject.id
      })

      setCurrentPlan(response.plan)
      setCurrentPlanId(response.planId)
      setIdea('')
    } catch (error) {
      setError(error.message)
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

  const handleOpenInCursor = async () => {
    if (!currentPlanId) return
    
    try {
      await openInCursor(currentPlanId)
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

  if (!user) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-primary-50 to-primary-100 flex items-center justify-center">
        <div className="max-w-md w-full mx-4">
          <div className="card">
            <div className="card-header text-center">
              <div className="flex items-center justify-center mb-4">
                <Sparkles className="h-12 w-12 text-primary-600" />
              </div>
              <h1 className="text-2xl font-bold text-gray-900">Blueprint Snap</h1>
              <p className="text-gray-600">Dev DNA Edition</p>
              <p className="text-sm text-gray-500 mt-2">
                One-line idea → Plan JSON + style-adapted scaffolds + Ask-Copilot + Cursor deep link
              </p>
            </div>
            <div className="card-content">
              <button
                onClick={handleSignIn}
                className="w-full btn-primary py-3 flex items-center justify-center gap-2"
              >
                <Github className="h-5 w-5" />
                Sign in with GitHub
              </button>
            </div>
          </div>
        </div>
      </div>
    )
  }

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
              {currentProject && (
                <div className="flex items-center gap-2 text-sm text-gray-600">
                  <span>/</span>
                  <span>{currentProject.name}</span>
                </div>
              )}
            </div>
            <div className="flex items-center gap-4">
              <button
                onClick={handleCreateProject}
                className="btn-outline flex items-center gap-2"
              >
                <Plus className="h-4 w-4" />
                New Project
              </button>
              <button
                onClick={handleSignOut}
                className="btn-outline flex items-center gap-2"
              >
                <LogOut className="h-4 w-4" />
                Sign Out
              </button>
            </div>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {error && (
          <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-md">
            <p className="text-red-800">{error}</p>
          </div>
        )}

        {!currentProject ? (
          <div className="text-center py-12">
            <h2 className="text-2xl font-bold text-gray-900 mb-4">Welcome to Blueprint Snap</h2>
            <p className="text-gray-600 mb-8">Create a project to get started with AI-powered development planning.</p>
            <button
              onClick={handleCreateProject}
              disabled={isLoading}
              className="btn-primary py-3 px-6 flex items-center gap-2 mx-auto"
            >
              <Plus className="h-5 w-5" />
              Create Your First Project
            </button>
          </div>
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
                  onClick={handleOpenInCursor}
                  className="btn-primary flex items-center gap-2"
                >
                  <ExternalLink className="h-4 w-4" />
                  Add to Cursor
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
