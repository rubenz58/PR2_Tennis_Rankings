import { useAuth } from "../../../contexts/AuthContext";

import './Dashboard.css';

export const Dashboard = () => {
    const { user, logout, loading, oAuthLoading } = useAuth();
    const isLoading = loading || oAuthLoading;

    // console.log("Dashboard/loading: ", isLoading);

    const handleUpdateProfile = () => {
    // Future functionality
    alert('Update profile feature coming soon!');
  };

  const handleViewSettings = () => {
    // Future functionality  
    alert('Settings feature coming soon!');
  };

  return (
    <div className={`dashboard-container ${isLoading ? 'dashboard-container-loading' : ''}`}>
      {/* Header with title and logout */}
      <div className="dashboard-header">
        <h1 className="dashboard-title">Dashboard</h1>
        <button onClick={logout} className="dashboard-logout-btn">
          Logout
        </button>
      </div>

      {/* Welcome message */}
      <div className="dashboard-welcome">
        <h2 className="dashboard-welcome-title">
          Welcome back, {user?.name}!
        </h2>
        <p className="dashboard-welcome-subtitle">
          Here's what's happening with your account
        </p>
      </div>

      {/* User information */}
      <div className="dashboard-user-info">
        <h3 className="dashboard-user-info-title">Account Information</h3>
        <div className="dashboard-user-details">
          <div className="dashboard-user-detail">
            <span className="dashboard-user-detail-label">Full Name</span>
            <span className="dashboard-user-detail-value">{user?.name}</span>
          </div>
          <div className="dashboard-user-detail">
            <span className="dashboard-user-detail-label">Email Address</span>
            <span className="dashboard-user-detail-value">{user?.email}</span>
          </div>
          <div className="dashboard-user-detail">
            <span className="dashboard-user-detail-label">Member Since</span>
            <span className="dashboard-user-detail-value">
              {user?.created_at ? new Date(user.created_at).toLocaleDateString() : 'N/A'}
            </span>
          </div>
          <div className="dashboard-user-detail">
            <span className="dashboard-user-detail-label">Account Status</span>
            <span className="dashboard-user-detail-value">Active</span>
          </div>
        </div>
      </div>

      {/* Stats cards */}
      <div className="dashboard-stats">
        <div className="dashboard-stat-card">
          <div className="dashboard-stat-number">1</div>
          <div className="dashboard-stat-label">Active Sessions</div>
        </div>
        <div className="dashboard-stat-card">
          <div className="dashboard-stat-number">0</div>
          <div className="dashboard-stat-label">Projects</div>
        </div>
        <div className="dashboard-stat-card">
          <div className="dashboard-stat-number">24/7</div>
          <div className="dashboard-stat-label">Support</div>
        </div>
      </div>

      {/* Action buttons */}
      <div className="dashboard-actions">
        <button 
          onClick={handleUpdateProfile}
          className="dashboard-action-btn primary"
        >
          Update Profile
        </button>
        <button 
          onClick={handleViewSettings}
          className="dashboard-action-btn"
        >
          Settings
        </button>
        <button 
          onClick={() => alert('Help center coming soon!')}
          className="dashboard-action-btn"
        >
          Help Center
        </button>
      </div>

      {/* Recent activity */}
      <div className="dashboard-activity">
        <h3 className="dashboard-activity-title">Recent Activity</h3>
        <div className="dashboard-activity-item">
          <div className="dashboard-activity-icon"></div>
          <span className="dashboard-activity-text">Successfully logged in</span>
          <span className="dashboard-activity-time">Just now</span>
        </div>
        <div className="dashboard-activity-item">
          <div className="dashboard-activity-icon"></div>
          <span className="dashboard-activity-text">Account created</span>
          <span className="dashboard-activity-time">
            {user?.created_at ? new Date(user.created_at).toLocaleDateString() : 'Recently'}
          </span>
        </div>
      </div>
    </div>
  );
}