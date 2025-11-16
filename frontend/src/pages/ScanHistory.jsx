/**
 * Scan History Page
 */
import { useState, useEffect } from 'react';
import api from '../utils/api';
import './ScanHistory.scss';

const ScanHistory = () => {
  const [scans, setScans] = useState([]);
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [selectedScan, setSelectedScan] = useState(null);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    setLoading(true);
    try {
      const [scansData, statsData] = await Promise.all([
        api.getScans(),
        api.getScanStats()
      ]);
      setScans(scansData);
      setStats(statsData);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (scanId) => {
    if (!confirm('Are you sure you want to delete this scan?')) {
      return;
    }

    try {
      await api.deleteScan(scanId);
      setScans(scans.filter(s => s.id !== scanId));
    } catch (err) {
      alert('Failed to delete scan: ' + err.message);
    }
  };

  const handleViewDetails = async (scan) => {
    try {
      const details = await api.getScanDetail(scan.id);
      setSelectedScan(details);
    } catch (err) {
      alert('Failed to load details: ' + err.message);
    }
  };

  const handleDownload = async (scanId) => {
    try {
      const { blob, filename } = await api.downloadScanPdf(scanId);
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = filename || `scan-${scanId}.pdf`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
    } catch (err) {
      alert('Failed to download: ' + err.message);
    }
  };

  if (loading) {
    return <div className="loading">Loading scan history...</div>;
  }

  if (error) {
    return <div className="error">Error: {error}</div>;
  }

  if (selectedScan) {
    return (
      <div className="scan-detail">
        <button onClick={() => setSelectedScan(null)} className="back-btn">
          ← Back to History
        </button>
        
        <h2>{selectedScan.document_name}</h2>
        
        <div className="scan-info">
          <div className="info-item">
            <strong>Scanned:</strong> {new Date(selectedScan.scan_date).toLocaleString()}
          </div>
          <div className="info-item">
            <strong>Expires:</strong> {new Date(selectedScan.expires_at).toLocaleDateString()}
          </div>
          <div className="info-item">
            <strong>Pages:</strong> {selectedScan.total_pages}
          </div>
          <div className="info-item">
            <strong>Processing Time:</strong> {selectedScan.processing_time?.toFixed(2)}s
          </div>
        </div>

        <div className="detections-summary">
          <div className="detection-card">
            <span className="count">{selectedScan.qr_count}</span>
            <span className="label">QR Codes</span>
          </div>
          <div className="detection-card">
            <span className="count">{selectedScan.signature_count}</span>
            <span className="label">Signatures</span>
          </div>
          <div className="detection-card">
            <span className="count">{selectedScan.stamp_count}</span>
            <span className="label">Stamps</span>
          </div>
        </div>

        <button onClick={() => handleDownload(selectedScan.id)} className="download-btn">
          Download PDF
        </button>
      </div>
    );
  }

  return (
    <div className="scan-history">
      <h2>Scan History</h2>

      {stats && (
        <div className="stats-cards">
          <div className="stat-card">
            <div className="stat-value">{stats.total_scans}</div>
            <div className="stat-label">Total Scans</div>
          </div>
          <div className="stat-card">
            <div className="stat-value">{stats.total_pages}</div>
            <div className="stat-label">Pages Scanned</div>
          </div>
          <div className="stat-card">
            <div className="stat-value">{stats.total_qr}</div>
            <div className="stat-label">QR Codes</div>
          </div>
          <div className="stat-card">
            <div className="stat-value">{stats.total_signatures}</div>
            <div className="stat-label">Signatures</div>
          </div>
          <div className="stat-card">
            <div className="stat-value">{stats.total_stamps}</div>
            <div className="stat-label">Stamps</div>
          </div>
        </div>
      )}

      {scans.length === 0 ? (
        <div className="empty-state">
          <p>No scans yet. Start by scanning a document!</p>
        </div>
      ) : (
        <div className="scans-list">
          {scans.map(scan => (
            <div key={scan.id} className="scan-card">
              <div className="scan-header">
                <h3>{scan.document_name}</h3>
                <span className="scan-date">
                  {new Date(scan.scan_date).toLocaleDateString()}
                </span>
              </div>
              
              <div className="scan-stats">
                <span>📄 {scan.total_pages} pages</span>
                <span>📱 {scan.qr_count} QR</span>
                <span>✍️ {scan.signature_count} sigs</span>
                <span>🏷️ {scan.stamp_count} stamps</span>
              </div>

              <div className="scan-actions">
                <button onClick={() => handleViewDetails(scan)} className="btn-view">
                  View Details
                </button>
                <button onClick={() => handleDownload(scan.id)} className="btn-download">
                  Download
                </button>
                <button onClick={() => handleDelete(scan.id)} className="btn-delete">
                  Delete
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default ScanHistory;

