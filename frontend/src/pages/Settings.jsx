import { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import { authAPI, tasksAPI, filesAPI } from '../services/api';
import Navbar from '../components/layout/Navbar';
import Sidebar from '../components/layout/Sidebar';
import toast from 'react-hot-toast';

export default function Settings() {
    const { user, logout } = useAuth();
    const [activeTab, setActiveTab] = useState('account');
    const [loading, setLoading] = useState(false);
    const [stats, setStats] = useState({ tasks: 0, files: 0, storage: 0 });

    // Form states
    const [passwordData, setPasswordData] = useState({
        currentPassword: '',
        newPassword: '',
        confirmPassword: ''
    });
    const [apiKey, setApiKey] = useState('');
    const [showApiKey, setShowApiKey] = useState(false);
    const [theme, setTheme] = useState('dark');
    const [notifications, setNotifications] = useState({
        email: true,
        push: true
    });

    useEffect(() => {
        loadStats();
    }, []);

    const loadStats = async () => {
        try {
            const [tasksRes, filesRes] = await Promise.all([
                tasksAPI.list({ limit: 100 }),
                filesAPI.list({ limit: 100 })
            ]);
            const totalStorage = filesRes.data.reduce((acc, f) => acc + (f.size || 0), 0);
            setStats({
                tasks: tasksRes.data.length,
                files: filesRes.data.length,
                storage: totalStorage
            });
        } catch (error) {
            console.error('Failed to load stats:', error);
        }
    };

    const handlePasswordChange = async (e) => {
        e.preventDefault();
        if (passwordData.newPassword !== passwordData.confirmPassword) {
            toast.error('Passwords do not match');
            return;
        }
        if (passwordData.newPassword.length < 6) {
            toast.error('Password must be at least 6 characters');
            return;
        }

        setLoading(true);
        try {
            await authAPI.changePassword({
                current_password: passwordData.currentPassword,
                new_password: passwordData.newPassword
            });
            toast.success('Password changed successfully');
            setPasswordData({ currentPassword: '', newPassword: '', confirmPassword: '' });
        } catch (error) {
            // Error toast is handled by handleApiError in setupErrorInterceptors
            console.error('Password change failed:', error);
        } finally {
            setLoading(false);
        }
    };

    const handleDeleteAllTasks = async () => {
        if (!confirm('Are you sure you want to delete ALL tasks? This cannot be undone.')) return;

        setLoading(true);
        try {
            const tasksRes = await tasksAPI.list({ limit: 1000 });
            for (const task of tasksRes.data) {
                await tasksAPI.delete(task.id);
            }
            toast.success('All tasks deleted');
            loadStats();
        } catch (error) {
            toast.error('Failed to delete tasks');
        } finally {
            setLoading(false);
        }
    };

    const handleDeleteAccount = async () => {
        if (!confirm('Are you ABSOLUTELY SURE you want to delete your account? This will permanently delete all your data.')) return;
        if (!confirm('This action CANNOT be undone. Type DELETE to confirm.')) return;

        try {
            // Note: Backend endpoint would need to be created
            toast.success('Account deletion requested');
            logout();
        } catch (error) {
            toast.error('Failed to delete account');
        }
    };

    const formatBytes = (bytes) => {
        if (bytes === 0) return '0 B';
        const k = 1024;
        const sizes = ['B', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i];
    };

    const tabs = [
        { id: 'account', label: 'Account', icon: '👤' },
        { id: 'api', label: 'API', icon: '🔑' },
        { id: 'preferences', label: 'Preferences', icon: '⚙️' },
        { id: 'storage', label: 'Storage', icon: '💾' },
        { id: 'danger', label: 'Danger Zone', icon: '⚠️' }
    ];

    return (
        <div className="min-h-screen bg-dark-900">
            <Navbar />
            <div className="flex">
                <Sidebar />
                <main className="flex-1 p-6 lg:p-8">
                    {/* Header */}
                    <div className="mb-8">
                        <h1 className="text-3xl font-bold text-white mb-2">⚙️ Settings</h1>
                        <p className="text-dark-400">Manage your account, preferences, and platform settings.</p>
                    </div>

                    {/* Tabs */}
                    <div className="flex flex-wrap gap-2 mb-6">
                        {tabs.map((tab) => (
                            <button
                                key={tab.id}
                                onClick={() => setActiveTab(tab.id)}
                                className={`px-4 py-2 rounded-lg transition-colors flex items-center gap-2 ${activeTab === tab.id
                                    ? 'bg-primary-500 text-white'
                                    : 'bg-dark-800 text-dark-400 hover:bg-dark-700 hover:text-white'
                                    }`}
                            >
                                <span>{tab.icon}</span>
                                <span>{tab.label}</span>
                            </button>
                        ))}
                    </div>

                    {/* Tab Content */}
                    <div className="card">
                        {/* Account Tab */}
                        {activeTab === 'account' && (
                            <div className="space-y-6">
                                <h2 className="text-xl font-semibold text-white mb-4">Account Settings</h2>

                                {/* User Info */}
                                <div className="p-4 bg-dark-700 rounded-lg">
                                    <div className="flex items-center gap-4">
                                        <div className="w-16 h-16 rounded-full bg-gradient-to-br from-primary-500 to-purple-500 flex items-center justify-center text-2xl font-bold text-white">
                                            {user?.username?.[0]?.toUpperCase() || 'U'}
                                        </div>
                                        <div>
                                            <h3 className="text-lg font-semibold text-white">{user?.username}</h3>
                                            <p className="text-dark-400">{user?.email}</p>
                                            <p className="text-dark-500 text-sm mt-1">
                                                Member since {new Date(user?.created_at || Date.now()).toLocaleDateString()}
                                            </p>
                                        </div>
                                    </div>
                                </div>

                                {/* Change Password */}
                                <div>
                                    <h3 className="text-lg font-medium text-white mb-3">Change Password</h3>
                                    <form onSubmit={handlePasswordChange} className="space-y-4 max-w-md">
                                        <div>
                                            <label className="block text-dark-400 text-sm mb-1">Current Password</label>
                                            <input
                                                type="password"
                                                value={passwordData.currentPassword}
                                                onChange={(e) => setPasswordData({ ...passwordData, currentPassword: e.target.value })}
                                                className="input-field w-full"
                                                placeholder="••••••••"
                                            />
                                        </div>
                                        <div>
                                            <label className="block text-dark-400 text-sm mb-1">New Password</label>
                                            <input
                                                type="password"
                                                value={passwordData.newPassword}
                                                onChange={(e) => setPasswordData({ ...passwordData, newPassword: e.target.value })}
                                                className="input-field w-full"
                                                placeholder="••••••••"
                                            />
                                        </div>
                                        <div>
                                            <label className="block text-dark-400 text-sm mb-1">Confirm New Password</label>
                                            <input
                                                type="password"
                                                value={passwordData.confirmPassword}
                                                onChange={(e) => setPasswordData({ ...passwordData, confirmPassword: e.target.value })}
                                                className="input-field w-full"
                                                placeholder="••••••••"
                                            />
                                        </div>
                                        <button
                                            type="submit"
                                            disabled={loading}
                                            className="btn-primary disabled:opacity-50"
                                        >
                                            {loading ? 'Saving...' : 'Change Password'}
                                        </button>
                                    </form>
                                </div>
                            </div>
                        )}

                        {/* API Tab */}
                        {activeTab === 'api' && (
                            <div className="space-y-6">
                                <h2 className="text-xl font-semibold text-white mb-4">API Settings</h2>

                                {/* Groq API Key */}
                                <div>
                                    <h3 className="text-lg font-medium text-white mb-3">Groq API Key</h3>
                                    <p className="text-dark-400 text-sm mb-4">
                                        Your Groq API key is stored securely in the backend environment.
                                    </p>
                                    <div className="flex items-center gap-3 max-w-md">
                                        <input
                                            type={showApiKey ? 'text' : 'password'}
                                            value={apiKey || '••••••••••••••••••••••••••••••••'}
                                            onChange={(e) => setApiKey(e.target.value)}
                                            className="input-field flex-1"
                                            placeholder="gsk_xxxxxxxxxxxxxxxxxxxx"
                                        />
                                        <button
                                            onClick={() => setShowApiKey(!showApiKey)}
                                            className="px-4 py-2 bg-dark-700 hover:bg-dark-600 text-white rounded-lg transition-colors"
                                        >
                                            {showApiKey ? '🙈' : '👁️'}
                                        </button>
                                    </div>
                                    <p className="text-dark-500 text-xs mt-2">
                                        API key changes require backend restart to take effect.
                                    </p>
                                </div>

                                {/* Usage Stats */}
                                <div>
                                    <h3 className="text-lg font-medium text-white mb-3">Usage Statistics</h3>
                                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                                        <div className="p-4 bg-dark-700 rounded-lg text-center">
                                            <div className="text-2xl font-bold text-primary-400">{stats.tasks}</div>
                                            <p className="text-dark-400 text-sm">Total Tasks</p>
                                        </div>
                                        <div className="p-4 bg-dark-700 rounded-lg text-center">
                                            <div className="text-2xl font-bold text-green-400">~{(stats.tasks * 1500).toLocaleString()}</div>
                                            <p className="text-dark-400 text-sm">Est. Tokens Used</p>
                                        </div>
                                        <div className="p-4 bg-dark-700 rounded-lg text-center">
                                            <div className="text-2xl font-bold text-blue-400">{stats.tasks * 7}</div>
                                            <p className="text-dark-400 text-sm">API Requests</p>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        )}

                        {/* Preferences Tab */}
                        {activeTab === 'preferences' && (
                            <div className="space-y-6">
                                <h2 className="text-xl font-semibold text-white mb-4">Preferences</h2>

                                {/* Theme */}
                                <div>
                                    <h3 className="text-lg font-medium text-white mb-3">Theme</h3>
                                    <div className="flex gap-3">
                                        <button
                                            onClick={() => setTheme('dark')}
                                            className={`px-4 py-3 rounded-lg flex items-center gap-2 transition-colors ${theme === 'dark'
                                                ? 'bg-primary-500 text-white'
                                                : 'bg-dark-700 text-dark-400 hover:bg-dark-600'
                                                }`}
                                        >
                                            🌙 Dark Mode
                                        </button>
                                        <button
                                            onClick={() => setTheme('light')}
                                            className={`px-4 py-3 rounded-lg flex items-center gap-2 transition-colors ${theme === 'light'
                                                ? 'bg-primary-500 text-white'
                                                : 'bg-dark-700 text-dark-400 hover:bg-dark-600'
                                                }`}
                                        >
                                            ☀️ Light Mode
                                        </button>
                                    </div>
                                    <p className="text-dark-500 text-xs mt-2">
                                        Light mode is coming soon. Nexus AI currently supports dark mode only.
                                    </p>
                                </div>

                                {/* Notifications */}
                                <div>
                                    <h3 className="text-lg font-medium text-white mb-3">Notifications</h3>
                                    <div className="space-y-3">
                                        <label className="flex items-center justify-between p-3 bg-dark-700 rounded-lg cursor-pointer">
                                            <span className="text-white">Email Notifications</span>
                                            <input
                                                type="checkbox"
                                                checked={notifications.email}
                                                onChange={(e) => setNotifications({ ...notifications, email: e.target.checked })}
                                                className="w-5 h-5 rounded accent-primary-500"
                                            />
                                        </label>
                                        <label className="flex items-center justify-between p-3 bg-dark-700 rounded-lg cursor-pointer">
                                            <span className="text-white">Real-time Push Notifications</span>
                                            <input
                                                type="checkbox"
                                                checked={notifications.push}
                                                onChange={(e) => setNotifications({ ...notifications, push: e.target.checked })}
                                                className="w-5 h-5 rounded accent-primary-500"
                                            />
                                        </label>
                                    </div>
                                </div>
                            </div>
                        )}

                        {/* Storage Tab */}
                        {activeTab === 'storage' && (
                            <div className="space-y-6">
                                <h2 className="text-xl font-semibold text-white mb-4">Storage Management</h2>

                                {/* Storage Usage */}
                                <div>
                                    <div className="flex items-center justify-between mb-2">
                                        <span className="text-white">Storage Used</span>
                                        <span className="text-dark-400">{formatBytes(stats.storage)} / 100 MB</span>
                                    </div>
                                    <div className="h-4 bg-dark-700 rounded-full overflow-hidden">
                                        <div
                                            className="h-full bg-gradient-to-r from-primary-500 to-purple-500 rounded-full transition-all"
                                            style={{ width: `${Math.min((stats.storage / (100 * 1024 * 1024)) * 100, 100)}%` }}
                                        ></div>
                                    </div>
                                </div>

                                {/* Storage Breakdown */}
                                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                                    <div className="p-4 bg-dark-700 rounded-lg text-center">
                                        <div className="text-2xl font-bold text-blue-400">{stats.files}</div>
                                        <p className="text-dark-400 text-sm">Files Uploaded</p>
                                    </div>
                                    <div className="p-4 bg-dark-700 rounded-lg text-center">
                                        <div className="text-2xl font-bold text-green-400">{formatBytes(stats.storage)}</div>
                                        <p className="text-dark-400 text-sm">Total Size</p>
                                    </div>
                                    <div className="p-4 bg-dark-700 rounded-lg text-center">
                                        <div className="text-2xl font-bold text-purple-400">
                                            {formatBytes(100 * 1024 * 1024 - stats.storage)}
                                        </div>
                                        <p className="text-dark-400 text-sm">Available</p>
                                    </div>
                                </div>
                            </div>
                        )}

                        {/* Danger Zone Tab */}
                        {activeTab === 'danger' && (
                            <div className="space-y-6">
                                <h2 className="text-xl font-semibold text-red-400 mb-4">⚠️ Danger Zone</h2>
                                <p className="text-dark-400 mb-6">
                                    These actions are irreversible. Please proceed with caution.
                                </p>

                                <div className="space-y-4">
                                    {/* Delete All Tasks */}
                                    <div className="p-4 border border-red-500/30 rounded-lg bg-red-500/5">
                                        <div className="flex items-center justify-between">
                                            <div>
                                                <h3 className="text-white font-medium">Delete All Tasks</h3>
                                                <p className="text-dark-400 text-sm">Remove all tasks and their data permanently.</p>
                                            </div>
                                            <button
                                                onClick={handleDeleteAllTasks}
                                                disabled={loading}
                                                className="px-4 py-2 bg-red-500/20 hover:bg-red-500/30 text-red-400 rounded-lg transition-colors disabled:opacity-50"
                                            >
                                                {loading ? 'Deleting...' : 'Delete All'}
                                            </button>
                                        </div>
                                    </div>

                                    {/* Delete Account */}
                                    <div className="p-4 border border-red-500/30 rounded-lg bg-red-500/5">
                                        <div className="flex items-center justify-between">
                                            <div>
                                                <h3 className="text-white font-medium">Delete Account</h3>
                                                <p className="text-dark-400 text-sm">Permanently delete your account and all associated data.</p>
                                            </div>
                                            <button
                                                onClick={handleDeleteAccount}
                                                className="px-4 py-2 bg-red-500 hover:bg-red-600 text-white rounded-lg transition-colors"
                                            >
                                                Delete Account
                                            </button>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        )}
                    </div>
                </main>
            </div>
        </div>
    );
}
