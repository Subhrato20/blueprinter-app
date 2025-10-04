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
  EyeOff
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
  code: 'text-blue-600 bg-blue-100',
  test: 'text-green-600 bg-green-100',
  config: 'text-purple-600 bg-purple-100',
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
        className="flex items-start gap-3 p-4 border border-gray-200 rounded-lg hover:bg-gray-50 cursor-pointer"
        onClick={() => handleTextSelection(`/steps/${index}/summary`, step.summary)}
      >
        <div className={`p-2 rounded-md ${colorClass}`}>
          <Icon className="h-4 w-4" />
        </div>
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 mb-1">
            <span className="text-sm font-medium text-gray-900">{step.target}</span>
            <span className={`badge ${colorClass}`}>{step.kind}</span>
          </div>
          <p className="text-sm text-gray-600">{step.summary}</p>
        </div>
      </div>
    )
  }

  const renderFile = (file: any, index: number) => {
    const isExpanded = expandedFiles.has(index)
    const lines = file.content.split('\n').length
    
    return (
      <div key={index} className="border border-gray-200 rounded-lg overflow-hidden">
        <div
          className="flex items-center justify-between p-4 bg-gray-50 cursor-pointer hover:bg-gray-100"
          onClick={() => toggleFile(index)}
        >
          <div className="flex items-center gap-3">
            <FileText className="h-4 w-4 text-gray-500" />
            <span className="font-medium text-gray-900">{file.path}</span>
            <span className="text-sm text-gray-500">{lines} lines</span>
          </div>
          <div className="flex items-center gap-2">
            <button
              onClick={(e) => {
                e.stopPropagation()
                copyToClipboard(file.content)
              }}
              className="p-1 hover:bg-gray-200 rounded"
            >
              <Copy className="h-4 w-4 text-gray-500" />
            </button>
            {isExpanded ? (
              <ChevronDown className="h-4 w-4 text-gray-500" />
            ) : (
              <ChevronRight className="h-4 w-4 text-gray-500" />
            )}
          </div>
        </div>
        {isExpanded && (
          <div className="p-4 bg-white">
            <pre
              className="text-sm text-gray-800 whitespace-pre-wrap font-mono cursor-pointer"
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
        className="flex items-start gap-3 p-3 bg-yellow-50 border border-yellow-200 rounded-lg cursor-pointer hover:bg-yellow-100"
        onClick={() => handleTextSelection(`/risks/${index}`, risk)}
      >
        <AlertTriangle className="h-4 w-4 text-yellow-600 mt-0.5 flex-shrink-0" />
        <p className="text-sm text-yellow-800">{risk}</p>
      </div>
    )
  }

  const renderTest = (test: string, index: number) => {
    return (
      <div
        key={index}
        className="flex items-start gap-3 p-3 bg-green-50 border border-green-200 rounded-lg cursor-pointer hover:bg-green-100"
        onClick={() => handleTextSelection(`/tests/${index}`, test)}
      >
        <CheckCircle className="h-4 w-4 text-green-600 mt-0.5 flex-shrink-0" />
        <p className="text-sm text-green-800">{test}</p>
      </div>
    )
  }

  const renderPRBody = () => {
    return (
      <div
        className="p-4 bg-gray-50 border border-gray-200 rounded-lg cursor-pointer hover:bg-gray-100"
        onClick={() => handleTextSelection('/prBody', plan.prBody)}
      >
        <pre className="text-sm text-gray-800 whitespace-pre-wrap font-mono">
          {plan.prBody}
        </pre>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Patch Preview Toggle */}
      {patchPreview && (
        <div className="card">
          <div className="card-content">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold">Patch Preview</h3>
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
                <div className="p-4 bg-blue-50 border border-blue-200 rounded-lg">
                  <h4 className="font-medium text-blue-900 mb-2">Rationale</h4>
                  <p className="text-sm text-blue-800">{patchPreview.rationale}</p>
                </div>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <h4 className="font-medium text-gray-900 mb-2">Original</h4>
                    <div className="p-3 bg-red-50 border border-red-200 rounded text-sm font-mono">
                      {JSON.stringify(patchPreview.original, null, 2)}
                    </div>
                  </div>
                  <div>
                    <h4 className="font-medium text-gray-900 mb-2">Modified</h4>
                    <div className="p-3 bg-green-50 border border-green-200 rounded text-sm font-mono">
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
          className="card-header cursor-pointer"
          onClick={() => toggleSection('steps')}
        >
          <div className="flex items-center justify-between">
            <h3 className="text-lg font-semibold">Development Steps</h3>
            {expandedSections.steps ? (
              <ChevronDown className="h-5 w-5 text-gray-500" />
            ) : (
              <ChevronRight className="h-5 w-5 text-gray-500" />
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
          className="card-header cursor-pointer"
          onClick={() => toggleSection('files')}
        >
          <div className="flex items-center justify-between">
            <h3 className="text-lg font-semibold">Files to Create/Modify</h3>
            {expandedSections.files ? (
              <ChevronDown className="h-5 w-5 text-gray-500" />
            ) : (
              <ChevronRight className="h-5 w-5 text-gray-500" />
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
          className="card-header cursor-pointer"
          onClick={() => toggleSection('risks')}
        >
          <div className="flex items-center justify-between">
            <h3 className="text-lg font-semibold">Potential Risks</h3>
            {expandedSections.risks ? (
              <ChevronDown className="h-5 w-5 text-gray-500" />
            ) : (
              <ChevronRight className="h-5 w-5 text-gray-500" />
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
          className="card-header cursor-pointer"
          onClick={() => toggleSection('tests')}
        >
          <div className="flex items-center justify-between">
            <h3 className="text-lg font-semibold">Test Scenarios</h3>
            {expandedSections.tests ? (
              <ChevronDown className="h-5 w-5 text-gray-500" />
            ) : (
              <ChevronRight className="h-5 w-5 text-gray-500" />
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
          className="card-header cursor-pointer"
          onClick={() => toggleSection('prBody')}
        >
          <div className="flex items-center justify-between">
            <h3 className="text-lg font-semibold">Pull Request Body</h3>
            {expandedSections.prBody ? (
              <ChevronDown className="h-5 w-5 text-gray-500" />
            ) : (
              <ChevronRight className="h-5 w-5 text-gray-500" />
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
