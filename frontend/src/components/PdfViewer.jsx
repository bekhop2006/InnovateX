import React, { useEffect, useMemo, useRef, useState } from 'react'
import { Document, Page, pdfjs } from 'react-pdf'
import 'react-pdf/dist/esm/Page/AnnotationLayer.css'
import 'react-pdf/dist/esm/Page/TextLayer.css'

pdfjs.GlobalWorkerOptions.workerSrc = `https://unpkg.com/pdfjs-dist@${pdfjs.version}/build/pdf.worker.min.js`

const categoryColor = (c) => {
  if (c === 'qr') return 'blue'
  if (c === 'signature') return 'green'
  return 'orange'
}

const PdfViewer = ({ file, pages, onClose }) => {
  const containerRef = useRef(null)
  const [containerWidth, setContainerWidth] = useState(0)
  const [renderedHeightState] = useState(0)
  const [pageIndex, setPageIndex] = useState(0)
  const [visible, setVisible] = useState({ qr: true, signature: true, stamp: true })
  const [thumbnailDimensions, setThumbnailDimensions] = useState({})
  const [expandedPages, setExpandedPages] = useState({})
  const [selectedItem, setSelectedItem] = useState(null)
  const [showSpotlight, setShowSpotlight] = useState(false)

  const onThumbnailRenderSuccess = (pageNum, page) => {
    const viewport = page.getViewport({ scale: 1 })
    setThumbnailDimensions(prev => ({
      ...prev,
      [pageNum]: { width: viewport.width, height: viewport.height }
    }))
  }

  useEffect(() => {
    const ro = new ResizeObserver((entries) => {
      const rect = entries[0].contentRect
      setContainerWidth(Math.floor(rect.width))
    })
    if (containerRef.current) ro.observe(containerRef.current)
    return () => ro.disconnect()
  }, [])

  const current = pages[pageIndex]
  const renderedHeight = useMemo(() => {
    if (!current || !containerWidth || !current.pageSize?.width || !current.pageSize?.height) return renderedHeightState
    return (containerWidth * current.pageSize.height) / current.pageSize.width
  }, [containerWidth, current, renderedHeightState])

  const scaleX = useMemo(() => {
    if (!current) return 1
    return containerWidth && current.pageSize?.width ? containerWidth / current.pageSize.width : 1
  }, [containerWidth, current])
  const scaleY = useMemo(() => {
    if (!current) return 1
    return renderedHeight && current.pageSize?.height ? renderedHeight / current.pageSize.height : 1
  }, [renderedHeight, current])

  const pageOptions = pages.map((p, i) => ({ label: `Page ${i + 1}`, value: i }))

  return (
    <div className="pdf-viewer">
      <div className="pdf-viewer__toolbar">
        <div className="pdf-viewer__nav">
          <button className="btn secondary" onClick={() => setPageIndex(Math.max(pageIndex - 1, 0))} disabled={pageIndex === 0}>Prev</button>
          <select className="pdf-viewer__select" value={pageIndex} onChange={(e) => setPageIndex(parseInt(e.target.value, 10))}>
            {pageOptions.map((o) => (
              <option key={o.value} value={o.value}>{o.label}</option>
            ))}
          </select>
          <button className="btn secondary" onClick={() => setPageIndex(Math.min(pageIndex + 1, pages.length - 1))} disabled={pageIndex === pages.length - 1}>Next</button>
        </div>
        <div className="pdf-viewer__toggles">
          <label><input type="checkbox" checked={visible.qr} onChange={(e) => setVisible((v) => ({ ...v, qr: e.target.checked }))} /> QR</label>
          <label><input type="checkbox" checked={visible.signature} onChange={(e) => setVisible((v) => ({ ...v, signature: e.target.checked }))} /> Signature</label>
          <label><input type="checkbox" checked={visible.stamp} onChange={(e) => setVisible((v) => ({ ...v, stamp: e.target.checked }))} /> Stamp</label>
        </div>
        <button className="btn" onClick={onClose}>Close</button>
      </div>

      <div className="pdf-viewer__content">
        <div className="pdf-viewer__sidebar">
          <div className="pdf-viewer__sidebar-title">Detected Items</div>
          {pages.filter(page => page.items.length > 0).map((page, idx) => {
            const originalIdx = pages.indexOf(page)
            const thumbWidth = 140
            const pageSize = page.pageSize
            const items = page.items
            const isExpanded = expandedPages[originalIdx]
            const displayLimit = isExpanded ? items.length : 4
            const hasMore = items.length > 4
            
            return (
              <div
                key={originalIdx}
                className={`pdf-viewer__thumbnail ${originalIdx === pageIndex ? 'is-active' : ''}`}
              >
                <div className="pdf-viewer__thumb-cutouts">
                  {items.slice(0, displayLimit).map((item, itemIdx) => {
                    const thumbHeight = pageSize?.height && pageSize?.width 
                      ? (thumbWidth * pageSize.height) / pageSize.width 
                      : thumbWidth
                    
                    const scaleX = thumbWidth / (pageSize?.width || 1)
                    const scaleY = thumbHeight / (pageSize?.height || 1)
                    
                    const clipX = item.bbox.x * scaleX
                    const clipY = item.bbox.y * scaleY
                    const clipWidth = item.bbox.width * scaleX
                    const clipHeight = item.bbox.height * scaleY
                    
                    const padding = 10
                    const cutoutWidth = Math.min(clipWidth + padding * 2, thumbWidth)
                    const cutoutHeight = Math.min(clipHeight + padding * 2, thumbHeight)
                    
                    const isSelected = selectedItem?.pageIdx === originalIdx && selectedItem?.itemId === item.id
                    
                    return (
                      <div
                        key={itemIdx}
                        className={`pdf-viewer__cutout overlay-${categoryColor(item.category)} ${isSelected ? 'is-selected' : ''}`}
                        style={{
                          width: cutoutWidth,
                          height: cutoutHeight,
                          position: 'relative',
                          overflow: 'hidden'
                        }}
                        onClick={() => {
                          setPageIndex(originalIdx)
                          setSelectedItem({ pageIdx: originalIdx, itemId: item.id })
                          setShowSpotlight(true)
                          setTimeout(() => setShowSpotlight(false), 2000)
                        }}
                      >
                        <div
                          style={{
                            position: 'absolute',
                            left: -(clipX - padding),
                            top: -(clipY - padding),
                            width: thumbWidth,
                            height: thumbHeight
                          }}
                        >
                          <Document file={file}>
                            <Page 
                              pageNumber={originalIdx + 1} 
                              width={thumbWidth} 
                              renderTextLayer={false} 
                              renderAnnotationLayer={false}
                              onRenderSuccess={(page) => onThumbnailRenderSuccess(originalIdx + 1, page)}
                            />
                          </Document>
                        </div>
                      </div>
                    )
                  })}
                </div>
                <div className="pdf-viewer__thumb-label">
                  Page {originalIdx + 1}
                  {items.length > 0 && <span className="thumb-count"> • {items.length}</span>}
                </div>
                {hasMore && (
                  <button 
                    className="pdf-viewer__expand-btn"
                    onClick={(e) => {
                      e.stopPropagation()
                      setExpandedPages(prev => ({ ...prev, [originalIdx]: !prev[originalIdx] }))
                    }}
                  >
                    {isExpanded ? '− Show Less' : `+ ${items.length - 4} More`}
                  </button>
                )}
              </div>
            )
          })}
        </div>

        <div className="pdf-viewer__main-content">
          <div className="pdf-viewer__stage" ref={containerRef}>
        <div className="pdf-viewer__page">
          <Document file={file} loading={<div className="pdf-viewer__loading">Loading PDF…</div>}>
            <Page pageNumber={pageIndex + 1} width={containerWidth ? containerWidth : undefined} renderTextLayer={false} />
          </Document>
          <div className="pdf-viewer__overlay">
            {showSpotlight && selectedItem?.pageIdx === pageIndex && (
              <>
                <div className="pdf-viewer__spotlight-bg" />
                {current.items.filter((it) => selectedItem?.itemId === it.id).map((it) => {
                  const left = it.bbox.x * scaleX
                  const top = it.bbox.y * scaleY
                  const width = it.bbox.width * scaleX
                  const height = it.bbox.height * scaleY
                  
                  return (
                    <div
                      key={`spotlight-${it.id}`}
                      className="pdf-viewer__spotlight-cutout"
                      style={{
                        left: `${left}px`,
                        top: `${top}px`,
                        width: `${width}px`,
                        height: `${height}px`
                      }}
                    />
                  )
                })}
              </>
            )}
            {current.items.filter((it) => visible[it.category] !== false).map((it) => {
              const left = it.bbox.x * scaleX
              const top = it.bbox.y * scaleY
              const width = it.bbox.width * scaleX
              const height = it.bbox.height * scaleY
              const isSelected = selectedItem?.pageIdx === pageIndex && selectedItem?.itemId === it.id
              return (
                <div
                  key={it.id}
                  className={`overlay-box overlay-${categoryColor(it.category)} ${isSelected ? 'is-selected' : ''}`}
                  style={{ left, top, width, height }}
                  title={`${it.category} • ${it.id}${it.confidence ? ` • ${(it.confidence * 100).toFixed(1)}%` : ''}`}
                />
              )
            })}
          </div>
        </div>
        </div>
        
        <div className="pdf-viewer__page-nav">
          <div className="pdf-viewer__page-nav-title">All Pages</div>
          {pages.map((page, idx) => (
            <button
              key={idx}
              className={`pdf-viewer__page-btn ${idx === pageIndex ? 'is-active' : ''}`}
              onClick={() => {
                setPageIndex(idx)
                setSelectedItem(null)
              }}
            >
              {idx + 1}
            </button>
          ))}
        </div>
      </div>
      </div>
    </div>
  )
}

export default PdfViewer