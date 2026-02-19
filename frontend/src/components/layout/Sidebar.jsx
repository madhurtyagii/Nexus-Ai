import { NavLink } from 'react-router-dom';
import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
    LayoutDashboard,
    ClipboardList,
    UserCircle2,
    FolderTree,
    GitBranch,
    Settings,
    HelpCircle,
    Activity,
    Database,
    Users,
    MessageSquareQuote,
    Image,
    PanelLeftClose,
    PanelLeft,
    Sparkles,
    Zap
} from 'lucide-react';

const navGroups = [
    {
        label: 'Core',
        items: [
            { path: '/dashboard', label: 'Dashboard', icon: LayoutDashboard },
            { path: '/tasks', label: 'Tasks', icon: ClipboardList },
            { path: '/agents', label: 'Agents', icon: UserCircle2 },
            { path: '/projects', label: 'Projects', icon: FolderTree },
        ]
    },
    {
        label: 'Tools',
        items: [
            { path: '/files', label: 'Ask Your Files', icon: MessageSquareQuote },
            { path: '/workflow-builder', label: 'Workflows', icon: GitBranch },
        ]
    },
    {
        label: 'System',
        items: [
            { path: '/settings', label: 'Settings', icon: Settings },
            { path: '/help', label: 'Help', icon: HelpCircle },
        ]
    }
];

const sidebarVariants = {
    expanded: { width: 280 },
    collapsed: { width: 72 },
};

