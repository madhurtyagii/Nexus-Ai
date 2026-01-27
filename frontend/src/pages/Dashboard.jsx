import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { agentsAPI, tasksAPI } from '../services/api';
import Navbar from '../components/layout/Navbar';
import Sidebar from '../components/layout/Sidebar';
import toast from 'react-hot-toast';

export default function Dashboard() {
    const { user } = useAuth();
    const navigate = useNavigate();
    const [agents, setAgents] = useState([]);
    const [recentTasks, setRecentTasks] = useState([]);
    const [prompt, setPrompt] = useState('');
    const [isSubmitting, setIsSubmitting] = useState(false);

    useEffect(() => {
        loadAgents();
        loadRecentTasks();

        // Auto-refresh tasks every 5 seconds
        const interval = setInterval(loadRecentTasks, 5000);
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
            const response = await tasksAPI.list({ limit: 10 });
            setRecentTasks(response.data);
        } catch (error) {
            console.error('Failed to load tasks:', error);
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

                    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                        {/* Available Agents */}
                        <div className="card">
                            <h2 className="text-xl font-semibold text-white mb-4">Available Agents</h2>
                            <div className="space-y-3">
                                {agents.map((agent) => (
                                    <div
                                        key={agent.id}
                                        className="flex items-center gap-4 p-3 rounded-lg bg-dark-700/50 hover:bg-dark-700 transition-colors"
                                    >
                                        <div className="text-2xl">
                                            {agentEmojis[agent.name] || '🤖'}
                                        </div>
                                        <div className="flex-1">
                                            <h3 className="font-medium text-white">{agent.name}</h3>
                                            <p className="text-sm text-dark-400">{agent.role}</p>
                                        </div>
                                        <div className={`w-2 h-2 rounded-full ${agent.is_active ? 'bg-green-400' : 'bg-dark-500'}`} />
                                    </div>
                                ))}
                                {agents.length === 0 && (
                                    <p className="text-dark-400 text-center py-4">Loading agents...</p>
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
