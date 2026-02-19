import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { agentsAPI, tasksAPI } from '../services/api';
import { motion, AnimatePresence } from 'framer-motion';
import {
    X,
    MessageSquare,
    Zap,
    BarChart3,
    CheckCircle2,
    Clock,
    TrendingUp
} from 'lucide-react';
import Navbar from '../components/layout/Navbar';
import Sidebar from '../components/layout/Sidebar';
import AgentChatModal from '../components/chat/AgentChatModal';

const containerVariants = {
    hidden: { opacity: 0 },
    visible: {
        opacity: 1,
        transition: { staggerChildren: 0.06, delayChildren: 0.1 }
    }
};

const cardVariants = {
    hidden: { y: 30, opacity: 0, scale: 0.95 },
    visible: {
        y: 0,
        opacity: 1,
        scale: 1,
        transition: { type: 'spring', stiffness: 300, damping: 24 }
    }
};

export default function Agents() {
    const navigate = useNavigate();
    const [agents, setAgents] = useState([]);
    const [tasks, setTasks] = useState([]);
    const [loading, setLoading] = useState(true);
    const [selectedAgent, setSelectedAgent] = useState(null);
    const [showModal, setShowModal] = useState(false);
    const [showChatModal, setShowChatModal] = useState(false);
    const [chatAgent, setChatAgent] = useState(null);

    const agentMeta = {
        'ResearchAgent': {
            emoji: '🔍',
            gradient: 'from-blue-500 to-cyan-500',
            glowColor: 'rgba(59, 130, 246, 0.15)',
            description: 'Expert at web research, information gathering, and fact-checking.',
            capabilities: ['Web Search', 'Source Verification', 'Topic Analysis', 'Fact Compilation']
        },
        'CodeAgent': {
            emoji: '💻',
            gradient: 'from-emerald-500 to-teal-500',
            glowColor: 'rgba(16, 185, 129, 0.15)',
            description: 'Specialized in writing, debugging, and optimizing code across languages.',
            capabilities: ['Code Generation', 'Bug Fixing', 'Refactoring', 'Testing']
        },
        'ContentAgent': {
            emoji: '✍️',
            gradient: 'from-purple-500 to-pink-500',
            glowColor: 'rgba(168, 85, 247, 0.15)',
            description: 'Master of creative writing, content creation, and documentation.',
            capabilities: ['Article Writing', 'SEO Content', 'Documentation', 'Copywriting']
        },
        'DataAgent': {
            emoji: '📊',
            gradient: 'from-orange-500 to-red-500',
            glowColor: 'rgba(249, 115, 22, 0.15)',
            description: 'Data analysis specialist with visualization capabilities.',
            capabilities: ['Data Analysis', 'Visualization', 'Statistical Modeling', 'CSV/Excel']
        },
        'QAAgent': {
            emoji: '✅',
            gradient: 'from-teal-500 to-green-500',
            glowColor: 'rgba(20, 184, 166, 0.15)',
            description: 'Quality assurance expert that validates outputs.',
            capabilities: ['Output Validation', 'Requirement Checking', 'Error Detection', 'Quality Scoring']
        },
        'MemoryAgent': {
            emoji: '🧠',
            gradient: 'from-indigo-500 to-violet-500',
            glowColor: 'rgba(99, 102, 241, 0.15)',
            description: 'Manages context and learns from interactions.',
            capabilities: ['Context Management', 'Preference Learning', 'History Recall', 'Pattern Recognition']
        },
        'ManagerAgent': {
            emoji: '🎯',
            gradient: 'from-amber-500 to-orange-500',
            glowColor: 'rgba(245, 158, 11, 0.15)',
            description: 'Orchestrates multi-agent workflows and project execution.',
            capabilities: ['Task Decomposition', 'Agent Coordination', 'Progress Tracking', 'Planning']
        },
        'VisualAgent': {
            emoji: '🎨',
            gradient: 'from-pink-500 to-rose-500',
            glowColor: 'rgba(236, 72, 153, 0.15)',
            description: 'Unified visual intelligence — analyzes images and generates artwork.',
            capabilities: ['Image Generation', 'Image Analysis', 'Style Presets', 'Scene Description']
        },
        'AudioAgent': {
            emoji: '🎵',
            gradient: 'from-red-500 to-pink-500',
            glowColor: 'rgba(239, 68, 68, 0.15)',
            description: 'Sound design and audio asset synthesis specialist.',
            capabilities: ['Sound Synthesis', 'Atmosphere Design', 'SFX Generation', 'Audio Prompting']
        }
    };

    useEffect(() => {
        loadData();
    }, []);

    const loadData = async () => {
        try {
            const [agentsRes, tasksRes] = await Promise.all([
                agentsAPI.list(),
                tasksAPI.list({ limit: 100 })
            ]);
            setAgents(agentsRes.data);
            setTasks(tasksRes.data);
        } catch (error) {
            console.error('Failed to load data:', error);
        } finally {
            setLoading(false);
        }
    };

    const getAgentStats = (agentName) => {
        const agentTasks = tasks.filter(t =>
            t.subtasks?.some(st => st.agent_name === agentName) ||
            t.assigned_agent === agentName
        );
        const completed = agentTasks.filter(t => t.status === 'completed').length;
        const total = agentTasks.length;
        const successRate = total > 0 ? Math.round((completed / total) * 100) : 100;
        return { total, completed, successRate };
    };

    const handleAgentClick = (agent) => {
        setSelectedAgent(agent);
        setShowModal(true);
    };

    return (
        <div className="min-h-screen selection:bg-primary-500/30">
            <Navbar />
            <div className="flex">
                <Sidebar />
                <main className="flex-1 p-6 lg:p-8">
                    {/* Header */}
                    <motion.div
                        initial={{ opacity: 0, y: -20 }}
                        animate={{ opacity: 1, y: 0 }}
                        className="mb-8"
                    >
                        <div className="flex items-center gap-3 mb-2">
                            <motion.span
                                className="text-3xl"
                                animate={{ rotate: [0, 10, -5, 0] }}
                                transition={{ duration: 1.5, delay: 0.3 }}
                            >
                                🤖
                            </motion.span>
                            <h1 className="text-3xl font-black text-white tracking-tight">
                                AI <span className="gradient-text-vivid">Agents</span>
                            </h1>
                        </div>
                        <p className="text-dark-400 text-sm font-medium">
                            Your specialized AI fleet · <span className="stat-number text-dark-300">{agents.length}</span> agents deployed
                        </p>
                        <div className="h-px mt-4 bg-gradient-to-r from-transparent via-primary-500/30 to-transparent" />
                    </motion.div>

                    {/* Agent Grid */}
                    {loading ? (
                        <div className="flex items-center justify-center py-20">
                            <motion.div
                                className="w-10 h-10 border-2 border-primary-500 border-t-transparent rounded-full"
                                animate={{ rotate: 360 }}
                                transition={{ duration: 1, repeat: Infinity, ease: 'linear' }}
                            />
                        </div>
                    ) : (
                        <motion.div
                            variants={containerVariants}
                            initial="hidden"
                            animate="visible"
                            className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-5"
                        >
                            {agents.map((agent) => {
                                const meta = agentMeta[agent.name] || {
                                    emoji: '🤖',
                                    gradient: 'from-gray-500 to-gray-600',
                                    glowColor: 'rgba(107, 114, 128, 0.15)',
                                    description: agent.description || 'AI Agent',
                                    capabilities: []
                                };
                                const stats = getAgentStats(agent.name);

                                return (
                                    <motion.div
                                        key={agent.id}
                                        variants={cardVariants}
                                        onClick={() => handleAgentClick(agent)}
                                        className="card-interactive p-5 group overflow-hidden relative holo-shimmer"
                                        whileHover={{ y: -6, scale: 1.02 }}
                                        whileTap={{ scale: 0.98 }}
                                    >
                                        {/* Gradient background on hover */}
                                        <div
                                            className="absolute inset-0 opacity-0 group-hover:opacity-100 transition-opacity duration-500 pointer-events-none"
                                            style={{ background: `radial-gradient(ellipse at top left, ${meta.glowColor}, transparent 70%)` }}
                                        />

                                        <div className="relative z-10">
                                            {/* Agent Icon with gradient border */}
                                            <div className="relative mb-4">
                                                <div className={`w-14 h-14 rounded-2xl bg-gradient-to-br ${meta.gradient} p-[1px] group-hover:shadow-lg transition-shadow duration-300`}
                                                    style={{ boxShadow: `0 0 0 0 ${meta.glowColor}` }}
                                                >
                                                    <div className="w-full h-full rounded-2xl bg-dark-900/90 flex items-center justify-center backdrop-blur">
                                                        <span className="text-3xl">{meta.emoji}</span>
                                                    </div>
                                                </div>

                                                {/* Status dot - using new CSS status-dot classes */}
                                                <div className="absolute -bottom-1 -right-1 border-2 border-dark-900 rounded-full">
                                                    <span className={`status-dot ${agent.is_active ? 'status-dot-active' : 'status-dot-offline'}`} />
                                                </div>
                                            </div>

                                            {/* Name & Description */}
                                            <h3 className="text-base font-bold text-white mb-1 group-hover:text-primary-400 transition-colors">
                                                {agent.name.replace('Agent', ' Agent')}
                                            </h3>
                                            <p className="text-dark-500 text-xs leading-relaxed mb-3 line-clamp-2">
                                                {meta.description}
                                            </p>

                                            {/* Capability Tags */}
                                            <div className="flex flex-wrap gap-1.5 mb-4">
                                                {meta.capabilities.slice(0, 3).map((cap, i) => (
                                                    <span
                                                        key={i}
                                                        className="text-[10px] font-semibold px-2 py-0.5 rounded-full bg-white/[0.04] border border-white/[0.06] text-dark-400 group-hover:text-dark-200 group-hover:border-white/10 transition-colors"
                                                    >
                                                        {cap}
                                                    </span>
                                                ))}
                                                {meta.capabilities.length > 3 && (
                                                    <span className="text-[10px] font-semibold px-2 py-0.5 rounded-full bg-white/[0.04] text-dark-600">
                                                        +{meta.capabilities.length - 3}
                                                    </span>
                                                )}
                                            </div>

                                            {/* Stats Row */}
                                            <div className="flex items-center justify-between text-xs">
                                                <div className="flex items-center gap-1 text-dark-500">
                                                    <BarChart3 className="w-3 h-3" />
                                                    <span className="stat-number">{stats.total} tasks</span>
                                                </div>
                                                <span className={`font-bold stat-number ${stats.successRate >= 90 ? 'text-emerald-400' : stats.successRate >= 70 ? 'text-amber-400' : 'text-red-400'}`}>
                                                    {stats.successRate}%
                                                </span>
                                            </div>
                                        </div>
                                    </motion.div>
                                );
                            })}
                        </motion.div>
                    )}

                    {/* Summary Stats */}
                    <motion.div
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ delay: 0.4 }}
                        className="mt-8 grid grid-cols-2 md:grid-cols-4 gap-4"
                    >
                        {[
                            { label: 'Total Agents', value: agents.length, icon: Zap, color: 'gradient-text-vivid' },
                            { label: 'Active', value: agents.filter(a => a.is_active).length, icon: CheckCircle2, color: 'text-emerald-400' },
                            { label: 'Total Tasks', value: tasks.length, icon: Clock, color: 'text-blue-400' },
                            { label: 'Completed', value: tasks.filter(t => t.status === 'completed').length, icon: TrendingUp, color: 'text-purple-400' },
                        ].map((stat) => (
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
                </main>
            </div>

            {/* Agent Detail Modal */}
            <AnimatePresence>
                {showModal && selectedAgent && (
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
                            className="glass rounded-2xl border border-white/[0.08] w-full max-w-2xl max-h-[80vh] overflow-hidden shadow-2xl"
                            onClick={(e) => e.stopPropagation()}
                        >
                            {/* Modal Header */}
                            <div className="p-6 border-b border-white/[0.06]">
                                <div className="flex items-center justify-between">
                                    <div className="flex items-center gap-4">
                                        <div className={`w-14 h-14 rounded-2xl bg-gradient-to-br ${agentMeta[selectedAgent.name]?.gradient || 'from-gray-500 to-gray-600'} p-[1px]`}>
                                            <div className="w-full h-full rounded-2xl bg-dark-900/90 flex items-center justify-center">
                                                <span className="text-3xl">{agentMeta[selectedAgent.name]?.emoji || '🤖'}</span>
                                            </div>
                                        </div>
                                        <div>
                                            <h2 className="text-xl font-bold text-white">
                                                {selectedAgent.name.replace('Agent', ' Agent')}
                                            </h2>
                                            <div className="flex items-center gap-2 mt-1">
                                                <span className={`w-2 h-2 rounded-full ${selectedAgent.is_active ? 'bg-emerald-400 animate-pulse' : 'bg-red-400'}`}
                                                    style={selectedAgent.is_active ? { boxShadow: '0 0 6px rgba(52, 211, 153, 0.5)' } : {}}
                                                />
                                                <span className={`text-xs font-semibold ${selectedAgent.is_active ? 'text-emerald-400' : 'text-red-400'}`}>
                                                    {selectedAgent.is_active ? 'Active' : 'Inactive'}
                                                </span>
                                            </div>
                                        </div>
                                    </div>
                                    <motion.button
                                        onClick={() => setShowModal(false)}
                                        className="p-2 text-dark-400 hover:text-white hover:bg-white/[0.05] rounded-xl transition-all"
                                        whileHover={{ scale: 1.1 }}
                                        whileTap={{ scale: 0.9 }}
                                    >
                                        <X className="w-5 h-5" />
                                    </motion.button>
                                </div>
                            </div>

                            {/* Modal Body */}
                            <div className="p-6 overflow-y-auto max-h-[50vh]">
                                <div className="mb-6">
                                    <h3 className="text-[10px] uppercase tracking-[0.15em] font-bold text-dark-600 mb-2">Description</h3>
                                    <p className="text-dark-200 text-sm leading-relaxed">
                                        {agentMeta[selectedAgent.name]?.description || selectedAgent.description}
                                    </p>
                                </div>

                                <div className="mb-6">
                                    <h3 className="text-[10px] uppercase tracking-[0.15em] font-bold text-dark-600 mb-2">Capabilities</h3>
                                    <div className="flex flex-wrap gap-2">
                                        {(agentMeta[selectedAgent.name]?.capabilities || []).map((cap, i) => (
                                            <motion.span
                                                key={i}
                                                initial={{ opacity: 0, scale: 0.8 }}
                                                animate={{ opacity: 1, scale: 1 }}
                                                transition={{ delay: i * 0.04 }}
                                                className={`px-3 py-1.5 rounded-full text-xs font-semibold bg-gradient-to-r ${agentMeta[selectedAgent.name]?.gradient || 'from-gray-500 to-gray-600'} bg-opacity-10 text-white border border-white/[0.06]`}
                                                style={{
                                                    background: `linear-gradient(135deg, ${agentMeta[selectedAgent.name]?.glowColor || 'rgba(107,114,128,0.15)'}, transparent)`
                                                }}
                                            >
                                                {cap}
                                            </motion.span>
                                        ))}
                                    </div>
                                </div>

                                <div>
                                    <h3 className="text-[10px] uppercase tracking-[0.15em] font-bold text-dark-600 mb-2">Performance</h3>
                                    <div className="grid grid-cols-3 gap-3">
                                        {(() => {
                                            const stats = getAgentStats(selectedAgent.name);
                                            return (
                                                <>
                                                    <div className="p-4 rounded-xl bg-white/[0.02] border border-white/[0.04] text-center">
                                                        <div className="text-2xl font-black text-white tabular-nums">{stats.total}</div>
                                                        <p className="text-dark-500 text-[10px] uppercase tracking-widest font-bold mt-1">Tasks</p>
                                                    </div>
                                                    <div className="p-4 rounded-xl bg-white/[0.02] border border-white/[0.04] text-center">
                                                        <div className="text-2xl font-black text-emerald-400 tabular-nums">{stats.completed}</div>
                                                        <p className="text-dark-500 text-[10px] uppercase tracking-widest font-bold mt-1">Completed</p>
                                                    </div>
                                                    <div className="p-4 rounded-xl bg-white/[0.02] border border-white/[0.04] text-center">
                                                        <div className="text-2xl font-black text-primary-400 tabular-nums">{stats.successRate}%</div>
                                                        <p className="text-dark-500 text-[10px] uppercase tracking-widest font-bold mt-1">Success</p>
                                                    </div>
                                                </>
                                            );
                                        })()}
                                    </div>
                                </div>
                            </div>

                            {/* Modal Footer */}
                            <div className="p-5 border-t border-white/[0.06] flex justify-end gap-3">
                                {['ResearchAgent', 'CodeAgent', 'ContentAgent', 'VisualAgent', 'AudioAgent'].includes(selectedAgent.name) && (
                                    <motion.button
                                        onClick={() => {
                                            setChatAgent(selectedAgent);
                                            setShowModal(false);
                                            setShowChatModal(true);
                                        }}
                                        className="px-5 py-2.5 bg-gradient-to-r from-purple-500 to-pink-500 text-white rounded-xl font-semibold text-sm flex items-center gap-2 hover:shadow-lg hover:shadow-purple-500/20 transition-all"
                                        whileHover={{ scale: 1.03 }}
                                        whileTap={{ scale: 0.97 }}
                                    >
                                        <MessageSquare className="w-4 h-4" />
                                        Direct Chat
                                    </motion.button>
                                )}
                                <motion.button
                                    onClick={() => {
                                        setShowModal(false);
                                        navigate('/dashboard');
                                    }}
                                    className="btn-primary text-sm"
                                    whileHover={{ scale: 1.03 }}
                                    whileTap={{ scale: 0.97 }}
                                >
                                    Use Agent
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

            <AgentChatModal
                isOpen={showChatModal}
                onClose={() => setShowChatModal(false)}
                agent={chatAgent}
            />
        </div>
    );
}
