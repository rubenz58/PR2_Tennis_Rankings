import React, { useState, useEffect } from 'react';
import { Navigate } from 'react-router-dom';

import { useAuth } from '../../../contexts/AuthContext';

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
        // Only load data if user is admin and not loading
        if (!loading && user && isAdmin) {
            loadOverviewData();
        }
    }, [loading, user, isAdmin]);

    // If still loading auth, show loading
    if (loading) {
        return (
            <div className="min-h-screen flex items-center justify-center">
                <div className="text-lg">Loading...</div>
            </div>
        );
    }

    // If not logged in, redirect to login
    if (!user) {
        return <Navigate to="/login" replace />;
    }

    // If not admin, show unauthorized
    if (!isAdmin) {
        return (
            <div className="min-h-screen flex items-center justify-center bg-gray-50">
                <div className="text-center">
                    <h1 className="text-3xl font-bold text-gray-900 mb-4">Access Denied</h1>
                    <p className="text-gray-600">You don't have admin privileges to access this page.</p>
                </div>
            </div>
        );
    }

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

    const handleLoadSpecificLogs = async (logType, lines = 50) => {
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
            const refreshedData = await getSpecificLogs(currentLogData.log_type, 50);
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
        <div className="min-h-screen bg-gray-50">
            {/* Header */}
            <header className="bg-white shadow">
                <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                    <div className="flex justify-between items-center py-6">
                        <div>
                            <h1 className="text-3xl font-bold text-gray-900">Admin Dashboard</h1>
                            <p className="text-gray-600">Welcome, {user.name}</p>
                        </div>
                        <div className="flex space-x-4">
                            <button
                                onClick={() => setActiveTab('overview')}
                                className={`px-4 py-2 rounded-md ${
                                    activeTab === 'overview'
                                        ? 'bg-blue-600 text-white'
                                        : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
                                }`}
                            >
                                Overview
                            </button>
                            <button
                                onClick={() => setActiveTab('scheduler')}
                                className={`px-4 py-2 rounded-md ${
                                    activeTab === 'scheduler'
                                        ? 'bg-blue-600 text-white'
                                        : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
                                }`}
                            >
                                Scheduler
                            </button>
                        </div>
                    </div>
                </div>
            </header>

            {/* Main Content */}
            <main className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
                {/* Error/Success Messages */}
                {error && (
                    <div className="mb-4 bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded">
                        {error}
                    </div>
                )}
                {success && (
                    <div className="mb-4 bg-green-100 border border-green-400 text-green-700 px-4 py-3 rounded">
                        {success}
                    </div>
                )}

                {/* Loading Spinner */}
                {adminLoading && (
                    <div className="flex justify-center py-8">
                        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
                    </div>
                )}

                {/* Overview Tab */}
                {activeTab === 'overview' && logsOverview && (
                    <div className="space-y-6">
                        <div className="bg-white shadow rounded-lg p-6">
                            <h2 className="text-xl font-semibold mb-4">Logs Overview</h2>
                            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                                {Object.entries(logsOverview.logs).map(([logType, info]) => (
                                    <div key={logType} className="border rounded-lg p-4">
                                        <div className="flex justify-between items-start mb-2">
                                            <h3 className="font-medium text-gray-900 capitalize">
                                                {logType} Logs
                                            </h3>
                                            <span className={`px-2 py-1 text-xs rounded-full ${
                                                info.exists 
                                                    ? 'bg-green-100 text-green-800' 
                                                    : 'bg-gray-100 text-gray-800'
                                            }`}>
                                                {info.exists ? 'Active' : 'No file'}
                                            </span>
                                        </div>
                                        <p className="text-sm text-gray-600 mb-3">{info.description}</p>
                                        {info.exists && (
                                            <div className="space-y-1 text-sm text-gray-500">
                                                <div>Lines: {info.lines.toLocaleString()}</div>
                                                <div>Size: {formatFileSize(info.size_kb)}</div>
                                                <div>Updated: {formatTimestamp(info.last_modified)}</div>
                                            </div>
                                        )}
                                        {info.exists && (
                                            <button
                                                onClick={() => handleLoadSpecificLogs(logType)}
                                                className="mt-3 w-full bg-blue-600 text-white px-3 py-1 rounded text-sm hover:bg-blue-700"
                                            >
                                                View Logs
                                            </button>
                                        )}
                                    </div>
                                ))}
                            </div>
                            {logsOverview.summary && (
                                <div className="mt-6 bg-gray-50 rounded-lg p-4">
                                    <h4 className="font-medium mb-2">Summary</h4>
                                    <div className="grid grid-cols-2 gap-4 text-sm">
                                        <div>Total Files: {logsOverview.summary.total_files}</div>
                                        <div>Total Size: {formatFileSize(logsOverview.summary.total_size_kb)}</div>
                                    </div>
                                </div>
                            )}
                        </div>
                    </div>
                )}

                {/* Scheduler Tab */}
                {activeTab === 'scheduler' && (
                    <div className="space-y-6">
                        <div className="bg-white shadow rounded-lg p-6">
                            <div className="flex justify-between items-center mb-4">
                                <h2 className="text-xl font-semibold">Scheduler Status</h2>
                                <button
                                    onClick={handleManualUpdate}
                                    disabled={adminLoading}
                                    className="bg-green-600 text-white px-4 py-2 rounded hover:bg-green-700 disabled:opacity-50"
                                >
                                    {adminLoading ? 'Triggering...' : 'Trigger Manual Update'}
                                </button>
                            </div>
                            {schedulerStatus && (
                                <div className="space-y-4">
                                    <div className="flex items-center space-x-2">
                                        <span className="font-medium">Status:</span>
                                        <span className={`px-2 py-1 text-xs rounded-full ${
                                            schedulerStatus.status === 'scheduler_running'
                                                ? 'bg-green-100 text-green-800'
                                                : 'bg-yellow-100 text-yellow-800'
                                        }`}>
                                            {schedulerStatus.status.replace('_', ' ').toUpperCase()}
                                        </span>
                                    </div>
                                    <div>
                                        <span className="font-medium">Active Jobs: </span>
                                        {schedulerStatus.job_count}
                                    </div>
                                    {schedulerStatus.jobs?.length > 0 && (
                                        <div>
                                            <span className="font-medium">Jobs:</span>
                                            <ul className="mt-2 space-y-1">
                                                {schedulerStatus.jobs.map((job, index) => (
                                                    <li key={index} className="text-sm text-gray-600 bg-gray-50 p-2 rounded">
                                                        {job}
                                                    </li>
                                                ))}
                                            </ul>
                                        </div>
                                    )}
                                    {schedulerStatus.error && (
                                        <div className="bg-red-50 p-3 rounded">
                                            <span className="font-medium text-red-800">Error:</span>
                                            <div className="text-red-600">{schedulerStatus.error}</div>
                                        </div>
                                    )}
                                </div>
                            )}
                        </div>
                    </div>
                )}

                {/* Logs View Tab */}
                {activeTab === 'logs' && currentLogData && (
                    <div className="space-y-6">
                        <div className="bg-white shadow rounded-lg p-6">
                            <div className="flex justify-between items-center mb-4">
                                <h2 className="text-xl font-semibold">{currentLogData.title}</h2>
                                <div className="flex space-x-2">
                                    <button
                                        onClick={handleRefreshLogs}
                                        disabled={refreshing}
                                        className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700 disabled:opacity-50"
                                    >
                                        {refreshing ? 'Refreshing...' : 'Refresh'}
                                    </button>
                                    <button
                                        onClick={() => setActiveTab('overview')}
                                        className="bg-gray-500 text-white px-4 py-2 rounded hover:bg-gray-600"
                                    >
                                        Back to Overview
                                    </button>
                                </div>
                            </div>
                            
                            {currentLogData.metadata && (
                                <div className="mb-4 bg-gray-50 rounded-lg p-4">
                                    <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                                        <div>
                                            <span className="font-medium">Total Lines:</span> {currentLogData.metadata.total_lines.toLocaleString()}
                                        </div>
                                        <div>
                                            <span className="font-medium">Showing:</span> {currentLogData.metadata.shown_lines} lines
                                        </div>
                                        <div>
                                            <span className="font-medium">Size:</span> {formatFileSize(currentLogData.metadata.file_size_kb)}
                                        </div>
                                        <div>
                                            <span className="font-medium">Updated:</span> {formatTimestamp(currentLogData.metadata.last_modified)}
                                        </div>
                                    </div>
                                </div>
                            )}

                            {currentLogData.success && currentLogData.content ? (
                                <div className="bg-black text-green-400 p-4 rounded-lg overflow-x-auto">
                                    <pre className="text-sm font-mono whitespace-pre-wrap">
                                        {currentLogData.content.join('')}
                                    </pre>
                                </div>
                            ) : (
                                <div className="bg-gray-100 p-4 rounded text-gray-600">
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