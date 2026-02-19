import { motion } from 'framer-motion';
import { TrendingUp, CheckCircle2, AlertCircle, Clock, Zap } from 'lucide-react';

/**
 * HeroStats — Big visual stats card with ring chart
 * Shows total operations, completion rate, and status breakdown
 */

export default function HeroStats({ tasks = [] }) {
    const completed = tasks.filter(t => t.status === 'completed').length;
    const inProgress = tasks.filter(t => t.status === 'in_progress').length;
    const failed = tasks.filter(t => t.status === 'failed').length;
    const total = tasks.length;
    const rate = total > 0 ? Math.round((completed / total) * 100) : 0;

    // SVG ring chart
    const radius = 40;
    const circumference = 2 * Math.PI * radius;
    const completedArc = total > 0 ? (completed / total) * circumference : 0;
    const inProgressArc = total > 0 ? (inProgress / total) * circumference : 0;
    const failedArc = total > 0 ? (failed / total) * circumference : 0;

    const stats = [
        { label: 'Done', value: completed, icon: CheckCircle2, color: 'text-emerald-400', bg: 'bg-emerald-400/10' },
        { label: 'Active', value: inProgress, icon: Clock, color: 'text-amber-400', bg: 'bg-amber-400/10' },
        { label: 'Failed', value: failed, icon: AlertCircle, color: 'text-red-400', bg: 'bg-red-400/10' },
    ];

    return (
        <div className="flex items-center gap-6 h-full">
            {/* Ring Chart */}
            <div className="relative flex-shrink-0">
                <svg width="100" height="100" className="-rotate-90">
                    {/* Background ring */}
                    <circle
                        cx="50" cy="50" r={radius}
                        fill="none" stroke="rgba(255,255,255,0.05)" strokeWidth="8"
                    />
                    {/* Completed arc */}
                    <motion.circle
                        cx="50" cy="50" r={radius}
                        fill="none" stroke="#34d399" strokeWidth="8"
                        strokeLinecap="round"
                        strokeDasharray={circumference}
                        initial={{ strokeDashoffset: circumference }}
                        animate={{ strokeDashoffset: circumference - completedArc }}
                        transition={{ duration: 1.5, ease: 'easeOut', delay: 0.2 }}
                    />
                    {/* In-progress arc */}
                    <motion.circle
                        cx="50" cy="50" r={radius}
                        fill="none" stroke="#fbbf24" strokeWidth="8"
                        strokeLinecap="round"
                        strokeDasharray={circumference}
                        initial={{ strokeDashoffset: circumference }}
                        animate={{ strokeDashoffset: circumference - inProgressArc }}
                        transition={{ duration: 1.5, ease: 'easeOut', delay: 0.4 }}
                        style={{ transform: `rotate(${(completed / Math.max(total, 1)) * 360}deg)`, transformOrigin: '50px 50px' }}
                    />
                    {/* Failed arc */}
                    <motion.circle
                        cx="50" cy="50" r={radius}
                        fill="none" stroke="#f87171" strokeWidth="8"
                        strokeLinecap="round"
                        strokeDasharray={circumference}
                        initial={{ strokeDashoffset: circumference }}
                        animate={{ strokeDashoffset: circumference - failedArc }}
                        transition={{ duration: 1.5, ease: 'easeOut', delay: 0.6 }}
                        style={{ transform: `rotate(${((completed + inProgress) / Math.max(total, 1)) * 360}deg)`, transformOrigin: '50px 50px' }}
                    />
                </svg>

                {/* Center label */}
                <div className="absolute inset-0 flex flex-col items-center justify-center">
                    <motion.span
                        className="text-2xl font-black text-white stat-number"
                        initial={{ opacity: 0, scale: 0.5 }}
                        animate={{ opacity: 1, scale: 1 }}
                        transition={{ delay: 0.5, type: 'spring' }}
                    >
                        {rate}%
                    </motion.span>
                    <span className="text-[8px] uppercase tracking-widest text-dark-500 font-bold">Success</span>
                </div>
            </div>

            {/* Stats breakdown */}
            <div className="flex-1 space-y-2">
                <div className="flex items-center gap-2 mb-3">
                    <Zap className="w-4 h-4 text-primary-400" />
                    <span className="text-lg font-black text-white stat-number">{total}</span>
                    <span className="text-xs text-dark-500 font-medium">total ops</span>
                </div>
                {stats.map((stat) => (
                    <div key={stat.label} className="flex items-center gap-2">
                        <div className={`p-1 rounded-md ${stat.bg}`}>
                            <stat.icon className={`w-3 h-3 ${stat.color}`} />
                        </div>
                        <span className="text-xs text-dark-400 flex-1">{stat.label}</span>
                        <span className={`text-sm font-bold stat-number ${stat.color}`}>{stat.value}</span>
                    </div>
                ))}
            </div>
        </div>
    );
}
