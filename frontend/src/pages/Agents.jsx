import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { agentsAPI, tasksAPI } from '../services/api';
import Navbar from '../components/layout/Navbar';
import Sidebar from '../components/layout/Sidebar';
import AgentChatModal from '../components/chat/AgentChatModal';

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
            color: 'from-blue-500 to-cyan-500',
            borderColor: 'border-blue-500/30',
            bgColor: 'bg-blue-500/10',
            description: 'Expert at web research, information gathering, and fact-checking. Searches the web and compiles comprehensive summaries.',
            capabilities: ['Web Search', 'Source Verification', 'Topic Analysis', 'Fact Compilation']
        },
        'CodeAgent': {
            emoji: '💻',
            color: 'from-green-500 to-emerald-500',
            borderColor: 'border-green-500/30',
            bgColor: 'bg-green-500/10',
            description: 'Specialized in writing, debugging, and optimizing code across multiple programming languages.',
            capabilities: ['Code Generation', 'Bug Fixing', 'Refactoring', 'Testing']
        },
        'ContentAgent': {
            emoji: '✍️',
            color: 'from-purple-500 to-pink-500',
            borderColor: 'border-purple-500/30',
            bgColor: 'bg-purple-500/10',
            description: 'Master of creative writing, content creation, and professional documentation.',
            capabilities: ['Article Writing', 'SEO Content', 'Documentation', 'Copywriting']
        },
        'DataAgent': {
            emoji: '📊',
            color: 'from-orange-500 to-red-500',
            borderColor: 'border-orange-500/30',
            bgColor: 'bg-orange-500/10',
            description: 'Data analysis specialist capable of processing datasets and creating visualizations.',
            capabilities: ['Data Analysis', 'Visualization', 'Statistical Modeling', 'CSV/Excel Processing']
        },
        'QAAgent': {
            emoji: '✅',
            color: 'from-teal-500 to-green-500',
            borderColor: 'border-teal-500/30',
            bgColor: 'bg-teal-500/10',
            description: 'Quality assurance expert that validates outputs and ensures requirements are met.',
            capabilities: ['Output Validation', 'Requirement Checking', 'Error Detection', 'Quality Scoring']
        },
        'MemoryAgent': {
            emoji: '🧠',
            color: 'from-indigo-500 to-violet-500',
            borderColor: 'border-indigo-500/30',
            bgColor: 'bg-indigo-500/10',
            description: 'Manages context and learns from previous interactions to improve future responses.',
            capabilities: ['Context Management', 'Preference Learning', 'History Recall', 'Pattern Recognition']
        },
        'ManagerAgent': {
            emoji: '🎯',
            color: 'from-yellow-500 to-orange-500',
            borderColor: 'border-yellow-500/30',
            bgColor: 'bg-yellow-500/10',
            description: 'Orchestrates complex multi-agent workflows and coordinates project execution.',
            capabilities: ['Task Decomposition', 'Agent Coordination', 'Progress Tracking', 'Project Planning']
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
        <div className="min-h-screen bg-dark-900">
            <Navbar />
            <div className="flex">
                <Sidebar />
                <main className="flex-1 p-6 lg:p-8">
                    {/* Header */}
                    <div className="mb-8">
                        <h1 className="text-3xl font-bold text-white mb-2">🤖 AI Agents</h1>
                        <p className="text-dark-400">Meet your specialized AI team. Each agent has unique capabilities.</p>
                    </div>

                    {/* Agent Grid */}
                    {loading ? (
                        <div className="text-center py-12">
                            <div className="animate-spin w-8 h-8 border-2 border-primary-500 border-t-transparent rounded-full mx-auto mb-4"></div>
                            <p className="text-dark-400">Loading agents...</p>
                        </div>
                    ) : (
                        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
                            {agents.map((agent) => {
                                const meta = agentMeta[agent.name] || {
                                    emoji: '🤖',
                                    color: 'from-gray-500 to-gray-600',
                                    borderColor: 'border-gray-500/30',
                                    bgColor: 'bg-gray-500/10',
                                    description: agent.description || 'AI Agent',
                                    capabilities: []
                                };
                                const stats = getAgentStats(agent.name);

                                return (
                                    <div
                                        key={agent.id}
                                        onClick={() => handleAgentClick(agent)}
                                        className={`card hover:border-primary-500/50 transition-all cursor-pointer group overflow-hidden relative`}
                                    >
                                        {/* Gradient Background */}
                                        <div className={`absolute inset-0 bg-gradient-to-br ${meta.color} opacity-5 group-hover:opacity-10 transition-opacity`}></div>

                                        <div className="relative z-10">
                                            {/* Agent Icon */}
                                            <div className={`w-16 h-16 rounded-2xl ${meta.bgColor} ${meta.borderColor} border flex items-center justify-center mb-4`}>
                                                <span className="text-4xl">{meta.emoji}</span>
                                            </div>

                                            {/* Agent Name */}
                                            <h3 className="text-lg font-semibold text-white mb-1 group-hover:text-primary-400 transition-colors">
                                                {agent.name.replace('Agent', ' Agent')}
                                            </h3>

                                            {/* Specialization */}
                                            <p className="text-dark-400 text-sm mb-3 line-clamp-2">
                                                {meta.description}
                                            </p>

                                            {/* Activity Heatmap (simulated) */}
                                            <div className="flex gap-0.5 mb-3">
                                                {[...Array(7)].map((_, i) => {
                                                    // Simulate activity levels based on agent type
                                                    const level = Math.floor(Math.random() * 4);
                                                    const colors = ['bg-dark-700', 'bg-green-900', 'bg-green-700', 'bg-green-500'];
                                                    return (
                                                        <div
                                                            key={i}
                                                            className={`w-full h-2 rounded-sm ${colors[level]}`}
                                                            title={`Day ${i + 1}`}
                                                        />
                                                    );
                                                })}
                                            </div>

                                            {/* Stats */}
                                            <div className="flex items-center justify-between text-sm mb-3">
                                                <span className="text-dark-500">{stats.total} tasks</span>
                                                <span className={`font-medium ${stats.successRate >= 90 ? 'text-green-400' : stats.successRate >= 70 ? 'text-yellow-400' : 'text-red-400'}`}>
                                                    {stats.successRate}% success
                                                </span>
                                            </div>

                                            {/* Avg Response Time (simulated) */}
                                            <div className="flex items-center justify-between text-xs text-dark-500 mb-3">
                                                <span>⚡ Avg: {(Math.random() * 2 + 0.5).toFixed(1)}s</span>
                                                <span>📈 {Math.floor(Math.random() * 50 + 50)} req/day</span>
                                            </div>

                                            {/* Status Indicator */}
                                            <div className="flex items-center gap-2">
                                                <div className={`w-2 h-2 rounded-full ${agent.is_active ? 'bg-green-400 animate-pulse' : 'bg-red-400'}`}></div>
                                                <span className={`text-xs ${agent.is_active ? 'text-green-400' : 'text-red-400'}`}>
                                                    {agent.is_active ? 'Active' : 'Inactive'}
                                                </span>
                                            </div>
                                        </div>
                                    </div>
                                );
                            })}
                        </div>
                    )}

                    {/* Summary Stats */}
                    <div className="mt-8 grid grid-cols-2 md:grid-cols-4 gap-4">
                        <div className="card text-center py-4">
                            <div className="text-2xl font-bold gradient-text">{agents.length}</div>
                            <p className="text-dark-400 text-sm">Total Agents</p>
                        </div>
                        <div className="card text-center py-4">
                            <div className="text-2xl font-bold text-green-400">
                                {agents.filter(a => a.is_active).length}
                            </div>
                            <p className="text-dark-400 text-sm">Active</p>
                        </div>
                        <div className="card text-center py-4">
                            <div className="text-2xl font-bold text-blue-400">{tasks.length}</div>
                            <p className="text-dark-400 text-sm">Total Tasks</p>
                        </div>
                        <div className="card text-center py-4">
                            <div className="text-2xl font-bold text-purple-400">
                                {tasks.filter(t => t.status === 'completed').length}
                            </div>
                            <p className="text-dark-400 text-sm">Completed</p>
                        </div>
                    </div>
                </main>
            </div>

            {/* Agent Detail Modal */}
            {showModal && selectedAgent && (
                <div className="fixed inset-0 bg-black/70 backdrop-blur-sm flex items-center justify-center z-50 p-4">
                    <div className="bg-dark-800 rounded-2xl border border-dark-700 w-full max-w-2xl max-h-[80vh] overflow-hidden">
                        <div className="p-6 border-b border-dark-700">
                            <div className="flex items-center justify-between">
                                <div className="flex items-center gap-4">
                                    <div className={`w-14 h-14 rounded-xl ${agentMeta[selectedAgent.name]?.bgColor || 'bg-gray-500/10'} flex items-center justify-center`}>
                                        <span className="text-3xl">{agentMeta[selectedAgent.name]?.emoji || '🤖'}</span>
                                    </div>
                                    <div>
                                        <h2 className="text-xl font-semibold text-white">
                                            {selectedAgent.name.replace('Agent', ' Agent')}
                                        </h2>
                                        <p className="text-dark-400 text-sm">
                                            {selectedAgent.is_active ? '🟢 Active' : '🔴 Inactive'}
                                        </p>
                                    </div>
                                </div>
                                <button
                                    onClick={() => setShowModal(false)}
                                    className="text-dark-400 hover:text-white text-2xl"
                                >
                                    ×
                                </button>
                            </div>
                        </div>
                        <div className="p-6 overflow-y-auto max-h-[50vh]">
                            {/* Description */}
                            <div className="mb-6">
                                <h3 className="text-sm text-dark-400 mb-2">Description</h3>
                                <p className="text-white">
                                    {agentMeta[selectedAgent.name]?.description || selectedAgent.description}
                                </p>
                            </div>

                            {/* Capabilities */}
                            <div className="mb-6">
                                <h3 className="text-sm text-dark-400 mb-2">Capabilities</h3>
                                <div className="flex flex-wrap gap-2">
                                    {(agentMeta[selectedAgent.name]?.capabilities || []).map((cap, i) => (
                                        <span key={i} className="px-3 py-1 bg-dark-700 text-dark-200 rounded-full text-sm">
                                            {cap}
                                        </span>
                                    ))}
                                </div>
                            </div>

                            {/* Stats */}
                            <div>
                                <h3 className="text-sm text-dark-400 mb-2">Performance</h3>
                                <div className="grid grid-cols-3 gap-4">
                                    {(() => {
                                        const stats = getAgentStats(selectedAgent.name);
                                        return (
                                            <>
                                                <div className="bg-dark-700 rounded-lg p-3 text-center">
                                                    <div className="text-xl font-bold text-white">{stats.total}</div>
                                                    <p className="text-dark-400 text-xs">Tasks</p>
                                                </div>
                                                <div className="bg-dark-700 rounded-lg p-3 text-center">
                                                    <div className="text-xl font-bold text-green-400">{stats.completed}</div>
                                                    <p className="text-dark-400 text-xs">Completed</p>
                                                </div>
                                                <div className="bg-dark-700 rounded-lg p-3 text-center">
                                                    <div className="text-xl font-bold text-blue-400">{stats.successRate}%</div>
                                                    <p className="text-dark-400 text-xs">Success Rate</p>
                                                </div>
                                            </>
                                        );
                                    })()}
                                </div>
                            </div>
                        </div>
                        <div className="p-6 border-t border-dark-700 flex justify-end gap-3">
                            <button
                                onClick={() => {
                                    setChatAgent(selectedAgent);
                                    setShowModal(false);
                                    setShowChatModal(true);
                                }}
                                className="px-4 py-2 bg-gradient-to-r from-purple-500 to-pink-500 text-white rounded-lg font-medium hover:shadow-lg hover:shadow-purple-500/25 transition-all"
                            >
                                💬 Direct Chat
                            </button>
                            <button
                                onClick={() => {
                                    setShowModal(false);
                                    navigate('/dashboard');
                                }}
                                className="btn-primary"
                            >
                                Use This Agent
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

            {/* Agent Chat Modal */}
            <AgentChatModal
                isOpen={showChatModal}
                onClose={() => setShowChatModal(false)}
                agent={chatAgent}
            />
        </div>
    );
}
