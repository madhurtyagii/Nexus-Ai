import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import toast from 'react-hot-toast';
import api, { projectsAPI, workflowTemplatesAPI } from '../services/api';
import {
    FolderPlus,
    Search,
    Archive,
    ArrowLeft,
    Pin,
    MoreVertical,
    Calendar,
    Clock,
    CheckCircle2,
    AlertCircle,
    Loader2,
    TrendingUp,
    Layers,
    Zap,
    ChevronRight,
    Plus,
    FolderOpen,
    Filter,
    Sparkles,
    X
} from 'lucide-react';
import Navbar from '../components/layout/Navbar';
import Sidebar from '../components/layout/Sidebar';
import { CardSkeleton, StatSkeleton } from '../components/common/Skeleton';

// Animation variants
const containerVariants = {
    hidden: { opacity: 0 },
    visible: {
        opacity: 1,
        transition: { staggerChildren: 0.08, delayChildren: 0.1 }
    }
};

const itemVariants = {
    hidden: { opacity: 0, y: 20, scale: 0.95 },
    visible: {
        opacity: 1,
        y: 0,
        scale: 1,
        transition: { type: "spring", stiffness: 300, damping: 24 }
    }
};

export default function Projects() {
    const [projects, setProjects] = useState([]);
    const [loading, setLoading] = useState(true);
    const [filter, setFilter] = useState('all');
    const [searchTerm, setSearchTerm] = useState('');
    const [showArchived, setShowArchived] = useState(false);
    const [showCreateModal, setShowCreateModal] = useState(false);
    const [newProject, setNewProject] = useState({ name: '', description: '', priority: 'medium' });
    const [creating, setCreating] = useState(false);
    const navigate = useNavigate();

    useEffect(() => {
        const delayDebounceFn = setTimeout(() => {
            fetchProjects();
        }, searchTerm ? 500 : 0);

        return () => clearTimeout(delayDebounceFn);
    }, [filter, searchTerm, showArchived]);

    const fetchProjects = async () => {
        setLoading(true);
        try {
            const params = {
                status: filter !== 'all' ? filter : undefined,
                q: searchTerm || undefined,
                is_archived: showArchived
            };
            const response = await projectsAPI.getProjects(params);
            setProjects(response.data);
        } catch (error) {
            console.error('Error fetching projects:', error);
            toast.error('Failed to load projects');
        } finally {
            setLoading(false);
        }
    };

    const handleCreateProject = async (e) => {
        e.preventDefault();
        if (!newProject.name.trim()) {
            toast.error('Project name is required');
            return;
        }
        setCreating(true);
        try {
            const response = await projectsAPI.createProject(newProject);
            toast.success('Project created successfully!');
            setShowCreateModal(false);
            setNewProject({ name: '', description: '', priority: 'medium' });
            navigate(`/projects/${response.data.id}`);
        } catch (error) {
            toast.error('Failed to create project');
        } finally {
            setCreating(false);
        }
    };

    const handlePinProject = async (e, project) => {
        e.stopPropagation();
        try {
            await projectsAPI.pinProject(project.id, !project.is_pinned);
            fetchProjects();
            toast.success(project.is_pinned ? 'Project unpinned' : 'Project pinned');
        } catch (error) {
            toast.error('Failed to update project');
        }
    };

    const getStatusConfig = (status) => {
        const configs = {
            completed: { color: 'text-emerald-400', bg: 'bg-emerald-500/10', border: 'border-emerald-500/20', icon: CheckCircle2, label: 'Completed' },
            in_progress: { color: 'text-primary-400', bg: 'bg-primary-500/10', border: 'border-primary-500/20', icon: Loader2, label: 'In Progress' },
            failed: { color: 'text-red-400', bg: 'bg-red-500/10', border: 'border-red-500/20', icon: AlertCircle, label: 'Failed' },
            planning: { color: 'text-amber-400', bg: 'bg-amber-500/10', border: 'border-amber-500/20', icon: Sparkles, label: 'Planning' },
        };
        return configs[status] || configs.planning;
    };

    const stats = [
        { label: 'Total', value: projects.length, icon: Layers, color: 'text-primary-400' },
        { label: 'Active', value: projects.filter(p => p.status === 'in_progress').length, icon: Zap, color: 'text-emerald-400' },
        { label: 'Planning', value: projects.filter(p => p.status === 'planning').length, icon: Sparkles, color: 'text-amber-400' },
        { label: 'Completed', value: projects.filter(p => p.status === 'completed').length, icon: CheckCircle2, color: 'text-purple-400' },
    ];

    const filters = [
        { id: 'all', label: 'All' },
        { id: 'planning', label: 'Planning' },
        { id: 'in_progress', label: 'In Progress' },
        { id: 'completed', label: 'Completed' },
        { id: 'failed', label: 'Failed' },
    ];

    return (
        <div className="min-h-screen bg-dark-900">
            <Navbar />
            <div className="flex">
                <Sidebar />
                <main className="flex-1 p-6 lg:p-10">
                    <motion.div
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        className="max-w-7xl mx-auto"
                    >
                        {/* Header */}
                        <div className="flex flex-col md:flex-row md:items-center justify-between gap-6 mb-10">
                            <div className="flex items-center gap-4">
                                <motion.button
                                    whileHover={{ scale: 1.05 }}
                                    whileTap={{ scale: 0.95 }}
                                    onClick={() => navigate('/dashboard')}
                                    className="w-10 h-10 glass rounded-xl flex items-center justify-center text-dark-400 hover:text-white transition-colors"
                                >
                                    <ArrowLeft className="w-5 h-5" />
                                </motion.button>
                                <div>
                                    <h1 className="text-3xl font-black text-white tracking-tight">Projects</h1>
                                    <p className="text-dark-400 font-medium">Manage multi-phase AI workflows</p>
                                </div>
                            </div>

                            <div className="flex items-center gap-3">
                                {/* Search */}
                                <div className="relative">
                                    <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-dark-500" />
                                    <input
                                        type="text"
                                        placeholder="Search projects..."
                                        value={searchTerm}
                                        onChange={(e) => setSearchTerm(e.target.value)}
                                        className="w-64 pl-10 pr-4 py-2.5 bg-white/[0.03] border border-white/5 rounded-xl text-white placeholder-dark-500 focus:outline-none focus:border-primary-500/50 transition-colors"
                                    />
                                </div>

                                {/* Archive Toggle */}
                                <motion.button
                                    whileHover={{ scale: 1.02 }}
                                    whileTap={{ scale: 0.98 }}
                                    onClick={() => setShowArchived(!showArchived)}
                                    className={`flex items-center gap-2 px-4 py-2.5 rounded-xl border font-medium transition-all ${showArchived
                                        ? 'bg-primary-500/10 border-primary-500/30 text-primary-400'
                                        : 'bg-white/[0.03] border-white/5 text-dark-400 hover:text-white'
                                        }`}
                                >
                                    <Archive className="w-4 h-4" />
                                    <span className="text-sm">{showArchived ? 'Active' : 'Archived'}</span>
                                </motion.button>

                                {/* Create Button */}
                                <motion.button
                                    whileHover={{ scale: 1.02, boxShadow: "0 10px 30px rgba(14,165,233,0.3)" }}
                                    whileTap={{ scale: 0.98 }}
                                    onClick={() => setShowCreateModal(true)}
                                    className="flex items-center gap-2 bg-primary-500 hover:bg-primary-400 text-white font-bold px-5 py-2.5 rounded-xl transition-all"
                                >
                                    <Plus className="w-4 h-4" />
                                    <span>New Project</span>
                                </motion.button>
                            </div>
                        </div>

                        {/* Stats */}
                        {!loading && projects.length > 0 && !showArchived && (
                            <motion.div
                                variants={containerVariants}
                                initial="hidden"
                                animate="visible"
                                className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8"
                            >
                                {stats.map((stat) => (
                                    <motion.div
                                        key={stat.label}
                                        variants={itemVariants}
                                        className="glass p-5 rounded-2xl border border-white/5"
                                    >
                                        <div className="flex items-center justify-between">
                                            <div>
                                                <p className="text-dark-500 text-xs font-bold uppercase tracking-wider mb-1">{stat.label}</p>
                                                <p className={`text-3xl font-black ${stat.color}`}>{stat.value}</p>
                                            </div>
                                            <stat.icon className={`w-8 h-8 ${stat.color} opacity-30`} />
                                        </div>
                                    </motion.div>
                                ))}
                            </motion.div>
                        )}

                        {/* Filters */}
                        <div className="flex items-center gap-2 mb-8 overflow-x-auto pb-2">
                            {filters.map((f) => (
                                <motion.button
                                    key={f.id}
                                    whileHover={{ scale: 1.02 }}
                                    whileTap={{ scale: 0.98 }}
                                    onClick={() => setFilter(f.id)}
                                    className={`px-4 py-2 rounded-xl text-sm font-bold transition-all whitespace-nowrap ${filter === f.id
                                        ? 'bg-primary-500 text-white shadow-[0_5px_20px_rgba(14,165,233,0.3)]'
                                        : 'bg-white/[0.03] text-dark-400 hover:text-white border border-white/5'
                                        }`}
                                >
                                    {f.label}
                                </motion.button>
                            ))}
                        </div>

                        {/* Content */}
                        {loading ? (
                            <div className="space-y-8">
                                {/* Stats Skeleton */}
                                <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                                    {[1, 2, 3, 4].map((i) => (
                                        <StatSkeleton key={i} />
                                    ))}
                                </div>
                                {/* Cards Skeleton */}
                                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
                                    {[1, 2, 3, 4, 5, 6].map((i) => (
                                        <CardSkeleton key={i} />
                                    ))}
                                </div>
                            </div>
                        ) : projects.length === 0 ? (
                            <motion.div
                                initial={{ opacity: 0, scale: 0.95 }}
                                animate={{ opacity: 1, scale: 1 }}
                                className="glass p-16 rounded-3xl border border-white/5 text-center"
                            >
                                <motion.div
                                    animate={{ rotate: [0, 10, -10, 0] }}
                                    transition={{ duration: 2, repeat: Infinity, repeatDelay: 3 }}
                                    className="w-24 h-24 bg-white/5 rounded-3xl flex items-center justify-center mx-auto mb-8"
                                >
                                    <FolderOpen className="w-12 h-12 text-dark-500" />
                                </motion.div>
                                <h3 className="text-2xl font-black text-white mb-3">No projects found</h3>
                                <p className="text-dark-400 mb-8 max-w-sm mx-auto">
                                    {searchTerm ? "Try a different search term" : "Create your first AI-powered project to get started"}
                                </p>
                                <motion.button
                                    whileHover={{ scale: 1.05 }}
                                    whileTap={{ scale: 0.95 }}
                                    onClick={() => setShowCreateModal(true)}
                                    className="bg-primary-500 hover:bg-primary-400 text-white font-bold px-8 py-3 rounded-xl transition-all"
                                >
                                    Create Project
                                </motion.button>
                            </motion.div>
                        ) : (
                            <motion.div
                                variants={containerVariants}
                                initial="hidden"
                                animate="visible"
                                className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5"
                            >
                                {projects.map((project) => {
                                    const statusConfig = getStatusConfig(project.status);
                                    return (
                                        <motion.div
                                            key={project.id}
                                            variants={itemVariants}
                                            whileHover={{ y: -5, scale: 1.01 }}
                                            onClick={() => navigate(`/projects/${project.id}`)}
                                            className={`glass p-6 rounded-2xl border cursor-pointer group relative overflow-hidden ${project.is_pinned ? 'border-primary-500/30' : 'border-white/5'
                                                }`}
                                        >
                                            {/* Hover gradient */}
                                            <div className="absolute inset-0 bg-gradient-to-br from-primary-500/5 to-purple-500/5 opacity-0 group-hover:opacity-100 transition-opacity" />

                                            {/* Pin indicator */}
                                            {project.is_pinned && (
                                                <div className="absolute top-3 right-3">
                                                    <Pin className="w-4 h-4 text-primary-400 fill-primary-400" />
                                                </div>
                                            )}

                                            <div className="relative z-10">
                                                {/* Status badge */}
                                                <div className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-lg ${statusConfig.bg} ${statusConfig.border} border mb-4`}>
                                                    <statusConfig.icon className={`w-3.5 h-3.5 ${statusConfig.color} ${project.status === 'in_progress' ? 'animate-spin' : ''}`} />
                                                    <span className={`text-xs font-bold ${statusConfig.color}`}>{statusConfig.label}</span>
                                                </div>

                                                {/* Title & Description */}
                                                <h3 className="text-lg font-bold text-white mb-2 group-hover:text-primary-400 transition-colors line-clamp-1">
                                                    {project.name}
                                                </h3>
                                                <p className="text-dark-400 text-sm line-clamp-2 mb-4">
                                                    {project.description || "No description"}
                                                </p>

                                                {/* Progress */}
                                                {project.progress !== undefined && (
                                                    <div className="mb-4">
                                                        <div className="flex items-center justify-between mb-1">
                                                            <span className="text-xs text-dark-500 font-medium">Progress</span>
                                                            <span className="text-xs text-primary-400 font-bold">{project.progress}%</span>
                                                        </div>
                                                        <div className="h-1.5 bg-white/5 rounded-full overflow-hidden">
                                                            <motion.div
                                                                initial={{ width: 0 }}
                                                                animate={{ width: `${project.progress}%` }}
                                                                transition={{ duration: 1, ease: "easeOut" }}
                                                                className="h-full bg-gradient-to-r from-primary-500 to-primary-400 rounded-full"
                                                            />
                                                        </div>
                                                    </div>
                                                )}

                                                {/* Footer */}
                                                <div className="flex items-center justify-between pt-4 border-t border-white/5">
                                                    <div className="flex items-center gap-3 text-dark-500 text-xs">
                                                        <div className="flex items-center gap-1">
                                                            <Calendar className="w-3.5 h-3.5" />
                                                            <span>{new Date(project.created_at).toLocaleDateString()}</span>
                                                        </div>
                                                        {project.total_tasks > 0 && (
                                                            <div className="flex items-center gap-1">
                                                                <CheckCircle2 className="w-3.5 h-3.5" />
                                                                <span>{project.completed_tasks || 0}/{project.total_tasks}</span>
                                                            </div>
                                                        )}
                                                    </div>
                                                    <motion.button
                                                        whileHover={{ scale: 1.1 }}
                                                        whileTap={{ scale: 0.9 }}
                                                        onClick={(e) => handlePinProject(e, project)}
                                                        className={`p-1.5 rounded-lg transition-colors ${project.is_pinned
                                                            ? 'text-primary-400 bg-primary-500/10'
                                                            : 'text-dark-500 hover:text-white hover:bg-white/5'
                                                            }`}
                                                    >
                                                        <Pin className={`w-4 h-4 ${project.is_pinned ? 'fill-current' : ''}`} />
                                                    </motion.button>
                                                </div>
                                            </div>
                                        </motion.div>
                                    );
                                })}
                            </motion.div>
                        )}
                    </motion.div>
                </main>
            </div>

            {/* Create Modal */}
            <AnimatePresence>
                {showCreateModal && (
                    <motion.div
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        exit={{ opacity: 0 }}
                        className="fixed inset-0 bg-black/60 backdrop-blur-sm z-50 flex items-center justify-center p-4"
                        onClick={() => setShowCreateModal(false)}
                    >
                        <motion.div
                            initial={{ opacity: 0, scale: 0.9, y: 20 }}
                            animate={{ opacity: 1, scale: 1, y: 0 }}
                            exit={{ opacity: 0, scale: 0.9, y: 20 }}
                            onClick={(e) => e.stopPropagation()}
                            className="w-full max-w-lg glass rounded-3xl p-8 border border-white/10"
                        >
                            <div className="flex items-center justify-between mb-6">
                                <h2 className="text-2xl font-black text-white">New Project</h2>
                                <button
                                    onClick={() => setShowCreateModal(false)}
                                    className="p-2 text-dark-400 hover:text-white hover:bg-white/5 rounded-xl transition-colors"
                                >
                                    <X className="w-5 h-5" />
                                </button>
                            </div>

                            <form onSubmit={handleCreateProject} className="space-y-5">
                                <div>
                                    <label className="block text-xs font-bold text-dark-400 uppercase tracking-wider mb-2">Project Name</label>
                                    <input
                                        type="text"
                                        value={newProject.name}
                                        onChange={(e) => setNewProject({ ...newProject, name: e.target.value })}
                                        placeholder="e.g., AI Research Assistant"
                                        className="w-full px-4 py-3 bg-white/[0.03] border border-white/5 rounded-xl text-white placeholder-dark-500 focus:outline-none focus:border-primary-500/50 transition-colors"
                                        autoFocus
                                    />
                                </div>

                                <div>
                                    <label className="block text-xs font-bold text-dark-400 uppercase tracking-wider mb-2">Description</label>
                                    <textarea
                                        value={newProject.description}
                                        onChange={(e) => setNewProject({ ...newProject, description: e.target.value })}
                                        placeholder="Describe your project goals..."
                                        rows={3}
                                        className="w-full px-4 py-3 bg-white/[0.03] border border-white/5 rounded-xl text-white placeholder-dark-500 focus:outline-none focus:border-primary-500/50 transition-colors resize-none"
                                    />
                                </div>

                                <div>
                                    <label className="block text-xs font-bold text-dark-400 uppercase tracking-wider mb-2">Priority</label>
                                    <div className="flex gap-3">
                                        {['low', 'medium', 'high'].map((p) => (
                                            <button
                                                key={p}
                                                type="button"
                                                onClick={() => setNewProject({ ...newProject, priority: p })}
                                                className={`flex-1 py-2.5 rounded-xl font-bold text-sm capitalize transition-all ${newProject.priority === p
                                                    ? 'bg-primary-500 text-white'
                                                    : 'bg-white/[0.03] text-dark-400 hover:text-white border border-white/5'
                                                    }`}
                                            >
                                                {p}
                                            </button>
                                        ))}
                                    </div>
                                </div>

                                <div className="flex gap-3 pt-4">
                                    <button
                                        type="button"
                                        onClick={() => setShowCreateModal(false)}
                                        className="flex-1 py-3 bg-white/[0.03] text-dark-400 hover:text-white font-bold rounded-xl border border-white/5 transition-colors"
                                    >
                                        Cancel
                                    </button>
                                    <motion.button
                                        type="submit"
                                        disabled={creating}
                                        whileHover={{ scale: 1.02 }}
                                        whileTap={{ scale: 0.98 }}
                                        className="flex-1 py-3 bg-primary-500 hover:bg-primary-400 text-white font-bold rounded-xl transition-colors disabled:opacity-50 flex items-center justify-center gap-2"
                                    >
                                        {creating ? (
                                            <>
                                                <Loader2 className="w-4 h-4 animate-spin" />
                                                Creating...
                                            </>
                                        ) : (
                                            <>
                                                <FolderPlus className="w-4 h-4" />
                                                Create Project
                                            </>
                                        )}
                                    </motion.button>
                                </div>
                            </form>
                        </motion.div>
                    </motion.div>
                )}
            </AnimatePresence>
        </div>
    );
}
