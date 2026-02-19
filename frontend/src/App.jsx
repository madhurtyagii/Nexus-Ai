import { Routes, Route, Navigate, useLocation } from 'react-router-dom';
import React, { Suspense, lazy } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { useAuth } from './context/AuthContext';
import ProtectedRoute from './components/common/ProtectedRoute';
import BottomNav from './components/layout/BottomNav';
import CommandPalette from './components/common/CommandPalette';
import CursorFollower from './components/common/CursorFollower';

// Lazy load route components
const Landing = lazy(() => import('./pages/Landing'));
const Login = lazy(() => import('./pages/Login'));
const Signup = lazy(() => import('./pages/Signup'));
const Dashboard = lazy(() => import('./pages/Dashboard'));
const TaskDetail = lazy(() => import('./pages/TaskDetail'));
const Tasks = lazy(() => import('./pages/Tasks'));
const Projects = lazy(() => import('./pages/Projects'));
const ProjectDetail = lazy(() => import('./pages/ProjectDetail'));
const Help = lazy(() => import('./pages/Help'));
const Files = lazy(() => import('./pages/Files'));
const Templates = lazy(() => import('./pages/Templates'));
const Agents = lazy(() => import('./pages/Agents'));
const Settings = lazy(() => import('./pages/Settings'));
const WorkflowBuilder = lazy(() => import('./pages/WorkflowBuilder'));
import ImageHistory from './components/layout/ImageHistory';

// Placeholder pages for routes we'll build later
function PlaceholderPage({ title }) {
    return (
        <div className="min-h-screen bg-dark-900 flex items-center justify-center">
            <div className="text-center">
                <h1 className="text-3xl font-bold text-white mb-2">{title}</h1>
                <p className="text-dark-400">Coming Soon</p>
            </div>
        </div>
    );
}

function App() {
    const { isAuthenticated, loading } = useAuth();
    const [isGalleryOpen, setIsGalleryOpen] = React.useState(false);

    React.useEffect(() => {
        const handleToggle = () => setIsGalleryOpen(prev => !prev);
        window.addEventListener('toggle-image-gallery', handleToggle);
        return () => window.removeEventListener('toggle-image-gallery', handleToggle);
    }, []);

    if (loading) {
        return (
            <div className="min-h-screen bg-dark-900 flex items-center justify-center">
                <div className="relative">
                    {/* Animated ring */}
                    <motion.div
                        className="w-20 h-20 rounded-full border-2 border-primary-500/20"
                        style={{ borderTopColor: 'rgba(14, 165, 233, 0.8)' }}
                        animate={{ rotate: 360 }}
                        transition={{ duration: 1, repeat: Infinity, ease: 'linear' }}
                    />
                    {/* Pulsing logo */}
                    <motion.div
                        className="absolute inset-0 flex items-center justify-center"
                        animate={{ scale: [1, 1.05, 1], opacity: [0.7, 1, 0.7] }}
                        transition={{ duration: 2, repeat: Infinity, ease: 'easeInOut' }}
                    >
                        <img src="/logo.png" alt="Nexus AI" className="w-10 h-10 object-contain" />
                    </motion.div>
                </div>
            </div>
        );
    }

    return (
        <>
            {/* ═══ Living Aurora Background ═══ */}
            <div className="aurora-layer-1" aria-hidden="true" />
            <div className="aurora-layer-2" aria-hidden="true" />
            <div className="aurora-layer-3" aria-hidden="true" />

            {/* Global Cursor Follower Effect */}
            <CursorFollower />

            <Suspense fallback={
                <div className="min-h-screen bg-dark-900 flex flex-col items-center justify-center gap-4">
                    <div className="relative">
                        <motion.div
                            className="w-12 h-12 rounded-full border-2 border-primary-500/20"
                            style={{ borderTopColor: 'rgba(14, 165, 233, 0.6)' }}
                            animate={{ rotate: 360 }}
                            transition={{ duration: 0.8, repeat: Infinity, ease: 'linear' }}
                        />
                        <motion.div
                            className="absolute inset-0 flex items-center justify-center"
                            animate={{ opacity: [0.5, 1, 0.5] }}
                            transition={{ duration: 1.5, repeat: Infinity }}
                        >
                            <img src="/logo.png" alt="Loading" className="w-6 h-6 object-contain" />
                        </motion.div>
                    </div>
                    <motion.div
                        className="h-0.5 w-32 rounded-full overflow-hidden bg-white/5"
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        transition={{ delay: 0.5 }}
                    >
                        <motion.div
                            className="h-full bg-gradient-to-r from-primary-500 to-purple-500 rounded-full"
                            animate={{ x: ['-100%', '100%'] }}
                            transition={{ duration: 1.2, repeat: Infinity, ease: 'easeInOut' }}
                        />
                    </motion.div>
                </div>
            }>
                {/* Global Components for Authenticated Users */}
                {isAuthenticated && <BottomNav />}
                {isAuthenticated && <CommandPalette />}

                <Routes>
                    {/* Landing Page - First impression for new users */}
                    <Route
                        path="/"
                        element={isAuthenticated ? <Navigate to="/dashboard" /> : <Landing />}
                    />

                    {/* Public Routes */}
                    <Route
                        path="/login"
                        element={isAuthenticated ? <Navigate to="/dashboard" /> : <Login />}
                    />
                    <Route
                        path="/signup"
                        element={isAuthenticated ? <Navigate to="/dashboard" /> : <Signup />}
                    />

                    {/* Protected Routes */}
                    <Route
                        path="/dashboard"
                        element={
                            <ProtectedRoute>
                                <Dashboard />
                            </ProtectedRoute>
                        }
                    />
                    <Route
                        path="/tasks/:taskId"
                        element={
                            <ProtectedRoute>
                                <TaskDetail />
                            </ProtectedRoute>
                        }
                    />
                    <Route
                        path="/tasks"
                        element={
                            <ProtectedRoute>
                                <Tasks />
                            </ProtectedRoute>
                        }
                    />
                    <Route
                        path="/files"
                        element={
                            <ProtectedRoute>
                                <Files />
                            </ProtectedRoute>
                        }
                    />
                    <Route
                        path="/agents"
                        element={
                            <ProtectedRoute>
                                <Agents />
                            </ProtectedRoute>
                        }
                    />
                    <Route
                        path="/projects"
                        element={
                            <ProtectedRoute>
                                <Projects />
                            </ProtectedRoute>
                        }
                    />
                    <Route
                        path="/projects/:id"
                        element={
                            <ProtectedRoute>
                                <ProjectDetail />
                            </ProtectedRoute>
                        }
                    />
                    <Route
                        path="/settings"
                        element={
                            <ProtectedRoute>
                                <Settings />
                            </ProtectedRoute>
                        }
                    />
                    <Route
                        path="/help"
                        element={
                            <ProtectedRoute>
                                <Help />
                            </ProtectedRoute>
                        }
                    />
                    <Route
                        path="/workflow-builder"
                        element={
                            <ProtectedRoute>
                                <WorkflowBuilder />
                            </ProtectedRoute>
                        }
                    />

                    {/* Default Redirect */}
                    <Route
                        path="*"
                        element={<Navigate to={isAuthenticated ? "/dashboard" : "/login"} />}
                    />
                </Routes>
            </Suspense>

            {isAuthenticated && (
                <ImageHistory
                    isOpen={isGalleryOpen}
                    onClose={() => setIsGalleryOpen(false)}
                />
            )}
        </>
    );
}

export default App;
