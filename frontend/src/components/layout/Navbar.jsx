import { Link } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';

/**
 * Navbar Component
 * 
 * The top navigation bar displaying the application logo, 
 * current user information, and logout functionality.
 * 
 * @component
 */
export default function Navbar() {
    const { user, logout } = useAuth();

    return (
        <nav className="bg-dark-800 border-b border-dark-700 px-6 py-4">
            <div className="flex items-center justify-between">
                {/* Logo */}
                <Link to="/dashboard" className="flex items-center gap-3">
                    <img src="/logo.png" alt="Nexus AI Logo" className="w-10 h-10 object-contain" />
                    <span className="text-xl font-bold gradient-text">Nexus AI</span>
                </Link>

                {/* Right Side */}
                <div className="flex items-center gap-4">
                    {/* User Menu */}
                    <div className="flex items-center gap-3">
                        <div className="text-right hidden sm:block">
                            <p className="text-sm font-medium text-white">{user?.username}</p>
                            <p className="text-xs text-dark-400">{user?.email}</p>
                        </div>

                        {/* Avatar */}
                        <div className="w-10 h-10 rounded-full bg-dark-600 flex items-center justify-center">
                            <span className="text-white font-medium">
                                {user?.username?.charAt(0).toUpperCase()}
                            </span>
                        </div>

                        {/* Logout Button */}
                        <button
                            onClick={logout}
                            className="btn-secondary text-sm"
                        >
                            Logout
                        </button>
                    </div>
                </div>
            </div>
        </nav>
    );
}
