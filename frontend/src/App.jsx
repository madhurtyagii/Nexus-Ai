import { Routes, Route, Navigate } from 'react-router-dom';
import { useAuth } from './context/AuthContext';
import ProtectedRoute from './components/common/ProtectedRoute';
import Login from './pages/Login';
import Signup from './pages/Signup';
import Dashboard from './pages/Dashboard';
import TaskDetail from './pages/TaskDetail';
import Projects from './pages/Projects';
import ProjectDetail from './pages/ProjectDetail';
import Help from './pages/Help';

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
                <div className="w-16 h-16 rounded-2xl bg-gradient-to-br from-primary-500 to-purple-500 flex items-center justify-center animate-pulse">
                    <span className="text-white font-bold text-2xl">N</span>
                </div>
            </div>
        );
    }

    return (
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
                        <PlaceholderPage title="Tasks" />
                    </ProtectedRoute>
                }
            />
            <Route
                path="/agents"
                element={
                    <ProtectedRoute>
                        <PlaceholderPage title="Agents" />
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
                        <PlaceholderPage title="Settings" />
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

            {/* Default Redirect */}
            <Route
                path="*"
                element={<Navigate to={isAuthenticated ? "/dashboard" : "/login"} />}
            />
        </Routes>
    );
}

export default App;
