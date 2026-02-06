import { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import { authAPI, default as api } from '../services/api';
import { motion, AnimatePresence } from 'framer-motion';
import {
    User,
    Shield,
    Bell,
    Zap,
    Eye,
    EyeOff,
    Key,
    Database,
    Moon,
    Sun,
    Mail,
    ChevronRight,
    MousePointer2,
    Pencil,
    Check,
    X
} from 'lucide-react';
import Navbar from '../components/layout/Navbar';
import Sidebar from '../components/layout/Sidebar';
import toast from 'react-hot-toast';
import { toggleCursorEffect, setCursorEffectType, CURSOR_EFFECTS } from '../components/common/CursorFollower';

export default function Settings() {
    const { user, refreshUser } = useAuth();
    const [activeTab, setActiveTab] = useState('account');
    const [apiKey, setApiKey] = useState('');
    const [showApiKey, setShowApiKey] = useState(false);
    const [theme, setTheme] = useState(localStorage.getItem('nexus_theme') || 'dark');
    const [cursorEnabled, setCursorEnabled] = useState(() => {
        const saved = localStorage.getItem('nexus-cursor-effect');
        return saved === null ? true : saved === 'true';
    });
    const [cursorEffect, setCursorEffect] = useState(() => {
        return localStorage.getItem('nexus-cursor-type') || 'ring';
    });

    // Account editing states
    const [editingUsername, setEditingUsername] = useState(false);
    const [editingEmail, setEditingEmail] = useState(false);
    const [newUsername, setNewUsername] = useState('');
    const [newEmail, setNewEmail] = useState('');
    const [savingAccount, setSavingAccount] = useState(false);

    const fetchApiKey = async () => {
        try {
            const response = await api.get('/auth/me/api-key');
            setApiKey(response.data.api_key);
            setShowApiKey(true);
        } catch (error) {
            toast.error('Failed to fetch API key');
        }
    };

    const saveUsername = async () => {
        if (!newUsername.trim() || newUsername === user?.username) {
            setEditingUsername(false);
            return;
        }
        setSavingAccount(true);
        try {
            await api.put('/auth/me', { username: newUsername.trim() });
            toast.success('Username updated!');
            if (refreshUser) refreshUser();
            setEditingUsername(false);
        } catch (error) {
            toast.error(error.response?.data?.detail || 'Failed to update username');
        } finally {
            setSavingAccount(false);
        }
    };

    const saveEmail = async () => {
        if (!newEmail.trim() || newEmail === user?.email) {
            setEditingEmail(false);
            return;
        }
        setSavingAccount(true);
        try {
            await api.put('/auth/me', { email: newEmail.trim() });
            toast.success('Email updated!');
            if (refreshUser) refreshUser();
            setEditingEmail(false);
        } catch (error) {
            toast.error(error.response?.data?.detail || 'Failed to update email');
        } finally {
            setSavingAccount(false);
        }
    };

    const toggleTheme = (newTheme, event) => {
        const x = event.clientX;
        const y = event.clientY;

        document.documentElement.style.setProperty('--transition-x', `${x}px`);
        document.documentElement.style.setProperty('--transition-y', `${y}px`);

        if (!document.startViewTransition) {
            setTheme(newTheme);
            localStorage.setItem('nexus_theme', newTheme);
            return;
        }

        document.startViewTransition(() => {
            setTheme(newTheme);
            localStorage.setItem('nexus_theme', newTheme);
            if (newTheme === 'light') {
                document.documentElement.classList.add('light');
            } else {
                document.documentElement.classList.remove('light');
            }
        });
    };

    const tabs = [
        { id: 'account', label: 'Account', icon: User },
        { id: 'security', label: 'Security', icon: Shield },
        { id: 'notifications', label: 'Notifications', icon: Bell },
        { id: 'api', label: 'API Keys', icon: Key },
        { id: 'appearance', label: 'Appearance', icon: Zap },
    ];

    return (
        <div className="min-h-screen bg-dark-900">
            <Navbar />
            <div className="flex">
                <Sidebar />
                <main className="flex-1 p-6 lg:p-10 max-w-6xl mx-auto">
                    <motion.div
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                    >
                        <header className="mb-10">
                            <h1 className="text-4xl font-bold text-white tracking-tight mb-2">Settings</h1>
                            <p className="text-dark-400 font-medium italic">Nexus Intelligence v2.0 Configuration</p>
                        </header>

                        <div className="flex flex-col md:flex-row gap-8">
                            {/* Navigation Sidebar */}
                            <aside className="w-full md:w-64 space-y-2">
                                {tabs.map((tab) => (
                                    <button
                                        key={tab.id}
                                        onClick={() => setActiveTab(tab.id)}
                                        className={`w-full flex items-center gap-3 px-4 py-3.5 rounded-2xl transition-all font-bold text-sm ${activeTab === tab.id
                                            ? 'bg-primary-500 text-white shadow-[0_10px_25px_rgba(14,165,233,0.3)]'
                                            : 'text-dark-400 hover:bg-white/5 hover:text-white'
                                            }`}
                                    >
                                        <tab.icon className="w-5 h-5" />
                                        {tab.label}
                                        {activeTab === tab.id && <ChevronRight className="ml-auto w-4 h-4" />}
                                    </button>
                                ))}
                            </aside>

                            {/* Content Area */}
                            <div className="flex-1">
                                <AnimatePresence mode="wait">
                                    {activeTab === 'account' && (
                                        <motion.div
                                            key="account"
                                            initial={{ opacity: 0, x: 10 }}
                                            animate={{ opacity: 1, x: 0 }}
                                            exit={{ opacity: 0, x: -10 }}
                                            className="glass p-8 rounded-[2rem] border border-white/5"
                                        >
                                            <h2 className="text-xl font-bold text-white mb-6 tracking-tight">Profile Matrix</h2>
                                            <div className="space-y-6">
                                                <div className="flex items-center gap-6 p-5 rounded-2xl bg-white/[0.02] border border-white/5 relative overflow-hidden group">
                                                    <div className="absolute inset-0 bg-gradient-to-r from-primary-500/5 to-transparent opacity-0 group-hover:opacity-100 transition-opacity" />
                                                    <div className="w-20 h-20 rounded-2xl bg-gradient-to-br from-primary-500 to-purple-600 flex items-center justify-center text-3xl font-black text-white shadow-2xl relative z-10">
                                                        {user?.username?.[0]?.toUpperCase()}
                                                    </div>
                                                    <div className="relative z-10">
                                                        <p className="text-xl font-black text-white tracking-tight">{user?.username}</p>
                                                        <p className="text-dark-400 font-medium">{user?.email}</p>
                                                    </div>
                                                </div>

                                                <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
                                                    {/* Username Field */}
                                                    <div className="space-y-2">
                                                        <label className="text-[10px] font-black text-dark-500 uppercase tracking-[0.2em] ml-1">Identity</label>
                                                        {editingUsername ? (
                                                            <div className="flex items-center gap-2">
                                                                <div className="flex-1 flex items-center gap-3 px-4 py-3 rounded-xl bg-white/[0.05] border border-primary-500/50">
                                                                    <User className="w-4 h-4 text-primary-400" />
                                                                    <input
                                                                        type="text"
                                                                        value={newUsername}
                                                                        onChange={(e) => setNewUsername(e.target.value)}
                                                                        className="flex-1 bg-transparent text-white text-sm font-bold outline-none"
                                                                        placeholder="Enter new username"
                                                                        autoFocus
                                                                    />
                                                                </div>
                                                                <button
                                                                    onClick={saveUsername}
                                                                    disabled={savingAccount}
                                                                    className="p-3 rounded-xl bg-green-500/20 text-green-400 hover:bg-green-500/30 transition-all"
                                                                >
                                                                    <Check className="w-4 h-4" />
                                                                </button>
                                                                <button
                                                                    onClick={() => setEditingUsername(false)}
                                                                    className="p-3 rounded-xl bg-red-500/20 text-red-400 hover:bg-red-500/30 transition-all"
                                                                >
                                                                    <X className="w-4 h-4" />
                                                                </button>
                                                            </div>
                                                        ) : (
                                                            <div className="flex items-center gap-2">
                                                                <div className="flex-1 flex items-center gap-3 px-4 py-4 rounded-xl bg-white/[0.03] border border-white/5 text-white">
                                                                    <User className="w-4 h-4 text-dark-400" />
                                                                    <span className="text-sm font-bold tracking-tight">{user?.username}</span>
                                                                </div>
                                                                <button
                                                                    onClick={() => { setNewUsername(user?.username || ''); setEditingUsername(true); }}
                                                                    className="p-3 rounded-xl bg-white/5 text-dark-400 hover:bg-white/10 hover:text-white transition-all"
                                                                >
                                                                    <Pencil className="w-4 h-4" />
                                                                </button>
                                                            </div>
                                                        )}
                                                    </div>

                                                    {/* Email Field */}
                                                    <div className="space-y-2">
                                                        <label className="text-[10px] font-black text-dark-500 uppercase tracking-[0.2em] ml-1">Neural Mail</label>
                                                        {editingEmail ? (
                                                            <div className="flex items-center gap-2">
                                                                <div className="flex-1 flex items-center gap-3 px-4 py-3 rounded-xl bg-white/[0.05] border border-primary-500/50">
                                                                    <Mail className="w-4 h-4 text-primary-400" />
                                                                    <input
                                                                        type="email"
                                                                        value={newEmail}
                                                                        onChange={(e) => setNewEmail(e.target.value)}
                                                                        className="flex-1 bg-transparent text-white text-sm font-bold outline-none"
                                                                        placeholder="Enter new email"
                                                                        autoFocus
                                                                    />
                                                                </div>
                                                                <button
                                                                    onClick={saveEmail}
                                                                    disabled={savingAccount}
                                                                    className="p-3 rounded-xl bg-green-500/20 text-green-400 hover:bg-green-500/30 transition-all"
                                                                >
                                                                    <Check className="w-4 h-4" />
                                                                </button>
                                                                <button
                                                                    onClick={() => setEditingEmail(false)}
                                                                    className="p-3 rounded-xl bg-red-500/20 text-red-400 hover:bg-red-500/30 transition-all"
                                                                >
                                                                    <X className="w-4 h-4" />
                                                                </button>
                                                            </div>
                                                        ) : (
                                                            <div className="flex items-center gap-2">
                                                                <div className="flex-1 flex items-center gap-3 px-4 py-4 rounded-xl bg-white/[0.03] border border-white/5 text-white">
                                                                    <Mail className="w-4 h-4 text-dark-400" />
                                                                    <span className="text-sm font-bold tracking-tight">{user?.email}</span>
                                                                </div>
                                                                <button
                                                                    onClick={() => { setNewEmail(user?.email || ''); setEditingEmail(true); }}
                                                                    className="p-3 rounded-xl bg-white/5 text-dark-400 hover:bg-white/10 hover:text-white transition-all"
                                                                >
                                                                    <Pencil className="w-4 h-4" />
                                                                </button>
                                                            </div>
                                                        )}
                                                    </div>
                                                </div>
                                            </div>
                                        </motion.div>
                                    )}

                                    {activeTab === 'appearance' && (
                                        <motion.div
                                            key="appearance"
                                            initial={{ opacity: 0, x: 10 }}
                                            animate={{ opacity: 1, x: 0 }}
                                            exit={{ opacity: 0, x: -10 }}
                                            className="glass p-8 rounded-[2rem] border border-white/5"
                                        >
                                            <h2 className="text-xl font-bold text-white mb-2 tracking-tight">Visual Resonance</h2>
                                            <p className="text-dark-400 text-sm font-medium mb-8">Synchronize the interface with your neural preference.</p>

                                            <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
                                                <button
                                                    onClick={(e) => toggleTheme('dark', e)}
                                                    className={`group relative p-8 rounded-3xl border transition-all text-left overflow-hidden ${theme === 'dark'
                                                        ? 'border-primary-500 bg-primary-500/5 shadow-[0_15px_35px_rgba(14,165,233,0.15)]'
                                                        : 'border-white/5 bg-white/[0.02] hover:border-white/20'
                                                        }`}
                                                >
                                                    <div className="flex flex-col gap-5 relative z-10">
                                                        <div className={`w-14 h-14 rounded-2xl flex items-center justify-center transition-all ${theme === 'dark' ? 'bg-primary-500 text-white shadow-lg' : 'bg-white/5 text-dark-400'
                                                            }`}>
                                                            <Moon className="w-7 h-7" />
                                                        </div>
                                                        <div>
                                                            <p className="text-lg font-black text-white tracking-tight italic">Deep Space</p>
                                                            <p className="text-dark-500 text-xs font-bold uppercase tracking-tight">High Contrast Dark</p>
                                                        </div>
                                                    </div>
                                                </button>

                                                <button
                                                    onClick={(e) => toggleTheme('light', e)}
                                                    className={`group relative p-8 rounded-3xl border transition-all text-left overflow-hidden ${theme === 'light'
                                                        ? 'border-primary-500 bg-primary-500/5 shadow-[0_15px_35px_rgba(14,165,233,0.15)]'
                                                        : 'border-white/5 bg-white/[0.02] hover:border-white/20'
                                                        }`}
                                                >
                                                    <div className="flex flex-col gap-5 relative z-10">
                                                        <div className={`w-14 h-14 rounded-2xl flex items-center justify-center transition-all ${theme === 'light' ? 'bg-primary-500 text-white shadow-lg' : 'bg-white/5 text-dark-400'
                                                            }`}>
                                                            <Sun className="w-7 h-7" />
                                                        </div>
                                                        <div>
                                                            <p className="text-lg font-black text-white tracking-tight italic">Pure Light</p>
                                                            <p className="text-dark-500 text-xs font-bold uppercase tracking-tight">Slate Surface Light</p>
                                                        </div>
                                                    </div>
                                                </button>
                                            </div>
                                            {/* Cursor Effects Section */}
                                            <div className="mt-8 pt-8 border-t border-white/5">
                                                <h3 className="text-lg font-bold text-white mb-2">Cursor Effects</h3>
                                                <p className="text-dark-500 text-xs mb-6">Customize the visual effect that follows your cursor</p>

                                                {/* Enable/Disable Toggle */}
                                                <div className="flex items-center justify-between mb-6 p-4 rounded-2xl bg-white/[0.02] border border-white/5">
                                                    <div className="flex items-center gap-4">
                                                        <div className={`w-10 h-10 rounded-xl flex items-center justify-center transition-all ${cursorEnabled ? 'bg-primary-500/20 text-primary-400' : 'bg-white/5 text-dark-400'}`}>
                                                            <MousePointer2 className="w-4 h-4" />
                                                        </div>
                                                        <div>
                                                            <p className="text-white font-bold text-sm">Enable Cursor Effect</p>
                                                            <p className="text-dark-500 text-xs">Show visual effect around cursor</p>
                                                        </div>
                                                    </div>
                                                    <button
                                                        onClick={() => {
                                                            const newValue = !cursorEnabled;
                                                            setCursorEnabled(newValue);
                                                            toggleCursorEffect(newValue);
                                                            toast.success(newValue ? 'Cursor effect enabled' : 'Cursor effect disabled');
                                                        }}
                                                        className={`relative w-12 h-7 rounded-full transition-all ${cursorEnabled ? 'bg-primary-500' : 'bg-white/10'}`}
                                                    >
                                                        <motion.div
                                                            className="absolute top-1 w-5 h-5 bg-white rounded-full shadow-lg"
                                                            animate={{ left: cursorEnabled ? 22 : 4 }}
                                                            transition={{ type: 'spring', stiffness: 500, damping: 30 }}
                                                        />
                                                    </button>
                                                </div>

                                                {/* Effect Type Selector */}
                                                {cursorEnabled && (
                                                    <motion.div
                                                        initial={{ opacity: 0, height: 0 }}
                                                        animate={{ opacity: 1, height: 'auto' }}
                                                        exit={{ opacity: 0, height: 0 }}
                                                        className="grid grid-cols-2 md:grid-cols-3 gap-3"
                                                    >
                                                        {CURSOR_EFFECTS.map((effect) => (
                                                            <button
                                                                key={effect.id}
                                                                onClick={() => {
                                                                    setCursorEffect(effect.id);
                                                                    setCursorEffectType(effect.id);
                                                                    toast.success(`Cursor effect: ${effect.name}`);
                                                                }}
                                                                className={`p-4 rounded-xl border text-left transition-all ${cursorEffect === effect.id
                                                                    ? 'border-primary-500 bg-primary-500/10 shadow-[0_5px_20px_rgba(14,165,233,0.15)]'
                                                                    : 'border-white/5 bg-white/[0.02] hover:border-white/20'
                                                                    }`}
                                                            >
                                                                <p className={`font-bold text-sm mb-1 ${cursorEffect === effect.id ? 'text-primary-400' : 'text-white'}`}>
                                                                    {effect.name}
                                                                </p>
                                                                <p className="text-dark-500 text-xs">{effect.description}</p>
                                                            </button>
                                                        ))}
                                                    </motion.div>
                                                )}
                                            </div>
                                        </motion.div>
                                    )}

                                    {activeTab === 'api' && (
                                        <motion.div
                                            key="api"
                                            initial={{ opacity: 0, x: 10 }}
                                            animate={{ opacity: 1, x: 0 }}
                                            exit={{ opacity: 0, x: -10 }}
                                            className="glass p-8 rounded-[2rem] border border-white/5"
                                        >
                                            <div className="flex items-center gap-3 mb-3">
                                                <h2 className="text-2xl font-black text-white tracking-tighter italic uppercase">Neural Keys</h2>
                                                <span className="px-2.5 py-1 rounded-lg bg-primary-500/10 text-primary-400 border border-primary-500/20 text-[10px] font-black uppercase tracking-widest">Inference Core</span>
                                            </div>
                                            <p className="text-dark-400 text-sm font-medium mb-10">Manage the cryptographic tokens used for agent orchestration.</p>

                                            <div className="p-8 rounded-3xl bg-white/[0.02] border border-white/5 relative group">
                                                <div className="flex items-center justify-between gap-6">
                                                    <div className="flex-1">
                                                        <p className="text-[10px] font-black text-dark-500 uppercase tracking-[0.2em] mb-3 ml-1">Groq API Key</p>
                                                        <div className="flex items-center gap-4 bg-black/20 p-4 rounded-xl border border-white/5">
                                                            <Key className="w-5 h-5 text-primary-400" />
                                                            <code className="text-primary-400 font-mono text-sm tracking-widest break-all">
                                                                {showApiKey ? apiKey : '••••••••••••••••••••••••••••••••'}
                                                            </code>
                                                        </div>
                                                    </div>
                                                    <button
                                                        onClick={showApiKey ? () => setShowApiKey(false) : fetchApiKey}
                                                        className="h-14 w-14 bg-white/5 hover:bg-white/10 rounded-2xl transition-all text-white flex items-center justify-center active:scale-90 shadow-inner group/btn"
                                                    >
                                                        {showApiKey ? <EyeOff className="w-6 h-6 group-hover/btn:text-primary-400 transition-colors" /> : <Eye className="w-6 h-6 group-hover/btn:text-primary-400 transition-colors" />}
                                                    </button>
                                                </div>
                                            </div>

                                            <div className="mt-8 p-6 rounded-2xl bg-primary-500/5 border border-primary-500/10 flex items-start gap-5">
                                                <Shield className="w-6 h-6 text-primary-400 mt-0.5 shrink-0" />
                                                <p className="text-xs text-dark-400 font-bold leading-relaxed uppercase tracking-tight">
                                                    Nexus AI utilizes AES-256 binary encryption. Your keys never leave the secure inference tunnel.
                                                </p>
                                            </div>
                                        </motion.div>
                                    )}

                                    {activeTab === 'security' && (
                                        <motion.div
                                            key="security"
                                            initial={{ opacity: 0, x: 10 }}
                                            animate={{ opacity: 1, x: 0 }}
                                            exit={{ opacity: 0, x: -10 }}
                                            className="glass p-8 rounded-[2rem] border border-white/5"
                                        >
                                            <h2 className="text-xl font-bold text-white mb-2 tracking-tight">Security Protocol</h2>
                                            <p className="text-dark-400 text-sm font-medium mb-8">Manage your authentication and security preferences.</p>

                                            <div className="space-y-6">
                                                {/* Two-Factor Authentication */}
                                                <div className="p-5 rounded-2xl bg-white/[0.02] border border-white/5">
                                                    <div className="flex items-center justify-between">
                                                        <div className="flex items-center gap-4">
                                                            <div className="w-12 h-12 rounded-xl bg-primary-500/10 flex items-center justify-center">
                                                                <Shield className="w-6 h-6 text-primary-400" />
                                                            </div>
                                                            <div>
                                                                <p className="text-white font-bold">Two-Factor Authentication</p>
                                                                <p className="text-dark-400 text-sm">Add an extra layer of security</p>
                                                            </div>
                                                        </div>
                                                        <button className="px-4 py-2 bg-primary-500 hover:bg-primary-400 text-white font-bold text-sm rounded-xl transition-colors">
                                                            Enable
                                                        </button>
                                                    </div>
                                                </div>

                                                {/* Change Password */}
                                                <div className="p-5 rounded-2xl bg-white/[0.02] border border-white/5">
                                                    <div className="flex items-center gap-4 mb-4">
                                                        <div className="w-12 h-12 rounded-xl bg-purple-500/10 flex items-center justify-center">
                                                            <Key className="w-6 h-6 text-purple-400" />
                                                        </div>
                                                        <div>
                                                            <p className="text-white font-bold">Change Password</p>
                                                            <p className="text-dark-400 text-sm">Update your password regularly</p>
                                                        </div>
                                                    </div>
                                                    <div className="space-y-4 mt-4">
                                                        <input
                                                            type="password"
                                                            placeholder="Current password"
                                                            className="w-full px-4 py-3 bg-white/[0.03] border border-white/5 rounded-xl text-white placeholder-dark-500 focus:outline-none focus:border-primary-500/50"
                                                        />
                                                        <input
                                                            type="password"
                                                            placeholder="New password"
                                                            className="w-full px-4 py-3 bg-white/[0.03] border border-white/5 rounded-xl text-white placeholder-dark-500 focus:outline-none focus:border-primary-500/50"
                                                        />
                                                        <input
                                                            type="password"
                                                            placeholder="Confirm new password"
                                                            className="w-full px-4 py-3 bg-white/[0.03] border border-white/5 rounded-xl text-white placeholder-dark-500 focus:outline-none focus:border-primary-500/50"
                                                        />
                                                        <button className="w-full py-3 bg-white/5 hover:bg-white/10 text-white font-bold rounded-xl transition-colors">
                                                            Update Password
                                                        </button>
                                                    </div>
                                                </div>

                                                {/* Active Sessions */}
                                                <div className="p-5 rounded-2xl bg-white/[0.02] border border-white/5">
                                                    <div className="flex items-center justify-between mb-4">
                                                        <div className="flex items-center gap-4">
                                                            <div className="w-12 h-12 rounded-xl bg-emerald-500/10 flex items-center justify-center">
                                                                <Zap className="w-6 h-6 text-emerald-400" />
                                                            </div>
                                                            <div>
                                                                <p className="text-white font-bold">Active Sessions</p>
                                                                <p className="text-dark-400 text-sm">1 device currently logged in</p>
                                                            </div>
                                                        </div>
                                                    </div>
                                                    <div className="p-4 rounded-xl bg-black/20 border border-white/5 flex items-center justify-between">
                                                        <div>
                                                            <p className="text-sm font-bold text-white">Current Session</p>
                                                            <p className="text-xs text-dark-500">Windows • Chrome • Active now</p>
                                                        </div>
                                                        <span className="px-2 py-1 bg-emerald-500/10 text-emerald-400 text-xs font-bold rounded-lg">Current</span>
                                                    </div>
                                                </div>
                                            </div>
                                        </motion.div>
                                    )}

                                    {activeTab === 'notifications' && (
                                        <motion.div
                                            key="notifications"
                                            initial={{ opacity: 0, x: 10 }}
                                            animate={{ opacity: 1, x: 0 }}
                                            exit={{ opacity: 0, x: -10 }}
                                            className="glass p-8 rounded-[2rem] border border-white/5"
                                        >
                                            <h2 className="text-xl font-bold text-white mb-2 tracking-tight">Notification Preferences</h2>
                                            <p className="text-dark-400 text-sm font-medium mb-8">Control how and when you receive notifications.</p>

                                            <div className="space-y-4">
                                                {[
                                                    { key: 'notify_task', label: 'Task Completion', desc: 'Get notified when AI tasks complete' },
                                                    { key: 'notify_agent', label: 'Agent Status', desc: 'Updates when agents come online/offline' },
                                                    { key: 'notify_project', label: 'Project Updates', desc: 'Progress updates on your projects' },
                                                    { key: 'notify_system', label: 'System Alerts', desc: 'Important system and API alerts' },
                                                    { key: 'notify_weekly', label: 'Weekly Summary', desc: 'Weekly digest of your activity' },
                                                    { key: 'notify_marketing', label: 'Marketing', desc: 'Product updates and announcements' },
                                                ].map((item) => {
                                                    const isEnabled = user?.settings?.[item.key] ?? false;

                                                    const handleToggle = async () => {
                                                        const newValue = !isEnabled;
                                                        try {
                                                            await api.put('/auth/me', {
                                                                settings: { [item.key]: newValue }
                                                            });
                                                            if (refreshUser) refreshUser();
                                                            toast.success(`${item.label} ${newValue ? 'enabled' : 'disabled'}`);
                                                        } catch (error) {
                                                            toast.error('Failed to update setting');
                                                        }
                                                    };

                                                    return (
                                                        <div key={item.key} className="p-5 rounded-2xl bg-white/[0.02] border border-white/5 flex items-center justify-between">
                                                            <div>
                                                                <p className="text-white font-bold">{item.label}</p>
                                                                <p className="text-dark-400 text-sm">{item.desc}</p>
                                                            </div>
                                                            <button
                                                                onClick={handleToggle}
                                                                className={`w-14 h-8 rounded-full transition-colors relative ${isEnabled ? 'bg-primary-500' : 'bg-white/10'}`}
                                                            >
                                                                <motion.div
                                                                    className="w-6 h-6 bg-white rounded-full absolute top-1 shadow-lg"
                                                                    animate={{ left: isEnabled ? 28 : 4 }}
                                                                    transition={{ type: 'spring', stiffness: 500, damping: 30 }}
                                                                />
                                                            </button>
                                                        </div>
                                                    );
                                                })}
                                            </div>
                                        </motion.div>
                                    )}
                                </AnimatePresence>
                            </div>
                        </div>
                    </motion.div>
                </main>
            </div>
        </div>
    );
}
