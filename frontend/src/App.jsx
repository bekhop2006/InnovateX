import React, { useState } from 'react'
import UploadCard from './components/UploadCard.jsx'
import MultiUploadCard from './components/MultiUploadCard.jsx'
import ResultsPanel from './components/ResultsPanel.jsx'
import DocumentsList from './components/DocumentsList.jsx'
import PdfViewer from './components/PdfViewer.jsx'

const App = () => {
  const [scanMode, setScanMode] = useState('single') // 'single' or 'multi'
  const [file, setFile] = useState(null)
  const [files, setFiles] = useState([])
  const [documents, setDocuments] = useState([]) // For multi-scan results
  const [view, setView] = useState('upload')
  const [isUploading, setIsUploading] = useState(false)
  const [error, setError] = useState(null)
  const [results, setResults] = useState(null)
  const [progress, setProgress] = useState({})

  const handleSelectFile = (f) => {
    setFile(f)
    setError(null)
  }

  const resetToUpload = () => {
    setFile(null)
    setFiles([])
    setDocuments([])
    setResults(null)
    setView('upload')
    setError(null)
    setIsUploading(false)
    setProgress({})
  }

  const toggleScanMode = () => {
    resetToUpload()
    setScanMode(mode => mode === 'single' ? 'multi' : 'single')
  }

  const handleSelectFiles = (newFiles) => {
    setFiles(prev => [...prev, ...newFiles])
    setError(null)
  }

  const handleRemoveFile = (idx) => {
    setFiles(prev => prev.filter((_, i) => i !== idx))
  }

  const analyzeDocument = async () => {
    if (!file) return
    setIsUploading(true)
    setError(null)
    try {
      // Try backend API first, fallback to local example.json
      const json = await (async () => {
        try {
          const form = new FormData()
          form.append('file', file)
          const res = await fetch('http://localhost:8000/api/document-inspector/detect?conf_threshold=0.5', {
            method: 'POST',
            body: form,
          })
          if (!res.ok) {
            const errorData = await res.json().catch(() => ({}))
            throw new Error(errorData.detail || `Backend error: ${res.status}`)
          }
          return await res.json()
        } catch (e) {
          console.warn('Backend not available, using example data:', e.message)
          // Backend not ready: load local example.json
          const res = await fetch('/example.json')
          if (!res.ok) throw new Error('Backend unavailable and local example not found')
          const exampleData = await res.json()
          // Convert old format to new format for compatibility
          return convertOldFormat(exampleData)
        }
      })()
      const parsed = parseBackend(json)
      if (!parsed) throw new Error('Invalid response format')
      setResults(parsed)
      setView('results')
    } catch (e) {
      setError(e.message || 'Unexpected error')
    } finally {
      setIsUploading(false)
    }
  }

  const analyzeMultipleDocuments = async () => {
    if (files.length === 0) return
    setIsUploading(true)
    setError(null)
    
    // Initialize documents state
    const initialDocs = files.map(file => ({
      file,
      status: 'processing',
      results: null,
      error: null
    }))
    setDocuments(initialDocs)
    setView('results')

    // Process each document
    for (let i = 0; i < files.length; i++) {
      try {
        setProgress(prev => ({ ...prev, [i]: 0 }))
        
        const form = new FormData()
        form.append('file', files[i])
        
        setProgress(prev => ({ ...prev, [i]: 30 }))
        
        const res = await fetch('http://localhost:8000/api/document-inspector/detect?conf_threshold=0.5', {
          method: 'POST',
          body: form,
        })
        
        setProgress(prev => ({ ...prev, [i]: 70 }))
        
        if (!res.ok) {
          const errorData = await res.json().catch(() => ({}))
          throw new Error(errorData.detail || `Backend error: ${res.status}`)
        }
        
        const json = await res.json()
        const parsed = parseBackend(json)
        
        if (!parsed) throw new Error('Invalid response format')
        
        setProgress(prev => ({ ...prev, [i]: 100 }))
        
        // Update document status
        setDocuments(prev => prev.map((doc, idx) => 
          idx === i ? { ...doc, status: 'completed', results: parsed } : doc
        ))
      } catch (e) {
        console.error(`Error processing ${files[i].name}:`, e)
        setDocuments(prev => prev.map((doc, idx) => 
          idx === i ? { ...doc, status: 'error', error: e.message } : doc
        ))
      }
    }
    
    setIsUploading(false)
  }

  const openViewer = (docIdx) => {
    if (scanMode === 'multi') {
      // Set current document for viewer
      setFile(documents[docIdx].file)
      setResults(documents[docIdx].results)
    }
    setView('viewer')
  }
  
  const closeViewer = () => setView('results')

  const exportResults = () => {
    const data = documents.map(doc => ({
      fileName: doc.file.name,
      status: doc.status,
      results: doc.results,
      error: doc.error
    }))
    
    const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `scan-results-${new Date().toISOString().split('T')[0]}.json`
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    URL.revokeObjectURL(url)
  }

  return (
    <div className="app">
      <header className="app__header">
        <div className="app__header-content">
          <h1>Construction PDF Analyzer</h1>
          <div className="app__mode-toggle">
            <button 
              className={`mode-btn ${scanMode === 'single' ? 'active' : ''}`}
              onClick={() => scanMode !== 'single' && toggleScanMode()}
            >
              Single Scan
            </button>
            <button 
              className={`mode-btn ${scanMode === 'multi' ? 'active' : ''}`}
              onClick={() => scanMode !== 'multi' && toggleScanMode()}
            >
              Multi Scan
            </button>
          </div>
        </div>
      </header>
      <main className="app__main">
        {view === 'upload' && scanMode === 'single' && (
          <UploadCard
            file={file}
            onSelectFile={handleSelectFile}
            onAnalyze={analyzeDocument}
            onReset={resetToUpload}
            isUploading={isUploading}
            error={error}
          />
        )}
        {view === 'upload' && scanMode === 'multi' && (
          <MultiUploadCard
            files={files}
            onSelectFiles={handleSelectFiles}
            onAnalyze={analyzeMultipleDocuments}
            onReset={resetToUpload}
            onRemoveFile={handleRemoveFile}
            isUploading={isUploading}
            progress={progress}
          />
        )}
        {view === 'results' && scanMode === 'single' && results && (
          <ResultsPanel
            fileName={results.fileName}
            pageCount={results.pages.length}
            counters={results.counters}
            processingTime={results.processingTime}
            onOpenViewer={() => openViewer(0)}
            onBack={resetToUpload}
          />
        )}
        {view === 'results' && scanMode === 'multi' && documents.length > 0 && (
          <DocumentsList
            documents={documents}
            onOpenViewer={openViewer}
            onBack={resetToUpload}
            onExportResults={exportResults}
          />
        )}
        {view === 'viewer' && results && file && (
          <PdfViewer
            file={file}
            pages={results.pages}
            onClose={closeViewer}
          />
        )}
      </main>
    </div>
  )
}

