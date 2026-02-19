import { motion, AnimatePresence } from 'framer-motion';
import { CheckCircle2, Loader2, XCircle, Clock, Zap } from 'lucide-react';

/**
 * ActivityTimeline — Visual vertical timeline with colored status nodes
 * Replaces boring flat list of recent operations
 */

const statusConfig = {
    completed: {
        color: 'bg-emerald-400',
        glow: 'shadow-[0_0_12px_rgba(52,211,153,0.5)]',
        icon: CheckCircle2,
        iconColor: 'text-emerald-400',
        label: 'Completed',
        lineColor: 'from-emerald-400/40',
    },
    in_progress: {
        color: 'bg-amber-400',
        glow: 'shadow-[0_0_12px_rgba(251,191,36,0.5)]',
        icon: Loader2,
        iconColor: 'text-amber-400',
        label: 'Running',
        lineColor: 'from-amber-400/40',
        animate: true,
    },
    failed: {
        color: 'bg-red-400',
        glow: 'shadow-[0_0_12px_rgba(248,113,113,0.5)]',
        icon: XCircle,
        iconColor: 'text-red-400',
        label: 'Failed',
        lineColor: 'from-red-400/40',
    },
    pending: {
        color: 'bg-primary-400',
        glow: 'shadow-[0_0_12px_rgba(14,165,233,0.5)]',
        icon: Clock,
        iconColor: 'text-primary-400',
        label: 'Pending',
        lineColor: 'from-primary-400/40',
    },
};

function formatTime(dateStr) {
    const d = new Date(dateStr);
    const now = new Date();
    const diffMs = now - d;
    const diffMins = Math.floor(diffMs / 60000);

    if (diffMins < 1) return 'Just now';
    if (diffMins < 60) return `${diffMins}m ago`;
    const diffHrs = Math.floor(diffMins / 60);
    if (diffHrs < 24) return `${diffHrs}h ago`;
    return d.toLocaleDateString([], { month: 'short', day: 'numeric' });
}

export default function ActivityTimeline({ tasks, onTaskClick, onCancelTask }) {
    if (!tasks || tasks.length === 0) {
        return (
            <div className="flex flex-col items-center justify-center py-12 opacity-30">
                <Zap className="w-8 h-8 mb-3" />
                <p className="text-xs font-bold uppercase tracking-widest">No activity yet</p>
                <p className="text-[10px] text-dark-600 mt-1">Create a task to see the timeline</p>
            </div>
        );
    }

    return (
        <div className="relative">
            {/* Timeline vertical line */}
            <div className="absolute left-[19px] top-4 bottom-4 w-px bg-gradient-to-b from-white/10 via-white/5 to-transparent" />

            <AnimatePresence mode="popLayout">
                {tasks.map((task, i) => {
                    const config = statusConfig[task.status] || statusConfig.pending;
                    const StatusIcon = config.icon;

                    return (
                        <motion.div
                            key={task.id}
                            layout
                            initial={{ opacity: 0, x: -20, filter: 'blur(4px)' }}
                            animate={{ opacity: 1, x: 0, filter: 'blur(0px)' }}
                            exit={{ opacity: 0, x: 20, filter: 'blur(4px)' }}
                            transition={{ delay: i * 0.05, duration: 0.3 }}
                            onClick={() => onTaskClick?.(task)}
                            className="relative flex gap-4 pl-1 py-2 group cursor-pointer"
                        >
                            {/* Status node */}
                            <div className="relative z-10 flex-shrink-0 mt-1">
                                <motion.div
                                    className={`w-[10px] h-[10px] rounded-full ${config.color} ${config.glow}`}
                                    animate={config.animate ? { scale: [1, 1.4, 1] } : {}}
                                    transition={config.animate ? { duration: 1.5, repeat: Infinity } : {}}
                                />
                            </div>

                            {/* Content */}
                            <div className="flex-1 min-w-0 pb-4">
                                <div className="flex items-center gap-2 mb-1">
                                    <StatusIcon className={`w-3 h-3 ${config.iconColor} ${config.animate ? 'animate-spin' : ''}`} />
                                    <span className={`text-[10px] font-bold uppercase tracking-wider ${config.iconColor}`}>
                                        {config.label}
                                    </span>
                                    <span className="text-[10px] text-dark-600 font-mono ml-auto">
                                        {formatTime(task.created_at)}
                                    </span>
                                </div>
                                <p className="text-sm font-medium text-dark-200 group-hover:text-white transition-colors line-clamp-2 leading-relaxed">
                                    {task.user_prompt}
                                </p>

                                {/* Cancel button for running tasks */}
                                {task.status === 'in_progress' && onCancelTask && (
                                    <motion.button
                                        initial={{ opacity: 0 }}
                                        animate={{ opacity: 1 }}
                                        onClick={(e) => { e.stopPropagation(); onCancelTask(task.id); }}
                                        className="mt-2 text-[10px] font-bold text-red-400/70 hover:text-red-400 uppercase tracking-wider transition-colors"
                                    >
                                        ■ Stop
                                    </motion.button>
                                )}
                            </div>
                        </motion.div>
                    );
                })}
            </AnimatePresence>
        </div>
    );
}
