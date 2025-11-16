import React, { useEffect, useState } from 'react'
import { Document, Page, pdfjs } from 'react-pdf'
import { decodeQRFromImageData, extractQRText, ensureURLProtocol } from '../utils/qrDecoder'

const QRAnalyzer = ({ file, pages, onClose }) => {
  const [qrItems, setQrItems] = useState([])
  const [hoveredQR, setHoveredQR] = useState(null)
  const [decodedQRs, setDecodedQRs] = useState({})
  const [isLoading, setIsLoading] = useState(true)
  const [expandedPages, setExpandedPages] = useState({})
  const [canvasCache, setCanvasCache] = useState({})

  // Extract QR codes from detection results
  useEffect(() => {
    const extractedQRs = []
    pages.forEach((page, pageIdx) => {
      page.items.forEach((item) => {
        if (item.category === 'qr') {
          extractedQRs.push({
            id: item.id,
            pageIdx,
            bbox: item.bbox,
            pageSize: page.pageSize,
            file,
            category: item.category
          })
        }
      })
    })
    setQrItems(extractedQRs)
  }, [pages, file])

  // Decode QR codes from their thumbnails
  useEffect(() => {
    const decodeQRs = async () => {
      setIsLoading(true)
      const decoded = {}
      const newCanvasCache = {}

      for (const qr of qrItems) {
        try {
          // Use cached canvas if available, otherwise create new one
          let canvas = canvasCache[qr.id]
          
          if (!canvas) {
            canvas = document.createElement('canvas')
            const thumbWidth = 300
            const pageSize = qr.pageSize
            const thumbHeight = pageSize?.height && pageSize?.width 
              ? (thumbWidth * pageSize.height) / pageSize.width 
              : thumbWidth

            canvas.width = thumbWidth
            canvas.height = thumbHeight

            const ctx = canvas.getContext('2d')
            if (!ctx) continue

            // Fill with white background
            ctx.fillStyle = 'white'
            ctx.fillRect(0, 0, thumbWidth, thumbHeight)

            newCanvasCache[qr.id] = canvas
          }

          // Try to decode from canvas
          const imageData = canvas.getContext('2d').getImageData(0, 0, canvas.width, canvas.height)
          const decodedData = decodeQRFromImageData(imageData)
          
          if (decodedData) {
            decoded[qr.id] = {
              data: decodedData.data,
              location: decodedData.location,
              canvasData: canvas.toDataURL()
            }
          } else {
            // If decoding fails on empty canvas, mark as error
            decoded[qr.id] = {
              data: null,
              error: 'Could not decode QR code'
            }
          }
        } catch (error) {
          console.error(`Error decoding QR ${qr.id}:`, error)
          decoded[qr.id] = {
            data: null,
            error: error.message
          }
        }
      }

      setCanvasCache(prev => ({ ...prev, ...newCanvasCache }))
      setDecodedQRs(decoded)
      setIsLoading(false)
    }

    if (qrItems.length > 0) {
      // Give a short delay to allow canvases to render
      const timer = setTimeout(decodeQRs, 500)
      return () => clearTimeout(timer)
    } else {
      setIsLoading(false)
    }
  }, [qrItems, canvasCache])

  const handleQRClick = (qrItem) => {
    const decodedData = decodedQRs[qrItem.id]
    if (decodedData && decodedData.data) {
      const url = ensureURLProtocol(decodedData.data)
      try {
        window.open(url, '_blank', 'noopener,noreferrer')
      } catch (error) {
        console.error('Error opening URL:', error)
        alert(`Could not open URL: ${url}`)
      }
    }
  }

  // Group QR codes by page
  const qrsByPage = {}
  qrItems.forEach((qr) => {
    if (!qrsByPage[qr.pageIdx]) {
      qrsByPage[qr.pageIdx] = []
    }
    qrsByPage[qr.pageIdx].push(qr)
  })

  const pageIndices = Object.keys(qrsByPage).sort((a, b) => parseInt(a) - parseInt(b))

  return (
    <div className="qr-analyzer">
      <div className="qr-analyzer__header">
        <h2 className="qr-analyzer__title">QR Code Analysis</h2>
        <button className="btn secondary" onClick={onClose}>Close</button>
      </div>

      {isLoading && qrItems.length > 0 && (
        <div className="qr-analyzer__loading">
          Analyzing QR codes...
        </div>
      )}

      {!isLoading && qrItems.length === 0 && (
        <div className="qr-analyzer__empty">
          No QR codes detected in this document
        </div>
      )}

      {!isLoading && qrItems.length > 0 && (
        <div className="qr-analyzer__content">
          {pageIndices.map((pageIdx) => {
            const pageNum = parseInt(pageIdx)
            const pageQRs = qrsByPage[pageNum]
            const isExpanded = expandedPages[pageNum]
            const displayLimit = isExpanded ? pageQRs.length : 6
            const hasMore = pageQRs.length > 6

            return (
              <div key={pageNum} className="qr-analyzer__page-group">
                <div className="qr-analyzer__page-header">
                  <h3 className="qr-analyzer__page-title">Page {pageNum + 1}</h3>
                  <span className="qr-analyzer__count">{pageQRs.length} QR codes</span>
                </div>

                <div className="qr-analyzer__grid">
                  {pageQRs.slice(0, displayLimit).map((qr, idx) => {
                    const decoded = decodedQRs[qr.id]
                    const isHovered = hoveredQR === qr.id
                    const isClickable = decoded && decoded.data

                    return (
                      <div
                        key={idx}
                        className={`qr-analyzer__item ${isHovered ? 'is-hovered' : ''} ${isClickable ? 'is-clickable' : ''}`}
                        onMouseEnter={() => setHoveredQR(qr.id)}
                        onMouseLeave={() => setHoveredQR(null)}
                        onClick={() => isClickable && handleQRClick(qr)}
                      >
                        {/* Render QR code thumbnail */}
                        <div className="qr-analyzer__thumbnail">
                          <Document file={qr.file}>
                            <Page
                              pageNumber={qr.pageIdx + 1}
                              width={220}
                              renderTextLayer={false}
                              renderAnnotationLayer={false}
                              scale={1}
                            />
                          </Document>
                          {/* Highlight QR area */}
                          <div
                            className="qr-analyzer__highlight"
                            style={{
                              left: `${(qr.bbox.x / qr.pageSize.width) * 100}%`,
                              top: `${(qr.bbox.y / qr.pageSize.height) * 100}%`,
                              width: `${(qr.bbox.width / qr.pageSize.width) * 100}%`,
                              height: `${(qr.bbox.height / qr.pageSize.height) * 100}%`
                            }}
                          />
                        </div>

                        {/* Hover tooltip showing QR URL */}
                        {isHovered && decoded && (
                          <>
                            {decoded.data ? (
                              <div className="qr-analyzer__tooltip">
                                <div className="qr-analyzer__tooltip-title">QR URL:</div>
                                <div className="qr-analyzer__tooltip-url">{decoded.data}</div>
                                <div className="qr-analyzer__tooltip-hint">Click to open</div>
                              </div>
                            ) : (
                              <div className="qr-analyzer__tooltip">
                                <div className="qr-analyzer__tooltip-error">
                                  {decoded.error || 'Could not decode QR code'}
                                </div>
                              </div>
                            )}
                          </>
                        )}
                      </div>
                    )
                  })}
                </div>

                {hasMore && (
                  <button
                    className="qr-analyzer__expand-btn"
                    onClick={() => setExpandedPages(prev => ({ ...prev, [pageNum]: !prev[pageNum] }))}
                  >
                    {isExpanded ? '− Show Less' : `+ ${pageQRs.length - 6} More QR Codes`}
                  </button>
                )}
              </div>
            )
          })}
        </div>
      )}

      {/* Hidden canvases for QR decoding */}
      <div style={{ display: 'none' }}>
        {qrItems.map((qr) => (
          <QRCanvasRenderer
            key={qr.id}
            qrId={qr.id}
            file={qr.file}
            pageNum={qr.pageIdx + 1}
            bbox={qr.bbox}
            pageSize={qr.pageSize}
            onCanvasReady={(canvas) => {
              setCanvasCache(prev => ({ ...prev, [qr.id]: canvas }))
            }}
          />
        ))}
      </div>
    </div>
  )
}

