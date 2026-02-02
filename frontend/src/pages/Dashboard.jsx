import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { agentsAPI, tasksAPI, projectsAPI } from '../services/api';
import Navbar from '../components/layout/Navbar';
import Sidebar from '../components/layout/Sidebar';
import toast from 'react-hot-toast';

export default function Dashboard() {
    const { user } = useAuth();
    const navigate = useNavigate();
    const [agents, setAgents] = useState([]);
    const [recentTasks, setRecentTasks] = useState([]);
    const [pinnedProjects, setPinnedProjects] = useState([]);
    const [prompt, setPrompt] = useState('');
    const [isSubmitting, setIsSubmitting] = useState(false);

    useEffect(() => {
        loadAgents();
        loadRecentTasks();
        loadPinnedProjects();

        // Auto-refresh tasks every 5 seconds
        const interval = setInterval(() => {
            loadRecentTasks();
            loadPinnedProjects();
        }, 5000);
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
            const response = await tasksAPI.create({ user_prompt: prompt });
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
            case 'completed': return 'text-green-400 bg-green-400/10';
            case 'in_progress': return 'text-yellow-400 bg-yellow-400/10';
            case 'failed': return 'text-red-400 bg-red-400/10';
            default: return 'text-blue-400 bg-blue-400/10';
        }
    };

    const agentEmojis = {
        'ResearchAgent': '🔍',
        'CodeAgent': '💻',
        'ContentAgent': '✍️',
        'DataAgent': '📊',
        'QAAgent': '✅',
        'MemoryAgent': '🧠',
        'ManagerAgent': '📋',
    };

    return (
        <div className="min-h-screen bg-dark-900">
            <Navbar />

            <div className="flex">
                <Sidebar />

                {/* Main Content */}
                <main className="flex-1 p-6 lg:p-8">
                    {/* Welcome Section */}
                    <div className="mb-8">
                        <h1 className="text-3xl font-bold text-white mb-2">
                            Welcome back, <span className="gradient-text">{user?.username}</span>
                        </h1>
                        <p className="text-dark-400">
                            What would you like your agents to work on today?
                        </p>
                    </div>

                    {/* Task Input */}
                    <div className="card gradient-border mb-8">
                        <form onSubmit={handleSubmitTask}>
                            <div className="flex gap-4">
                                <input
                                    type="text"
                                    value={prompt}
                                    onChange={(e) => setPrompt(e.target.value)}
                                    placeholder="Describe your task... e.g., 'Research the latest AI trends and write a summary'"
                                    className="flex-1 input-field"
                                />
                                <button
                                    type="submit"
                                    disabled={isSubmitting || !prompt.trim()}
                                    className="btn-primary px-8 disabled:opacity-50"
                                >
                                    {isSubmitting ? 'Sending...' : 'Send Task'}
                                </button>
                            </div>
                        </form>
                    </div>

                    {/* Quick Actions & System Status Row */}
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-6">
                        {/* Quick Actions */}
                        <div className="card">
                            <h2 className="text-lg font-semibold text-white mb-4">⚡ Quick Actions</h2>
                            <div className="space-y-2">
                                <button
                                    onClick={() => document.querySelector('input[placeholder*="Describe"]')?.focus()}
                                    className="w-full p-3 rounded-lg bg-dark-700 hover:bg-dark-600 text-left text-white transition-colors flex items-center gap-3"
                                >
                                    <span className="text-xl">➕</span>
                                    <span>New Task</span>
                                </button>
                                <button
                                    onClick={() => navigate('/projects')}
                                    className="w-full p-3 rounded-lg bg-dark-700 hover:bg-dark-600 text-left text-white transition-colors flex items-center gap-3"
                                >
                                    <span className="text-xl">📁</span>
                                    <span>New Project</span>
                                </button>
                                <button
                                    onClick={() => navigate('/files')}
                                    className="w-full p-3 rounded-lg bg-dark-700 hover:bg-dark-600 text-left text-white transition-colors flex items-center gap-3"
                                >
                                    <span className="text-xl">📤</span>
                                    <span>Upload File</span>
                                </button>
                                <button
                                    onClick={() => navigate('/agents')}
                                    className="w-full p-3 rounded-lg bg-dark-700 hover:bg-dark-600 text-left text-white transition-colors flex items-center gap-3"
                                >
                                    <span className="text-xl">🤖</span>
                                    <span>Browse Agents</span>
                                </button>
                            </div>
                        </div>

                        {/* Activity Feed */}
                        <div className="card">
                            <div className="flex items-center justify-between mb-4">
                                <h2 className="text-lg font-semibold text-white">📈 Recent Activity</h2>
                                <button
                                    onClick={() => navigate('/tasks')}
                                    className="text-xs text-primary-400 hover:text-primary-300"
                                >
                                    View All
                                </button>
                            </div>
                            <div className="space-y-3">
                                {recentTasks.slice(0, 4).map((task, i) => (
                                    <div key={task.id} className="flex items-start gap-3">
                                        <div className={`w-2 h-2 rounded-full mt-2 ${task.status === 'completed' ? 'bg-green-400' :
                                                task.status === 'in_progress' ? 'bg-yellow-400 animate-pulse' :
                                                    task.status === 'failed' ? 'bg-red-400' : 'bg-blue-400'
                                            }`}></div>
                                        <div className="flex-1 min-w-0">
                                            <p className="text-white text-sm line-clamp-1">{task.user_prompt}</p>
                                            <p className="text-dark-500 text-xs">
                                                {task.status === 'completed' ? 'Completed' :
                                                    task.status === 'in_progress' ? 'Running...' :
                                                        task.status === 'failed' ? 'Failed' : 'Queued'} • {
                                                    new Date(task.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
                                                }
                                            </p>
                                        </div>
                                    </div>
                                ))}
                                {recentTasks.length === 0 && (
                                    <p className="text-dark-500 text-sm text-center py-4">No activity yet</p>
                                )}
                            </div>
                        </div>

                        {/* System Status */}
                        <div className="card">
                            <h2 className="text-lg font-semibold text-white mb-4">🏥 System Status</h2>
                            <div className="space-y-3">
                                <div className="flex items-center justify-between">
                                    <span className="text-dark-400">Backend API</span>
                                    <span className="flex items-center gap-2 text-green-400 text-sm">
                                        <span className="w-2 h-2 rounded-full bg-green-400 animate-pulse"></span>
                                        Online
                                    </span>
                                </div>
                                <div className="flex items-center justify-between">
                                    <span className="text-dark-400">Redis Queue</span>
                                    <span className="flex items-center gap-2 text-green-400 text-sm">
                                        <span className="w-2 h-2 rounded-full bg-green-400 animate-pulse"></span>
                                        Connected
                                    </span>
                                </div>
                                <div className="flex items-center justify-between">
                                    <span className="text-dark-400">AI Agents</span>
                                    <span className="flex items-center gap-2 text-green-400 text-sm">
                                        <span className="w-2 h-2 rounded-full bg-green-400 animate-pulse"></span>
                                        {agents.length} Active
                                    </span>
                                </div>
                                <div className="flex items-center justify-between">
                                    <span className="text-dark-400">Database</span>
                                    <span className="flex items-center gap-2 text-green-400 text-sm">
                                        <span className="w-2 h-2 rounded-full bg-green-400 animate-pulse"></span>
                                        Healthy
                                    </span>
                                </div>
                            </div>
                        </div>
                    </div>

                    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                        {/* Pinned Projects */}
                        <div className="card">
                            <div className="flex items-center justify-between mb-4">
                                <h2 className="text-xl font-semibold text-white">📌 Pinned Projects</h2>
                                <button
                                    onClick={() => navigate('/projects')}
                                    className="text-sm text-primary-400 hover:text-primary-300"
                                >
                                    View All
                                </button>
                            </div>
                            <div className="grid grid-cols-1 gap-3">
                                {pinnedProjects.map((project) => (
                                    <div
                                        key={project.id}
                                        onClick={() => navigate(`/projects/${project.id}`)}
                                        className="p-4 rounded-xl bg-dark-700/50 border border-dark-600 hover:border-primary-500/50 transition-all cursor-pointer group relative overflow-hidden"
                                    >
                                        <div className="flex items-center justify-between mb-2">
                                            <h3 className="font-semibold text-white group-hover:text-primary-400 transition-colors">
                                                {project.name}
                                            </h3>
                                            <span className={`text-[10px] px-2 py-0.5 rounded-full bg-primary-500/10 text-primary-400 border border-primary-500/20`}>
                                                {project.status.replace('_', ' ')}
                                            </span>
                                        </div>
                                        <p className="text-xs text-dark-400 line-clamp-1 mb-3">
                                            {project.description || 'No description'}
                                        </p>
                                        <div className="flex items-center gap-3">
                                            <div className="flex-1 h-1 bg-dark-600 rounded-full overflow-hidden">
                                                <div
                                                    className="h-full bg-gradient-to-r from-primary-500 to-purple-500"
                                                    style={{ width: `${project.progress}%` }}
                                                />
                                            </div>
                                            <span className="text-[10px] text-dark-400 font-medium">
                                                {project.progress}%
                                            </span>
                                        </div>
                                    </div>
                                ))}
                                {pinnedProjects.length === 0 && (
                                    <div className="text-center py-6 border-2 border-dashed border-dark-700 rounded-xl">
                                        <p className="text-dark-500 text-sm">No pinned projects yet</p>
                                        <button
                                            onClick={() => navigate('/projects')}
                                            className="mt-2 text-xs text-primary-400 hover:underline"
                                        >
                                            Go to Projects
                                        </button>
                                    </div>
                                )}
                            </div>
                        </div>

                        {/* Recent Tasks */}
                        <div className="card">
                            <div className="flex items-center justify-between mb-4">
                                <h2 className="text-xl font-semibold text-white">Recent Tasks</h2>
                                <span className="text-xs text-dark-500">Auto-refreshing</span>
                            </div>
                            <div className="space-y-3">
                                {recentTasks.map((task) => (
                                    <div
                                        key={task.id}
                                        onClick={() => navigate(`/tasks/${task.id}`)}
                                        className="p-3 rounded-lg bg-dark-700/50 hover:bg-dark-700 transition-colors cursor-pointer group"
                                    >
                                        <p className="text-white text-sm mb-2 line-clamp-2 group-hover:text-primary-400 transition-colors">
                                            {task.user_prompt}
                                        </p>
                                        <div className="flex items-center justify-between">
                                            <span className={`text-xs px-2 py-1 rounded-full ${getStatusColor(task.status)}`}>
                                                {task.status}
                                            </span>
                                            <span className="text-xs text-dark-500">
                                                {new Date(task.created_at).toLocaleDateString()}
                                            </span>
                                        </div>
                                        {task.status === 'in_progress' && (
                                            <div className="mt-2 h-1 bg-dark-600 rounded-full overflow-hidden">
                                                <div className="h-full w-1/2 bg-gradient-to-r from-primary-500 to-purple-500 rounded-full animate-pulse" />
                                            </div>
                                        )}
                                    </div>
                                ))}
                                {recentTasks.length === 0 && (
                                    <p className="text-dark-400 text-center py-4">No tasks yet. Create your first one!</p>
                                )}
                            </div>
                        </div>
                    </div>

                    {/* Quick Stats */}
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mt-6">
                        <div className="card text-center">
                            <div className="text-3xl font-bold gradient-text">{agents.length}</div>
                            <p className="text-dark-400 text-sm">Active Agents</p>
                        </div>
                        <div className="card text-center">
                            <div className="text-3xl font-bold text-green-400">{recentTasks.filter(t => t.status === 'completed').length}</div>
                            <p className="text-dark-400 text-sm">Completed</p>
                        </div>
                        <div className="card text-center">
                            <div className="text-3xl font-bold text-yellow-400">{recentTasks.filter(t => t.status === 'in_progress').length}</div>
                            <p className="text-dark-400 text-sm">In Progress</p>
                        </div>
                        <div className="card text-center">
                            <div className="text-3xl font-bold text-blue-400">{recentTasks.filter(t => t.status === 'queued').length}</div>
                            <p className="text-dark-400 text-sm">Queued</p>
                        </div>
                    </div>
                </main>
            </div>
        </div>
    );
}
