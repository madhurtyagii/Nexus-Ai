/**
 * Nexus AI - Mobile Bottom Navigation
 * Touch-friendly navigation bar for mobile devices
 */

import { NavLink, useNavigate } from 'react-router-dom';

const navItems = [
    { path: '/dashboard', label: 'Home', icon: '🏠' },
    { path: '/tasks', label: 'Tasks', icon: '📋' },
    { path: '/agents', label: 'Agents', icon: '🤖' },
    { path: '/projects', label: 'Projects', icon: '📁' },
    { path: '/files', label: 'Ask Files', icon: '💬' },
];

export default function BottomNav() {
    const navigate = useNavigate();

    return (
        <>
            {/* Bottom Navigation - visible on mobile only */}
            <nav className="bottom-nav lg:hidden">
                <div className="flex justify-around items-center">
                    {navItems.map((item) => (
                        <NavLink
                            key={item.path}
                            to={item.path}
                            className={({ isActive }) =>
                                `bottom-nav-item flex-1 ${isActive ? 'active' : ''}`
                            }
                        >
                            <span className="text-xl mb-0.5">{item.icon}</span>
                            <span className="text-[10px]">{item.label}</span>
                        </NavLink>
                    ))}
                    <button
                        onClick={() => window.dispatchEvent(new CustomEvent('toggle-image-gallery'))}
                        className="bottom-nav-item flex-1"
                    >
                        <span className="text-xl mb-0.5">🖼️</span>
                        <span className="text-[10px]">Gallery</span>
                    </button>
                </div>
            </nav>

            {/* Floating Action Button - Quick Task */}
            <button
                onClick={() => navigate('/tasks')}
                className="fab lg:hidden"
                aria-label="Create new task"
            >
                <span className="text-2xl text-white">+</span>
            </button>
        </>
    );
}
