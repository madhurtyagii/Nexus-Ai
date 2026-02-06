import { useState, useEffect, useMemo } from 'react';
import { useNavigate } from 'react-router-dom';
import { tasksAPI } from '../services/api';
import Navbar from '../components/layout/Navbar';
import Sidebar from '../components/layout/Sidebar';
import MarkdownRenderer from '../components/common/MarkdownRenderer';
import toast from 'react-hot-toast';

export default function Tasks() {
    const navigate = useNavigate();
    const [tasks, setTasks] = useState([]);
    const [loading, setLoading] = useState(true);
    const [searchQuery, setSearchQuery] = useState('');
    const [statusFilter, setStatusFilter] = useState('all');
    const [sortOrder, setSortOrder] = useState('newest');
    const [selectedTask, setSelectedTask] = useState(null);
    const [showModal, setShowModal] = useState(false);
    const [deleting, setDeleting] = useState(null);

    useEffect(() => {
        loadTasks();
        const interval = setInterval(loadTasks, 5000);
        return () => clearInterval(interval);
    }, []);

    const loadTasks = async () => {
        try {
            const response = await tasksAPI.list({ limit: 100 });
            setTasks(response.data);
        } catch (error) {
            console.error('Failed to load tasks:', error);
        } finally {
            setLoading(false);
        }
    };

    const handleDelete = async (taskId, e) => {
        e.stopPropagation();
        if (!confirm('Are you sure you want to delete this task?')) return;

        setDeleting(taskId);
        try {
            await tasksAPI.delete(taskId);
            toast.success('Task deleted');
            setTasks(tasks.filter(t => t.id !== taskId));
        } catch (error) {
            toast.error('Failed to delete task');
        } finally {
            setDeleting(null);
        }
    };

    const handleViewTask = (task) => {
        setSelectedTask(task);
        setShowModal(true);
    };

    const getStatusColor = (status) => {
        switch (status) {
            case 'completed': return 'text-green-400 bg-green-400/10 border-green-400/30';
            case 'in_progress': return 'text-yellow-400 bg-yellow-400/10 border-yellow-400/30';
            case 'failed': return 'text-red-400 bg-red-400/10 border-red-400/30';
            case 'queued': return 'text-blue-400 bg-blue-400/10 border-blue-400/30';
            default: return 'text-gray-400 bg-gray-400/10 border-gray-400/30';
        }
    };

    const getStatusIcon = (status) => {
        switch (status) {
            case 'completed': return '✅';
            case 'in_progress': return '⏳';
            case 'failed': return '❌';
            case 'queued': return '📋';
            default: return '❓';
        }
    };

    const filteredAndSortedTasks = useMemo(() => {
        let result = [...tasks];

        // Filter by status
        if (statusFilter !== 'all') {
            result = result.filter(t => t.status === statusFilter);
        }

        // Filter by search query
        if (searchQuery.trim()) {
            const query = searchQuery.toLowerCase();
            result = result.filter(t =>
                t.user_prompt?.toLowerCase().includes(query)
            );
        }

        // Sort
        result.sort((a, b) => {
            const dateA = new Date(a.created_at);
            const dateB = new Date(b.created_at);
            return sortOrder === 'newest' ? dateB - dateA : dateA - dateB;
        });

        return result;
    }, [tasks, statusFilter, searchQuery, sortOrder]);

    const statusOptions = [
        { value: 'all', label: 'All Status' },
        { value: 'queued', label: 'Queued' },
        { value: 'in_progress', label: 'In Progress' },
        { value: 'completed', label: 'Completed' },
        { value: 'failed', label: 'Failed' },
    ];

    return (
        <div className="min-h-screen bg-dark-900">
            <Navbar />
            <div className="flex">
                <Sidebar />
                <main className="flex-1 p-6 lg:p-8">
                    {/* Header */}
                    <div className="mb-8">
                        <div className="flex items-center gap-4 mb-2">
                            <button
                                onClick={() => navigate('/dashboard')}
                                className="bg-dark-700 hover:bg-dark-600 text-white w-8 h-8 rounded-full flex items-center justify-center transition-colors"
                                title="Back to Dashboard"
                            >
                                ←
                            </button>
                            <h1 className="text-3xl font-bold text-white">📋 All Tasks</h1>
                        </div>
                        <p className="text-dark-400">View, manage, and track all your AI tasks.</p>
                    </div>

                    {/* Filters */}
                    <div className="card mb-6">
                        <div className="flex flex-col md:flex-row gap-4">
                            <div className="flex-1">
                                <input
                                    type="text"
                                    value={searchQuery}
                                    onChange={(e) => setSearchQuery(e.target.value)}
                                    placeholder="Search tasks..."
                                    className="w-full input-field"
                                />
                            </div>
                            <select
                                value={statusFilter}
                                onChange={(e) => setStatusFilter(e.target.value)}
                                className="input-field md:w-48"
                            >
                                {statusOptions.map(opt => (
                                    <option key={opt.value} value={opt.value}>{opt.label}</option>
                                ))}
                            </select>
                            <select
                                value={sortOrder}
                                onChange={(e) => setSortOrder(e.target.value)}
                                className="input-field md:w-40"
                            >
                                <option value="newest">Newest First</option>
                                <option value="oldest">Oldest First</option>
                            </select>
                        </div>
                    </div>

                    {/* Task List */}
                    {loading ? (
                        <div className="text-center py-12">
                            <div className="animate-spin w-8 h-8 border-2 border-primary-500 border-t-transparent rounded-full mx-auto mb-4"></div>
                            <p className="text-dark-400">Loading tasks...</p>
                        </div>
                    ) : filteredAndSortedTasks.length === 0 ? (
                        <div className="card text-center py-12">
                            <div className="w-16 h-16 bg-dark-700 rounded-full flex items-center justify-center mx-auto mb-4">
                                <span className="text-3xl">📋</span>
                            </div>
                            <h3 className="text-xl font-semibold text-white mb-2">No Tasks Found</h3>
                            <p className="text-dark-400 mb-4">
                                {searchQuery || statusFilter !== 'all'
                                    ? 'Try adjusting your filters.'
                                    : 'Create your first task from the Dashboard!'}
                            </p>
                            <button
                                onClick={() => navigate('/dashboard')}
                                className="btn-primary"
                            >
                                Go to Dashboard
                            </button>
                        </div>
                    ) : (
                        <div className="space-y-4">
                            {filteredAndSortedTasks.map((task) => (
                                <div
                                    key={task.id}
                                    onClick={() => handleViewTask(task)}
                                    className="card hover:border-primary-500/50 transition-all cursor-pointer group"
                                >
                                    <div className="flex items-start justify-between gap-4">
                                        <div className="flex-1 min-w-0">
                                            <p className="text-white font-medium mb-2 line-clamp-2 group-hover:text-primary-400 transition-colors">
                                                {task.user_prompt}
                                            </p>
                                            <div className="flex flex-wrap items-center gap-3 text-sm">
                                                <span className={`px-2 py-1 rounded-full border ${getStatusColor(task.status)}`}>
                                                    {getStatusIcon(task.status)} {task.status.replace('_', ' ')}
                                                </span>
                                                <span className="text-dark-500">
                                                    {(() => {
                                                        if (!task.created_at) return '';
                                                        let dateStr = task.created_at;
                                                        if (typeof dateStr === 'string' && !dateStr.includes('Z') && !dateStr.includes('+')) {
                                                            dateStr += 'Z';
                                                        }
                                                        const date = new Date(dateStr);
                                                        if (isNaN(date.getTime())) return task.created_at;

                                                        return date.toLocaleString();
                                                    })()}
                                                </span>
                                            </div>
                                            {task.status === 'in_progress' && (
                                                <div className="mt-3 h-2 bg-dark-700 rounded-full overflow-hidden">
                                                    <div className="h-full bg-gradient-to-r from-primary-500 to-purple-500 rounded-full animate-pulse w-1/2"></div>
                                                </div>
                                            )}
                                        </div>
                                        <div className="flex items-center gap-2">
                                            <button
                                                onClick={(e) => {
                                                    e.stopPropagation();
                                                    navigate(`/tasks/${task.id}`);
                                                }}
                                                className="px-3 py-1.5 text-sm bg-dark-700 hover:bg-dark-600 text-white rounded-lg transition-colors"
                                            >
                                                View
                                            </button>
                                            <button
                                                onClick={(e) => handleDelete(task.id, e)}
                                                disabled={deleting === task.id}
                                                className="px-3 py-1.5 text-sm bg-red-500/10 hover:bg-red-500/20 text-red-400 rounded-lg transition-colors disabled:opacity-50"
                                            >
                                                {deleting === task.id ? '...' : 'Delete'}
                                            </button>
                                        </div>
                                    </div>
                                </div>
                            ))}
                        </div>
                    )}

                    {/* Stats Footer */}
                    <div className="mt-8 grid grid-cols-2 md:grid-cols-4 gap-4">
                        <div className="card text-center py-4">
                            <div className="text-2xl font-bold text-white">{tasks.length}</div>
                            <p className="text-dark-400 text-sm">Total Tasks</p>
                        </div>
                        <div className="card text-center py-4">
                            <div className="text-2xl font-bold text-green-400">
                                {tasks.filter(t => t.status === 'completed').length}
                            </div>
                            <p className="text-dark-400 text-sm">Completed</p>
                        </div>
                        <div className="card text-center py-4">
                            <div className="text-2xl font-bold text-yellow-400">
                                {tasks.filter(t => t.status === 'in_progress').length}
                            </div>
                            <p className="text-dark-400 text-sm">In Progress</p>
                        </div>
                        <div className="card text-center py-4">
                            <div className="text-2xl font-bold text-red-400">
                                {tasks.filter(t => t.status === 'failed').length}
                            </div>
                            <p className="text-dark-400 text-sm">Failed</p>
                        </div>
                    </div>
                </main>
            </div>

            {/* Task Detail Modal */}
            {showModal && selectedTask && (
                <div className="fixed inset-0 bg-black/70 backdrop-blur-sm flex items-center justify-center z-50 p-4">
                    <div className="bg-dark-800 rounded-2xl border border-dark-700 w-full max-w-3xl max-h-[80vh] overflow-hidden">
                        <div className="p-6 border-b border-dark-700 flex items-center justify-between">
                            <h2 className="text-xl font-semibold text-white">Task Details</h2>
                            <button
                                onClick={() => setShowModal(false)}
                                className="text-dark-400 hover:text-white text-2xl"
                            >
                                ×
                            </button>
                        </div>
                        <div className="p-6 overflow-y-auto max-h-[60vh]">
                            <div className="mb-4">
                                <label className="text-dark-400 text-sm">Prompt</label>
                                <p className="text-white mt-1">{selectedTask.user_prompt}</p>
                            </div>
                            <div className="mb-4">
                                <label className="text-dark-400 text-sm">Status</label>
                                <p className={`mt-1 inline-block px-3 py-1 rounded-full ${getStatusColor(selectedTask.status)}`}>
                                    {getStatusIcon(selectedTask.status)} {selectedTask.status}
                                </p>
                            </div>
                            <div className="mb-4">
                                <label className="text-dark-400 text-sm">Created</label>
                                <p className="text-white mt-1">
                                    {(() => {
                                        if (!selectedTask.created_at) return '';
                                        let dateStr = selectedTask.created_at;
                                        if (typeof dateStr === 'string' && !dateStr.includes('Z') && !dateStr.includes('+')) {
                                            dateStr += 'Z';
                                        }
                                        return new Date(dateStr).toLocaleString();
                                    })()}
                                </p>
                            </div>
                            {selectedTask.output && (
                                <div className="mb-4">
                                    <label className="text-dark-400 text-sm">Output</label>
                                    <div className="mt-2 p-4 bg-dark-900 rounded-lg border border-dark-700 max-h-60 overflow-y-auto">
                                        <MarkdownRenderer content={selectedTask.output} />
                                    </div>
                                </div>
                            )}
                        </div>
                        <div className="p-6 border-t border-dark-700 flex justify-end gap-3">
                            <button
                                onClick={() => navigate(`/tasks/${selectedTask.id}`)}
                                className="btn-primary"
                            >
                                View Full Details
                            </button>
                            <button
                                onClick={() => setShowModal(false)}
                                className="px-4 py-2 bg-dark-700 hover:bg-dark-600 text-white rounded-lg transition-colors"
                            >
                                Close
                            </button>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
}
