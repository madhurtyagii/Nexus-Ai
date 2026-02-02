import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import toast from 'react-hot-toast';
import api, { projectsAPI, workflowTemplatesAPI } from '../services/api';
import './Projects.css';

function Projects() {
    const [projects, setProjects] = useState([]);
    const [loading, setLoading] = useState(true);
    const [filter, setFilter] = useState('all');
    const [searchTerm, setSearchTerm] = useState('');
    const [showArchived, setShowArchived] = useState(false);
    const [showCreateModal, setShowCreateModal] = useState(false);
    const navigate = useNavigate();

    useEffect(() => {
        const delayDebounceFn = setTimeout(() => {
            fetchProjects();
        }, searchTerm ? 500 : 0);

        return () => clearTimeout(delayDebounceFn);
    }, [filter, searchTerm, showArchived]);

    const fetchProjects = async () => {
        setLoading(true);
        try {
            const params = {
                status: filter !== 'all' ? filter : undefined,
                q: searchTerm || undefined,
                is_archived: showArchived
            };
            const response = await projectsAPI.getProjects(params);
            setProjects(response.data);
        } catch (error) {
            console.error('Error fetching projects:', error);
            toast.error('Failed to load projects');
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
                    <div className="flex items-center gap-4 mb-1">
                        <button
                            onClick={() => navigate('/dashboard')}
                            className="bg-dark-700 hover:bg-dark-600 text-white w-8 h-8 rounded-full flex items-center justify-center transition-colors"
                            title="Back to Dashboard"
                        >
                            ←
                        </button>
                        <h1>📋 Projects</h1>
                    </div>
                    <p>Manage complex multi-phase AI projects</p>
                </div>
                <div className="header-actions">
                    <div className="search-box">
                        <input
                            type="text"
                            placeholder="Search projects..."
                            value={searchTerm}
                            onChange={(e) => setSearchTerm(e.target.value)}
                        />
                        <span className="search-icon">🔍</span>
                    </div>
                    <button
                        className={`archive-toggle-btn ${showArchived ? 'active' : ''}`}
                        onClick={() => setShowArchived(!showArchived)}
                        title={showArchived ? "Back to active projects" : "View archived projects"}
                    >
                        {showArchived ? '📁 Active' : '📜 Archived'}
                    </button>
                    <button
                        className="create-project-btn"
                        onClick={() => setShowCreateModal(true)}
                    >
                        <span>+</span> New Project
                    </button>
                </div>
            </div>

            {/* Dashboard Stats */}
            {!loading && projects.length > 0 && !showArchived && (
                <div className="stats-dashboard">
                    <div className="stat-card">
                        <span className="stat-icon">📁</span>
                        <div className="stat-info">
                            <span className="stat-label">Total Projects</span>
                            <span className="stat-count">{projects.length}</span>
                        </div>
                    </div>
                    <div className="stat-card">
                        <span className="stat-icon pulse">🚀</span>
                        <div className="stat-info">
                            <span className="stat-label">Active</span>
                            <span className="stat-count">
                                {projects.filter(p => p.status === 'in_progress').length}
                            </span>
                        </div>
                    </div>
                    <div className="stat-card">
                        <span className="stat-icon">⏳</span>
                        <div className="stat-info">
                            <span className="stat-label">Planning</span>
                            <span className="stat-count">
                                {projects.filter(p => p.status === 'planning').length}
                            </span>
                        </div>
                    </div>
                    <div className="stat-card">
                        <span className="stat-icon">✅</span>
                        <div className="stat-info">
                            <span className="stat-label">Completed</span>
                            <span className="stat-count">
                                {projects.filter(p => p.status === 'completed').length}
                            </span>
                        </div>
                    </div>
                </div>
            )}

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
                    <h3>No projects found</h3>
                    <p>{searchTerm ? "Try a different search term" : "Create your first AI-powered project to get started"}</p>
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
                            className={`project-card ${project.is_archived ? 'archived' : ''} ${project.is_pinned ? 'pinned' : ''}`}
                            onClick={() => navigate(`/projects/${project.id}`)}
                        >
                            <div className="project-card-header">
                                <div className="project-title-area">
                                    <button
                                        className={`pin-btn ${project.is_pinned ? 'active' : ''}`}
                                        onClick={(e) => {
                                            e.stopPropagation();
                                            projectsAPI.pinProject(project.id, !project.is_pinned)
                                                .then(() => {
                                                    fetchProjects();
                                                    toast.success(project.is_pinned ? 'Project unpinned' : 'Project pinned');
                                                });
                                        }}
                                        title={project.is_pinned ? "Unpin project" : "Pin project"}
                                    >
                                        📌
                                    </button>
                                    <h3>{project.name}</h3>
                                </div>
                                <div style={{ display: 'flex', gap: '0.4rem', alignItems: 'center' }}>
                                    <span className={`status-badge ${getStatusColor(project.status)}`}>
                                        {project.status?.replace('_', ' ')}
                                    </span>
                                    <button
                                        className="card-action-btn"
                                        onClick={(e) => {
                                            e.stopPropagation();
                                            projectsAPI.archiveProject(project.id, !project.is_archived)
                                                .then(() => {
                                                    fetchProjects();
                                                    toast.success(project.is_archived ? 'Project unarchived' : 'Project archived');
                                                });
                                        }}
                                        title={project.is_archived ? "Unarchive" : "Archive"}
                                    >
                                        {project.is_archived ? '📤' : '📥'}
                                    </button>
                                    <button
                                        className="card-action-btn delete"
                                        onClick={(e) => {
                                            e.stopPropagation();
                                            if (window.confirm('Are you sure you want to delete this project?')) {
                                                projectsAPI.delete(project.id)
                                                    .then(() => {
                                                        fetchProjects();
                                                        toast.success('Project deleted');
                                                    })
                                                    .catch(error => {
                                                        console.error('Error deleting project:', error);
                                                        toast.error('Failed to delete project');
                                                    });
                                            }
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
    const [creationMethod, setCreationMethod] = useState('template'); // 'template' or 'ai'
    const [templates, setTemplates] = useState([]);
    const [selectedTemplateId, setSelectedTemplateId] = useState(null);
    const [loadingTemplates, setLoadingTemplates] = useState(false);
    const [creating, setCreating] = useState(false);
    const [error, setError] = useState(null);

    useEffect(() => {
        fetchTemplates();
    }, []);

    const fetchTemplates = async () => {
        setLoadingTemplates(true);
        try {
            const response = await workflowTemplatesAPI.list();
            setTemplates(response.data);
            if (response.data.length > 0) {
                setSelectedTemplateId(response.data[0].id);
            }
        } catch (err) {
            console.error('Error fetching templates:', err);
        } finally {
            setLoadingTemplates(false);
        }
    };

    const handleCreate = async (e) => {
        e.preventDefault();
        if (!name.trim()) return;

        setCreating(true);
        setError(null);

        try {
            const payload = {
                name: name.trim(),
            };

            if (creationMethod === 'ai') {
                payload.description = description.trim() || null;
                payload.complexity = complexity;
            } else {
                payload.template_id = selectedTemplateId;
            }

            const response = await api.post('/projects/', payload);
            onCreated(response.data);
            toast.success('Project created successfully');
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
                    <div className="form-tabs">
                        <button
                            type="button"
                            className={`tab-btn ${creationMethod === 'template' ? 'active' : ''}`}
                            onClick={() => setCreationMethod('template')}
                        >
                            📋 Use Template
                        </button>
                        <button
                            type="button"
                            className={`tab-btn ${creationMethod === 'ai' ? 'active' : ''}`}
                            onClick={() => setCreationMethod('ai')}
                        >
                            🤖 AI Planning
                        </button>
                    </div>

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

                    {creationMethod === 'template' && (
                        <div className="form-group">
                            <label>Select Template</label>
                            {loadingTemplates ? (
                                <p className="loading-text">Loading templates...</p>
                            ) : (
                                <div className="templates-grid">
                                    {templates.map((template) => (
                                        <div
                                            key={template.id}
                                            className={`template-card-mini ${selectedTemplateId === template.id ? 'active' : ''}`}
                                            onClick={() => setSelectedTemplateId(template.id)}
                                        >
                                            <div className="template-icon">{template.icon || '📁'}</div>
                                            <div className="template-info">
                                                <div className="template-name">{template.name}</div>
                                                <div className="template-category">{template.category}</div>
                                            </div>
                                        </div>
                                    ))}
                                </div>
                            )}
                        </div>
                    )}

                    {creationMethod === 'ai' && (
                        <div className="form-group">
                            <label htmlFor="description">Description (for AI Planning)</label>
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
                    )}

                    {creationMethod === 'ai' && (
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
                    )}

                    {error && <div className="error-message">{error}</div>}

                    <div className="modal-actions">
                        <button type="button" className="btn-secondary" onClick={onClose}>
                            Cancel
                        </button>
                        <button
                            type="submit"
                            className="btn-primary"
                            disabled={creating || !name.trim() || (creationMethod === 'template' && !selectedTemplateId)}
                        >
                            {creating ? (
                                <>
                                    <span className="mini-spinner"></span>
                                    {creationMethod === 'ai' ? 'Planning...' : 'Creating...'}
                                </>
                            ) : (
                                creationMethod === 'ai' ? 'Create & Plan' : 'Create Project'
                            )}
                        </button>
                    </div>
                </form>
            </div>
        </div>
    );
}

export default Projects;
