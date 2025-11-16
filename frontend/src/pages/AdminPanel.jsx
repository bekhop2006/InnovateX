/**
 * Admin Panel - User Management
 */
import { useState, useEffect } from 'react';
import api from '../utils/api';
import './AdminPanel.scss';

const AdminPanel = () => {
  const [users, setUsers] = useState([]);
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [selectedUser, setSelectedUser] = useState(null);
  const [userScans, setUserScans] = useState([]);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    setLoading(true);
    try {
      const [usersData, statsData] = await Promise.all([
        api.getUsers(),
        api.getSystemStats()
      ]);
      setUsers(usersData);
      setStats(statsData);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleViewUserScans = async (user) => {
    try {
      setSelectedUser(user);
      const scans = await api.getUserScans(user.id);
      setUserScans(scans);
    } catch (err) {
      alert('Failed to load user scans: ' + err.message);
    }
  };

  const handleDeleteUser = async (userId) => {
    if (!confirm('Are you sure you want to delete this user?')) {
      return;
    }

    try {
      await api.deleteUser(userId);
      setUsers(users.filter(u => u.id !== userId));
    } catch (err) {
      alert('Failed to delete user: ' + err.message);
    }
  };

  if (loading) {
    return <div className="loading">Loading admin panel...</div>;
  }

  if (error) {
    return <div className="error">Error: {error}</div>;
  }

  if (selectedUser) {
    return (
      <div className="user-scans-view">
        <button onClick={() => setSelectedUser(null)} className="back-btn">
          ← Back to Users
        </button>

        <h2>{selectedUser.name}'s Scans</h2>
        <p className="user-email">{selectedUser.email}</p>

        {userScans.length === 0 ? (
          <div className="empty-state">
            <p>This user has no scans yet.</p>
          </div>
        ) : (
          <div className="scans-list">
            {userScans.map(scan => (
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
              </div>
            ))}
          </div>
        )}
      </div>
    );
  }

  return (
    <div className="admin-panel">
      <h2>Admin Panel</h2>

      {stats && (
        <div className="admin-stats">
          <div className="stat-group">
            <h3>Users</h3>
            <div className="stat-cards">
              <div className="stat-card">
                <div className="stat-value">{stats.total_users}</div>
                <div className="stat-label">Total Users</div>
              </div>
              <div className="stat-card">
                <div className="stat-value">{stats.total_admin}</div>
                <div className="stat-label">Admins</div>
              </div>
              <div className="stat-card">
                <div className="stat-value">{stats.total_regular_users}</div>
                <div className="stat-label">Regular Users</div>
              </div>
            </div>
          </div>

          <div className="stat-group">
            <h3>System</h3>
            <div className="stat-cards">
              <div className="stat-card">
                <div className="stat-value">{stats.total_scans}</div>
                <div className="stat-label">Total Scans</div>
              </div>
              <div className="stat-card">
                <div className="stat-value">{stats.total_pages_scanned}</div>
                <div className="stat-label">Pages Scanned</div>
              </div>
              <div className="stat-card">
                <div className="stat-value">{stats.storage_used_mb} MB</div>
                <div className="stat-label">Storage Used</div>
              </div>
            </div>
          </div>

          <div className="stat-group">
            <h3>Detections</h3>
            <div className="stat-cards">
              <div className="stat-card">
                <div className="stat-value">{stats.total_qr_detected}</div>
                <div className="stat-label">QR Codes</div>
              </div>
              <div className="stat-card">
                <div className="stat-value">{stats.total_signatures_detected}</div>
                <div className="stat-label">Signatures</div>
              </div>
              <div className="stat-card">
                <div className="stat-value">{stats.total_stamps_detected}</div>
                <div className="stat-label">Stamps</div>
              </div>
            </div>
          </div>
        </div>
      )}

      <h3>User Management</h3>
      <div className="users-table">
        <table>
          <thead>
            <tr>
              <th>Name</th>
              <th>Email</th>
              <th>Role</th>
              <th>Joined</th>
              <th>Scans</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {users.map(user => (
              <tr key={user.id}>
                <td>{user.name}</td>
                <td>{user.email}</td>
                <td>
                  <span className={`role-badge ${user.role}`}>
                    {user.role}
                  </span>
                </td>
                <td>{new Date(user.created_at).toLocaleDateString()}</td>
                <td>{user.total_scans}</td>
                <td className="actions">
                  <button
                    onClick={() => handleViewUserScans(user)}
                    className="btn-view"
                  >
                    View Scans
                  </button>
                  {user.role !== 'admin' && (
                    <button
                      onClick={() => handleDeleteUser(user.id)}
                      className="btn-delete"
                    >
                      Delete
                    </button>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default AdminPanel;

