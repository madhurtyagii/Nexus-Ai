import { NavLink } from 'react-router-dom';

const navItems = [
    { path: '/dashboard', label: 'Dashboard', icon: '🏠' },
    { path: '/tasks', label: 'Tasks', icon: '📋' },
    { path: '/agents', label: 'Agents', icon: '🤖' },
    { path: '/projects', label: 'Projects', icon: '📁' },
    { path: '/settings', label: 'Settings', icon: '⚙️' },
];

export default function Sidebar() {
    return (
        <aside className="w-64 min-h-[calc(100vh-73px)] bg-dark-800 border-r border-dark-700 p-4 hidden lg:block">
            <nav className="space-y-2">
                {navItems.map((item) => (
                    <NavLink
                        key={item.path}
                        to={item.path}
                        className={({ isActive }) =>
                            `flex items-center gap-3 px-4 py-3 rounded-lg transition-colors ${isActive
                                ? 'bg-primary-500/10 text-primary-400 border border-primary-500/30'
                                : 'text-dark-300 hover:bg-dark-700 hover:text-white'
                            }`
                        }
                    >
                        <span className="text-xl">{item.icon}</span>
                        <span className="font-medium">{item.label}</span>
                    </NavLink>
                ))}
            </nav>

            {/* Agent Status */}
            <div className="mt-8 p-4 rounded-xl bg-dark-700/50 border border-dark-600">
                <h3 className="text-sm font-medium text-dark-300 mb-3">System Status</h3>
                <div className="space-y-2">
                    <div className="flex items-center justify-between text-sm">
                        <span className="text-dark-400">Backend</span>
                        <span className="flex items-center gap-1 text-green-400">
                            <span className="w-2 h-2 rounded-full bg-green-400 animate-pulse" />
                            Online
                        </span>
                    </div>
                    <div className="flex items-center justify-between text-sm">
                        <span className="text-dark-400">Redis</span>
                        <span className="flex items-center gap-1 text-green-400">
                            <span className="w-2 h-2 rounded-full bg-green-400 animate-pulse" />
                            Connected
                        </span>
                    </div>
                    <div className="flex items-center justify-between text-sm">
                        <span className="text-dark-400">Agents</span>
                        <span className="text-primary-400">7 Active</span>
                    </div>
                </div>
            </div>
        </aside>
    );
}
