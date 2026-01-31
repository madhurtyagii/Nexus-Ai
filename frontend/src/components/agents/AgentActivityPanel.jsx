/**
 * Nexus AI - Agent Activity Panel
 * Shows real-time agent activity and status
 */

import { useState, useEffect } from 'react';
import { useTaskUpdates, EventType } from '../../hooks/useWebSocket';
import './AgentActivityPanel.css';

/**
 * AgentCard - Shows individual agent status
 * 
 * @component
 * @param {Object} props - Component props.
 * @param {string} props.agentName - The name of the agent.
 * @param {string} props.status - Current status (e.g., 'starting', 'completed').
 * @param {number} [props.progress] - Completion percentage.
 * @param {string} [props.message] - Latest status message from the agent.
 * @param {string} [props.timestamp] - Time of the last update.
 */
function AgentCard({ agentName, status, progress, message, timestamp }) {
    const getStatusColor = () => {
        switch (status) {
            case 'starting':
            case 'agent_started':
                return 'agent-status-starting';
            case 'completed':
            case 'agent_completed':
                return 'agent-status-completed';
            case 'error':
            case 'agent_error':
                return 'agent-status-error';
            case 'in_progress':
            case 'agent_progress':
                return 'agent-status-progress';
            default:
                return 'agent-status-pending';
        }
    };

    const getStatusText = () => {
        switch (status) {
            case 'starting':
            case 'agent_started':
                return 'Starting...';
            case 'completed':
            case 'agent_completed':
                return 'Completed';
            case 'error':
            case 'agent_error':
                return 'Error';
            case 'in_progress':
            case 'agent_progress':
                return `In Progress${progress ? ` (${progress}%)` : ''}`;
            default:
                return 'Pending';
        }
    };

    const getIcon = () => {
        const name = agentName.toLowerCase();
        if (name.includes('research')) return '🔍';
        if (name.includes('code')) return '💻';
        if (name.includes('content')) return '📝';
        if (name.includes('data')) return '📊';
        return '🤖';
    };

    return (
        <div className={`agent-card ${getStatusColor()}`}>
            <div className="agent-card-header">
                <span className="agent-icon">{getIcon()}</span>
                <span className="agent-name">{agentName}</span>
                <span className={`agent-status-badge ${getStatusColor()}`}>
                    {getStatusText()}
                </span>
            </div>

            {message && (
                <div className="agent-message">
                    {message}
                </div>
            )}

            {progress !== undefined && progress > 0 && progress < 100 && (
                <div className="agent-progress-bar">
                    <div
                        className="agent-progress-fill"
                        style={{ width: `${progress}%` }}
                    />
                </div>
            )}

            {timestamp && (
                <div className="agent-timestamp">
                    {new Date(timestamp).toLocaleTimeString()}
                </div>
            )}
        </div>
    );
}

/**
 * TaskProgressTimeline - Shows a timeline of task and agent events.
 * 
 * @component
 * @param {Object} props - Component props.
 * @param {Array} props.events - List of event objects to display.
 */
function TaskProgressTimeline({ events }) {
    if (!events || events.length === 0) {
        return null;
    }

    const getEventIcon = (eventType) => {
        switch (eventType) {
            case EventType.TASK_STARTED:
                return '🚀';
            case EventType.TASK_COMPLETED:
                return '✅';
            case EventType.TASK_FAILED:
                return '❌';
            case EventType.AGENT_STARTED:
                return '🤖';
            case EventType.AGENT_COMPLETED:
                return '✓';
            case EventType.AGENT_ERROR:
                return '⚠️';
            case EventType.AGENT_PROGRESS:
                return '⏳';
            default:
                return '•';
        }
    };

    return (
        <div className="timeline-container">
            <h4 className="timeline-title">Activity Timeline</h4>
            <div className="timeline">
                {events.slice(-10).reverse().map((event, index) => (
                    <div key={index} className="timeline-item">
                        <span className="timeline-icon">{getEventIcon(event.event_type)}</span>
                        <div className="timeline-content">
                            <span className="timeline-event-type">
                                {event.event_type?.replace(/_/g, ' ').toUpperCase()}
                            </span>
                            {event.data?.agent_name && (
                                <span className="timeline-agent">{event.data.agent_name}</span>
                            )}
                            {event.data?.message && (
                                <span className="timeline-message">{event.data.message}</span>
                            )}
                            <span className="timeline-time">
                                {new Date(event.timestamp).toLocaleTimeString()}
                            </span>
                        </div>
                    </div>
                ))}
            </div>
        </div>
    );
}

/**
 * AgentActivityPanel - Main panel showing real-time agent activity.
 * 
 * Uses WebSockets to receive live updates about agent status and 
 * task progress.
 * 
 * @component
 * @param {Object} props - Component props.
 * @param {string|number} props.taskId - The ID of the task to monitor.
 * @param {string} props.token - JWT authentication token.
 */
function AgentActivityPanel({ taskId, token }) {
    const {
        isConnected,
        connectionState,
        taskEvents,
        agentStatus
    } = useTaskUpdates(taskId, token);

    return (
        <div className="agent-activity-panel">
            <div className="panel-header">
                <h3>Agent Activity</h3>
                <div className={`connection-status ${isConnected ? 'connected' : 'disconnected'}`}>
                    <span className="status-dot" />
                    {isConnected ? 'Live' : connectionState}
                </div>
            </div>

            <div className="panel-content">
                {/* Active Agents */}
                <div className="agents-grid">
                    {Object.entries(agentStatus).length > 0 ? (
                        Object.entries(agentStatus).map(([name, data]) => (
                            <AgentCard
                                key={name}
                                agentName={name}
                                status={data.status}
                                progress={data.progress}
                                message={data.message}
                                timestamp={data.timestamp}
                            />
                        ))
                    ) : (
                        <div className="no-agents">
                            <p>No agent activity yet</p>
                            {!isConnected && (
                                <p className="hint">Waiting for connection...</p>
                            )}
                        </div>
                    )}
                </div>

                {/* Timeline */}
                <TaskProgressTimeline events={taskEvents} />
            </div>
        </div>
    );
}

/**
 * AgentActivityPanelPolling - Version of the panel for use without WebSockets.
 * 
 * Typically used for historical tasks or when subtasks are already loaded.
 * 
 * @component
 * @param {Object} props - Component props.
 * @param {Array} [props.subtasks] - List of subtasks to display as cards.
 * @param {string} [props.status] - Overall task status badge.
 */
export function AgentActivityPanelPolling({ subtasks = [], status }) {
    return (
        <div className="agent-activity-panel">
            <div className="panel-header">
                <h3>Subtasks</h3>
                <span className={`task-status-badge status-${status}`}>{status}</span>
            </div>

            <div className="panel-content">
                <div className="agents-grid">
                    {subtasks.map((subtask) => (
                        <AgentCard
                            key={subtask.id}
                            agentName={subtask.assigned_agent}
                            status={subtask.status}
                            progress={subtask.status === 'completed' ? 100 : subtask.status === 'in_progress' ? 50 : 0}
                            timestamp={subtask.completed_at || subtask.created_at}
                        />
                    ))}
                </div>
            </div>
        </div>
    );
}

export { AgentCard, TaskProgressTimeline };
export default AgentActivityPanel;
