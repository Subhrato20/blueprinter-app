import React, { useState } from 'react'
import { 
  FileText, 
  Code, 
  TestTube, 
  Settings as ConfigIcon,
  AlertTriangle,
  CheckCircle,
  ChevronDown,
  ChevronRight,
  Copy,
  Eye,
  EyeOff,
  Sparkles
} from 'lucide-react'
import type { PlanJSON, SelectionState, PatchPreview } from '../types'
import { applyPatch } from 'fast-json-patch'

interface PlanViewerProps {
  plan: PlanJSON
  onSelection: (nodePath: string, selectionText: string) => void
  patchPreview?: PatchPreview | null
}

const stepIcons = {
  code: Code,
  test: TestTube,
  config: ConfigIcon,
}

const stepColors = {
  code: 'text-blue-700 bg-gradient-to-br from-blue-100 to-blue-50 border-blue-200',
  test: 'text-success-700 bg-gradient-to-br from-success-100 to-success-50 border-success-200',
  config: 'text-accent-700 bg-gradient-to-br from-accent-100 to-accent-50 border-accent-200',
}

export function PlanViewer({ plan, onSelection, patchPreview }: PlanViewerProps) {
  const [expandedSections, setExpandedSections] = useState({
    steps: true,
    files: true,
    risks: true,
    tests: true,
    prBody: true,
  })
  const [expandedFiles, setExpandedFiles] = useState<Set<number>>(new Set())
  const [showPatchPreview, setShowPatchPreview] = useState(false)

  const toggleSection = (section: keyof typeof expandedSections) => {
    setExpandedSections(prev => ({
      ...prev,
      [section]: !prev[section]
    }))
  }

  const toggleFile = (index: number) => {
    setExpandedFiles(prev => {
      const newSet = new Set(prev)
      if (newSet.has(index)) {
        newSet.delete(index)
      } else {
        newSet.add(index)
      }
      return newSet
    })
  }

  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text)
  }

  const handleTextSelection = (nodePath: string, text: string) => {
    onSelection(nodePath, text)
  }

  const renderStep = (step: any, index: number) => {
    const Icon = stepIcons[step.kind]
    const colorClass = stepColors[step.kind]
    
    return (
      <div
        key={index}
        className="group flex items-start gap-4 p-5 border-2 border-gray-200 rounded-xl hover:border-primary-300 hover:shadow-soft cursor-pointer transition-all duration-200 bg-white"
        onClick={() => handleTextSelection(`/steps/${index}/summary`, step.summary)}
      >
        <div className={`p-3 rounded-xl ${colorClass} border shadow-sm group-hover:scale-110 transition-transform duration-200`}>
          <Icon className="h-5 w-5" />
        </div>
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 mb-2">
            <span className="text-sm font-semibold text-gray-900">{step.target}</span>
            <span className={`badge ${colorClass} border`}>{step.kind}</span>
          </div>
          <p className="text-sm text-gray-600 leading-relaxed">{step.summary}</p>
        </div>
      </div>
    )
  }

  const renderFile = (file: any, index: number) => {
    const isExpanded = expandedFiles.has(index)
    const lines = file.content.split('\n').length
    
    return (
      <div key={index} className="border-2 border-gray-200 rounded-xl overflow-hidden hover:border-primary-300 transition-all duration-200">
        <div
          className="flex items-center justify-between p-4 bg-gradient-to-r from-gray-50 to-blue-50/30 cursor-pointer hover:from-gray-100 hover:to-blue-100/30 transition-all duration-200"
          onClick={() => toggleFile(index)}
        >
          <div className="flex items-center gap-3">
            <div className="p-2 rounded-lg bg-white shadow-sm">
              <FileText className="h-4 w-4 text-primary-600" />
            </div>
            <div>
              <span className="font-semibold text-gray-900 block">{file.path}</span>
              <span className="text-xs text-gray-500">{lines} lines</span>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <button
              onClick={(e) => {
                e.stopPropagation()
                copyToClipboard(file.content)
              }}
              className="p-2 hover:bg-white rounded-lg transition-colors"
              title="Copy to clipboard"
            >
              <Copy className="h-4 w-4 text-gray-600" />
            </button>
            {isExpanded ? (
              <ChevronDown className="h-5 w-5 text-gray-600" />
            ) : (
              <ChevronRight className="h-5 w-5 text-gray-600" />
            )}
          </div>
        </div>
        {isExpanded && (
          <div className="p-4 bg-white border-t border-gray-200">
            <pre
              className="text-sm text-gray-800 whitespace-pre-wrap font-mono cursor-pointer hover:bg-gray-50 p-3 rounded-lg transition-colors"
              onClick={() => handleTextSelection(`/files/${index}/content`, file.content)}
            >
              {file.content}
            </pre>
          </div>
        )}
      </div>
    )
  }

  const renderRisk = (risk: string, index: number) => {
    return (
      <div
        key={index}
        className="flex items-start gap-3 p-4 bg-gradient-to-br from-yellow-50 to-orange-50 border-2 border-yellow-200 rounded-xl cursor-pointer hover:border-yellow-300 hover:shadow-soft transition-all duration-200"
        onClick={() => handleTextSelection(`/risks/${index}`, risk)}
      >
        <div className="p-2 rounded-lg bg-white shadow-sm">
          <AlertTriangle className="h-4 w-4 text-yellow-600" />
        </div>
        <p className="text-sm text-yellow-900 leading-relaxed flex-1">{risk}</p>
      </div>
    )
  }

  const renderTest = (test: string, index: number) => {
    return (
      <div
        key={index}
        className="flex items-start gap-3 p-4 bg-gradient-to-br from-success-50 to-emerald-50 border-2 border-success-200 rounded-xl cursor-pointer hover:border-success-300 hover:shadow-soft transition-all duration-200"
        onClick={() => handleTextSelection(`/tests/${index}`, test)}
      >
        <div className="p-2 rounded-lg bg-white shadow-sm">
          <CheckCircle className="h-4 w-4 text-success-600" />
        </div>
        <p className="text-sm text-success-900 leading-relaxed flex-1">{test}</p>
      </div>
    )
  }

  const renderPRBody = () => {
    return (
      <div
        className="p-5 bg-gradient-to-br from-gray-50 to-blue-50/30 border-2 border-gray-200 rounded-xl cursor-pointer hover:border-primary-300 hover:shadow-soft transition-all duration-200"
        onClick={() => handleTextSelection('/prBody', plan.prBody)}
      >
        <pre className="text-sm text-gray-800 whitespace-pre-wrap font-mono leading-relaxed">
          {plan.prBody}
        </pre>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Patch Preview Toggle */}
      {patchPreview && (
        <div className="card border-2 border-primary-300 shadow-medium animate-slide-up">
          <div className="card-content">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-bold bg-gradient-to-r from-primary-600 to-accent-600 bg-clip-text text-transparent flex items-center gap-2">
                <Sparkles className="h-5 w-5 text-primary-600" />
                AI Patch Preview
              </h3>
              <button
                onClick={() => setShowPatchPreview(!showPatchPreview)}
                className="btn-outline flex items-center gap-2"
              >
                {showPatchPreview ? (
                  <>
                    <EyeOff className="h-4 w-4" />
                    Hide Preview
                  </>
                ) : (
                  <>
                    <Eye className="h-4 w-4" />
                    Show Preview
                  </>
                )}
              </button>
            </div>
            {showPatchPreview && (
              <div className="space-y-4">
                <div className="p-5 bg-gradient-to-br from-blue-50 to-primary-50 border-2 border-blue-200 rounded-xl">
                  <h4 className="font-semibold text-blue-900 mb-2">💡 Rationale</h4>
                  <p className="text-sm text-blue-800 leading-relaxed">{patchPreview.rationale}</p>
                </div>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <h4 className="font-semibold text-gray-900 mb-2 flex items-center gap-2">
                      <span className="text-red-600">❌</span> Original
                    </h4>
                    <div className="p-4 bg-red-50 border-2 border-red-200 rounded-xl text-sm font-mono overflow-x-auto">
                      {JSON.stringify(patchPreview.original, null, 2)}
                    </div>
                  </div>
                  <div>
                    <h4 className="font-semibold text-gray-900 mb-2 flex items-center gap-2">
                      <span className="text-success-600">✅</span> Modified
                    </h4>
                    <div className="p-4 bg-success-50 border-2 border-success-200 rounded-xl text-sm font-mono overflow-x-auto">
                      {JSON.stringify(patchPreview.modified, null, 2)}
                    </div>
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Steps Section */}
      <div className="card">
        <div
          className="card-header cursor-pointer hover:bg-gray-100 transition-colors"
          onClick={() => toggleSection('steps')}
        >
          <div className="flex items-center justify-between">
            <h3 className="text-lg font-bold text-gray-900 flex items-center gap-2">
              <Code className="h-5 w-5 text-primary-600" />
              Development Steps
            </h3>
            {expandedSections.steps ? (
              <ChevronDown className="h-5 w-5 text-gray-600" />
            ) : (
              <ChevronRight className="h-5 w-5 text-gray-600" />
            )}
          </div>
        </div>
        {expandedSections.steps && (
          <div className="card-content">
            <div className="space-y-3">
              {plan.steps.map((step, index) => renderStep(step, index))}
            </div>
          </div>
        )}
      </div>

      {/* Files Section */}
      <div className="card">
        <div
          className="card-header cursor-pointer hover:bg-gray-100 transition-colors"
          onClick={() => toggleSection('files')}
        >
          <div className="flex items-center justify-between">
            <h3 className="text-lg font-bold text-gray-900 flex items-center gap-2">
              <FileText className="h-5 w-5 text-blue-600" />
              Files to Create/Modify
            </h3>
            {expandedSections.files ? (
              <ChevronDown className="h-5 w-5 text-gray-600" />
            ) : (
              <ChevronRight className="h-5 w-5 text-gray-600" />
            )}
          </div>
        </div>
        {expandedSections.files && (
          <div className="card-content">
            <div className="space-y-3">
              {plan.files.map((file, index) => renderFile(file, index))}
            </div>
          </div>
        )}
      </div>

      {/* Risks Section */}
      <div className="card">
        <div
          className="card-header cursor-pointer hover:bg-gray-100 transition-colors"
          onClick={() => toggleSection('risks')}
        >
          <div className="flex items-center justify-between">
            <h3 className="text-lg font-bold text-gray-900 flex items-center gap-2">
              <AlertTriangle className="h-5 w-5 text-yellow-600" />
              Potential Risks
            </h3>
            {expandedSections.risks ? (
              <ChevronDown className="h-5 w-5 text-gray-600" />
            ) : (
              <ChevronRight className="h-5 w-5 text-gray-600" />
            )}
          </div>
        </div>
        {expandedSections.risks && (
          <div className="card-content">
            <div className="space-y-3">
              {plan.risks.map((risk, index) => renderRisk(risk, index))}
            </div>
          </div>
        )}
      </div>

      {/* Tests Section */}
      <div className="card">
        <div
          className="card-header cursor-pointer hover:bg-gray-100 transition-colors"
          onClick={() => toggleSection('tests')}
        >
          <div className="flex items-center justify-between">
            <h3 className="text-lg font-bold text-gray-900 flex items-center gap-2">
              <TestTube className="h-5 w-5 text-success-600" />
              Test Scenarios
            </h3>
            {expandedSections.tests ? (
              <ChevronDown className="h-5 w-5 text-gray-600" />
            ) : (
              <ChevronRight className="h-5 w-5 text-gray-600" />
            )}
          </div>
        </div>
        {expandedSections.tests && (
          <div className="card-content">
            <div className="space-y-3">
              {plan.tests.map((test, index) => renderTest(test, index))}
            </div>
          </div>
        )}
      </div>

      {/* PR Body Section */}
      <div className="card">
        <div
          className="card-header cursor-pointer hover:bg-gray-100 transition-colors"
          onClick={() => toggleSection('prBody')}
        >
          <div className="flex items-center justify-between">
            <h3 className="text-lg font-bold text-gray-900 flex items-center gap-2">
              <Copy className="h-5 w-5 text-accent-600" />
              Pull Request Body
            </h3>
            {expandedSections.prBody ? (
              <ChevronDown className="h-5 w-5 text-gray-600" />
            ) : (
              <ChevronRight className="h-5 w-5 text-gray-600" />
            )}
          </div>
        </div>
        {expandedSections.prBody && (
          <div className="card-content">
            {renderPRBody()}
          </div>
        )}
      </div>
    </div>
  )
}
