import { useState, useRef, useEffect } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import { motion, AnimatePresence } from 'framer-motion';
import {
    LogOut,
    Bell,
    Search,
    ChevronDown,
    Settings,
    User,
    HelpCircle,
    Zap,
    CheckCircle2,
    Info,
    AlertTriangle
} from 'lucide-react';

export default function Navbar() {
    const { user, logout } = useAuth();
    const navigate = useNavigate();
    const [showNotifications, setShowNotifications] = useState(false);
    const [showAccountMenu, setShowAccountMenu] = useState(false);
    const notificationRef = useRef(null);
    const accountRef = useRef(null);

    // Close dropdowns when clicking outside
    useEffect(() => {
        const handleClickOutside = (event) => {
            if (notificationRef.current && !notificationRef.current.contains(event.target)) {
                setShowNotifications(false);
            }
            if (accountRef.current && !accountRef.current.contains(event.target)) {
                setShowAccountMenu(false);
            }
        };
        document.addEventListener('mousedown', handleClickOutside);
        return () => document.removeEventListener('mousedown', handleClickOutside);
    }, []);

    const handleLogout = () => {
        logout();
        navigate('/login');
    };

    // Sample notifications
    const notifications = [
        { id: 1, type: 'success', title: 'Task Completed', message: 'Your AI task finished successfully', time: '2m ago' },
        { id: 2, type: 'info', title: 'New Agent Online', message: 'Research Agent is now available', time: '10m ago' },
        { id: 3, type: 'warning', title: 'API Limit', message: 'Approaching daily usage limit', time: '1h ago' },
    ];

    const getNotificationIcon = (type) => {
        switch (type) {
            case 'success': return <CheckCircle2 className="w-4 h-4 text-emerald-400" />;
            case 'warning': return <AlertTriangle className="w-4 h-4 text-amber-400" />;
            default: return <Info className="w-4 h-4 text-primary-400" />;
        }
    };

    const accountMenuItems = [
        { label: 'My Account', icon: User, action: () => navigate('/settings') },
        { label: 'Settings', icon: Settings, action: () => navigate('/settings') },
        { label: 'Help & Support', icon: HelpCircle, action: () => navigate('/help') },
    ];

    return (
        <motion.nav
            initial={{ y: -20, opacity: 0 }}
            animate={{ y: 0, opacity: 1 }}
            className="h-[76px] glass border-b border-white/5 px-6 flex items-center justify-between sticky top-0 z-50 m-4 rounded-3xl"
        >
            <Link to="/dashboard" className="flex items-center gap-3 group">
                <div className="w-11 h-11 rounded-xl flex items-center justify-center shadow-[0_0_25px_rgba(14,165,233,0.4)] group-hover:scale-105 transition-transform overflow-hidden bg-gradient-to-br from-primary-500/20 to-purple-500/20 p-0.5">
                    <img src="/logo.png" alt="Nexus AI" className="w-full h-full object-contain rounded-lg" />
                </div>
                <div className="flex flex-col">
                    <span className="text-xl font-black tracking-tighter text-white leading-none">Nexus AI</span>
                    <span className="text-[10px] uppercase tracking-[0.15em] text-primary-400 font-bold mt-0.5">Intelligence v2.0</span>
                </div>
            </Link>

            <div className="flex items-center gap-5">
                {/* Search Button - Triggers Command Palette */}
                <button
                    onClick={() => {
                        const event = new KeyboardEvent('keydown', {
                            key: 'k',
                            ctrlKey: true,
                            metaKey: true,
                            bubbles: true
                        });
                        document.dispatchEvent(event);
                    }}
                    className="hidden md:flex items-center gap-2 px-3 py-1.5 rounded-full bg-white/[0.03] border border-white/5 text-dark-400 hover:text-white hover:bg-white/5 transition-all cursor-pointer"
                >
                    <Search className="w-4 h-4" />
                    <span className="text-xs font-medium">Search anything...</span>
                    <kbd className="text-[10px] opacity-40 ml-4 px-1.5 py-0.5 rounded bg-white/10 uppercase">⌘K</kbd>
                </button>

                <div className="h-6 w-px bg-white/5 mx-2 hidden md:block" />

                <div className="flex items-center gap-4">
                    {/* Notifications Dropdown */}
                    <div className="relative" ref={notificationRef}>
                        <button
                            onClick={() => {
                                setShowNotifications(!showNotifications);
                                setShowAccountMenu(false);
                            }}
                            className="p-2 text-dark-400 hover:text-primary-400 hover:bg-primary-500/10 rounded-xl transition-all relative group/btn"
                        >
                            <Bell className="w-5 h-5" />
                            <span className="absolute top-2 right-2 w-2 h-2 bg-primary-500 rounded-full border-2 border-dark-900 group-hover/btn:scale-125 transition-transform" />
                        </button>

                        <AnimatePresence>
                            {showNotifications && (
                                <motion.div
                                    initial={{ opacity: 0, y: 10, scale: 0.95 }}
                                    animate={{ opacity: 1, y: 0, scale: 1 }}
                                    exit={{ opacity: 0, y: 10, scale: 0.95 }}
                                    className="absolute right-0 top-full mt-2 w-80 glass rounded-2xl border border-white/10 shadow-2xl overflow-hidden z-50"
                                >
                                    <div className="px-4 py-3 border-b border-white/5 flex items-center justify-between">
                                        <h3 className="text-sm font-bold text-white">Notifications</h3>
                                        <span className="text-[10px] font-bold text-primary-400 uppercase tracking-wider">
                                            {notifications.length} New
                                        </span>
                                    </div>
                                    <div className="max-h-80 overflow-y-auto">
                                        {notifications.map((notif) => (
                                            <div
                                                key={notif.id}
                                                className="px-4 py-3 hover:bg-white/5 transition-colors cursor-pointer border-b border-white/5 last:border-0"
                                            >
                                                <div className="flex items-start gap-3">
                                                    <div className="p-1.5 rounded-lg bg-white/5">
                                                        {getNotificationIcon(notif.type)}
                                                    </div>
                                                    <div className="flex-1 min-w-0">
                                                        <p className="text-sm font-bold text-white">{notif.title}</p>
                                                        <p className="text-xs text-dark-400 line-clamp-1">{notif.message}</p>
                                                        <p className="text-[10px] text-dark-500 mt-1">{notif.time}</p>
                                                    </div>
                                                </div>
                                            </div>
                                        ))}
                                    </div>
                                    <div className="px-4 py-3 border-t border-white/5">
                                        <button
                                            onClick={() => {
                                                navigate('/settings');
                                                setShowNotifications(false);
                                            }}
                                            className="w-full text-center text-xs font-bold text-primary-400 hover:text-primary-300 transition-colors"
                                        >
                                            View All Notifications
                                        </button>
                                    </div>
                                </motion.div>
                            )}
                        </AnimatePresence>
                    </div>

                    {/* Account Dropdown */}
                    <div className="relative" ref={accountRef}>
                        <button
                            onClick={() => {
                                setShowAccountMenu(!showAccountMenu);
                                setShowNotifications(false);
                            }}
                            className="flex items-center gap-3 pl-1 pr-3 py-1 bg-white/[0.02] hover:bg-white/[0.05] border border-white/5 rounded-full transition-all group/profile"
                        >
                            <div className="w-8 h-8 rounded-full bg-gradient-to-br from-primary-500 to-purple-600 flex items-center justify-center text-xs font-bold text-white shadow-lg overflow-hidden relative">
                                <div className="absolute inset-0 bg-white/10 opacity-0 group-hover/profile:opacity-100 transition-opacity" />
                                {user?.username?.[0]?.toUpperCase() || 'U'}
                            </div>
                            <div className="hidden sm:block text-left">
                                <p className="text-xs font-bold text-white leading-none">{user?.username}</p>
                                <p className="text-[10px] text-dark-400 font-medium mt-0.5">Pro Developer</p>
                            </div>
                            <ChevronDown className={`w-3.5 h-3.5 text-dark-500 transition-transform ${showAccountMenu ? 'rotate-180' : ''}`} />
                        </button>

                        <AnimatePresence>
                            {showAccountMenu && (
                                <motion.div
                                    initial={{ opacity: 0, y: 10, scale: 0.95 }}
                                    animate={{ opacity: 1, y: 0, scale: 1 }}
                                    exit={{ opacity: 0, y: 10, scale: 0.95 }}
                                    className="absolute right-0 top-full mt-2 w-56 glass rounded-2xl border border-white/10 shadow-2xl overflow-hidden z-50"
                                >
                                    {/* User Info Header */}
                                    <div className="px-4 py-4 border-b border-white/5">
                                        <div className="flex items-center gap-3">
                                            <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-primary-500 to-purple-600 flex items-center justify-center text-sm font-bold text-white">
                                                {user?.username?.[0]?.toUpperCase() || 'U'}
                                            </div>
                                            <div>
                                                <p className="text-sm font-bold text-white">{user?.username}</p>
                                                <p className="text-xs text-dark-400">{user?.email}</p>
                                            </div>
                                        </div>
                                    </div>

                                    {/* Menu Items */}
                                    <div className="py-2">
                                        {accountMenuItems.map((item) => (
                                            <button
                                                key={item.label}
                                                onClick={() => {
                                                    item.action();
                                                    setShowAccountMenu(false);
                                                }}
                                                className="w-full flex items-center gap-3 px-4 py-2.5 text-dark-300 hover:text-white hover:bg-white/5 transition-colors"
                                            >
                                                <item.icon className="w-4 h-4" />
                                                <span className="text-sm font-medium">{item.label}</span>
                                            </button>
                                        ))}
                                    </div>

                                    {/* Logout */}
                                    <div className="border-t border-white/5 py-2">
                                        <button
                                            onClick={() => {
                                                handleLogout();
                                                setShowAccountMenu(false);
                                            }}
                                            className="w-full flex items-center gap-3 px-4 py-2.5 text-red-400 hover:bg-red-500/10 transition-colors"
                                        >
                                            <LogOut className="w-4 h-4" />
                                            <span className="text-sm font-medium">Log out</span>
                                        </button>
                                    </div>
                                </motion.div>
                            )}
                        </AnimatePresence>
                    </div>

                    <button
                        onClick={handleLogout}
                        className="p-2 text-dark-400 hover:text-red-400 hover:bg-red-500/10 rounded-xl transition-all"
                        title="Logout"
                    >
                        <LogOut className="w-5 h-5" />
                    </button>
                </div>
            </div>
        </motion.nav>
    );
}
