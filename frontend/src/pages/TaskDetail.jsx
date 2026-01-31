import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import api from '../services/api';
import Navbar from '../components/layout/Navbar';
import { AgentActivityPanelPolling } from '../components/agents/AgentActivityPanel';
import FileUpload from '../components/files/FileUpload';
import FileManager from '../components/files/FileManager';

/**
 * TaskDetail Page
 * Shows full task details, progress, subtasks, and output
 */
export default function TaskDetail() {
    const { taskId } = useParams();
    const navigate = useNavigate();
    const [task, setTask] = useState(null);
    const [progress, setProgress] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [isPolling, setIsPolling] = useState(false);
    const [fileRefreshTrigger, setFileRefreshTrigger] = useState(0);

    // Fetch task details
    const fetchTask = async () => {
        try {
            const response = await api.get(`/tasks/${taskId}`);
            setTask(response.data);
            setError(null);
        } catch (err) {
            setError('Failed to load task');
            console.error(err);
        } finally {
            setLoading(false);
        }
    };

    // Fetch progress
    const fetchProgress = async () => {
        try {
            const response = await api.get(`/tasks/${taskId}/status`);
            setProgress(response.data);

            // Stop polling if completed or failed
            if (response.data.status === 'completed' || response.data.status === 'failed') {
                setIsPolling(false);
                fetchTask(); // Refresh full task data
            }
        } catch (err) {
            console.error('Progress fetch error:', err);
        }
    };

    useEffect(() => {
        fetchTask();
        fetchProgress();
    }, [taskId]);

    // Poll for updates when in progress
    useEffect(() => {
        let interval;

        if (task?.status === 'in_progress' || task?.status === 'queued') {
            setIsPolling(true);
            interval = setInterval(fetchProgress, 3000);
        }

        return () => {
            if (interval) clearInterval(interval);
        };
    }, [task?.status]);

    const handleRetry = async () => {
        try {
            await api.post(`/tasks/${taskId}/retry`);
            fetchTask();
            fetchProgress();
        } catch (err) {
            console.error('Retry failed:', err);
        }
    };

    const handleDelete = async () => {
        if (window.confirm('Are you sure you want to delete this task?')) {
            try {
                await api.delete(`/tasks/${taskId}`);
                navigate('/dashboard');
            } catch (err) {
                console.error('Delete failed:', err);
            }
        }
    };

    const getStatusColor = (status) => {
        switch (status?.toLowerCase()) {
            case 'completed':
                return 'bg-emerald-500/20 text-emerald-400 border-emerald-500/30';
            case 'in_progress':
                return 'bg-blue-500/20 text-blue-400 border-blue-500/30';
            case 'queued':
                return 'bg-yellow-500/20 text-yellow-400 border-yellow-500/30';
            case 'failed':
                return 'bg-red-500/20 text-red-400 border-red-500/30';
            default:
                return 'bg-gray-500/20 text-gray-400 border-gray-500/30';
        }
    };

    const formatDate = (dateString) => {
        if (!dateString) return '';
        return new Date(dateString).toLocaleString();
    };

    const renderOutput = (output) => {
        if (!output) return null;

        // Check if it's markdown-like content
        if (typeof output === 'string') {
            // Simple markdown rendering
            const lines = output.split('\n');

            return (
                <div className="prose prose-invert max-w-none">
                    {lines.map((line, i) => {
                        if (line.startsWith('## ')) {
                            return <h2 key={i} className="text-xl font-bold text-white mt-4 mb-2">{line.replace('## ', '')}</h2>;
                        }
                        if (line.startsWith('### ')) {
                            return <h3 key={i} className="text-lg font-semibold text-slate-200 mt-3 mb-1">{line.replace('### ', '')}</h3>;
                        }
                        if (line.startsWith('- ')) {
                            return <li key={i} className="text-slate-300 ml-4">{line.replace('- ', '')}</li>;
                        }
                        if (line.match(/^\[.+\]\(.+\)$/)) {
                            // Markdown link
                            const match = line.match(/^\[(.+)\]\((.+)\)$/);
                            if (match) {
                                return (
                                    <a
                                        key={i}
                                        href={match[2]}
                                        target="_blank"
                                        rel="noopener noreferrer"
                                        className="text-purple-400 hover:text-purple-300 underline block"
                                    >
                                        🔗 {match[1]}
                                    </a>
                                );
                            }
                        }
                        if (line.trim() === '---') {
                            return <hr key={i} className="border-slate-700 my-4" />;
                        }
                        if (line.trim()) {
                            return <p key={i} className="text-slate-300 leading-relaxed mb-2">{line}</p>;
                        }
                        return null;
                    })}
                </div>
            );
        }

        return <pre className="text-slate-300 whitespace-pre-wrap">{JSON.stringify(output, null, 2)}</pre>;
    };

    if (loading) {
        return (
            <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900">
                <Navbar />
                <div className="flex items-center justify-center h-96">
                    <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-purple-500"></div>
                </div>
            </div>
        );
    }

    if (error) {
        return (
            <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900">
                <Navbar />
                <div className="max-w-4xl mx-auto px-6 py-8">
                    <div className="bg-red-500/10 border border-red-500/30 rounded-xl p-6 text-center">
                        <p className="text-red-400">{error}</p>
                        <button
                            onClick={() => navigate('/dashboard')}
                            className="mt-4 px-4 py-2 bg-slate-700 text-white rounded-lg hover:bg-slate-600"
                        >
                            Back to Dashboard
                        </button>
                    </div>
                </div>
            </div>
        );
    }

    return (
        <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900">
            <Navbar />

            <div className="max-w-4xl mx-auto px-6 py-8">
                {/* Back button */}
                <button
                    onClick={() => navigate('/dashboard')}
                    className="flex items-center gap-2 text-slate-400 hover:text-white mb-6 transition-colors"
                >
                    <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                        <path fillRule="evenodd" d="M9.707 16.707a1 1 0 01-1.414 0l-6-6a1 1 0 010-1.414l6-6a1 1 0 011.414 1.414L5.414 9H17a1 1 0 110 2H5.414l4.293 4.293a1 1 0 010 1.414z" clipRule="evenodd" />
                    </svg>
                    Back to Dashboard
                </button>

                {/* Header */}
                <div className="bg-slate-800/50 backdrop-blur-sm border border-slate-700/50 rounded-xl p-6 mb-6">
                    <div className="flex items-start justify-between mb-4">
                        <h1 className="text-xl font-bold text-white leading-relaxed flex-1">
                            {task?.user_prompt}
                        </h1>
                        <span className={`px-3 py-1 rounded-full text-sm font-medium border ${getStatusColor(task?.status)}`}>
                            {task?.status}
                        </span>
                    </div>

                    <div className="flex items-center gap-4 text-sm text-slate-400">
                        <span>Created: {formatDate(task?.created_at)}</span>
                        {task?.completed_at && (
                            <span>Completed: {formatDate(task?.completed_at)}</span>
                        )}
                    </div>

                    {/* Progress bar */}
                    {progress && (task?.status === 'in_progress' || task?.status === 'queued') && (
                        <div className="mt-4">
                            <div className="flex items-center justify-between mb-2">
                                <span className="text-sm text-slate-400">
                                    {progress.current_agent ? `${progress.current_agent} working...` : 'Processing...'}
                                </span>
                                <span className="text-sm text-purple-400">
                                    {progress.progress_percentage}%
                                </span>
                            </div>
                            <div className="h-2 bg-slate-700 rounded-full overflow-hidden">
                                <div
                                    className="h-full bg-gradient-to-r from-purple-500 to-blue-500 rounded-full transition-all duration-500"
                                    style={{ width: `${progress.progress_percentage}%` }}
                                />
                            </div>
                            {isPolling && (
                                <p className="text-xs text-slate-500 mt-2">Auto-refreshing every 3 seconds...</p>
                            )}
                        </div>
                    )}
                </div>

                {/* Subtasks */}
                {task?.subtasks && task.subtasks.length > 0 && (
                    <div className="bg-slate-800/50 backdrop-blur-sm border border-slate-700/50 rounded-xl p-6 mb-6">
                        <h2 className="text-lg font-semibold text-white mb-4">Subtasks</h2>
                        <div className="space-y-3">
                            {task.subtasks.map((subtask) => (
                                <div
                                    key={subtask.id}
                                    className="flex items-center justify-between p-3 bg-slate-900/50 rounded-lg"
                                >
                                    <div className="flex items-center gap-3">
                                        <div className={`w-2 h-2 rounded-full ${subtask.status === 'completed' ? 'bg-emerald-500' :
                                            subtask.status === 'in_progress' ? 'bg-blue-500 animate-pulse' :
                                                subtask.status === 'failed' ? 'bg-red-500' :
                                                    'bg-yellow-500'
                                            }`} />
                                        <span className="text-slate-300 font-medium">{subtask.assigned_agent}</span>
                                    </div>
                                    <span className={`text-xs px-2 py-1 rounded ${getStatusColor(subtask.status)}`}>
                                        {subtask.status}
                                    </span>
                                </div>
                            ))}
                        </div>
                    </div>
                )}

                {/* Agent Activity Panel */}
                {task?.subtasks && task.subtasks.length > 0 && (
                    <div className="mb-6">
                        <AgentActivityPanelPolling
                            subtasks={task.subtasks}
                            status={task.status}
                        />
                    </div>
                )}

                {/* File Management */}
                <div className="bg-slate-800/50 backdrop-blur-sm border border-slate-700/50 rounded-xl p-6 mb-6">
                    <div className="flex items-center justify-between mb-4">
                        <h2 className="text-lg font-semibold text-white">📁 Files</h2>
                        <FileUpload
                            taskId={taskId}
                            onUploadSuccess={() => setFileRefreshTrigger(prev => prev + 1)}
                        />
                    </div>
                    <FileManager taskId={taskId} refreshTrigger={fileRefreshTrigger} />
                </div>

                {/* Output */}
                {task?.output && (
                    <div className="bg-slate-800/50 backdrop-blur-sm border border-slate-700/50 rounded-xl p-6 mb-6">
                        <h2 className="text-lg font-semibold text-white mb-4">Output</h2>
                        <div className="bg-slate-900/50 rounded-lg p-4">
                            {renderOutput(task.output)}
                        </div>
                    </div>
                )}

                {/* Actions */}
                <div className="flex gap-3">
                    {task?.status === 'failed' && (
                        <button
                            onClick={handleRetry}
                            className="px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-500 transition-colors"
                        >
                            Retry Task
                        </button>
                    )}
                    <button
                        onClick={handleDelete}
                        className="px-4 py-2 bg-red-600/20 text-red-400 border border-red-500/30 rounded-lg hover:bg-red-600/30 transition-colors"
                    >
                        Delete Task
                    </button>
                </div>
            </div>
        </div>
    );
}
