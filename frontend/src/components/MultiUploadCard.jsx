import React, { useRef, useState } from 'react'

const MultiUploadCard = ({ files, onSelectFiles, onAnalyze, onReset, onRemoveFile, isUploading, progress }) => {
  const inputRef = useRef(null)
  const [dragOver, setDragOver] = useState(false)

  const onClickUpload = () => inputRef.current?.click()
  
  const onFileChange = (e) => {
    const newFiles = Array.from(e.target.files || [])
    const pdfFiles = newFiles.filter(f => f.type === 'application/pdf')
    
    if (pdfFiles.length !== newFiles.length) {
      alert('Some files were skipped. Only PDF files are supported.')
    }
    
    if (pdfFiles.length > 0) {
      onSelectFiles(pdfFiles)
    }
  }

  const onDrop = (e) => {
    e.preventDefault()
    setDragOver(false)
    const newFiles = Array.from(e.dataTransfer.files || [])
    const pdfFiles = newFiles.filter(f => f.type === 'application/pdf')
    
    if (pdfFiles.length !== newFiles.length) {
      alert('Some files were skipped. Only PDF files are supported.')
    }
    
    if (pdfFiles.length > 0) {
      onSelectFiles(pdfFiles)
    }
  }

  return (
    <div className="multi-upload-card">
      <div
        className={`multi-upload-card__drop ${dragOver ? 'is-over' : ''}`}
        onClick={onClickUpload}
        onDragOver={(e) => { e.preventDefault(); setDragOver(true) }}
        onDragLeave={() => setDragOver(false)}
        onDrop={onDrop}
      >
        <div className="multi-upload-card__icon">📄</div>
        <div className="multi-upload-card__title">Upload Multiple PDFs</div>
        <div className="multi-upload-card__hint">
          Click to upload or drag & drop multiple PDF files
        </div>
        <input 
          ref={inputRef} 
          type="file" 
          accept="application/pdf" 
          multiple
          className="multi-upload-card__input" 
          onChange={onFileChange} 
        />
      </div>

      {files.length > 0 && (
        <div className="multi-upload-card__list">
          <div className="multi-upload-card__header">
            <h3>Selected Files ({files.length})</h3>
            <button 
              className="btn small secondary" 
              onClick={onClickUpload}
              disabled={isUploading}
            >
              Add More
            </button>
          </div>
          
          <div className="multi-upload-card__files">
            {files.map((file, idx) => (
              <div key={idx} className="file-item">
                <div className="file-item__icon">📄</div>
                <div className="file-item__info">
                  <div className="file-item__name">{file.name}</div>
                  <div className="file-item__size">
                    {(file.size / 1024 / 1024).toFixed(2)} MB
                  </div>
                </div>
                {progress && progress[idx] !== undefined && (
                  <div className="file-item__progress">
                    <div className="progress-bar">
                      <div 
                        className="progress-bar__fill" 
                        style={{ width: `${progress[idx]}%` }}
                      />
                    </div>
                    <span className="progress-text">{progress[idx]}%</span>
                  </div>
                )}
                <button
                  className="file-item__remove"
                  onClick={() => onRemoveFile(idx)}
                  disabled={isUploading}
                  title="Remove file"
                >
                  ✕
                </button>
              </div>
            ))}
          </div>

          <div className="multi-upload-card__actions">
            <button 
              className="btn" 
              onClick={onAnalyze} 
              disabled={isUploading || files.length === 0}
            >
              {isUploading ? 'Analyzing...' : `Analyze ${files.length} Document${files.length > 1 ? 's' : ''}`}
            </button>
            <button 
              className="btn danger" 
              onClick={onReset} 
              disabled={isUploading}
            >
              Clear All
            </button>
          </div>
        </div>
      )}
    </div>
  )
}

export default MultiUploadCard

