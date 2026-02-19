import { useState, useEffect, useMemo } from 'react';
import { useNavigate } from 'react-router-dom';
import { tasksAPI } from '../services/api';
import { motion, AnimatePresence } from 'framer-motion';
import {
    ArrowLeft,
    Search,
    Filter,
    ChevronDown,
    Trash2,
    ExternalLink,
    Clock,
    CheckCircle2,
    AlertCircle,
    Loader2,
    ClipboardList,
    X,
    Zap,
    Square,
    SortDesc,
    SortAsc
} from 'lucide-react';
import Navbar from '../components/layout/Navbar';
import Sidebar from '../components/layout/Sidebar';
import MarkdownRenderer from '../components/common/MarkdownRenderer';
import ExpandableOutput from '../components/common/ExpandableOutput';
import toast from 'react-hot-toast';

const containerVariants = {
    hidden: { opacity: 0 },
    visible: {
        opacity: 1,
        transition: { staggerChildren: 0.04, delayChildren: 0.1 }
    }
};

const itemVariants = {
    hidden: { y: 16, opacity: 0 },
    visible: {
        y: 0,
        opacity: 1,
        transition: { type: 'spring', stiffness: 300, damping: 24 }
    }
};

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

    const getStatusConfig = (status) => {
        switch (status) {
            case 'completed': return { color: 'text-emerald-400', bg: 'bg-emerald-400/10', border: 'border-emerald-400/20', icon: CheckCircle2, label: 'Completed' };
            case 'in_progress': return { color: 'text-amber-400', bg: 'bg-amber-400/10', border: 'border-amber-400/20', icon: Loader2, label: 'In Progress' };
            case 'failed': return { color: 'text-red-400', bg: 'bg-red-400/10', border: 'border-red-400/20', icon: AlertCircle, label: 'Failed' };
            case 'queued': return { color: 'text-blue-400', bg: 'bg-blue-400/10', border: 'border-blue-400/20', icon: Clock, label: 'Queued' };
            default: return { color: 'text-dark-400', bg: 'bg-dark-400/10', border: 'border-dark-400/20', icon: Clock, label: status };
        }
    };

    const formatDate = (dateStr) => {
        if (!dateStr) return '';
        let d = dateStr;
        if (typeof d === 'string' && !d.includes('Z') && !d.includes('+')) {
            d += 'Z';
        }
        const date = new Date(d);
        if (isNaN(date.getTime())) return dateStr;
        return date.toLocaleString(undefined, {
            month: 'short',
            day: 'numeric',
            year: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        });
    };

    const filteredAndSortedTasks = useMemo(() => {
        let result = [...tasks];

        if (statusFilter !== 'all') {
            result = result.filter(t => t.status === statusFilter);
        }

        if (searchQuery.trim()) {
            const query = searchQuery.toLowerCase();
            result = result.filter(t =>
                t.user_prompt?.toLowerCase().includes(query)
            );
        }

        result.sort((a, b) => {
            const dateA = new Date(a.created_at);
            const dateB = new Date(b.created_at);
            return sortOrder === 'newest' ? dateB - dateA : dateA - dateB;
        });

        return result;
    }, [tasks, statusFilter, searchQuery, sortOrder]);

    const statusOptions = [
        { value: 'all', label: 'All Status', count: tasks.length },
        { value: 'queued', label: 'Queued', count: tasks.filter(t => t.status === 'queued').length },
        { value: 'in_progress', label: 'In Progress', count: tasks.filter(t => t.status === 'in_progress').length },
        { value: 'completed', label: 'Completed', count: tasks.filter(t => t.status === 'completed').length },
        { value: 'failed', label: 'Failed', count: tasks.filter(t => t.status === 'failed').length },
    ];

    const stats = [
        { label: 'Total', value: tasks.length, color: 'gradient-text-vivid', icon: ClipboardList },
        { label: 'Completed', value: tasks.filter(t => t.status === 'completed').length, color: 'text-emerald-400', icon: CheckCircle2 },
        { label: 'Running', value: tasks.filter(t => t.status === 'in_progress').length, color: 'text-amber-400', icon: Loader2 },
        { label: 'Failed', value: tasks.filter(t => t.status === 'failed').length, color: 'text-red-400', icon: AlertCircle },
    ];

    return (
        <div className="min-h-screen selection:bg-primary-500/30">
            <Navbar />
            <div className="flex">
                <Sidebar />
                <main className="flex-1 p-6 lg:p-8">
                    <motion.div
                        variants={containerVariants}
                        initial="hidden"
                        animate="visible"
                        className="max-w-6xl mx-auto"
                    >
                        {/* Header */}
                        <motion.div variants={itemVariants} className="mb-8">
                            <div className="flex items-center gap-3 mb-2">
                                <motion.button
                                    onClick={() => navigate('/dashboard')}
                                    className="p-2 rounded-xl bg-white/[0.03] hover:bg-white/[0.06] border border-white/[0.06] text-dark-400 hover:text-white transition-all"
                                    whileHover={{ scale: 1.05 }}
                                    whileTap={{ scale: 0.95 }}
                                >
                                    <ArrowLeft className="w-4 h-4" />
                                </motion.button>
                                <div>
                                    <h1 className="text-3xl font-black text-white tracking-tight flex items-center gap-3">
                                        <span>📋</span> All <span className="gradient-text-vivid">Tasks</span>
                                    </h1>
                                    <p className="text-dark-400 text-sm font-medium mt-1">
                                        <span className="stat-number text-dark-300">{tasks.length}</span> operations tracked
                                    </p>
                                </div>
                            </div>
                            <div className="h-px mt-4 bg-gradient-to-r from-transparent via-primary-500/30 to-transparent" />
                        </motion.div>

                        {/* Filters Bar */}
                        <motion.div variants={itemVariants} className="card p-4 mb-6">
                            <div className="flex flex-col md:flex-row gap-3 items-stretch md:items-center">
                                {/* Search */}
                                <div className="flex-1 relative">
                                    <Search className="absolute left-4 top-1/2 -translate-y-1/2 w-4 h-4 text-dark-600" />
                                    <input
                                        type="text"
                                        value={searchQuery}
                                        onChange={(e) => setSearchQuery(e.target.value)}
                                        placeholder="Search tasks..."
                                        className="w-full pl-11 pr-4 py-2.5 bg-white/[0.03] border border-white/[0.06] rounded-xl text-white text-sm placeholder:text-dark-600 focus:outline-none focus:border-primary-500/30 focus:bg-white/[0.05] transition-all"
                                    />
                                </div>

                                {/* Status Filter */}
                                <div className="relative">
                                    <select
                                        value={statusFilter}
                                        onChange={(e) => setStatusFilter(e.target.value)}
                                        className="appearance-none pl-4 pr-10 py-2.5 bg-white/[0.03] border border-white/[0.06] rounded-xl text-dark-200 text-sm font-medium focus:outline-none focus:border-primary-500/30 cursor-pointer transition-all min-w-[150px]"
                                    >
                                        {statusOptions.map(opt => (
                                            <option key={opt.value} value={opt.value} className="bg-dark-900 text-white">
                                                {opt.label} ({opt.count})
                                            </option>
                                        ))}
                                    </select>
                                    <ChevronDown className="absolute right-3 top-1/2 -translate-y-1/2 w-4 h-4 text-dark-500 pointer-events-none" />
                                </div>

                                {/* Sort Toggle */}
                                <motion.button
                                    onClick={() => setSortOrder(prev => prev === 'newest' ? 'oldest' : 'newest')}
                                    className="flex items-center gap-2 px-4 py-2.5 bg-white/[0.03] border border-white/[0.06] rounded-xl text-dark-300 text-sm font-medium hover:bg-white/[0.06] transition-all whitespace-nowrap"
                                    whileHover={{ scale: 1.02 }}
                                    whileTap={{ scale: 0.98 }}
                                >
                                    {sortOrder === 'newest' ? (
                                        <><SortDesc className="w-4 h-4" /> Newest</>
                                    ) : (
                                        <><SortAsc className="w-4 h-4" /> Oldest</>
                                    )}
                                </motion.button>
                            </div>
                        </motion.div>

                        {/* Task List */}
                        {loading ? (
                            <div className="flex items-center justify-center py-20">
                                <motion.div
                                    className="w-10 h-10 border-2 border-primary-500 border-t-transparent rounded-full"
                                    animate={{ rotate: 360 }}
                                    transition={{ duration: 1, repeat: Infinity, ease: 'linear' }}
                                />
                            </div>
                        ) : filteredAndSortedTasks.length === 0 ? (
                            <motion.div variants={itemVariants} className="card text-center py-16">
                                <div className="w-16 h-16 bg-white/[0.03] rounded-2xl flex items-center justify-center mx-auto mb-4 border border-white/[0.06]">
                                    <ClipboardList className="w-7 h-7 text-dark-600" />
                                </div>
                                <h3 className="text-lg font-bold text-white mb-2">No Tasks Found</h3>
                                <p className="text-dark-500 text-sm mb-6 max-w-sm mx-auto">
                                    {searchQuery || statusFilter !== 'all'
                                        ? 'Try adjusting your filters to find what you\'re looking for.'
                                        : 'Create your first task from the Dashboard to get started!'}
                                </p>
                                <motion.button
                                    onClick={() => navigate('/dashboard')}
                                    className="btn-primary text-sm"
                                    whileHover={{ scale: 1.03 }}
                                    whileTap={{ scale: 0.97 }}
                                >
                                    Go to Dashboard
                                </motion.button>
                            </motion.div>
                        ) : (
                            <motion.div
                                variants={containerVariants}
                                initial="hidden"
                                animate="visible"
                                className="space-y-3"
                            >
                                {filteredAndSortedTasks.map((task) => {
                                    const status = getStatusConfig(task.status);
                                    const StatusIcon = status.icon;

                                    return (
                                        <motion.div
                                            key={task.id}
                                            variants={itemVariants}
                                            layout
                                            onClick={() => handleViewTask(task)}
                                            className="card-interactive p-5 group hover:border-primary-500/20 transition-all"
                                            whileHover={{ x: 4 }}
                                        >
                                            <div className="flex items-center gap-4">
                                                {/* Status Icon */}
                                                <div className={`flex-shrink-0 w-10 h-10 rounded-xl ${status.bg} border ${status.border} flex items-center justify-center`}>
                                                    <StatusIcon className={`w-4 h-4 ${status.color} ${task.status === 'in_progress' ? 'animate-spin' : ''}`} />
                                                </div>

                                                {/* Content */}
                                                <div className="flex-1 min-w-0">
                                                    <p className="text-sm font-semibold text-dark-100 line-clamp-1 group-hover:text-white transition-colors">
                                                        {task.user_prompt}
                                                    </p>
                                                    <div className="flex items-center gap-3 mt-1.5">
                                                        <span className={`text-[10px] font-bold uppercase tracking-wider px-2 py-0.5 rounded-md ${status.bg} ${status.color} border ${status.border}`}>
                                                            {status.label}
                                                        </span>
                                                        <span className="text-[11px] text-dark-600 font-medium">
                                                            {formatDate(task.created_at)}
                                                        </span>
                                                    </div>

                                                    {/* Progress bar for in-progress */}
                                                    {task.status === 'in_progress' && (
                                                        <div className="mt-2.5 h-1 bg-dark-800 rounded-full overflow-hidden">
                                                            <motion.div
                                                                className="h-full bg-gradient-to-r from-primary-500 to-purple-500 rounded-full"
                                                                animate={{ width: ['20%', '80%', '40%', '70%'] }}
                                                                transition={{ duration: 3, repeat: Infinity, ease: 'easeInOut' }}
                                                                style={{ boxShadow: '0 0 8px rgba(14, 165, 233, 0.3)' }}
                                                            />
                                                        </div>
                                                    )}
                                                </div>

                                                {/* Actions */}
                                                <div className="flex items-center gap-2 flex-shrink-0">
                                                    <motion.button
                                                        onClick={(e) => {
                                                            e.stopPropagation();
                                                            navigate(`/tasks/${task.id}`);
                                                        }}
                                                        className="flex items-center gap-1.5 px-3 py-2 text-xs font-semibold bg-white/[0.04] hover:bg-primary-500/10 text-dark-300 hover:text-primary-400 border border-white/[0.06] hover:border-primary-500/20 rounded-lg transition-all"
                                                        whileHover={{ scale: 1.05 }}
                                                        whileTap={{ scale: 0.95 }}
                                                    >
                                                        <ExternalLink className="w-3 h-3" />
                                                        View
                                                    </motion.button>
                                                    <motion.button
                                                        onClick={(e) => handleDelete(task.id, e)}
                                                        disabled={deleting === task.id}
                                                        className="flex items-center gap-1.5 px-3 py-2 text-xs font-semibold bg-red-500/5 hover:bg-red-500/15 text-red-400/70 hover:text-red-400 border border-red-500/10 hover:border-red-500/20 rounded-lg transition-all disabled:opacity-30"
                                                        whileHover={{ scale: 1.05 }}
                                                        whileTap={{ scale: 0.95 }}
                                                    >
                                                        {deleting === task.id ? (
                                                            <Loader2 className="w-3 h-3 animate-spin" />
                                                        ) : (
                                                            <Trash2 className="w-3 h-3" />
                                                        )}
                                                        Delete
                                                    </motion.button>
                                                </div>
                                            </div>
                                        </motion.div>
                                    );
                                })}
                            </motion.div>
                        )}

                        {/* Stats Footer */}
                        <motion.div
                            variants={itemVariants}
                            className="mt-8 grid grid-cols-2 md:grid-cols-4 gap-4"
                        >
                            {stats.map((stat) => (
                                <motion.div
                                    key={stat.label}
                                    className="card-glow p-4 text-center group"
                                    whileHover={{ scale: 1.03, y: -3 }}
                                >
                                    <stat.icon className={`w-5 h-5 mx-auto mb-2 ${stat.color} opacity-40 group-hover:opacity-100 transition-opacity`} />
                                    <div className={`text-2xl font-black tracking-tighter ${stat.color} stat-number`}>{stat.value}</div>
                                    <p className="text-[10px] uppercase font-bold tracking-widest text-dark-600 mt-1">{stat.label}</p>
                                </motion.div>
                            ))}
                        </motion.div>
                    </motion.div>
                </main>
            </div>

            {/* Task Detail Modal */}
            <AnimatePresence>
                {showModal && selectedTask && (
                    <motion.div
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        exit={{ opacity: 0 }}
                        className="fixed inset-0 bg-black/60 backdrop-blur-md flex items-center justify-center z-50 p-4"
                        onClick={() => setShowModal(false)}
                    >
                        <motion.div
                            initial={{ scale: 0.92, opacity: 0, y: 20 }}
                            animate={{ scale: 1, opacity: 1, y: 0 }}
                            exit={{ scale: 0.92, opacity: 0, y: 20 }}
                            transition={{ type: 'spring', stiffness: 300, damping: 25 }}
                            className="glass rounded-2xl border border-white/[0.08] w-full max-w-3xl max-h-[80vh] overflow-hidden shadow-2xl"
                            onClick={(e) => e.stopPropagation()}
                        >
                            <div className="p-6 border-b border-white/[0.06] flex items-center justify-between">
                                <h2 className="text-lg font-bold text-white">Task Details</h2>
                                <motion.button
                                    onClick={() => setShowModal(false)}
                                    className="p-2 text-dark-400 hover:text-white hover:bg-white/[0.05] rounded-xl transition-all"
                                    whileHover={{ scale: 1.1 }}
                                    whileTap={{ scale: 0.9 }}
                                >
                                    <X className="w-5 h-5" />
                                </motion.button>
                            </div>
                            <div className="p-6 overflow-y-auto max-h-[60vh]">
                                <div className="mb-5">
                                    <h3 className="text-[10px] uppercase tracking-[0.15em] font-bold text-dark-600 mb-1.5">Prompt</h3>
                                    <p className="text-dark-100 text-sm leading-relaxed">{selectedTask.user_prompt}</p>
                                </div>
                                <div className="mb-5">
                                    <h3 className="text-[10px] uppercase tracking-[0.15em] font-bold text-dark-600 mb-1.5">Status</h3>
                                    {(() => {
                                        const st = getStatusConfig(selectedTask.status);
                                        return (
                                            <span className={`inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-bold ${st.bg} ${st.color} border ${st.border}`}>
                                                <st.icon className={`w-3.5 h-3.5 ${selectedTask.status === 'in_progress' ? 'animate-spin' : ''}`} />
                                                {st.label}
                                            </span>
                                        );
                                    })()}
                                </div>
                                <div className="mb-5">
                                    <h3 className="text-[10px] uppercase tracking-[0.15em] font-bold text-dark-600 mb-1.5">Created</h3>
                                    <p className="text-dark-300 text-sm">{formatDate(selectedTask.created_at)}</p>
                                </div>
                                {selectedTask.output && (
                                    <div>
                                        <h3 className="text-[10px] uppercase tracking-[0.15em] font-bold text-dark-600 mb-2">Output</h3>
                                        <div className="rounded-xl bg-white/[0.02] border border-white/[0.04] p-4">
                                            <ExpandableOutput
                                                content={selectedTask.output}
                                                title="Task Output"
                                                collapsedHeight={250}
                                            />
                                        </div>
                                    </div>
                                )}
                            </div>
                            <div className="p-5 border-t border-white/[0.06] flex justify-end gap-3">
                                <motion.button
                                    onClick={() => navigate(`/tasks/${selectedTask.id}`)}
                                    className="btn-primary text-sm"
                                    whileHover={{ scale: 1.03 }}
                                    whileTap={{ scale: 0.97 }}
                                >
                                    View Full Details
                                </motion.button>
                                <button
                                    onClick={() => setShowModal(false)}
                                    className="px-5 py-2.5 bg-white/[0.04] hover:bg-white/[0.08] text-dark-300 rounded-xl transition-colors text-sm font-medium"
                                >
                                    Close
                                </button>
                            </div>
                        </motion.div>
                    </motion.div>
                )}
            </AnimatePresence>
        </div>
    );
}
