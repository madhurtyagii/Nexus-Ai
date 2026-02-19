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
    AlertTriangle,
    Command
} from 'lucide-react';

export default function Navbar() {
    const { user, logout } = useAuth();
    const navigate = useNavigate();
    const [showNotifications, setShowNotifications] = useState(false);
    const [showAccountMenu, setShowAccountMenu] = useState(false);
    const [scrolled, setScrolled] = useState(false);
    const notificationRef = useRef(null);
    const accountRef = useRef(null);

    // Track scroll for dynamic border
    useEffect(() => {
        const handleScroll = () => setScrolled(window.scrollY > 10);
        window.addEventListener('scroll', handleScroll, { passive: true });
        return () => window.removeEventListener('scroll', handleScroll);
    }, []);

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
            transition={{ type: 'spring', stiffness: 300, damping: 30 }}
            className={`h-[72px] glass px-6 flex items-center justify-between sticky top-0 z-50 m-4 rounded-2xl transition-all duration-500 ${scrolled
                ? 'border-b-2 border-transparent shadow-lg'
                : 'border-b border-border'
                }`}
            style={{
                borderImage: scrolled
                    ? 'linear-gradient(90deg, transparent, rgba(14, 165, 233, 0.3), rgba(139, 92, 246, 0.3), transparent) 1'
                    : 'none',
            }}
        >
            {/* Logo */}
            <Link to="/dashboard" className="flex items-center gap-3 group">
                <div className="relative">
                    <motion.div
                        className="w-10 h-10 rounded-xl flex items-center justify-center overflow-hidden bg-gradient-to-br from-primary-500/20 to-purple-500/20 p-0.5"
                        whileHover={{ scale: 1.08, rotate: 3 }}
                        transition={{ type: 'spring', stiffness: 400, damping: 17 }}
                    >
                        <img src="/logo.png" alt="Nexus AI" className="w-full h-full object-contain rounded-lg" />
                    </motion.div>

                    {/* Logo glow */}
                    <div className="absolute inset-0 rounded-xl opacity-40 group-hover:opacity-70 transition-opacity"
                        style={{ boxShadow: '0 0 20px rgba(14, 165, 233, 0.3)' }}
                    />
                </div>

                <div className="flex flex-col">
                    <span className="text-lg font-black tracking-tighter text-text-primary leading-none">
                        Nexus AI
                    </span>
                    <span className="text-[9px] uppercase tracking-[0.2em] font-bold mt-0.5 gradient-text">
                        Intelligence v2.0
                    </span>
                </div>
            </Link>

            {/* Right Section */}
            <div className="flex items-center gap-3">
                {/* Search Bar */}
                <motion.button
                    onClick={() => {
                        const event = new KeyboardEvent('keydown', {
                            key: 'k',
                            ctrlKey: true,
                            metaKey: true,
                            bubbles: true
                        });
                        document.dispatchEvent(event);
                    }}
                    className="hidden md:flex items-center gap-2.5 px-4 py-2 rounded-xl bg-white/[0.03] border border-white/[0.06] text-dark-500 hover:text-dark-300 hover:bg-white/[0.06] hover:border-white/10 transition-all cursor-pointer group"
                    whileHover={{ scale: 1.02 }}
                    whileTap={{ scale: 0.98 }}
                >
                    <Search className="w-3.5 h-3.5 group-hover:text-primary-400 transition-colors" />
                    <span className="text-xs font-medium">Search anything...</span>
                    <div className="flex items-center gap-0.5 ml-4 opacity-30">
                        <kbd className="text-[9px] px-1.5 py-0.5 rounded bg-white/10 font-mono">⌘</kbd>
                        <kbd className="text-[9px] px-1.5 py-0.5 rounded bg-white/10 font-mono">K</kbd>
                    </div>
                </motion.button>

                <div className="h-5 w-px bg-border mx-1 hidden md:block" />

                <div className="flex items-center gap-2">
                    {/* Notifications */}
                    <div className="relative" ref={notificationRef}>
                        <motion.button
                            onClick={() => {
                                setShowNotifications(!showNotifications);
                                setShowAccountMenu(false);
                            }}
                            className="p-2.5 text-dark-400 hover:text-primary-400 hover:bg-primary-500/10 rounded-xl transition-all relative"
                            whileHover={{ scale: 1.05 }}
                            whileTap={{ scale: 0.95 }}
                        >
                            <Bell className="w-[18px] h-[18px]" />
                            {/* Animated notification badge */}
                            <motion.span
                                className="absolute top-2 right-2 w-2 h-2 bg-primary-500 rounded-full"
                                animate={{ scale: [1, 1.3, 1] }}
                                transition={{ duration: 2, repeat: Infinity }}
                                style={{ boxShadow: '0 0 6px rgba(14, 165, 233, 0.6)' }}
                            />
                        </motion.button>

                        <AnimatePresence>
                            {showNotifications && (
                                <motion.div
                                    initial={{ opacity: 0, y: 8, scale: 0.96 }}
                                    animate={{ opacity: 1, y: 0, scale: 1 }}
                                    exit={{ opacity: 0, y: 8, scale: 0.96 }}
                                    transition={{ type: 'spring', stiffness: 400, damping: 25 }}
                                    className="absolute right-0 top-full mt-2 w-80 glass rounded-2xl border border-border shadow-2xl overflow-hidden z-50"
                                >
                                    <div className="px-4 py-3 border-b border-white/5 flex items-center justify-between">
                                        <h3 className="text-sm font-bold text-white">Notifications</h3>
                                        <span className="text-[10px] font-bold text-primary-400 uppercase tracking-wider bg-primary-500/10 px-2 py-0.5 rounded-full">
                                            {notifications.length} New
                                        </span>
                                    </div>
                                    <div className="max-h-80 overflow-y-auto">
                                        {notifications.map((notif, i) => (
                                            <motion.div
                                                key={notif.id}
                                                initial={{ opacity: 0, x: -10 }}
                                                animate={{ opacity: 1, x: 0 }}
                                                transition={{ delay: i * 0.05 }}
                                                className="px-4 py-3 hover:bg-white/[0.03] transition-colors cursor-pointer border-b border-white/[0.03] last:border-0"
                                            >
                                                <div className="flex items-start gap-3">
                                                    <div className="p-1.5 rounded-lg bg-white/5 mt-0.5">
                                                        {getNotificationIcon(notif.type)}
                                                    </div>
                                                    <div className="flex-1 min-w-0">
                                                        <p className="text-sm font-semibold text-white">{notif.title}</p>
                                                        <p className="text-xs text-dark-400 line-clamp-1 mt-0.5">{notif.message}</p>
                                                        <p className="text-[10px] text-dark-600 mt-1">{notif.time}</p>
                                                    </div>
                                                </div>
                                            </motion.div>
                                        ))}
                                    </div>
                                    <div className="px-4 py-2.5 border-t border-white/5">
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
                        <motion.button
                            onClick={() => {
                                setShowAccountMenu(!showAccountMenu);
                                setShowNotifications(false);
                            }}
                            className="flex items-center gap-3 pl-1 pr-1 py-1 rounded-full transition-all group/profile"
                            whileHover={{ scale: 1.02 }}
                            whileTap={{ scale: 0.98 }}
                        >
                            {/* Animated gradient ring avatar */}
                            <div className="relative group-hover/profile:scale-105 transition-transform duration-300">
                                <div
                                    className="w-9 h-9 rounded-full bg-gradient-to-br from-primary-500 via-purple-500 to-pink-500 flex items-center justify-center overflow-hidden transition-all duration-300 relative z-10"
                                    style={{
                                        boxShadow: '0 4px 10px rgba(0,0,0,0.1)', // Default subtle shadow
                                    }}
                                >
                                    <div className="absolute inset-0 bg-white/0 group-hover/profile:bg-white/10 transition-colors duration-300" />
                                    <User className="w-5 h-5 text-white relative z-10" fill="rgba(255,255,255,0.2)" />
                                </div>

                                {/* Pure CSS Glow using box-shadow on a pseudo-element equivalent (absolute div) to ensure perfect circle */}
                                <div
                                    className="absolute inset-0 rounded-full opacity-0 group-hover/profile:opacity-100 transition-opacity duration-300 -z-10"
                                    style={{
                                        boxShadow: '0 0 15px 2px rgba(139, 92, 246, 0.6), 0 0 30px 5px rgba(14, 165, 233, 0.3)',
                                    }}
                                />
                            </div>

                            <div className="hidden sm:block text-left mr-2">
                                <p className="text-sm font-bold text-white leading-none group-hover/profile:text-primary-400 transition-colors">{user?.username}</p>
                                <p className="text-[10px] text-dark-500 font-medium mt-0.5">Pro Developer</p>
                            </div>
                            <ChevronDown className={`w-3.5 h-3.5 text-dark-500 transition-transform duration-300 group-hover/profile:text-white ${showAccountMenu ? 'rotate-180' : ''}`} />
                        </motion.button>

                        <AnimatePresence>
                            {showAccountMenu && (
                                <motion.div
                                    initial={{ opacity: 0, y: 8, scale: 0.96 }}
                                    animate={{ opacity: 1, y: 0, scale: 1 }}
                                    exit={{ opacity: 0, y: 8, scale: 0.96 }}
                                    transition={{ type: 'spring', stiffness: 400, damping: 25 }}
                                    className="absolute right-0 top-full mt-2 w-64 glass rounded-2xl border border-border shadow-2xl overflow-hidden z-50"
                                >
                                    <div className="px-5 py-5 border-b border-white/5 bg-white/[0.02]">
                                        <div className="flex items-center gap-4">
                                            <div className="w-12 h-12 rounded-full bg-gradient-to-br from-primary-500 via-purple-500 to-pink-500 flex items-center justify-center shadow-lg shadow-purple-500/20">
                                                <User className="w-6 h-6 text-white" fill="rgba(255,255,250,0.2)" />
                                            </div>
                                            <div>
                                                <p className="text-sm font-bold text-white">{user?.username}</p>
                                                <p className="text-xs text-dark-500">{user?.email}</p>
                                            </div>
                                        </div>
                                    </div>

                                    <div className="py-1.5">
                                        {accountMenuItems.map((item, i) => (
                                            <motion.button
                                                key={item.label}
                                                initial={{ opacity: 0, x: -8 }}
                                                animate={{ opacity: 1, x: 0 }}
                                                transition={{ delay: i * 0.04 }}
                                                onClick={() => {
                                                    item.action();
                                                    setShowAccountMenu(false);
                                                }}
                                                className="w-full flex items-center gap-3 px-4 py-2.5 text-dark-400 hover:text-white hover:bg-white/[0.04] transition-all"
                                            >
                                                <item.icon className="w-4 h-4" />
                                                <span className="text-sm font-medium">{item.label}</span>
                                            </motion.button>
                                        ))}
                                    </div>

                                    <div className="border-t border-white/5 py-1.5">
                                        <button
                                            onClick={() => {
                                                handleLogout();
                                                setShowAccountMenu(false);
                                            }}
                                            className="w-full flex items-center gap-3 px-4 py-2.5 text-red-400 hover:bg-red-500/10 transition-all"
                                        >
                                            <LogOut className="w-4 h-4" />
                                            <span className="text-sm font-medium">Log out</span>
                                        </button>
                                    </div>
                                </motion.div>
                            )}
                        </AnimatePresence>
                    </div>

                    {/* Logout button */}
                    <motion.button
                        onClick={handleLogout}
                        className="p-2.5 text-dark-400 hover:text-red-400 hover:bg-red-500/10 rounded-xl transition-all"
                        title="Logout"
                        whileHover={{ scale: 1.05 }}
                        whileTap={{ scale: 0.95 }}
                    >
                        <LogOut className="w-[18px] h-[18px]" />
                    </motion.button>
                </div>
            </div>
        </motion.nav>
    );
}
