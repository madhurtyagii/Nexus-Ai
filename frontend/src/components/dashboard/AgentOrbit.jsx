import { motion } from 'framer-motion';
import { Brain } from 'lucide-react';

/**
 * AgentOrbit — Orbital visualization of active agents
 * Shows agents as colored dots orbiting a central brain icon
 */

const ORBIT_COLORS = [
    '#0ea5e9', // sky
    '#8b5cf6', // violet
    '#10b981', // emerald
    '#f59e0b', // amber
    '#ec4899', // pink
    '#06b6d4', // cyan
    '#f97316', // orange
    '#6366f1', // indigo
    '#14b8a6', // teal
];

export default function AgentOrbit({ agents = [], className = '' }) {
    // Show all agents, not just active ones. If empty/loading, show 8 "ghost" agents for visual effect
    const displayCount = agents.length || 8;
    const isGhost = agents.length === 0;
    const activeCount = agents.filter(a => a.status === 'active').length;

    // If we have actual agents, use them. If ghost, use default colors.
    const orbitItems = agents.length > 0 ? agents : Array.from({ length: 8 }, (_, i) => ({ id: i }));

    return (
        <div className={`relative flex items-center justify-center ${className} overflow-visible`}>
            {/* Center brain icon container - Orbits are relative to THIS */}
            <div className="flex flex-col items-center">
                <motion.div
                    className="relative flex items-center justify-center w-16 h-16 overflow-visible"
                    initial={{ scale: 0.9 }}
                    animate={{ scale: 1 }}
                >
                    {/* ORBITS - Centered on Brain */}
                    <div className="absolute inset-0 flex items-center justify-center pointer-events-none overflow-visible z-0">
                        {/* Outer glow ring */}
                        <motion.div
                            className="absolute w-[200px] h-[200px] rounded-full"
                            style={{
                                background: 'radial-gradient(circle, rgba(14,165,233,0.06) 0%, transparent 70%)',
                            }}
                            animate={{ scale: [1, 1.05, 1] }}
                            transition={{ duration: 4, repeat: Infinity, ease: 'easeInOut' }}
                        />

                        {/* Orbit rings */}
                        <div className="absolute w-[140px] h-[140px] rounded-full border border-white/[0.04]" />
                        <div className="absolute w-[180px] h-[180px] rounded-full border border-white/[0.03]" />
                        <div className="absolute w-[220px] h-[220px] rounded-full border border-white/[0.02]" />

                        {/* Orbiting agent dots */}
                        {orbitItems.slice(0, 8).map((agent, i) => {
                            // Distribute agents across 3 distinct orbit rings to avoid overlap
                            // Ring 0 (inner): agents 0, 1, 2  — radius 35
                            // Ring 1 (middle): agents 3, 4, 5  — radius 55  
                            // Ring 2 (outer): agents 6, 7       — radius 75
                            const ring = i < 3 ? 0 : i < 6 ? 1 : 2;
                            const orbitRadius = [35, 55, 75][ring];
                            const agentsInRing = ring === 0 ? 3 : ring === 1 ? 3 : 2;
                            const indexInRing = ring === 0 ? i : ring === 1 ? i - 3 : i - 6;
                            const startAngle = (indexInRing * (360 / agentsInRing)) + ring * 30; // offset each ring
                            const speed = 10 + ring * 6 + i * 1.5; // outer = slower
                            const color = isGhost ? ORBIT_COLORS[i % ORBIT_COLORS.length] : (agent.status === 'active' ? '#10b981' : ORBIT_COLORS[i % ORBIT_COLORS.length]);
                            const size = 7 - ring; // inner dots slightly bigger
                            const opacity = isGhost ? 0.6 : 1;

                            return (
                                <motion.div
                                    key={i}
                                    className="absolute"
                                    style={{
                                        width: size,
                                        height: size,
                                    }}
                                    animate={{
                                        rotate: [startAngle, startAngle + 360],
                                    }}
                                    transition={{
                                        duration: speed,
                                        repeat: Infinity,
                                        ease: 'linear',
                                    }}
                                >
                                    <motion.div
                                        className="rounded-full"
                                        style={{
                                            width: size,
                                            height: size,
                                            backgroundColor: color,
                                            boxShadow: `0 0 ${size * 2}px ${color}60`,
                                        }}
                                        initial={{ x: orbitRadius, opacity: opacity, scale: 1 }}
                                        animate={{ scale: [1, 1.3, 1] }}
                                        transition={{
                                            duration: 2 + i * 0.3,
                                            repeat: Infinity,
                                            ease: 'easeInOut',
                                        }}
                                    />
                                </motion.div>
                            );
                        })}
                    </div>

                    {/* Brain Icon Itself */}
                    <div className="absolute inset-0 bg-primary-500/10 rounded-2xl border border-primary-500/20 backdrop-blur-sm z-10" />
                    <Brain className={`relative z-20 w-8 h-8 ${activeCount > 0 ? 'text-primary-400' : 'text-dark-400'}`} />
                </motion.div>

                {/* Text Label - Pushed down below orbits */}
                <div className="mt-8 text-center relative z-20">
                    <div className="text-xl font-black text-white stat-number leading-none">{displayCount}</div>
                    <div className="text-[9px] uppercase tracking-widest text-dark-500 font-bold leading-none mt-1">
                        {activeCount > 0 ? 'Active' : 'Fleet'}
                    </div>
                </div>
            </div>
        </div>
    );
}
