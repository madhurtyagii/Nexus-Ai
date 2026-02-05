import { NavLink } from 'react-router-dom';
import { motion } from 'framer-motion';
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
    Users
} from 'lucide-react';

const navItems = [
    { path: '/dashboard', label: 'Dashboard', icon: LayoutDashboard },
    { path: '/tasks', label: 'Tasks', icon: ClipboardList },
    { path: '/agents', label: 'Agents', icon: UserCircle2 },
    { path: '/projects', label: 'Projects', icon: FolderTree },
    { path: '/workflow-builder', label: 'Workflow Builder', icon: GitBranch },
    { path: '/settings', label: 'Settings', icon: Settings },
    { path: '/help', label: 'Help', icon: HelpCircle },
];

export default function Sidebar() {
    return (
        <aside className="w-72 min-h-[calc(100vh-76px)] glass border-r border-white/5 p-4 hidden lg:block m-4 rounded-3xl sticky top-[80px]">
            <nav className="space-y-1.5">
                {navItems.map((item) => (
                    <NavLink
                        key={item.path}
                        to={item.path}
                        className={({ isActive }) =>
                            `group flex items-center gap-3 px-4 py-3 rounded-xl transition-all duration-300 relative overflow-hidden ${isActive
                                ? 'text-primary-400 bg-primary-500/10'
                                : 'text-dark-400 hover:text-white hover:bg-white/5'
                            }`
                        }
                    >
                        {({ isActive }) => (
                            <>
                                <item.icon className={`w-5 h-5 transition-transform duration-300 group-hover:scale-110 ${isActive ? 'text-primary-400' : 'text-dark-400'}`} />
                                <span className="font-medium tracking-tight text-sm">{item.label}</span>
                                {isActive && (
                                    <motion.div
                                        layoutId="sidebar-active"
                                        className="absolute left-0 w-1 h-6 bg-primary-500 rounded-full"
                                        initial={{ opacity: 0 }}
                                        animate={{ opacity: 1 }}
                                        transition={{ type: "spring", stiffness: 300, damping: 30 }}
                                    />
                                )}
                            </>
                        )}
                    </NavLink>
                ))}
            </nav>

            {/* System Status - Micro-Card */}
            <div className="mt-8 p-5 rounded-2xl bg-white/[0.02] border border-white/5 backdrop-blur-sm">
                <div className="flex items-center gap-2 mb-4 opacity-70">
                    <Activity className="w-4 h-4 text-primary-400" />
                    <h3 className="text-xs font-semibold uppercase tracking-widest text-dark-300">System</h3>
                </div>

                <div className="space-y-3.5">
                    <div className="flex items-center justify-between text-xs">
                        <span className="text-dark-400 flex items-center gap-2">
                            <Database className="w-3.5 h-3.5" />
                            Backend
                        </span>
                        <span className="flex items-center gap-1.5 text-green-400 font-medium">
                            <span className="w-1.5 h-1.5 rounded-full bg-green-400 animate-pulse shadow-[0_0_8px_rgba(74,222,128,0.5)]" />
                            Active
                        </span>
                    </div>
                    <div className="flex items-center justify-between text-xs">
                        <span className="text-dark-400 flex items-center gap-2">
                            <Database className="w-3.5 h-3.5" />
                            Redis
                        </span>
                        <span className="flex items-center gap-1.5 text-green-400 font-medium">
                            <span className="w-1.5 h-1.5 rounded-full bg-green-400 animate-pulse shadow-[0_0_8px_rgba(74,222,128,0.5)]" />
                            Synced
                        </span>
                    </div>
                    <div className="flex items-center justify-between text-xs">
                        <span className="text-dark-400 flex items-center gap-2">
                            <Users className="w-3.5 h-3.5" />
                            Agents
                        </span>
                        <span className="text-primary-400 font-semibold tracking-wide">7 Online</span>
                    </div>
                </div>
            </div>
        </aside>
    );
}
