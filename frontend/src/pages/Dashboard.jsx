/**
 * Dashboard - Main authenticated page
 */
import { Routes, Route, Link, Navigate, useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import ScanHistory from './ScanHistory';
import AdminPanel from './AdminPanel';
import './Dashboard.scss';

// Import your existing App component for scanning
// For now, we'll create a placeholder
const ScanPage = () => {
  return (
    <div className="scan-page">
      <h2>Document Scanner</h2>
      <p>Your existing document scanner component goes here.</p>
      <p>This should be your current App.jsx content.</p>
    </div>
  );
};

const Profile = () => {
  const { user } = useAuth();
  
  return (
    <div className="profile-page">
      <h2>Profile</h2>
      <div className="profile-info">
        <p><strong>Name:</strong> {user.name} {user.surname || ''}</p>
        <p><strong>Email:</strong> {user.email}</p>
        <p><strong>Role:</strong> {user.role}</p>
        <p><strong>Member since:</strong> {new Date(user.created_at).toLocaleDateString()}</p>
      </div>
    </div>
  );
};

const Dashboard = () => {
  const { user, logout, isAdmin } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/auth');
  };

  return (
    <div className="dashboard">
      <aside className="sidebar">
        <div className="sidebar-header">
          <h1>InnovateX</h1>
          <p>{user.name}</p>
        </div>

        <nav className="sidebar-nav">
          <Link to="/dashboard/scan" className="nav-link">
            📄 New Scan
          </Link>
          <Link to="/dashboard/history" className="nav-link">
            📋 Scan History
          </Link>
          <Link to="/dashboard/profile" className="nav-link">
            👤 Profile
          </Link>
          {isAdmin() && (
            <Link to="/dashboard/admin" className="nav-link admin-link">
              👑 Admin Panel
            </Link>
          )}
        </nav>

        <button onClick={handleLogout} className="logout-btn">
          Logout
        </button>
      </aside>

      <main className="main-content">
        <Routes>
          <Route path="/" element={<Navigate to="/dashboard/scan" replace />} />
          <Route path="/scan" element={<ScanPage />} />
          <Route path="/history" element={<ScanHistory />} />
          <Route path="/profile" element={<Profile />} />
          {isAdmin() && (
            <Route path="/admin" element={<AdminPanel />} />
          )}
        </Routes>
      </main>
    </div>
  );
};

export default Dashboard;

