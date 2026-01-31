import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import toast from 'react-hot-toast';
import api, { projectsAPI, exportsAPI } from '../services/api';
import { ProjectTimeline, PhaseAccordion, ActivityFeed } from '../components/projects';
import FileUpload from '../components/files/FileUpload';
import FileManager from '../components/files/FileManager';
import './ProjectDetail.css';

function ProjectDetail() {
    const { id } = useParams();
    const navigate = useNavigate();
    const [project, setProject] = useState(null);
    const [progress, setProgress] = useState(null);
    const [loading, setLoading] = useState(true);
    const [executing, setExecuting] = useState(false);
    const [viewMode, setViewMode] = useState('accordion'); // 'accordion' or 'timeline'
    const [fileRefreshTrigger, setFileRefreshTrigger] = useState(0);
    const [showExportOptions, setShowExportOptions] = useState(false);
    const [exporting, setExporting] = useState(false);

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
            toast.success('Execution started');
        } catch (error) {
            console.error('Error executing project:', error);
            toast.error(error.response?.data?.detail || 'Failed to start execution');
        } finally {
            setExecuting(false);
        }
    };

    const handleExport = async (format) => {
        setExporting(true);
        setShowExportOptions(false);
        try {
            const response = await exportsAPI.exportProject(id, format);
            const blob = new Blob([response.data], {
                type: response.headers['content-type']
            });
            const url = window.URL.createObjectURL(blob);
            const link = document.createElement('a');
            link.href = url;
            const extension = format === 'markdown' ? 'md' : format;
            link.setAttribute('download', `${project?.name.replace(/\s+/g, '_')}_export.${extension}`);
            document.body.appendChild(link);
            link.click();
            link.remove();
            window.URL.revokeObjectURL(url);
        } catch (error) {
            console.error('Export failed:', error);
            toast.error('Failed to export project');
        } finally {
            setExporting(false);
        }
    };

    const handleReplan = async () => {
        try {
            const response = await api.post(`/projects/${id}/replan`);
            setProject(response.data.project);
            toast.success('Project plan regenerated');
        } catch (error) {
            console.error('Error replanning:', error);
            toast.error(error.response?.data?.detail || 'Failed to replan');
        }
    };

    const handleDuplicate = async () => {
        try {
            const response = await projectsAPI.duplicateProject(id);
            toast.success('Project duplicated');
            navigate(`/projects/${response.data.id}`);
        } catch (error) {
            console.error('Error duplicating:', error);
            toast.error('Failed to duplicate project');
        }
    };

    const handleArchive = async () => {
        try {
            const response = await projectsAPI.archiveProject(id, !project.is_archived);
            setProject(response.data);
            toast.success(response.data.is_archived ? 'Project archived' : 'Project unarchived');
        } catch (error) {
            console.error('Error archiving:', error);
            toast.error('Failed to update archive status');
        }
    };

    const handlePin = async () => {
        try {
            const response = await projectsAPI.pinProject(id, !project.is_pinned);
            setProject(response.data);
            toast.success(response.data.is_pinned ? 'Project pinned' : 'Project unpinned');
        } catch (error) {
            console.error('Error pinning:', error);
            toast.error('Failed to update pin status');
        }
    };

    const handleAddTag = async (tagName) => {
        if (!tagName.trim()) return;
        const newTags = [...(project.tags || []), tagName.trim()];
        try {
            const response = await projectsAPI.updateProjectTags(id, newTags);
            setProject(response.data);
            toast.success('Tag added');
        } catch (error) {
            console.error('Error adding tag:', error);
            toast.error('Failed to add tag');
        }
    };

    const handleRemoveTag = async (tagToRemove) => {
        const newTags = (project.tags || []).filter(t => t !== tagToRemove);
        try {
            const response = await projectsAPI.updateProjectTags(id, newTags);
            setProject(response.data);
            toast.success('Tag removed');
        } catch (error) {
            console.error('Error removing tag:', error);
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
                    <div className="title-area">
                        <button
                            className={`pin-btn ${project.is_pinned ? 'active' : ''}`}
                            onClick={handlePin}
                            title={project.is_pinned ? "Unpin project" : "Pin project"}
                        >
                            📌
                        </button>
                        <h1>{project.name}</h1>
                    </div>
                    <span className={`status-badge status-${project.status}`}>
                        {project.status?.replace('_', ' ')}
                    </span>
                    {project.is_archived && <span className="archived-badge">Archived</span>}
                </div>
                <div className="header-actions">
                    <button className="btn-secondary" onClick={handleDuplicate} title="Duplicate Project">
                        👯 Duplicate
                    </button>
                    <button
                        className={`btn-secondary ${project.is_archived ? 'active' : ''}`}
                        onClick={handleArchive}
                    >
                        {project.is_archived ? '📤 Unarchive' : '📥 Archive'}
                    </button>
                    <div className="export-dropdown-container">
                        <button
                            className="btn-secondary btn-export"
                            onClick={() => setShowExportOptions(!showExportOptions)}
                            disabled={exporting}
                        >
                            {exporting ? '⏳' : '📤'} Export
                        </button>
                        {showExportOptions && (
                            <div className="export-menu">
                                <button onClick={() => handleExport('pdf')}>📄 PDF Report</button>
                                <button onClick={() => handleExport('docx')}>📝 Word Document</button>
                                <button onClick={() => handleExport('markdown')}>⬇️ Markdown</button>
                                <button onClick={() => handleExport('json')}>⚙️ Raw JSON</button>
                            </div>
                        )}
                    </div>
                    {['planning', 'failed', 'completed'].includes(project.status) && (
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

                    <div className="tags-section">
                        <div className="tags-list">
                            {(project.tags || []).map((tag, i) => (
                                <span key={i} className="tag-badge">
                                    {tag}
                                    <button onClick={() => handleRemoveTag(tag)}>×</button>
                                </span>
                            ))}
                            <div className="add-tag-form">
                                <input
                                    type="text"
                                    placeholder="Add tag..."
                                    onKeyDown={(e) => {
                                        if (e.key === 'Enter') {
                                            handleAddTag(e.target.value);
                                            e.target.value = '';
                                        }
                                    }}
                                />
                            </div>
                        </div>
                    </div>

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

            {/* File Management */}
            <div className="project-files-section">
                <div className="section-header">
                    <h2>📁 Files</h2>
                    <FileUpload
                        projectId={id}
                        onUploadSuccess={() => setFileRefreshTrigger(prev => prev + 1)}
                    />
                </div>
                <FileManager projectId={id} refreshTrigger={fileRefreshTrigger} />
            </div>

            {/* Activity Feed */}
            <div className="project-activity-section">
                <div className="section-header">
                    <h2>🕒 Recent Activity</h2>
                </div>
                <div className="activity-card">
                    <ActivityFeed project={project} tasks={project.tasks || []} />
                </div>
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