export default function Sidebar() {
    const [collapsed, setCollapsed] = useState(false);

    // Persist collapsed state
    useEffect(() => {
        const saved = localStorage.getItem('nexus_sidebar_collapsed');
        if (saved === 'true') setCollapsed(true);
    }, []);

    const toggleCollapse = () => {
        setCollapsed(prev => {
            localStorage.setItem('nexus_sidebar_collapsed', String(!prev));
            return !prev;
        });
    };

    return (
        <motion.aside
            variants={sidebarVariants}
            animate={collapsed ? 'collapsed' : 'expanded'}
            transition={{ type: 'spring', stiffness: 300, damping: 30 }}
            className="min-h-[calc(100vh-76px)] glass border-r border-border p-3 hidden lg:flex flex-col m-4 rounded-3xl sticky top-[80px] overflow-hidden"
        >
            {/* Collapse Toggle */}
            <button
                onClick={toggleCollapse}
                className="flex items-center justify-center w-full p-2 mb-2 rounded-xl text-dark-500 hover:text-text-primary hover:bg-bg-secondary transition-all duration-300 group"
                title={collapsed ? 'Expand sidebar' : 'Collapse sidebar'}
            >
                {collapsed ? (
                    <PanelLeft className="w-5 h-5 group-hover:text-primary-400 transition-colors" />
                ) : (
                    <div className="flex items-center justify-between w-full px-1">
                        <span className="text-[10px] uppercase tracking-[0.2em] font-bold text-dark-600">Navigation</span>
                        <PanelLeftClose className="w-4 h-4 group-hover:text-primary-400 transition-colors" />
                    </div>
                )}
            </button>

            {/* Nav Groups */}
            <nav className="flex-1 space-y-4">
                {navGroups.map((group, groupIdx) => (
                    <div key={group.label}>
                        {/* Group Label */}
                        <AnimatePresence>
                            {!collapsed && (
                                <motion.div
                                    initial={{ opacity: 0 }}
                                    animate={{ opacity: 1 }}
                                    exit={{ opacity: 0 }}
                                    className="px-3 mb-2"
                                >
                                    <span className="text-[10px] uppercase tracking-[0.2em] font-bold text-dark-600">{group.label}</span>
                                </motion.div>
                            )}
                        </AnimatePresence>

                        {/* Items */}
                        <div className="space-y-0.5">
                            {group.items.map((item) => (
                                <NavLink
                                    key={item.path}
                                    to={item.path}
                                    title={collapsed ? item.label : undefined}
                                    className={({ isActive }) =>
                                        `group flex items-center gap-3 px-3 py-2.5 rounded-xl transition-all duration-300 relative overflow-hidden ${collapsed ? 'justify-center' : ''
                                        } ${isActive
                                            ? 'text-white bg-primary-500/10'
                                            : 'text-dark-400 hover:text-text-primary hover:bg-bg-secondary'
                                        }`
                                    }
                                >
                                    {({ isActive }) => (
                                        <>
                                            {/* Active Indicator + Glow */}
                                            {isActive && (
                                                <motion.div
                                                    layoutId="sidebar-active"
                                                    className="absolute inset-0 rounded-xl"
                                                    style={{
                                                        background: 'linear-gradient(135deg, rgba(14, 165, 233, 0.08), rgba(139, 92, 246, 0.05))',
                                                        boxShadow: 'inset 0 0 20px rgba(14, 165, 233, 0.05)',
                                                    }}
                                                    initial={false}
                                                    transition={{ type: "spring", stiffness: 350, damping: 30 }}
                                                />
                                            )}

                                            {/* Left accent bar */}
                                            {isActive && (
                                                <motion.div
                                                    layoutId="sidebar-accent"
                                                    className="absolute left-0 top-1/2 -translate-y-1/2 w-[3px] h-5 bg-gradient-to-b from-primary-400 to-purple-500 rounded-full"
                                                    initial={{ opacity: 0, scaleY: 0 }}
                                                    animate={{ opacity: 1, scaleY: 1 }}
                                                    transition={{ type: "spring", stiffness: 300, damping: 25 }}
                                                    style={{ boxShadow: '0 0 8px rgba(14, 165, 233, 0.5)' }}
                                                />
                                            )}

                                            <item.icon className={`w-[18px] h-[18px] relative z-10 transition-all duration-300 ${isActive
                                                ? 'text-primary-400'
                                                : 'text-dark-500 group-hover:text-dark-200 group-hover:scale-110'
                                                }`}
                                            />

                                            <AnimatePresence>
                                                {!collapsed && (
                                                    <motion.span
                                                        initial={{ opacity: 0, x: -10 }}
                                                        animate={{ opacity: 1, x: 0 }}
                                                        exit={{ opacity: 0, x: -10 }}
                                                        className={`text-sm font-medium relative z-10 whitespace-nowrap ${isActive ? 'text-text-primary' : ''}`}
                                                    >
                                                        {item.label}
                                                    </motion.span>
                                                )}
                                            </AnimatePresence>
                                        </>
                                    )}
                                </NavLink>
                            ))}
                        </div>

                        {/* Group Separator */}
                        {groupIdx < navGroups.length - 1 && (
                            <div className={`mt-3 mx-3 h-px bg-gradient-to-r from-transparent via-border to-transparent`} />
                        )}
                    </div>
                ))}
            </nav>

            {/* Gallery Toggle */}
            <div className="mt-3 px-1">
                <button
                    onClick={() => window.dispatchEvent(new CustomEvent('toggle-image-gallery'))}
                    className={`w-full flex items-center gap-3 px-3 py-2.5 rounded-xl text-dark-400 hover:text-white transition-all duration-300 group relative overflow-hidden ${collapsed ? 'justify-center' : ''}`}
                >
                    <div className="absolute inset-0 bg-gradient-to-r from-primary-500/5 to-purple-500/5 opacity-0 group-hover:opacity-100 transition-opacity rounded-xl" />
                    <Image className="w-[18px] h-[18px] text-primary-400 relative z-10 transition-transform group-hover:scale-110" />
                    <AnimatePresence>
                        {!collapsed && (
                            <motion.span
                                initial={{ opacity: 0 }}
                                animate={{ opacity: 1 }}
                                exit={{ opacity: 0 }}
                                className="font-medium text-sm relative z-10"
                            >
                                Image Gallery
                            </motion.span>
                        )}
                    </AnimatePresence>
                </button>
            </div>

            {/* System Status */}
            <AnimatePresence>
                {!collapsed && (
                    <motion.div
                        initial={{ opacity: 0, height: 0 }}
                        animate={{ opacity: 1, height: 'auto' }}
                        exit={{ opacity: 0, height: 0 }}
                        className="mt-4 p-4 rounded-2xl relative overflow-hidden"
                        style={{
                            background: 'linear-gradient(135deg, var(--mesh-1), var(--mesh-2))',
                            border: '1px solid var(--border)',
                        }}
                    >
                        <div className="flex items-center gap-2 mb-3">
                            <Zap className="w-3.5 h-3.5 text-primary-400" />
                            <h3 className="text-[10px] font-bold uppercase tracking-[0.15em] text-dark-400">System</h3>
                        </div>

                        <div className="space-y-2.5">
                            {[
                                { label: 'Backend', status: 'Active', icon: Database, color: 'text-emerald-400' },
                                { label: 'Redis', status: 'Synced', icon: Activity, color: 'text-emerald-400' },
                                { label: 'Agents', status: '8 Online', icon: Users, color: 'text-primary-400' },
                            ].map((stat) => (
                                <div key={stat.label} className="flex items-center justify-between text-xs">
                                    <span className="text-dark-500 flex items-center gap-2">
                                        <stat.icon className="w-3 h-3" />
                                        {stat.label}
                                    </span>
                                    <span className={`flex items-center gap-1.5 ${stat.color} font-semibold text-[11px]`}>
                                        <span
                                            className="w-1.5 h-1.5 rounded-full animate-pulse"
                                            style={{
                                                backgroundColor: 'currentColor',
                                                boxShadow: '0 0 6px currentColor',
                                            }}
                                        />
                                        {stat.status}
                                    </span>
                                </div>
                            ))}
                        </div>
                    </motion.div>
                )}
            </AnimatePresence>

            {/* Collapsed mini-status */}
            {collapsed && (
                <div className="mt-4 flex flex-col items-center gap-2 pb-2">
                    <div className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" style={{ boxShadow: '0 0 6px rgba(52, 211, 153, 0.5)' }} />
                    <span className="text-[8px] text-dark-600 font-bold uppercase">Live</span>
                </div>
            )}
        </motion.aside>
    );
}
