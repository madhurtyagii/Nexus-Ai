import { useState, useEffect, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { agentsAPI, tasksAPI, projectsAPI } from '../services/api';
import { useWebSocket, EventType } from '../hooks/useWebSocket';
import { motion, AnimatePresence } from 'framer-motion';
import {
    Plus,
    FolderPlus,
    Upload,
    Users,
    Activity,
    ShieldCheck,
    Database,
    Zap,
    ChevronRight,
    Pin,
    ArrowUpRight,
    Sparkles,
    Search,
    BrainCircuit
} from 'lucide-react';
import Navbar from '../components/layout/Navbar';
import Sidebar from '../components/layout/Sidebar';
import { Skeleton, TaskListSkeleton, CardSkeleton } from '../components/common/Skeleton';
import toast from 'react-hot-toast';

const containerVariants = {
    hidden: { opacity: 0 },
    visible: {
        opacity: 1,
        transition: {
            staggerChildren: 0.1,
            delayChildren: 0.2
        }
    }
};

const itemVariants = {
    hidden: { y: 20, opacity: 0 },
    visible: {
        y: 0,
        opacity: 1,
        transition: { type: 'spring', stiffness: 300, damping: 24 }
    }
};

export default function Dashboard() {
    const { user, token } = useAuth();
    const navigate = useNavigate();
    const [agents, setAgents] = useState([]);
    const [recentTasks, setRecentTasks] = useState([]);
    const [pinnedProjects, setPinnedProjects] = useState([]);
    const [prompt, setPrompt] = useState('');
    const [isSubmitting, setIsSubmitting] = useState(false);
    const [isLoading, setIsLoading] = useState(true);

    const handleWebSocketMessage = useCallback((message) => {
        if ([EventType.TASK_CREATED, EventType.TASK_COMPLETED, EventType.TASK_FAILED].includes(message.event_type)) {
            loadRecentTasks();
        }
    }, []);

    const { isConnected } = useWebSocket(token, {
        onMessage: handleWebSocketMessage,
        autoConnect: !!token
    });

    useEffect(() => {
        const loadInitialData = async () => {
            setIsLoading(true);
            await Promise.all([loadAgents(), loadRecentTasks(), loadPinnedProjects()]);
            setIsLoading(false);
        };
        loadInitialData();

        const interval = setInterval(() => {
            loadRecentTasks();
            loadPinnedProjects();
        }, 30000);
        return () => clearInterval(interval);
    }, []);

    const loadAgents = async () => {
        try {
            const response = await agentsAPI.list();
            setAgents(response.data);
        } catch (error) {
            console.error('Failed to load agents:', error);
        }
    };

    const loadRecentTasks = async () => {
        try {
            const response = await tasksAPI.list({ limit: 5 });
            setRecentTasks(response.data);
        } catch (error) {
            console.error('Failed to load tasks:', error);
        }
    };

    const loadPinnedProjects = async () => {
        try {
            const response = await projectsAPI.getProjects({ is_pinned: true });
            setPinnedProjects(response.data);
        } catch (error) {
            console.error('Failed to load pinned projects:', error);
        }
    };

    const handleSubmitTask = async (e) => {
        e.preventDefault();
        if (!prompt.trim()) return;

        setIsSubmitting(true);
        try {
            await tasksAPI.create({ user_prompt: prompt });
            toast.success('Task created! Processing...');
            setPrompt('');
            loadRecentTasks();
        } catch (error) {
            toast.error('Failed to create task');
        } finally {
            setIsSubmitting(false);
        }
    };

    const getStatusColor = (status) => {
        switch (status) {
            case 'completed': return 'text-green-400 bg-green-400/10 border-green-400/20';
            case 'in_progress': return 'text-yellow-400 bg-yellow-400/10 border-yellow-400/20';
            case 'failed': return 'text-red-400 bg-red-400/10 border-red-400/20';
            default: return 'text-primary-400 bg-primary-400/10 border-primary-400/20';
        }
    };

    return (
        <div className="min-h-screen bg-dark-900 selection:bg-primary-500/30">
            <Navbar />

            <div className="flex">
                <Sidebar />

                <main className="flex-1 p-6 lg:p-8">
                    <motion.div
                        variants={containerVariants}
                        initial="hidden"
                        animate="visible"
                        className="max-w-7xl mx-auto"
                    >
                        {/* Welcome Section */}
                        <motion.div variants={itemVariants} className="mb-8">
                            <div className="flex items-center gap-4 mb-3">
                                <div className="w-1.5 h-8 bg-primary-500 rounded-full shadow-[0_0_15px_rgba(14,165,233,0.5)]" />
                                <h1 className="text-4xl font-bold tracking-tight text-white">
                                    Welcome back, <span className="text-primary-400 tracking-tighter">{user?.username}</span>
                                </h1>
                                {isConnected && (
                                    <span className="flex items-center gap-2 px-3 py-1 text-[10px] font-bold uppercase tracking-widest text-green-400 bg-green-400/10 rounded-full border border-green-400/20 backdrop-blur-md">
                                        <span className="w-1.5 h-1.5 bg-green-400 rounded-full animate-ping"></span>
                                        Live Connection
                                    </span>
                                )}
                            </div>
                            <p className="text-dark-400 text-lg max-w-2xl font-medium leading-relaxed">
                                Your autonomous fleet is standby. What should we build next? 🚀
                            </p>
                        </motion.div>

                        {/* Premium Task Input */}
                        <motion.div variants={itemVariants} className="card p-1.5 mb-10 overflow-hidden relative group">
                            <div className="absolute inset-x-0 bottom-0 h-px bg-gradient-to-r from-transparent via-primary-500/50 to-transparent opacity-0 group-hover:opacity-100 transition-opacity" />
                            <form onSubmit={handleSubmitTask} className="flex gap-2">
                                <div className="flex-1 relative flex items-center">
                                    <Search className="absolute left-6 w-5 h-5 text-dark-500 group-focus-within:text-primary-400 transition-colors" />
                                    <input
                                        type="text"
                                        value={prompt}
                                        onChange={(e) => setPrompt(e.target.value)}
                                        placeholder="Command your agents... e.g., 'Draft a technical spec for the new API'"
                                        className="w-full bg-transparent border-none text-white pl-14 pr-6 py-5 focus:ring-0 text-lg placeholder:text-dark-600 font-medium"
                                    />
                                </div>
                                <button
                                    type="submit"
                                    disabled={isSubmitting || !prompt.trim()}
                                    className="btn-primary rounded-xl px-10 m-1 flex items-center gap-2 shadow-[0_10px_20px_rgba(14,165,233,0.2)] hover:shadow-[0_15px_30px_rgba(14,165,233,0.3)] disabled:opacity-30 disabled:grayscale transition-all"
                                >
                                    <Zap className={`w-5 h-5 ${isSubmitting ? 'animate-spin' : 'animate-pulse'}`} />
                                    <span className="font-bold tracking-tight">{isSubmitting ? 'Executing...' : 'Deploy'}</span>
                                </button>
                            </form>
                        </motion.div>

                        {/* Grid Row 1 */}
                        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8 mb-8">
                            {/* Quick Actions */}
                            <motion.div variants={itemVariants} className="card p-6 flex flex-col">
                                <div className="flex items-center gap-3 mb-6">
                                    <div className="p-2 bg-primary-500/10 rounded-lg">
                                        <ArrowUpRight className="w-5 h-5 text-primary-400" />
                                    </div>
                                    <h2 className="text-xl font-bold text-white tracking-tight">Quick Actions</h2>
                                </div>
                                <div className="grid grid-cols-2 gap-3 flex-1">
                                    {[
                                        { label: 'New Task', icon: Plus, path: '/tasks', color: 'bg-primary-500/10' },
                                        { label: 'Project', icon: FolderPlus, path: '/projects', color: 'bg-purple-500/10' },
                                        { label: 'Upload', icon: Upload, path: '/files', color: 'bg-blue-500/10' },
                                        { label: 'Agents', icon: Users, path: '/agents', color: 'bg-green-500/10' },
                                    ].map((action) => (
                                        <button
                                            key={action.label}
                                            onClick={() => navigate(action.path)}
                                            className="p-4 rounded-2xl bg-white/[0.02] hover:bg-white/[0.06] border border-white/5 transition-all group/action text-left"
                                        >
                                            <action.icon className="w-6 h-6 text-dark-300 group-hover/action:text-white transition-colors mb-4" />
                                            <p className="text-sm font-bold text-white leading-none">{action.label}</p>
                                        </button>
                                    ))}
                                </div>
                            </motion.div>

                            {/* Activity Feed */}
                            <motion.div variants={itemVariants} className="card p-6">
                                <div className="flex items-center justify-between mb-6">
                                    <div className="flex items-center gap-3">
                                        <div className="p-2 bg-yellow-500/10 rounded-lg">
                                            <Activity className="w-5 h-5 text-yellow-500" />
                                        </div>
                                        <h2 className="text-xl font-bold text-white tracking-tight">Intelligence Feed</h2>
                                    </div>
                                    <button onClick={() => navigate('/tasks')} className="text-xs font-bold text-primary-400 hover:text-white transition-colors">VIEW ALL</button>
                                </div>
                                <div className="space-y-4">
                                    <AnimatePresence mode="popLayout">
                                        {recentTasks.slice(0, 4).map((task) => (
                                            <motion.div
                                                layout
                                                key={task.id}
                                                className="flex items-center gap-4 group/feed cursor-pointer"
                                                onClick={() => navigate(`/tasks/${task.id}`)}
                                            >
                                                <div className={`w-1.5 h-1.5 rounded-full ${getStatusColor(task.status).split(' ')[0]} ${task.status === 'in_progress' ? 'animate-ping' : ''}`} />
                                                <div className="flex-1 min-w-0">
                                                    <p className="text-sm font-medium text-dark-100 line-clamp-1 group-hover/feed:text-white transition-colors">{task.user_prompt}</p>
                                                    <p className="text-[10px] font-bold text-dark-500 uppercase tracking-widest mt-1">
                                                        {task.status.replace('_', ' ')} • {new Date(task.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                                                    </p>
                                                </div>
                                            </motion.div>
                                        ))}
                                    </AnimatePresence>
                                    {recentTasks.length === 0 && (
                                        <div className="flex flex-col items-center justify-center py-8 opacity-30">
                                            <Sparkles className="w-8 h-8 mb-2" />
                                            <p className="text-xs font-bold uppercase tracking-widest">Awaiting Signals</p>
                                        </div>
                                    )}
                                </div>
                            </motion.div>

                            {/* System Status Container */}
                            <motion.div variants={itemVariants} className="card p-6 bg-primary-500/5 border-primary-500/10 overflow-hidden relative">
                                <div className="flex items-center gap-3 mb-6 relative z-10">
                                    <div className="p-2 bg-green-500/10 rounded-lg">
                                        <ShieldCheck className="w-5 h-5 text-green-500" />
                                    </div>
                                    <h2 className="text-xl font-bold tracking-tight">Pro Monitor</h2>
                                </div>
                                <div className="space-y-4 relative z-10">
                                    {[
                                        { label: 'Neural Backend', status: 'Optimal', icon: Database },
                                        { label: 'Redis Streams', status: 'Synced', icon: Activity },
                                        { label: 'Active Fleet', status: `${agents.length} Online`, icon: Users },
                                    ].map((stat) => (
                                        <div key={stat.label} className="flex items-center justify-between p-3 rounded-xl bg-black/5 dark:bg-white/[0.02] border border-black/5 dark:border-white/5">
                                            <div className="flex items-center gap-3">
                                                <stat.icon className="w-4 h-4 text-slate-500 dark:text-dark-400" />
                                                <span className="text-xs font-bold text-slate-700 dark:text-dark-200">{stat.label}</span>
                                            </div>
                                            <span className="text-[10px] font-black uppercase text-green-500 tracking-tighter">{stat.status}</span>
                                        </div>
                                    ))}
                                </div>
                            </motion.div>
                        </div>

                        {/* Grid Row 2: Projects & Detailed Tasks */}
                        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8">
                            <motion.div variants={itemVariants} className="card p-8">
                                <div className="flex items-center justify-between mb-8">
                                    <div className="flex items-center gap-3">
                                        <Pin className="w-6 h-6 text-primary-400 -rotate-45" />
                                        <h2 className="text-2xl font-black text-white tracking-tighter italic">Pinned Core</h2>
                                    </div>
                                    <button onClick={() => navigate('/projects')} className="bg-white/5 hover:bg-white/10 p-2 rounded-full transition-colors"><ChevronRight className="w-5 h-5 text-white" /></button>
                                </div>
                                <div className="space-y-4">
                                    {pinnedProjects.map((project) => (
                                        <div
                                            key={project.id}
                                            onClick={() => navigate(`/projects/${project.id}`)}
                                            className="group relative p-5 rounded-2xl bg-white/[0.02] border border-white/5 hover:border-primary-500/30 transition-all cursor-pointer overflow-hidden"
                                        >
                                            <div className="flex items-center justify-between mb-3">
                                                <h3 className="font-bold text-lg text-white group-hover:text-primary-400 transition-colors uppercase tracking-tight">{project.name}</h3>
                                                <Zap className="w-4 h-4 text-dark-600 group-hover:text-primary-400 transition-colors" />
                                            </div>
                                            <p className="text-sm text-dark-500 font-medium mb-5 line-clamp-1">{project.description || 'System generated core project'}</p>
                                            <div className="flex items-center gap-4">
                                                <div className="flex-1 h-1.5 bg-dark-800 rounded-full overflow-hidden">
                                                    <motion.div
                                                        initial={{ width: 0 }}
                                                        animate={{ width: `${project.progress}%` }}
                                                        className="h-full bg-gradient-to-r from-primary-500 to-primary-300 rounded-full"
                                                    />
                                                </div>
                                                <span className="text-xs font-black text-primary-400 tracking-tighter italic">{project.progress}%</span>
                                            </div>
                                        </div>
                                    ))}
                                </div>
                            </motion.div>

                            <motion.div variants={itemVariants} className="card p-8">
                                <div className="flex items-center justify-between mb-8">
                                    <h2 className="text-2xl font-black text-white tracking-tighter italic">Recent Operations</h2>
                                    <span className="text-[10px] font-bold text-dark-600 uppercase tracking-widest bg-white/5 px-2 py-1 rounded">Real-time Node</span>
                                </div>
                                <div className="space-y-3">
                                    {recentTasks.map((task) => (
                                        <div
                                            key={task.id}
                                            onClick={() => navigate(`/tasks/${task.id}`)}
                                            className="p-4 rounded-xl bg-white/[0.01] hover:bg-white/[0.04] border border-white/5 hover:border-primary-500/20 transition-all cursor-pointer group"
                                        >
                                            <div className="flex items-center justify-between mb-3">
                                                <span className={`text-[10px] font-black uppercase px-2 py-0.5 rounded-md border ${getStatusColor(task.status)}`}>
                                                    {task.status}
                                                </span>
                                                <span className="text-[10px] font-bold text-dark-500">#{task.id.slice(-6)}</span>
                                            </div>
                                            <p className="text-sm font-bold text-dark-100 group-hover:text-white transition-colors line-clamp-2">
                                                {task.user_prompt}
                                            </p>
                                        </div>
                                    ))}
                                </div>
                            </motion.div>
                        </div>

                        {/* Staggered Quick Stats */}
                        <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
                            {[
                                { label: 'Active Fleet', value: agents.length, icon: Users, color: 'text-primary-400' },
                                { label: 'Completed', value: recentTasks.filter(t => t.status === 'completed').length, icon: ShieldCheck, color: 'text-green-400' },
                                { label: 'In Execution', value: recentTasks.filter(t => t.status === 'in_progress').length, icon: Activity, color: 'text-yellow-400' },
                                { label: 'Operations', value: recentTasks.length, icon: BrainCircuit, color: 'text-blue-400' },
                            ].map((stat) => (
                                <motion.div
                                    key={stat.label}
                                    variants={itemVariants}
                                    whileHover={{ scale: 1.05, y: -5 }}
                                    className="card p-6 text-center group cursor-default"
                                >
                                    <stat.icon className={`w-8 h-8 mx-auto mb-4 ${stat.color} opacity-40 group-hover:opacity-100 transition-opacity`} />
                                    <div className={`text-3xl font-black italic tracking-tighter ${stat.color}`}>{stat.value}</div>
                                    <p className="text-[10px] uppercase font-bold tracking-widest text-dark-500 mt-2">{stat.label}</p>
                                </motion.div>
                            ))}
                        </div>
                    </motion.div>
                </main>
            </div>
        </div>
    );
}
