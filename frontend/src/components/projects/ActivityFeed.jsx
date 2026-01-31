import React from 'react';
import './ActivityFeed.css';

const ActivityFeed = ({ project, tasks = [] }) => {
    // Combine various events into a single timeline
    const events = [];

    // Add project creation
    if (project.created_at) {
        events.push({
            type: 'project_created',
            title: 'Project Created',
            description: `Project "${project.name}" was initialized.`,
            timestamp: project.created_at,
            icon: '🆕'
        });
    }

    // Add project start
    if (project.started_at) {
        events.push({
            type: 'project_started',
            title: 'Project Started',
            description: 'Execution phase commenced.',
            timestamp: project.started_at,
            icon: '🚀'
        });
    }

    // Add task events
    tasks.forEach(task => {
        if (task.created_at) {
            events.push({
                type: 'task_created',
                title: 'Task Queued',
                description: task.user_prompt.substring(0, 60) + (task.user_prompt.length > 60 ? '...' : ''),
                timestamp: task.created_at,
                icon: '📝'
            });
        }
        if (task.completed_at) {
            events.push({
                type: 'task_completed',
                title: 'Task Completed',
                description: 'Results delivered by agents.',
                timestamp: task.completed_at,
                icon: '✅'
            });
        }
    });

    // Add project completion
    if (project.completed_at) {
        events.push({
            type: 'project_completed',
            title: 'Project Completed',
            description: 'Final goal achieved.',
            timestamp: project.completed_at,
            icon: '🏆'
        });
    }

    // Sort events by timestamp (newest first)
    const sortedEvents = events.sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp));

    if (sortedEvents.length === 0) {
        return (
            <div className="activity-feed-empty">
                <p>No activity recorded yet.</p>
            </div>
        );
    }

    return (
        <div className="activity-feed">
            {sortedEvents.map((event, index) => (
                <div key={index} className="activity-item">
                    <div className="activity-line"></div>
                    <div className="activity-icon-container">
                        <span className="activity-icon">{event.icon}</span>
                    </div>
                    <div className="activity-content">
                        <div className="activity-header">
                            <span className="activity-title">{event.title}</span>
                            <span className="activity-time">
                                {new Date(event.timestamp).toLocaleString([], {
                                    month: 'short',
                                    day: 'numeric',
                                    hour: '2-digit',
                                    minute: '2-digit'
                                })}
                            </span>
                        </div>
                        <p className="activity-desc">{event.description}</p>
                    </div>
                </div>
            ))}
        </div>
    );
};

export default ActivityFeed;
