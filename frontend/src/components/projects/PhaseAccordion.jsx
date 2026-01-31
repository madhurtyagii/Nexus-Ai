import { useState } from 'react';
import './PhaseAccordion.css';

/**
 * PhaseAccordion Component
 * 
 * A collapsible accordion that organizes project phases into expandable 
 * sections, showing the list of tasks for each phase.
 * 
 * @component
 * @param {Object} props - Component props.
 * @param {Array} props.phases - List of project phases.
 * @param {number} props.currentPhase - The index of the active phase.
 * @param {Function} [props.onTaskClick] - Callback when a task is clicked.
 */
function PhaseAccordion({ phases, currentPhase, onTaskClick }) {
    const [expandedPhases, setExpandedPhases] = useState(() => {
        // Expand current phase by default
        return currentPhase ? [currentPhase] : [1];
    });

    const togglePhase = (phaseNumber) => {
        setExpandedPhases(prev =>
            prev.includes(phaseNumber)
                ? prev.filter(p => p !== phaseNumber)
                : [...prev, phaseNumber]
        );
    };

    const getPhaseStatus = (phaseNumber) => {
        if (!currentPhase) return 'pending';
        if (phaseNumber < currentPhase) return 'completed';
        if (phaseNumber === currentPhase) return 'in_progress';
        return 'pending';
    };

    const getTaskStatus = (task, phaseStatus) => {
        if (task.status) return task.status;
        if (phaseStatus === 'completed') return 'completed';
        return 'pending';
    };

    if (!phases || phases.length === 0) {
        return (
            <div className="phase-accordion-empty">
                <p>No phases defined yet</p>
            </div>
        );
    }

    return (
        <div className="phase-accordion">
            {phases.map((phase, index) => {
                const phaseNumber = phase.phase_number || index + 1;
                const isExpanded = expandedPhases.includes(phaseNumber);
                const status = getPhaseStatus(phaseNumber);

                return (
                    <div
                        key={index}
                        className={`accordion-item ${status} ${isExpanded ? 'expanded' : ''}`}
                    >
                        {/* Header */}
                        <div
                            className="accordion-header"
                            onClick={() => togglePhase(phaseNumber)}
                        >
                            <div className="header-left">
                                <span className={`phase-badge ${status}`}>
                                    {status === 'completed' ? '✓' :
                                        status === 'in_progress' ? '⏳' :
                                            phaseNumber}
                                </span>
                                <h4 className="phase-name">{phase.phase_name || `Phase ${phaseNumber}`}</h4>
                            </div>

                            <div className="header-right">
                                <span className="task-count">
                                    {phase.tasks?.length || 0} tasks
                                </span>
                                <span className={`chevron ${isExpanded ? 'up' : 'down'}`}>
                                    ▼
                                </span>
                            </div>
                        </div>

                        {/* Content */}
                        <div className={`accordion-content ${isExpanded ? 'show' : ''}`}>
                            {phase.tasks && phase.tasks.length > 0 ? (
                                <div className="tasks-list">
                                    {phase.tasks.map((task, taskIndex) => {
                                        const taskStatus = getTaskStatus(task, status);

                                        return (
                                            <div
                                                key={taskIndex}
                                                className={`task-row ${taskStatus}`}
                                                onClick={() => onTaskClick && onTaskClick(task)}
                                            >
                                                <span className={`task-status-icon ${taskStatus}`}>
                                                    {taskStatus === 'completed' ? '✓' :
                                                        taskStatus === 'in_progress' ? '●' :
                                                            taskStatus === 'failed' ? '✗' : '○'}
                                                </span>

                                                <div className="task-details">
                                                    <span className="task-id">{task.task_id}</span>
                                                    <span className="task-description">
                                                        {task.description || 'No description'}
                                                    </span>
                                                </div>

                                                <div className="task-meta">
                                                    <span className="agent-badge">{task.assigned_agent}</span>
                                                    <span className="estimated-time">{task.estimated_time || '--'}</span>
                                                </div>
                                            </div>
                                        );
                                    })}
                                </div>
                            ) : (
                                <p className="no-tasks">No tasks in this phase</p>
                            )}

                            {/* Phase Summary */}
                            {phase.estimated_time && (
                                <div className="phase-summary">
                                    <span>Estimated Duration: {phase.estimated_time}</span>
                                </div>
                            )}
                        </div>
                    </div>
                );
            })}
        </div>
    );
}

export default PhaseAccordion;
