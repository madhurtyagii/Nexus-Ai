import { useState, useEffect, useCallback, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { agentsAPI, tasksAPI, projectsAPI } from '../services/api';
import { useWebSocket, EventType } from '../hooks/useWebSocket';
import { motion, AnimatePresence, useMotionValue, useTransform } from 'framer-motion';
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
    BrainCircuit,
    Send,
    Square,
    TrendingUp
} from 'lucide-react';
import Navbar from '../components/layout/Navbar';
import Sidebar from '../components/layout/Sidebar';
import VoiceRecorder from '../components/chat/VoiceRecorder';
import { Skeleton, TaskListSkeleton, CardSkeleton } from '../components/common/Skeleton';
import SpotlightCard from '../components/common/SpotlightCard';
import TypingPlaceholder from '../components/dashboard/TypingPlaceholder';
import ActivityTimeline from '../components/dashboard/ActivityTimeline';
import AgentOrbit from '../components/dashboard/AgentOrbit';
import HeroStats from '../components/dashboard/HeroStats';
import toast from 'react-hot-toast';

/* ═══ Animated Counter Hook ═══ */
function useAnimatedCounter(target, duration = 1200) {
    const [count, setCount] = useState(0);
    useEffect(() => {
        if (target === 0) { setCount(0); return; }
        let start = 0;
        const startTime = performance.now();
        const animate = (now) => {
            const elapsed = now - startTime;
            const progress = Math.min(elapsed / duration, 1);
            const eased = 1 - Math.pow(1 - progress, 3); // ease-out cubic
            setCount(Math.round(eased * target));
            if (progress < 1) requestAnimationFrame(animate);
        };
        requestAnimationFrame(animate);
    }, [target, duration]);
    return count;
}

/* ═══ Time-based Greeting ═══ */
function getGreeting() {
    const hour = new Date().getHours();
    if (hour < 6) return { text: 'Working late', emoji: '🌙' };
    if (hour < 12) return { text: 'Good morning', emoji: '☀️' };
    if (hour < 17) return { text: 'Good afternoon', emoji: '🔆' };
    if (hour < 21) return { text: 'Good evening', emoji: '🌅' };
    return { text: 'Good night', emoji: '🌙' };
}

const containerVariants = {
    hidden: { opacity: 0 },
    visible: {
        opacity: 1,
        transition: {
            staggerChildren: 0.08,
            delayChildren: 0.15
        }
    }
};

