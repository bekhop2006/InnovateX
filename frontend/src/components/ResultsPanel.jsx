import React from 'react'

const ResultsPanel = ({ fileName, pageCount, counters, processingTime, onOpenViewer, onBack }) => {
  return (
    <div className="results-panel">
      <div className="results-panel__header">
        <div className="results-panel__file">{fileName}</div>
        <div className="results-panel__pages">Pages: {pageCount}</div>
        {processingTime !== undefined && processingTime > 0 && (
          <div className="results-panel__time">Processing time: {processingTime.toFixed(2)}s</div>
        )}
      </div>
      <div className="results-panel__stats">
        <div className="stat stat--blue">QR: {counters.qr}</div>
        <div className="stat stat--green">Signatures: {counters.signatures}</div>
        <div className="stat stat--orange">Stamps: {counters.stamps}</div>
      </div>
      <div className="results-panel__actions">
        <button className="btn" onClick={onOpenViewer}>Open PDF viewer</button>
        <button className="btn secondary" onClick={onBack}>Back</button>
      </div>
      <div className="results-panel__legend">
        <div className="legend__item"><span className="legend__swatch legend__swatch--blue" /> QR</div>
        <div className="legend__item"><span className="legend__swatch legend__swatch--green" /> Signature</div>
        <div className="legend__item"><span className="legend__swatch legend__swatch--orange" /> Stamp</div>
      </div>
    </div>
  )
}

export default ResultsPanel