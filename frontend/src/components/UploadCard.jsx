import React, { useRef, useState } from 'react'

const UploadCard = ({ file, onSelectFile, onAnalyze, onReset, isUploading, error }) => {
  const inputRef = useRef(null)
  const [dragOver, setDragOver] = useState(false)

  const onClickUpload = () => inputRef.current?.click()
  const onFileChange = (e) => {
    const f = e.target.files?.[0]
    if (!f) return
    if (f.type !== 'application/pdf') {
      return alert('Unsupported file format. Please upload a PDF.')
    }
    onSelectFile(f)
  }

  const onDrop = (e) => {
    e.preventDefault()
    setDragOver(false)
    const f = e.dataTransfer.files?.[0]
    if (!f) return
    if (f.type !== 'application/pdf') {
      return alert('Unsupported file format. Please upload a PDF.')
    }
    onSelectFile(f)
  }

  return (
    <div className="upload-card">
      {!file && (
        <div
          className={`upload-card__drop ${dragOver ? 'is-over' : ''}`}
          onClick={onClickUpload}
          onDragOver={(e) => { e.preventDefault(); setDragOver(true) }}
          onDragLeave={() => setDragOver(false)}
          onDrop={onDrop}
        >
          <div className="upload-card__icon">📄</div>
          <div className="upload-card__title">Upload PDF</div>
          <div className="upload-card__hint">Click to upload or drag & drop (PDF only)</div>
          <input ref={inputRef} type="file" accept="application/pdf" className="upload-card__input" onChange={onFileChange} />
        </div>
      )}

      {file && (
        <div className="upload-card__selected">
          <div className="upload-card__file">{file.name}</div>
          <div className="upload-card__actions">
            <button className="btn" onClick={onAnalyze} disabled={isUploading}>Analyze document</button>
            <button className="btn secondary" onClick={() => onSelectFile(null)} disabled={isUploading}>Change file</button>
            <button className="btn danger" onClick={onReset} disabled={isUploading}>Reset</button>
          </div>
          {isUploading && <div className="upload-card__loading">Uploading and analyzing…</div>}
          {error && <div className="upload-card__error">{error}</div>}
        </div>
      )}
    </div>
  )
}

export default UploadCard