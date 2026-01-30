import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import api from '../services/api';
import { ProjectTimeline, PhaseAccordion } from '../components/projects';
import './ProjectDetail.css';

function ProjectDetail() {
    const { id } = useParams();
    const navigate = useNavigate();
    const [project, setProject] = useState(null);
    const [progress, setProgress] = useState(null);
    const [loading, setLoading] = useState(true);
    const [executing, setExecuting] = useState(false);
    const [viewMode, setViewMode] = useState('accordion'); // 'accordion' or 'timeline'

    const [error, setError] = useState(null);

    useEffect(() => {
        if (!id) return;
        fetchProject();
        // Poll for progress if project is in progress
        const interval = setInterval(() => {
            if (project?.status === 'in_progress') {
                fetchProgress();
            }
        }, 3000);
        return () => clearInterval(interval);
    }, [id, project?.status]);

    const fetchProject = async () => {
        try {
            console.log(`Fetching project ${id}...`);
            const response = await api.get(`/projects/${id}/`);
            setProject(response.data);
            if (response.data.status === 'in_progress') {
                fetchProgress();
            }
        } catch (error) {
            console.error('Error fetching project:', error);
            setError(error.response?.data?.detail || error.message || 'Failed to load project');
        } finally {
            setLoading(false);
        }
    };

    const fetchProgress = async () => {
        try {
            const response = await api.get(`/projects/${id}/progress`);
            setProgress(response.data);
        } catch (error) {
            console.error('Error fetching progress:', error);
        }
    };

    const handleExecute = async () => {
        setExecuting(true);
        try {
            await api.post(`/projects/${id}/execute`, {
                add_qa_checkpoints: true
            });
            // Refresh project
            await fetchProject();
        } catch (error) {
            console.error('Error executing project:', error);
            alert(error.response?.data?.detail || 'Failed to start execution');
        } finally {
            setExecuting(false);
        }
    };

    const handleReplan = async () => {
        try {
            const response = await api.post(`/projects/${id}/replan`);
            setProject(response.data.project);
        } catch (error) {
            console.error('Error replanning:', error);
            alert(error.response?.data?.detail || 'Failed to replan');
        }
    };

    if (loading) {
        return (
            <div className="project-detail-loading">
                <div className="spinner"></div>
                <p>Loading project...</p>
            </div>
        );
    }

    if (error || !project) {
        return (
            <div className="project-not-found">
                <h2>Error Loading Project</h2>
                <p style={{ color: '#ef4444', marginBottom: '1rem' }}>{error || 'Project not found'}</p>
                <p className="text-muted">ID: {id}</p>
                <button onClick={() => navigate('/projects')}>Back to Projects</button>
            </div>
        );
    }

    return (
        <div className="project-detail">
            {/* Header */}
            <div className="project-detail-header">
                <button className="back-btn" onClick={() => navigate('/projects')}>
                    ← Back
                </button>
                <div className="header-content">
                    <h1>{project.name}</h1>
                    <span className={`status-badge status-${project.status}`}>
                        {project.status?.replace('_', ' ')}
                    </span>
                </div>
                <div className="header-actions">
                    {project.status === 'planning' && (
                        <>
                            <button className="btn-secondary" onClick={handleReplan}>
                                🔄 Replan
                            </button>
                            <button
                                className="btn-primary"
                                onClick={handleExecute}
                                disabled={executing}
                            >
                                {executing ? '⏳ Starting...' : '▶️ Execute'}
                            </button>
                        </>
                    )}
                </div>
            </div>

            {/* Progress Bar */}
            {(progress || project.progress > 0) && (
                <div className="project-progress-bar">
                    <div className="progress-header">
                        <span>Overall Progress</span>
                        <span>{progress?.progress_percentage || project.progress}%</span>
                    </div>
                    <div className="progress-track">
                        <div
                            className="progress-fill"
                            style={{ width: `${progress?.progress_percentage || project.progress}%` }}
                        ></div>
                    </div>
                    {progress?.active_agents?.length > 0 && (
                        <div className="active-agents">
                            <span>Active: </span>
                            {progress.active_agents.map((agent, i) => (
                                <span key={i} className="agent-badge">{agent}</span>
                            ))}
                        </div>
                    )}
                </div>
            )}

            {/* Project Info */}
            <div className="project-info-grid">
                <div className="info-card">
                    <h3>📋 Overview</h3>
                    <p className="description">{project.description || 'No description'}</p>
                    <div className="info-stats">
                        <div className="stat">
                            <span className="stat-value">{project.total_phases || 0}</span>
                            <span className="stat-label">Phases</span>
                        </div>
                        <div className="stat">
                            <span className="stat-value">{project.total_tasks || 0}</span>
                            <span className="stat-label">Tasks</span>
                        </div>
                        <div className="stat">
                            <span className="stat-value">{project.completed_tasks || 0}</span>
                            <span className="stat-label">Completed</span>
                        </div>
                        <div className="stat">
                            <span className="stat-value">{project.estimated_minutes || '--'}m</span>
                            <span className="stat-label">Est. Time</span>
                        </div>
                    </div>
                </div>

                {project.risk_level && (
                    <div className="info-card risk-card">
                        <h3>⚠️ Risk Assessment</h3>
                        <div className={`risk-indicator risk-${project.risk_level}`}>
                            {project.risk_level.toUpperCase()}
                        </div>
                    </div>
                )}
            </div>

            {/* Project Plan */}
            {project.project_plan && project.project_plan.length > 0 && (
                <div className="project-plan">
                    <div className="plan-header">
                        <h2>📊 Execution Plan</h2>
                        <div className="view-toggle">
                            <button
                                className={`toggle-btn ${viewMode === 'accordion' ? 'active' : ''}`}
                                onClick={() => setViewMode('accordion')}
                            >
                                📋 Accordion
                            </button>
                            <button
                                className={`toggle-btn ${viewMode === 'timeline' ? 'active' : ''}`}
                                onClick={() => setViewMode('timeline')}
                            >
                                📊 Timeline
                            </button>
                        </div>
                    </div>

                    {viewMode === 'timeline' ? (
                        <ProjectTimeline
                            phases={project.project_plan}
                            currentPhase={project.current_phase || 1}
                            progressData={progress}
                        />
                    ) : (
                        <PhaseAccordion
                            phases={project.project_plan}
                            currentPhase={project.current_phase || 1}
                        />
                    )}
                </div>
            )}

            {/* Output */}
            {project.output && (
                <div className="project-output">
                    <h2>📄 Output</h2>
                    <div className="output-content">
                        <pre>{project.output}</pre>
                    </div>
                </div>
            )}
        </div>
    );
}

export default ProjectDetail;
