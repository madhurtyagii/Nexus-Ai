import { useMemo } from 'react';
import './ProjectTimeline.css';

/**
 * ProjectTimeline Component
 * 
 * Renders a visual representation of the project's execution flow, 
 * showing phases, tasks, and their respective completion statuses.
 * 
 * @component
 * @param {Object} props - Component props.
 * @param {Array} props.phases - List of project phases to display.
 * @param {number} props.currentPhase - The index of the currently active phase.
 * @param {Object} props.progressData - Real-time progress metadata.
 */
function ProjectTimeline({ phases, currentPhase, progressData }) {
    const timelineItems = useMemo(() => {
        if (!phases || phases.length === 0) return [];

        return phases.map((phase, index) => ({
            phase_number: phase.phase_number || index + 1,
            phase_name: phase.phase_name || `Phase ${index + 1}`,
            tasks: phase.tasks || [],
            status: getPhaseStatus(index, currentPhase, progressData),
            isActive: index + 1 === currentPhase,
            isCompleted: index + 1 < currentPhase
        }));
    }, [phases, currentPhase, progressData]);

    return (
        <div className="project-timeline">
            <h3 className="timeline-title">📊 Execution Timeline</h3>

            <div className="timeline-container">
                {timelineItems.map((item, index) => (
                    <div
                        key={index}
                        className={`timeline-phase ${item.status}`}
                    >
                        {/* Connector Line */}
                        {index > 0 && (
                            <div className={`timeline-connector ${item.isCompleted || item.isActive ? 'active' : ''}`} />
                        )}

                        {/* Phase Node */}
                        <div className="phase-node">
                            <div className={`phase-indicator ${item.status}`}>
                                {item.status === 'completed' ? '✓' :
                                    item.status === 'in_progress' ? '⏳' :
                                        item.phase_number}
                            </div>

                            <div className="phase-info">
                                <h4>{item.phase_name}</h4>
                                <span className="task-count">
                                    {item.tasks.length} task{item.tasks.length !== 1 ? 's' : ''}
                                </span>
                            </div>
                        </div>

                        {/* Task List */}
                        <div className="phase-tasks">
                            {item.tasks.map((task, taskIndex) => (
                                <div
                                    key={taskIndex}
                                    className={`timeline-task ${getTaskStatus(task, item.status)}`}
                                >
                                    <span className="task-indicator">
                                        {getTaskIcon(task, item.status)}
                                    </span>
                                    <div className="task-info">
                                        <span className="task-name">{task.description || task.task_id}</span>
                                        <span className="task-agent">{task.assigned_agent}</span>
                                    </div>
                                    <span className="task-time">{task.estimated_time || '--'}</span>
                                </div>
                            ))}
                        </div>
                    </div>
                ))}
            </div>

            {/* Legend */}
            <div className="timeline-legend">
                <div className="legend-item">
                    <span className="legend-dot completed"></span>
                    <span>Completed</span>
                </div>
                <div className="legend-item">
                    <span className="legend-dot in_progress"></span>
                    <span>In Progress</span>
                </div>
                <div className="legend-item">
                    <span className="legend-dot pending"></span>
                    <span>Pending</span>
                </div>
            </div>
        </div>
    );
}

function getPhaseStatus(phaseIndex, currentPhase, progressData) {
    if (currentPhase === undefined || currentPhase === null) {
        return 'pending';
    }

    if (phaseIndex + 1 < currentPhase) return 'completed';
    if (phaseIndex + 1 === currentPhase) return 'in_progress';
    return 'pending';
}

function getTaskStatus(task, phaseStatus) {
    if (task.status) return task.status;
    if (phaseStatus === 'completed') return 'completed';
    if (phaseStatus === 'pending') return 'pending';
    return 'pending';
}

function getTaskIcon(task, phaseStatus) {
    const status = getTaskStatus(task, phaseStatus);
    switch (status) {
        case 'completed': return '✓';
        case 'in_progress': return '●';
        case 'failed': return '✗';
        default: return '○';
    }
}

export default ProjectTimeline;