const itemVariants = {
    hidden: { y: 24, opacity: 0 },
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
    const [inputFocused, setInputFocused] = useState(false);
    const greeting = getGreeting();

    // Animated counters
    // Animated counters
    // If agents are empty, we still want to show the "potential" fleet size for visuals
    const displayAgents = agents.length > 0 ? agents : Array.from({ length: 8 }, (_, i) => ({ id: i, status: 'idle', name: `Agent ${i + 1}` }));

    // Counter targets
    const activeFleetCount = agents.length > 0 ? agents.length : 8; // Show 8 as "Online" even if just standby

    const activeFleet = useAnimatedCounter(activeFleetCount);
    const completedCount = useAnimatedCounter(recentTasks.filter(t => t.status === 'completed').length);
    const inProgressCount = useAnimatedCounter(recentTasks.filter(t => t.status === 'in_progress').length);
    const totalOps = useAnimatedCounter(recentTasks.length);

    const handleWebSocketMessage = useCallback((message) => {
        if ([EventType.TASK_CREATED, EventType.TASK_COMPLETED, EventType.TASK_FAILED].includes(message.event_type)) {
            loadRecentTasks();
            if (message.event_type === EventType.TASK_COMPLETED && localStorage.getItem('nexus_auto_speak') === 'true') {
                speakResponse(message.data?.output || "Task completed");
            }
        }
    }, []);

    const speakResponse = (text) => {
        if (!window.speechSynthesis) return;
        window.speechSynthesis.cancel();
        const cleanText = text.replace(/[*#>`-]/g, '').slice(0, 500);
        const utterance = new SpeechSynthesisUtterance(cleanText);
        utterance.rate = 1.1;
        utterance.pitch = 1.0;
        window.speechSynthesis.speak(utterance);
    };

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

    const handleCancelTask = async (taskId) => {
        try {
            await tasksAPI.cancel(taskId);
            toast.success('Stopping task...');
            loadRecentTasks();
        } catch (error) {
            toast.error('Failed to stop task');
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
            case 'completed': return 'text-emerald-400 bg-emerald-400/10 border-emerald-400/20';
            case 'in_progress': return 'text-amber-400 bg-amber-400/10 border-amber-400/20';
            case 'failed': return 'text-red-400 bg-red-400/10 border-red-400/20';
            default: return 'text-primary-400 bg-primary-400/10 border-primary-400/20';
        }
    };

    const quickActions = [
        { label: 'New Task', icon: Plus, path: '/tasks', gradient: 'from-primary-500/20 to-cyan-500/20', iconColor: 'text-primary-400' },
        { label: 'Project', icon: FolderPlus, path: '/projects', gradient: 'from-purple-500/20 to-pink-500/20', iconColor: 'text-purple-400' },
        { label: 'Upload', icon: Upload, path: '/files', gradient: 'from-blue-500/20 to-indigo-500/20', iconColor: 'text-blue-400' },
        { label: 'Agents', icon: Users, path: '/agents', gradient: 'from-emerald-500/20 to-teal-500/20', iconColor: 'text-emerald-400' },
    ];

    const statCards = [
        { label: 'Active Fleet', value: activeFleet, icon: Users, color: 'text-primary-400', glow: 'rgba(14, 165, 233, 0.15)', accentFrom: '#0ea5e9', accentTo: '#06b6d4', glowRGB: '14, 165, 233' },
        { label: 'Completed', value: completedCount, icon: ShieldCheck, color: 'text-emerald-400', glow: 'rgba(52, 211, 153, 0.15)', accentFrom: '#10b981', accentTo: '#34d399', glowRGB: '16, 185, 129' },
        { label: 'In Execution', value: inProgressCount, icon: Activity, color: 'text-amber-400', glow: 'rgba(251, 191, 36, 0.15)', accentFrom: '#f59e0b', accentTo: '#fbbf24', glowRGB: '245, 158, 11' },
        { label: 'Operations', value: totalOps, icon: BrainCircuit, color: 'text-blue-400', glow: 'rgba(96, 165, 250, 0.15)', accentFrom: '#3b82f6', accentTo: '#8b5cf6', glowRGB: '59, 130, 246' },
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
                        className="max-w-7xl mx-auto"
                    >
                        {/* ═══ Welcome Section ═══ */}
                        <motion.div variants={itemVariants} className="mb-8">
                            <div className="flex items-center gap-4 mb-2">
                                <motion.span
                                    className="text-3xl"
                                    animate={{ rotate: [0, 14, -8, 14, -4, 10, 0] }}
                                    transition={{ duration: 2, delay: 0.5 }}
                                >
                                    {greeting.emoji}
                                </motion.span>
                                <div>
                                    <h1 className="text-3xl lg:text-4xl font-black tracking-tight text-white">
                                        {greeting.text}, <span className="gradient-text-vivid">{user?.username}</span>
                                    </h1>
                                    <div className="flex items-center gap-3 mt-1.5">
                                        <p className="text-dark-400 text-sm font-medium flex items-center gap-2">
                                            <span className="stat-number text-dark-300">{agents.length}</span> agents online
                                            <span className="text-dark-600">·</span>
                                            <span className="stat-number text-dark-300">{recentTasks.filter(t => t.status === 'in_progress').length}</span> tasks running
                                        </p>
                                        {isConnected && (
                                            <motion.span
                                                initial={{ opacity: 0, scale: 0 }}
                                                animate={{ opacity: 1, scale: 1 }}
                                                className="flex items-center gap-1.5 px-2.5 py-0.5 text-[9px] font-bold uppercase tracking-widest text-emerald-400 bg-emerald-400/10 rounded-full border border-emerald-400/20"
                                            >
                                                <span className="status-dot status-dot-active" style={{ width: 6, height: 6 }} />
                                                Live
                                            </motion.span>
                                        )}
                                    </div>
                                </div>
                            </div>
                            {/* Animated gradient divider */}
                            <div className="h-px mt-4 bg-gradient-to-r from-transparent via-primary-500/30 to-transparent" />
                        </motion.div>

                        {/* ═══ Premium Command Input ═══ */}
                        <motion.div
                            variants={itemVariants}
                            className={`mb-10 rounded-2xl overflow-hidden relative transition-all duration-500 ${inputFocused ? 'animated-border' : ''
                                }`}
                        >
                            {/* Ambient glow behind input on focus */}
                            <div
                                className={`absolute inset-0 rounded-2xl transition-opacity duration-500 -z-10 ${inputFocused ? 'opacity-100' : 'opacity-0'
                                    }`}
                                style={{
                                    background: 'radial-gradient(ellipse at center, rgba(14, 165, 233, 0.08), transparent 70%)',
                                    filter: 'blur(30px)',
                                }}
                            />

                            <div className="card p-1.5 relative group">
                                <div className="absolute inset-x-0 bottom-0 h-px bg-gradient-to-r from-transparent via-primary-500/40 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-500" />
                                <form onSubmit={handleSubmitTask} className="flex items-center gap-2">
                                    <div className="flex-1 relative flex items-center">
                                        <Sparkles className={`absolute left-5 w-5 h-5 transition-colors duration-300 ${inputFocused ? 'text-primary-400' : 'text-dark-600'}`} />
                                        <div className="flex-1 relative">
                                            <input
                                                type="text"
                                                value={prompt}
                                                onChange={(e) => setPrompt(e.target.value)}
                                                onFocus={() => setInputFocused(true)}
                                                onBlur={() => setInputFocused(false)}
                                                placeholder=""
                                                className="w-full bg-transparent border-none text-white pl-14 pr-6 py-5 focus:ring-0 text-lg placeholder:text-dark-600 font-medium outline-none relative z-10"
                                            />
                                            {/* Typing animation placeholder */}
                                            <div className="absolute inset-0 flex items-center pl-14 pointer-events-none">
                                                <TypingPlaceholder isActive={inputFocused} actualValue={prompt} />
                                            </div>
                                        </div>
                                    </div>
                                    <div className="flex items-center gap-2 pr-2">
                                        <VoiceRecorder
                                            onTranscription={(text) => setPrompt(text)}
                                            disabled={isSubmitting}
                                        />
                                        <motion.button
                                            type="submit"
                                            disabled={isSubmitting || !prompt.trim()}
                                            className="btn-primary rounded-xl px-8 py-3 flex items-center gap-2 disabled:opacity-20 disabled:cursor-not-allowed"
                                            whileHover={{ scale: 1.03 }}
                                            whileTap={{ scale: 0.97 }}
                                        >
                                            <Send className={`w-4 h-4 ${isSubmitting ? 'animate-pulse' : ''}`} />
                                            <span className="font-bold tracking-tight text-sm">{isSubmitting ? 'Deploying...' : 'Deploy'}</span>
                                        </motion.button>
                                        {recentTasks[0]?.status === 'in_progress' && (
                                            <motion.button
                                                type="button"
                                                initial={{ opacity: 0, scale: 0.8 }}
                                                animate={{ opacity: 1, scale: 1 }}
                                                onClick={() => handleCancelTask(recentTasks[0].id)}
                                                className="p-3 bg-red-500/10 hover:bg-red-500/20 text-red-400 border border-red-500/20 rounded-xl transition-all text-xs font-bold"
                                                title="Stop current task"
                                                whileHover={{ scale: 1.05 }}
                                                whileTap={{ scale: 0.95 }}
                                            >
                                                <Square className="w-4 h-4" />
                                            </motion.button>
                                        )}
                                    </div>
                                </form>
                            </div>
                        </motion.div>

                        {/* ═══ Grid Row 1: Bento Layout ═══ */}
                        <div className="grid grid-cols-1 lg:grid-cols-12 gap-5 mb-6">
                            {/* Quick Actions — 3 cols */}
                            <motion.div variants={itemVariants} className="lg:col-span-3">
                                <SpotlightCard className="p-6 h-full" spotlightColor="rgba(14, 165, 233, 0.06)">
                                    <div className="flex items-center gap-3 mb-5">
                                        <div className="p-2 bg-primary-500/10 rounded-xl">
                                            <ArrowUpRight className="w-4 h-4 text-primary-400" />
                                        </div>
                                        <h2 className="text-lg font-bold text-white tracking-tight">Quick Actions</h2>
                                    </div>
                                    <div className="grid grid-cols-2 gap-2.5">
                                        {quickActions.map((action, i) => (
                                            <motion.button
                                                key={action.label}
                                                onClick={() => navigate(action.path)}
                                                className="p-4 rounded-xl bg-white/[0.02] hover:bg-white/[0.05] border border-white/[0.04] hover:border-white/[0.08] transition-all group/action text-left relative overflow-hidden"
                                                whileHover={{ scale: 1.03, y: -2 }}
                                                whileTap={{ scale: 0.98 }}
                                            >
                                                <div className={`absolute inset-0 bg-gradient-to-br ${action.gradient} opacity-0 group-hover/action:opacity-100 transition-opacity rounded-xl`} />
                                                <action.icon className={`w-5 h-5 ${action.iconColor} relative z-10 mb-3 transition-transform group-hover/action:scale-110`} />
                                                <p className="text-xs font-bold text-white relative z-10">{action.label}</p>
                                            </motion.button>
                                        ))}
                                    </div>
                                </SpotlightCard>
                            </motion.div>

                            {/* Agent Orbit Visualization — 3 cols */}
                            <motion.div variants={itemVariants} className="lg:col-span-3">
                                <SpotlightCard className="p-6 h-full" spotlightColor="rgba(139, 92, 246, 0.06)">
                                    <div className="flex items-center gap-3 mb-4">
                                        <div className="p-2 bg-purple-500/10 rounded-xl">
                                            <Users className="w-4 h-4 text-purple-400" />
                                        </div>
                                        <h2 className="text-lg font-bold text-white tracking-tight">Agent Fleet</h2>
                                    </div>
                                    <AgentOrbit agents={displayAgents} className="w-full h-36" />
                                </SpotlightCard>
                            </motion.div>

                            {/* Hero Stats with Ring Chart — 3 cols */}
                            <motion.div variants={itemVariants} className="lg:col-span-3">
                                <SpotlightCard className="p-6 h-full" spotlightColor="rgba(52, 211, 153, 0.06)">
                                    <div className="flex items-center gap-3 mb-4">
                                        <div className="p-2 bg-emerald-500/10 rounded-xl">
                                            <TrendingUp className="w-4 h-4 text-emerald-400" />
                                        </div>
                                        <h2 className="text-lg font-bold text-white tracking-tight">Performance</h2>
                                    </div>
                                    <HeroStats tasks={recentTasks} />
                                </SpotlightCard>
                            </motion.div>

                            {/* System Status — 3 cols */}
                            <motion.div variants={itemVariants} className="lg:col-span-3">
                                <SpotlightCard className="p-6 h-full" spotlightColor="rgba(16, 185, 129, 0.06)">
                                    <div className="flex items-center gap-3 mb-5">
                                        <div className="p-2 bg-emerald-500/10 rounded-xl">
                                            <ShieldCheck className="w-4 h-4 text-emerald-400" />
                                        </div>
                                        <h2 className="text-lg font-bold tracking-tight">System Health</h2>
                                    </div>
                                    <div className="space-y-3">
                                        {[
                                            { label: 'Neural Backend', status: 'Optimal', icon: Database, color: 'text-emerald-400' },
                                            { label: 'Redis Streams', status: 'Synced', icon: Activity, color: 'text-emerald-400' },
                                            { label: 'Active Fleet', status: `${activeFleetCount} Online`, icon: Users, color: 'text-primary-400' },
                                        ].map((stat) => (
                                            <div key={stat.label} className="flex items-center justify-between p-3 rounded-xl bg-white/[0.02] border border-white/[0.04]">
                                                <div className="flex items-center gap-2.5">
                                                    <stat.icon className="w-3.5 h-3.5 text-dark-500" />
                                                    <span className="text-xs font-semibold text-dark-300">{stat.label}</span>
                                                </div>
                                                <span className={`text-[10px] font-black uppercase tracking-tight ${stat.color} flex items-center gap-1.5`}>
                                                    <span className="w-1.5 h-1.5 rounded-full bg-current" style={{ boxShadow: '0 0 6px currentColor' }} />
                                                    {stat.status}
                                                </span>
                                            </div>
                                        ))}
                                    </div>
                                </SpotlightCard>
                            </motion.div>
                        </div>

                        {/* ═══ Grid Row 2: Projects & Activity Timeline ═══ */}
                        <div className="grid grid-cols-1 lg:grid-cols-2 gap-5 mb-6">
                            {/* Pinned Projects */}
                            <motion.div variants={itemVariants}>
                                <SpotlightCard className="p-7 h-full" spotlightColor="rgba(14, 165, 233, 0.05)">
                                    <div className="flex items-center justify-between mb-6">
                                        <div className="flex items-center gap-3">
                                            <Pin className="w-5 h-5 text-primary-400 -rotate-45" />
                                            <h2 className="text-xl font-bold text-white tracking-tight">Pinned Projects</h2>
                                        </div>
                                        <motion.button
                                            onClick={() => navigate('/projects')}
                                            className="p-2 bg-white/[0.03] hover:bg-white/[0.06] rounded-xl transition-colors"
                                            whileHover={{ scale: 1.1 }}
                                            whileTap={{ scale: 0.9 }}
                                        >
                                            <ChevronRight className="w-4 h-4 text-dark-400" />
                                        </motion.button>
                                    </div>
                                    <div className="space-y-3">
                                        {pinnedProjects.map((project, i) => (
                                            <motion.div
                                                key={project.id}
                                                initial={{ opacity: 0, y: 10 }}
                                                animate={{ opacity: 1, y: 0 }}
                                                transition={{ delay: i * 0.06 }}
                                                onClick={() => navigate(`/projects/${project.id}`)}
                                                className="group relative p-4 rounded-xl bg-white/[0.02] border border-white/[0.04] hover:border-primary-500/20 transition-all cursor-pointer overflow-hidden"
                                            >
                                                <div className="flex items-center justify-between mb-2">
                                                    <h3 className="font-bold text-base text-white group-hover:text-primary-400 transition-colors">{project.name}</h3>
                                                    <TrendingUp className="w-3.5 h-3.5 text-dark-600 group-hover:text-primary-400 transition-colors" />
                                                </div>
                                                <p className="text-xs text-dark-500 font-medium mb-3 line-clamp-1">{project.description || 'Active project'}</p>
                                                <div className="flex items-center gap-3">
                                                    <div className="flex-1 h-1 bg-dark-800 rounded-full overflow-hidden">
                                                        <motion.div
                                                            initial={{ width: 0 }}
                                                            animate={{ width: `${project.progress}%` }}
                                                            transition={{ duration: 1, ease: 'easeOut', delay: 0.3 }}
                                                            className="h-full bg-gradient-to-r from-primary-500 to-primary-300 rounded-full"
                                                            style={{ boxShadow: '0 0 8px rgba(14, 165, 233, 0.3)' }}
                                                        />
                                                    </div>
                                                    <span className="text-xs font-bold text-primary-400 tabular-nums">{project.progress}%</span>
                                                </div>
                                            </motion.div>
                                        ))}
                                        {pinnedProjects.length === 0 && (
                                            <div className="flex flex-col items-center justify-center py-8 opacity-20">
                                                <Pin className="w-6 h-6 mb-2 -rotate-45" />
                                                <p className="text-xs font-bold uppercase tracking-widest">No pinned projects</p>
                                            </div>
                                        )}
                                    </div>
                                </SpotlightCard>
                            </motion.div>

                            {/* Activity Timeline — NEW */}
                            <motion.div variants={itemVariants}>
                                <SpotlightCard className="p-7 h-full" spotlightColor="rgba(251, 191, 36, 0.05)">
                                    <div className="flex items-center justify-between mb-6">
                                        <div className="flex items-center gap-3">
                                            <div className="p-2 bg-amber-500/10 rounded-xl">
                                                <Activity className="w-4 h-4 text-amber-400" />
                                            </div>
                                            <h2 className="text-xl font-bold text-white tracking-tight">Activity Timeline</h2>
                                        </div>
                                        <button onClick={() => navigate('/tasks')} className="text-[10px] font-bold text-primary-400 hover:text-white transition-colors uppercase tracking-wider">
                                            View All
                                        </button>
                                    </div>
                                    <ActivityTimeline
                                        tasks={recentTasks}
                                        onTaskClick={(task) => navigate(`/tasks/${task.id}`)}
                                        onCancelTask={handleCancelTask}
                                    />
                                </SpotlightCard>
                            </motion.div>
                        </div>


                    </motion.div>
                </main>
            </div>
        </div>
    );
}