// Convert old format (example.json) to new backend format
function convertOldFormat(json) {
  try {
    const fileKey = Object.keys(json)[0]
    if (!fileKey) return null
    const fileData = json[fileKey]
    const pageKeys = Object.keys(fileData || {}).sort((a, b) => 
      parseInt(a.replace('page_', ''), 10) - parseInt(b.replace('page_', ''), 10)
    )
    
    return {
      document_name: fileKey,
      total_pages: pageKeys.length,
      pages: pageKeys.map((pk, idx) => {
        const page = fileData[pk]
        return {
          page_number: idx + 1,
          page_size: page.page_size,
          annotations: (page.annotations || []).map((entry) => {
            const idKey = Object.keys(entry)[0]
            const v = entry[idKey]
            return {
              id: idKey,
              category: v.category,
              bbox: v.bbox,
              confidence: 0.95, // Fake confidence for old format
              area: v.area
            }
          })
        }
      }),
      processing_time: 0
    }
  } catch (e) {
    console.error('Error converting old format:', e)
    return null
  }
}

// Parse new backend response format
function parseBackend(json) {
  try {
    // Check if it's the new backend format
    if (!json.document_name || !json.pages || !Array.isArray(json.pages)) {
      console.error('Invalid backend response format', json)
      return null
    }

    const pages = json.pages.map((page, idx) => {
      const items = (page.annotations || []).map((ann) => ({
        id: ann.id,
        category: ann.category,
        bbox: ann.bbox,
        confidence: ann.confidence,
        area: ann.bbox.width * ann.bbox.height
      }))
      
      return {
        index: idx,
        pageKey: `page_${page.page_number}`,
        pageSize: page.page_size,
        items
      }
    })

    const counters = pages.reduce(
      (acc, p) => {
        p.items.forEach((it) => {
          if (it.category === 'qr') acc.qr += 1
          else if (it.category === 'signature') acc.signatures += 1
          else if (it.category === 'stamp') acc.stamps += 1
        })
        return acc
      },
      { qr: 0, signatures: 0, stamps: 0 }
    )

    return {
      fileName: json.document_name,
      pages,
      counters,
      processingTime: json.processing_time
    }
  } catch (e) {
    console.error('Error parsing backend response:', e)
    return null
  }
}

export default App