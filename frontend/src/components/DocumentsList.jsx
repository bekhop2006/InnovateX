import React, { useState } from 'react'

const DocumentsList = ({ documents, onOpenViewer, onBack, onExportResults }) => {
  const [expandedDocs, setExpandedDocs] = useState({})

  const toggleExpand = (idx) => {
    setExpandedDocs(prev => ({ ...prev, [idx]: !prev[idx] }))
  }

  const totalStats = documents.reduce((acc, doc) => {
    if (doc.results) {
      acc.qr += doc.results.counters.qr
      acc.signatures += doc.results.counters.signatures
      acc.stamps += doc.results.counters.stamps
      acc.pages += doc.results.pages.length
      acc.processingTime += doc.results.processingTime || 0
    }
    return acc
  }, { qr: 0, signatures: 0, stamps: 0, pages: 0, processingTime: 0 })

  const completedDocs = documents.filter(doc => doc.status === 'completed').length
  const errorDocs = documents.filter(doc => doc.status === 'error').length

  return (
    <div className="documents-list">
      <div className="documents-list__header">
        <div className="documents-list__title">
          <h2>Scan Results</h2>
          <div className="documents-list__summary">
            {completedDocs} successful • {errorDocs} failed • {documents.length} total
          </div>
        </div>
        <div className="documents-list__actions">
          {onExportResults && (
            <button className="btn secondary" onClick={onExportResults}>
              Export Results (JSON)
            </button>
          )}
          <button className="btn" onClick={onBack}>
            New Scan
          </button>
        </div>
      </div>

      <div className="documents-list__stats">
        <div className="stat-card">
          <div className="stat-card__value">{totalStats.pages}</div>
          <div className="stat-card__label">Total Pages</div>
        </div>
        <div className="stat-card stat-card--blue">
          <div className="stat-card__value">{totalStats.qr}</div>
          <div className="stat-card__label">QR Codes</div>
        </div>
        <div className="stat-card stat-card--green">
          <div className="stat-card__value">{totalStats.signatures}</div>
          <div className="stat-card__label">Signatures</div>
        </div>
        <div className="stat-card stat-card--orange">
          <div className="stat-card__value">{totalStats.stamps}</div>
          <div className="stat-card__label">Stamps</div>
        </div>
        <div className="stat-card">
          <div className="stat-card__value">{totalStats.processingTime.toFixed(1)}s</div>
          <div className="stat-card__label">Total Time</div>
        </div>
      </div>

      <div className="documents-list__items">
        {documents.map((doc, idx) => (
          <div key={idx} className={`document-card ${doc.status}`}>
            <div className="document-card__header" onClick={() => toggleExpand(idx)}>
              <div className="document-card__main">
                <div className="document-card__icon">
                  {doc.status === 'completed' && '✅'}
                  {doc.status === 'processing' && '⏳'}
                  {doc.status === 'error' && '❌'}
                </div>
                <div className="document-card__info">
                  <div className="document-card__name">{doc.file.name}</div>
                  <div className="document-card__meta">
                    {doc.status === 'completed' && doc.results && (
                      <>
                        {doc.results.pages.length} pages • 
                        {doc.results.counters.qr + doc.results.counters.signatures + doc.results.counters.stamps} items • 
                        {doc.results.processingTime?.toFixed(2)}s
                      </>
                    )}
                    {doc.status === 'processing' && 'Processing...'}
                    {doc.status === 'error' && `Error: ${doc.error}`}
                  </div>
                </div>
              </div>
              {doc.status === 'completed' && (
                <button
                  className="btn small"
                  onClick={(e) => {
                    e.stopPropagation()
                    onOpenViewer(idx)
                  }}
                >
                  View PDF
                </button>
              )}
              <div className="document-card__expand">
                {expandedDocs[idx] ? '▼' : '▶'}
              </div>
            </div>

            {expandedDocs[idx] && doc.status === 'completed' && doc.results && (
              <div className="document-card__details">
                <div className="document-card__counters">
                  <div className="counter counter--blue">
                    <span className="counter__value">{doc.results.counters.qr}</span>
                    <span className="counter__label">QR</span>
                  </div>
                  <div className="counter counter--green">
                    <span className="counter__value">{doc.results.counters.signatures}</span>
                    <span className="counter__label">Signatures</span>
                  </div>
                  <div className="counter counter--orange">
                    <span className="counter__value">{doc.results.counters.stamps}</span>
                    <span className="counter__label">Stamps</span>
                  </div>
                </div>
                <div className="document-card__pages">
                  <strong>Pages:</strong>
                  {doc.results.pages.map((page, pidx) => (
                    <span key={pidx} className="page-badge">
                      Page {pidx + 1} ({page.items.length})
                    </span>
                  ))}
                </div>
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  )
}

export default DocumentsList

