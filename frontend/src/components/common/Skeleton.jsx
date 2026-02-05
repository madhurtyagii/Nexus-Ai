import { motion } from 'framer-motion';

// Base skeleton with shimmer animation
export function Skeleton({ className = '', ...props }) {
    return (
        <div
            className={`relative overflow-hidden bg-white/5 rounded-lg ${className}`}
            {...props}
        >
            <motion.div
                className="absolute inset-0 bg-gradient-to-r from-transparent via-white/10 to-transparent"
                animate={{ x: ['-100%', '100%'] }}
                transition={{ duration: 1.5, repeat: Infinity, ease: 'linear' }}
            />
        </div>
    );
}

// Card skeleton for project/task cards
export function CardSkeleton() {
    return (
        <div className="glass p-6 rounded-2xl border border-white/5 space-y-4">
            <div className="flex items-center justify-between">
                <Skeleton className="h-6 w-24 rounded-lg" />
                <Skeleton className="h-4 w-4 rounded" />
            </div>
            <Skeleton className="h-5 w-3/4 rounded" />
            <Skeleton className="h-4 w-full rounded" />
            <Skeleton className="h-4 w-2/3 rounded" />
            <div className="flex items-center justify-between pt-4 border-t border-white/5">
                <Skeleton className="h-4 w-20 rounded" />
                <Skeleton className="h-4 w-16 rounded" />
            </div>
        </div>
    );
}

// Stat card skeleton
export function StatSkeleton() {
    return (
        <div className="glass p-5 rounded-2xl border border-white/5">
            <div className="flex items-center justify-between">
                <div className="space-y-2">
                    <Skeleton className="h-3 w-16 rounded" />
                    <Skeleton className="h-8 w-12 rounded" />
                </div>
                <Skeleton className="h-8 w-8 rounded-lg" />
            </div>
        </div>
    );
}

// Task list skeleton
export function TaskListSkeleton({ count = 4 }) {
    return (
        <div className="space-y-4">
            {Array.from({ length: count }).map((_, i) => (
                <div key={i} className="flex items-center gap-4 p-4 rounded-xl bg-white/[0.02] border border-white/5">
                    <Skeleton className="h-3 w-3 rounded-full" />
                    <div className="flex-1 space-y-2">
                        <Skeleton className="h-4 w-3/4 rounded" />
                        <Skeleton className="h-3 w-1/2 rounded" />
                    </div>
                </div>
            ))}
        </div>
    );
}

// Dashboard skeleton
export function DashboardSkeleton() {
    return (
        <div className="space-y-8 animate-pulse">
            {/* Welcome section */}
            <div className="space-y-2">
                <Skeleton className="h-10 w-80 rounded-lg" />
                <Skeleton className="h-5 w-96 rounded" />
            </div>

            {/* Command input */}
            <Skeleton className="h-16 w-full rounded-2xl" />

            {/* Grid row 1 */}
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
                <div className="space-y-4">
                    <Skeleton className="h-8 w-32 rounded" />
                    <div className="grid grid-cols-2 gap-3">
                        {[1, 2, 3, 4].map((i) => (
                            <Skeleton key={i} className="h-20 rounded-2xl" />
                        ))}
                    </div>
                </div>
                <div className="space-y-4">
                    <Skeleton className="h-8 w-40 rounded" />
                    <TaskListSkeleton count={3} />
                </div>
                <div className="space-y-4">
                    <Skeleton className="h-8 w-32 rounded" />
                    <Skeleton className="h-40 rounded-2xl" />
                </div>
            </div>
        </div>
    );
}

// Projects grid skeleton
export function ProjectsGridSkeleton({ count = 6 }) {
    return (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
            {Array.from({ length: count }).map((_, i) => (
                <CardSkeleton key={i} />
            ))}
        </div>
    );
}

// Table skeleton
export function TableSkeleton({ rows = 5, cols = 4 }) {
    return (
        <div className="space-y-3">
            <div className="flex gap-4 p-4 border-b border-white/5">
                {Array.from({ length: cols }).map((_, i) => (
                    <Skeleton key={i} className="h-4 flex-1 rounded" />
                ))}
            </div>
            {Array.from({ length: rows }).map((_, i) => (
                <div key={i} className="flex gap-4 p-4">
                    {Array.from({ length: cols }).map((_, j) => (
                        <Skeleton key={j} className="h-4 flex-1 rounded" />
                    ))}
                </div>
            ))}
        </div>
    );
}

export default Skeleton;
