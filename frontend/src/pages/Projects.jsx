import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../services/api';
import './Projects.css';

function Projects() {
    const [projects, setProjects] = useState([]);
    const [loading, setLoading] = useState(true);
    const [filter, setFilter] = useState('all');
    const [showCreateModal, setShowCreateModal] = useState(false);
    const navigate = useNavigate();

    useEffect(() => {
        fetchProjects();
    }, [filter]);

    const fetchProjects = async () => {
        setLoading(true);
        try {
            const params = filter !== 'all' ? { status_filter: filter } : {};
            const response = await api.get('/projects', { params });
            setProjects(response.data);
        } catch (error) {
            console.error('Error fetching projects:', error);
        } finally {
            setLoading(false);
        }
    };

    const getStatusColor = (status) => {
        switch (status) {
            case 'completed': return 'status-completed';
            case 'in_progress': return 'status-in-progress';
            case 'failed': return 'status-failed';
            case 'planning': return 'status-planning';
            default: return 'status-default';
        }
    };

    const getRiskColor = (risk) => {
        switch (risk) {
            case 'high': return 'risk-high';
            case 'medium': return 'risk-medium';
            case 'low': return 'risk-low';
            default: return 'risk-default';
        }
    };

    const formatDuration = (minutes) => {
        if (!minutes) return '--';
        if (minutes < 60) return `${minutes}m`;
        const hours = Math.floor(minutes / 60);
        const mins = minutes % 60;
        return mins > 0 ? `${hours}h ${mins}m` : `${hours}h`;
    };

    return (
        <div className="projects-container">
            <div className="projects-header">
                <div className="header-left">
                    <h1>📋 Projects</h1>
                    <p>Manage complex multi-phase AI projects</p>
                </div>
                <button
                    className="create-project-btn"
                    onClick={() => setShowCreateModal(true)}
                >
                    <span>+</span> New Project
                </button>
            </div>

            {/* Filters */}
            <div className="projects-filters">
                {['all', 'planning', 'in_progress', 'completed', 'failed'].map((f) => (
                    <button
                        key={f}
                        className={`filter-btn ${filter === f ? 'active' : ''}`}
                        onClick={() => setFilter(f)}
                    >
                        {f === 'all' ? 'All' : f.replace('_', ' ')}
                    </button>
                ))}
            </div>

            {/* Projects Grid */}
            {loading ? (
                <div className="projects-loading">
                    <div className="spinner"></div>
                    <p>Loading projects...</p>
                </div>
            ) : projects.length === 0 ? (
                <div className="no-projects">
                    <div className="no-projects-icon">📁</div>
                    <h3>No projects yet</h3>
                    <p>Create your first AI-powered project to get started</p>
                    <button
                        className="create-first-btn"
                        onClick={() => setShowCreateModal(true)}
                    >
                        Create Project
                    </button>
                </div>
            ) : (
                <div className="projects-grid">
                    {projects.map((project) => (
                        <div
                            key={project.id}
                            className="project-card"
                            onClick={() => navigate(`/projects/${project.id}`)}
                        >
                            <div className="project-card-header">
                                <h3>{project.name}</h3>
                                <div style={{ display: 'flex', gap: '0.5rem', alignItems: 'center' }}>
                                    <span className={`status-badge ${getStatusColor(project.status)}`}>
                                        {project.status?.replace('_', ' ')}
                                    </span>
                                    <button
                                        onClick={(e) => {
                                            e.stopPropagation();
                                            if (window.confirm('Are you sure you want to delete this project?')) {
                                                api.delete(`/projects/${project.id}`)
                                                    .then(() => fetchProjects())
                                                    .catch(error => console.error('Error deleting project:', error));
                                            }
                                        }}
                                        style={{
                                            background: 'none',
                                            border: 'none',
                                            color: '#ef4444',
                                            cursor: 'pointer',
                                            padding: '4px',
                                            fontSize: '1.2rem',
                                            lineHeight: 1
                                        }}
                                        title="Delete Project"
                                    >
                                        🗑️
                                    </button>
                                </div>
                            </div>

                            <p className="project-description">
                                {project.description || 'No description'}
                            </p>

                            <div className="project-progress">
                                <div className="progress-bar">
                                    <div
                                        className="progress-fill"
                                        style={{ width: `${project.progress || 0}%` }}
                                    ></div>
                                </div>
                                <span className="progress-text">{project.progress || 0}%</span>
                            </div>

                            <div className="project-meta">
                                <div className="meta-item">
                                    <span className="meta-label">Tasks</span>
                                    <span className="meta-value">
                                        {project.completed_tasks}/{project.total_tasks}
                                    </span>
                                </div>
                                <div className="meta-item">
                                    <span className="meta-label">Est. Time</span>
                                    <span className="meta-value">
                                        {formatDuration(project.estimated_minutes)}
                                    </span>
                                </div>
                                {project.risk_level && (
                                    <div className="meta-item">
                                        <span className="meta-label">Risk</span>
                                        <span className={`meta-value ${getRiskColor(project.risk_level)}`}>
                                            {project.risk_level}
                                        </span>
                                    </div>
                                )}
                            </div>
                        </div>
                    ))}
                </div>
            )}

            {/* Create Project Modal */}
            {showCreateModal && (
                <CreateProjectModal
                    onClose={() => setShowCreateModal(false)}
                    onCreated={(project) => {
                        setProjects([project, ...projects]);
                        setShowCreateModal(false);
                        navigate(`/projects/${project.id}`);
                    }}
                />
            )}
        </div>
    );
}

