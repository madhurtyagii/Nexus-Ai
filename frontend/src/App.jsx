import { Routes, Route, Navigate } from 'react-router-dom';
import React, { Suspense, lazy } from 'react';
import { useAuth } from './context/AuthContext';
import ProtectedRoute from './components/common/ProtectedRoute';
import BottomNav from './components/layout/BottomNav';

// Lazy load route components
const Login = lazy(() => import('./pages/Login'));
const Signup = lazy(() => import('./pages/Signup'));
const Dashboard = lazy(() => import('./pages/Dashboard'));
const TaskDetail = lazy(() => import('./pages/TaskDetail'));
const Tasks = lazy(() => import('./pages/Tasks'));
const Projects = lazy(() => import('./pages/Projects'));
const ProjectDetail = lazy(() => import('./pages/ProjectDetail'));
const Help = lazy(() => import('./pages/Help'));
const FileManager = lazy(() => import('./pages/FileManager'));
const Files = lazy(() => import('./pages/Files'));
const Templates = lazy(() => import('./pages/Templates'));
const Agents = lazy(() => import('./pages/Agents'));
const Settings = lazy(() => import('./pages/Settings'));
const WorkflowBuilder = lazy(() => import('./pages/WorkflowBuilder'));

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

    if (loading) {
        return (
            <div className="min-h-screen bg-dark-900 flex items-center justify-center">
                <div className="w-20 h-20 flex items-center justify-center animate-pulse">
                    <img src="/logo.png" alt="Nexus AI Logo" className="w-full h-full object-contain" />
                </div>
            </div>
        );
    }

    return (
        <Suspense fallback={
            <div className="min-h-screen bg-dark-900 flex items-center justify-center">
                <div className="w-16 h-16 flex items-center justify-center animate-spin">
                    <img src="/logo.png" alt="Loading..." className="w-full h-full object-contain opacity-50" />
                </div>
            </div>
        }>
            {/* Mobile Bottom Navigation */}
            {isAuthenticated && <BottomNav />}

            <Routes>
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
    );
}

export default App;
