import React, { useState, useEffect } from 'react';
import { useAuth } from '../../../contexts/AuthContext';

import { Navigate } from 'react-router-dom';
import './Admin.css';

const Admin = () => {
    const { 
        user, 
        isAdmin, 
        loading, 
        adminLoading,
        getLogsOverview,
        getSpecificLogs,
        tailLogs,
        getSchedulerStatus,
        triggerManualUpdate
    } = useAuth();

    // State for the dashboard
    const [activeTab, setActiveTab] = useState('overview');
    const [logsOverview, setLogsOverview] = useState(null);
    const [currentLogData, setCurrentLogData] = useState(null);
    const [schedulerStatus, setSchedulerStatus] = useState(null);
    const [error, setError] = useState('');
    const [success, setSuccess] = useState('');
    const [refreshing, setRefreshing] = useState(false);

    // Load initial data - useEffect must come before any early returns
    useEffect(() => {
        loadOverviewData();
    }, []);

    // useEffect(() => {
    //     // Only load data if user is admin and not loading
    //     if (!loading && user && isAdmin) {
    //         loadOverviewData();
    //     }
    // }, [loading, user, isAdmin]);

    // If still loading auth, show loading
    // if (loading) {
    //     return (
    //         <div className="loading-container">
    //             <div className="loading-text">Loading...</div>
    //         </div>
    //     );
    // }

    // If not logged in, redirect to login
    // if (!user) {
    //     return <Navigate to="/login" replace />;
    // }

    // If not admin, show unauthorized
    // if (!isAdmin) {
    //     return (
    //         <div className="unauthorized-container">
    //             <div className="unauthorized-content">
    //                 <h1 className="unauthorized-title">Access Denied</h1>
    //                 <p className="unauthorized-message">You don't have admin privileges to access this page.</p>
    //             </div>
    //         </div>
    //     );
    // }

    const loadOverviewData = async () => {
        try {
            setError('');
            const [overview, scheduler] = await Promise.all([
                getLogsOverview(),
                getSchedulerStatus()
            ]);
            setLogsOverview(overview);
            setSchedulerStatus(scheduler);
        } catch (err) {
            setError(err.message);
        }
    };

    const handleLoadSpecificLogs = async (logType, lines = 200) => {
        try {
            setError('');
            const logData = await getSpecificLogs(logType, lines);
            setCurrentLogData(logData);
            setActiveTab('logs');
        } catch (err) {
            setError(err.message);
        }
    };

    const handleRefreshLogs = async () => {
        if (!currentLogData?.log_type) return;
        
        try {
            setRefreshing(true);
            setError('');
            const refreshedData = await getSpecificLogs(currentLogData.log_type, 200);
            setCurrentLogData(refreshedData);
        } catch (err) {
            setError(err.message);
        } finally {
            setRefreshing(false);
        }
    };

    const handleManualUpdate = async () => {
        try {
            setError('');
            setSuccess('');
            await triggerManualUpdate();
            setSuccess('Manual update triggered successfully!');
            // Refresh scheduler status after a brief delay
            setTimeout(loadOverviewData, 1000);
        } catch (err) {
            setError(err.message);
        }
    };

    const formatTimestamp = (timestamp) => {
        if (!timestamp) return 'N/A';
        return new Date(timestamp).toLocaleString();
    };

    const formatFileSize = (sizeKb) => {
        if (sizeKb < 1) return `${Math.round(sizeKb * 1024)} bytes`;
        if (sizeKb < 1024) return `${sizeKb} KB`;
        return `${(sizeKb / 1024).toFixed(1)} MB`;
    };

    return (
        <div className="admin-container">
            {/* Header */}
            <header className="admin-header">
                <div className="header-content">
                    <div className="header-info">
                        <h1 className="header-title">Admin Dashboard</h1>
                        <p className="header-subtitle">Welcome, {user.name}</p>
                    </div>
                    <div className="tab-navigation">
                        <button
                            onClick={() => setActiveTab('overview')}
                            className={`tab-button ${activeTab === 'overview' ? 'active' : ''}`}
                        >
                            Overview
                        </button>
                        <button
                            onClick={() => setActiveTab('scheduler')}
                            className={`tab-button ${activeTab === 'scheduler' ? 'active' : ''}`}
                        >
                            Scheduler
                        </button>
                    </div>
                </div>
            </header>

            {/* Main Content */}
            <main className="admin-main">
                {/* Error/Success Messages */}
                {error && (
                    <div className="message error-message">
                        {error}
                    </div>
                )}
                {success && (
                    <div className="message success-message">
                        {success}
                    </div>
                )}

                {/* Loading Spinner */}
                {adminLoading && (
                    <div className="loading-spinner-container">
                        <div className="loading-spinner"></div>
                    </div>
                )}

                {/* Overview Tab */}
                {activeTab === 'overview' && logsOverview && (
                    <div className="tab-content">
                        <div className="content-card">
                            <h2 className="card-title">Logs Overview</h2>
                            <div className="logs-grid">
                                {Object.entries(logsOverview.logs).map(([logType, info]) => (
                                    <div key={logType} className="log-card">
                                        <div className="log-card-header">
                                            <h3 className="log-card-title">{logType} Logs</h3>
                                            <span className={`status-badge ${info.exists ? 'active' : 'inactive'}`}>
                                                {info.exists ? 'Active' : 'No file'}
                                            </span>
                                        </div>
                                        <p className="log-card-description">{info.description}</p>
                                        {info.exists && (
                                            <div className="log-card-stats">
                                                <div className="stat">
                                                    <span className="stat-label">Lines:</span>
                                                    <span className="stat-value">{info.lines.toLocaleString()}</span>
                                                </div>
                                                <div className="stat">
                                                    <span className="stat-label">Size:</span>
                                                    <span className="stat-value">{formatFileSize(info.size_kb)}</span>
                                                </div>
                                                <div className="stat">
                                                    <span className="stat-label">Updated:</span>
                                                    <span className="stat-value">{formatTimestamp(info.last_modified)}</span>
                                                </div>
                                            </div>
                                        )}
                                        {info.exists && (
                                            <button
                                                onClick={() => handleLoadSpecificLogs(logType)}
                                                className="log-view-button"
                                            >
                                                View Logs
                                            </button>
                                        )}
                                    </div>
                                ))}
                            </div>
                            {logsOverview.summary && (
                                <div className="summary-card">
                                    <h4 className="summary-title">Summary</h4>
                                    <div className="summary-stats">
                                        <div className="summary-stat">
                                            <span className="stat-label">Total Files:</span>
                                            <span className="stat-value">{logsOverview.summary.total_files}</span>
                                        </div>
                                        <div className="summary-stat">
                                            <span className="stat-label">Total Size:</span>
                                            <span className="stat-value">{formatFileSize(logsOverview.summary.total_size_kb)}</span>
                                        </div>
                                    </div>
                                </div>
                            )}
                        </div>
                    </div>
                )}

                {/* Scheduler Tab */}
                {activeTab === 'scheduler' && (
                    <div className="tab-content">
                        <div className="content-card">
                            <div className="card-header">
                                <h2 className="card-title">Scheduler Status</h2>
                                <button
                                    onClick={handleManualUpdate}
                                    disabled={adminLoading}
                                    className="manual-update-button"
                                >
                                    {adminLoading ? 'Triggering...' : 'Trigger Manual Update'}
                                </button>
                            </div>
                            {schedulerStatus && (
                                <div className="scheduler-info">
                                    <div className="scheduler-stat">
                                        <span className="stat-label">Status:</span>
                                        <span className={`status-badge ${schedulerStatus.status === 'scheduler_running' ? 'active' : 'warning'}`}>
                                            {schedulerStatus.status.replace('_', ' ').toUpperCase()}
                                        </span>
                                    </div>
                                    <div className="scheduler-stat">
                                        <span className="stat-label">Active Jobs:</span>
                                        <span className="stat-value">{schedulerStatus.job_count}</span>
                                    </div>
                                    {schedulerStatus.jobs?.length > 0 && (
                                        <div className="jobs-section">
                                            <span className="stat-label">Jobs:</span>
                                            <div className="jobs-list">
                                                {schedulerStatus.jobs.map((job, index) => (
                                                    <div key={index} className="job-item">
                                                        {job}
                                                    </div>
                                                ))}
                                            </div>
                                        </div>
                                    )}
                                    {schedulerStatus.error && (
                                        <div className="error-section">
                                            <span className="stat-label error-label">Error:</span>
                                            <div className="error-content">{schedulerStatus.error}</div>
                                        </div>
                                    )}
                                </div>
                            )}
                        </div>
                    </div>
                )}

                {/* Logs View Tab */}
                {activeTab === 'logs' && currentLogData && (
                    <div className="tab-content">
                        <div className="content-card">
                            <div className="card-header">
                                <h2 className="card-title">{currentLogData.title}</h2>
                                <div className="log-actions">
                                    <button
                                        onClick={handleRefreshLogs}
                                        disabled={refreshing}
                                        className="refresh-button"
                                    >
                                        {refreshing ? 'Refreshing...' : 'Refresh'}
                                    </button>
                                    <button
                                        onClick={() => setActiveTab('overview')}
                                        className="back-button"
                                    >
                                        Back to Overview
                                    </button>
                                </div>
                            </div>
                            
                            {currentLogData.metadata && (
                                <div className="log-metadata">
                                    <div className="metadata-grid">
                                        <div className="metadata-item">
                                            <span className="metadata-label">Total Lines:</span>
                                            <span className="metadata-value">{currentLogData.metadata.total_lines.toLocaleString()}</span>
                                        </div>
                                        <div className="metadata-item">
                                            <span className="metadata-label">Showing:</span>
                                            <span className="metadata-value">{currentLogData.metadata.shown_lines} lines</span>
                                        </div>
                                        <div className="metadata-item">
                                            <span className="metadata-label">Size:</span>
                                            <span className="metadata-value">{formatFileSize(currentLogData.metadata.file_size_kb)}</span>
                                        </div>
                                        <div className="metadata-item">
                                            <span className="metadata-label">Updated:</span>
                                            <span className="metadata-value">{formatTimestamp(currentLogData.metadata.last_modified)}</span>
                                        </div>
                                    </div>
                                </div>
                            )}

                            {currentLogData.success && currentLogData.content ? (
                                <div className="log-content">
                                    <pre className="log-text">
                                        {currentLogData.content.join('')}
                                    </pre>
                                </div>
                            ) : (
                                <div className="log-error">
                                    {currentLogData.error || 'No log content available'}
                                </div>
                            )}
                        </div>
                    </div>
                )}
            </main>
        </div>
    );
};

export default Admin;