/**
 * Component to render a specific PDF region and expose it as a canvas
 */
const QRCanvasRenderer = ({ qrId, file, pageNum, bbox, pageSize, onCanvasReady }) => {
  const containerRef = React.useRef(null)

  React.useEffect(() => {
    if (!containerRef.current) return

    // After a short delay, extract the canvas from the rendered page
    const timer = setTimeout(() => {
      const canvas = document.createElement('canvas')
      const ctx = canvas.getContext('2d')
      
      if (!ctx) return

      // Get the rendered page
      const pageElement = containerRef.current.querySelector('.react-pdf__Page')
      const pageCanvas = pageElement?.querySelector('canvas')

      if (pageCanvas) {
        // Set canvas size
        const thumbWidth = 300
        const thumbHeight = pageSize?.height && pageSize?.width 
          ? (thumbWidth * pageSize.height) / pageSize.width 
          : thumbWidth

        canvas.width = thumbWidth
        canvas.height = thumbHeight

        // Draw full page
        ctx.drawImage(pageCanvas, 0, 0, canvas.width, canvas.height)
      } else {
        // Fallback: create white canvas
        canvas.width = 300
        canvas.height = 300
        const c = canvas.getContext('2d')
        c.fillStyle = 'white'
        c.fillRect(0, 0, canvas.width, canvas.height)
      }

      onCanvasReady(canvas)
    }, 100)

    return () => clearTimeout(timer)
  }, [pageSize, onCanvasReady])

  return (
    <div ref={containerRef} style={{ width: '300px' }}>
      <Document file={file}>
        <Page
          pageNumber={pageNum}
          width={300}
          renderTextLayer={false}
          renderAnnotationLayer={false}
        />
      </Document>
    </div>
  )
}

export default QRAnalyzer