function CreateProjectModal({ onClose, onCreated }) {
    const [name, setName] = useState('');
    const [description, setDescription] = useState('');
    const [complexity, setComplexity] = useState('auto');
    const [creating, setCreating] = useState(false);
    const [error, setError] = useState(null);

    const handleCreate = async (e) => {
        e.preventDefault();
        if (!name.trim()) return;

        setCreating(true);
        setError(null);

        try {
            const response = await api.post('/projects/', {
                name: name.trim(),
                description: description.trim() || null,
                complexity
            });
            onCreated(response.data);
        } catch (err) {
            setError(err.response?.data?.detail || 'Failed to create project');
        } finally {
            setCreating(false);
        }
    };

    return (
        <div className="modal-overlay" onClick={onClose}>
            <div className="modal-content" onClick={(e) => e.stopPropagation()}>
                <div className="modal-header">
                    <h2>🚀 Create New Project</h2>
                    <button className="close-btn" onClick={onClose}>&times;</button>
                </div>

                <form onSubmit={handleCreate}>
                    <div className="form-group">
                        <label htmlFor="name">Project Name</label>
                        <input
                            type="text"
                            id="name"
                            value={name}
                            onChange={(e) => setName(e.target.value)}
                            placeholder="e.g., AI-Powered Blog System"
                            required
                        />
                    </div>

                    <div className="form-group">
                        <label htmlFor="description">Description</label>
                        <textarea
                            id="description"
                            value={description}
                            onChange={(e) => setDescription(e.target.value)}
                            placeholder="Describe what you want to build. The AI will automatically plan the project..."
                            rows={4}
                        />
                        <span className="form-hint">
                            Be descriptive! The ManagerAgent will create a detailed plan based on this.
                        </span>
                    </div>

                    <div className="form-group">
                        <label>Complexity</label>
                        <div className="complexity-options">
                            {[
                                { value: 'auto', label: '🤖 Auto-detect', desc: 'Let AI determine' },
                                { value: 'low', label: '🟢 Simple', desc: 'Quick tasks' },
                                { value: 'medium', label: '🟡 Medium', desc: 'Multi-step project' },
                                { value: 'high', label: '🔴 Complex', desc: 'Full workflow' }
                            ].map((opt) => (
                                <button
                                    key={opt.value}
                                    type="button"
                                    className={`complexity-btn ${complexity === opt.value ? 'active' : ''}`}
                                    onClick={() => setComplexity(opt.value)}
                                >
                                    <span className="complexity-label">{opt.label}</span>
                                    <span className="complexity-desc">{opt.desc}</span>
                                </button>
                            ))}
                        </div>
                    </div>

                    {error && <div className="error-message">{error}</div>}

                    <div className="modal-actions">
                        <button type="button" className="btn-secondary" onClick={onClose}>
                            Cancel
                        </button>
                        <button
                            type="submit"
                            className="btn-primary"
                            disabled={creating || !name.trim()}
                        >
                            {creating ? (
                                <>
                                    <span className="mini-spinner"></span>
                                    Planning...
                                </>
                            ) : (
                                'Create & Plan'
                            )}
                        </button>
                    </div>
                </form>
            </div>
        </div>
    );
}

export default Projects;
