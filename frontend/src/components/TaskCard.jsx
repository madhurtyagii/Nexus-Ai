import React from 'react';
import { useNavigate } from 'react-router-dom';

/**
 * TaskCard Component
 * Displays a single task with status badge and click handler
 */
export default function TaskCard({ task, onClick }) {
    const navigate = useNavigate();

    const getStatusColor = (status) => {
        switch (status?.toLowerCase()) {
            case 'completed':
                return 'bg-emerald-500/20 text-emerald-400 border-emerald-500/30';
            case 'in_progress':
                return 'bg-blue-500/20 text-blue-400 border-blue-500/30';
            case 'queued':
                return 'bg-yellow-500/20 text-yellow-400 border-yellow-500/30';
            case 'failed':
                return 'bg-red-500/20 text-red-400 border-red-500/30';
            default:
                return 'bg-gray-500/20 text-gray-400 border-gray-500/30';
        }
    };

    const getStatusIcon = (status) => {
        switch (status?.toLowerCase()) {
            case 'completed':
                return '✓';
            case 'in_progress':
                return '⟳';
            case 'queued':
                return '⏳';
            case 'failed':
                return '✕';
            default:
                return '•';
        }
    };

    const formatDate = (dateString) => {
        if (!dateString) return '';
        const date = new Date(dateString);
        return date.toLocaleDateString('en-GB', {
            day: 'numeric',
            month: 'numeric',
            year: 'numeric'
        });
    };

    const truncateText = (text, maxLength = 100) => {
        if (!text) return '';
        return text.length > maxLength ? text.substring(0, maxLength) + '...' : text;
    };

    const handleClick = () => {
        if (onClick) {
            onClick(task);
        } else {
            navigate(`/tasks/${task.id}`);
        }
    };

    return (
        <div
            onClick={handleClick}
            className="group bg-slate-800/50 backdrop-blur-sm border border-slate-700/50 rounded-xl p-4 
                 cursor-pointer transition-all duration-300 hover:bg-slate-800/80 hover:border-slate-600/50
                 hover:shadow-lg hover:shadow-purple-500/5"
        >
            <div className="flex items-start justify-between gap-3">
                <div className="flex-1 min-w-0">
                    <p className="text-slate-200 font-medium text-sm leading-relaxed mb-2">
                        {truncateText(task.user_prompt, 120)}
                    </p>

                    <div className="flex items-center gap-3">
                        <span className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-medium border ${getStatusColor(task.status)}`}>
                            <span className="text-[10px]">{getStatusIcon(task.status)}</span>
                            {task.status}
                        </span>

                        <span className="text-slate-500 text-xs">
                            {formatDate(task.created_at)}
                        </span>
                    </div>
                </div>

                <div className="text-slate-500 group-hover:text-purple-400 transition-colors">
                    <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                        <path fillRule="evenodd" d="M7.293 14.707a1 1 0 010-1.414L10.586 10 7.293 6.707a1 1 0 011.414-1.414l4 4a1 1 0 010 1.414l-4 4a1 1 0 01-1.414 0z" clipRule="evenodd" />
                    </svg>
                </div>
            </div>

            {/* Progress bar for in-progress tasks */}
            {task.status === 'in_progress' && (
                <div className="mt-3 h-1.5 bg-slate-700 rounded-full overflow-hidden">
                    <div
                        className="h-full bg-gradient-to-r from-blue-500 to-purple-500 rounded-full animate-pulse"
                        style={{ width: '60%' }}
                    />
                </div>
            )}
        </div>
    );
}
