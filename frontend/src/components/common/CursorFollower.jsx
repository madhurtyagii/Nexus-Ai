import { useState, useEffect, useRef } from 'react';
import { motion, useMotionValue, useSpring, AnimatePresence } from 'framer-motion';

// Available effect types
export const CURSOR_EFFECTS = [
    { id: 'ring', name: 'Neon Ring', description: 'Subtle glowing ring' },
    { id: 'particles', name: 'Particles', description: 'Floating glowing dots' },
    { id: 'ribbon', name: 'Ribbon', description: 'Smooth flowing line' },
    { id: 'aurora', name: 'Aurora', description: 'Rotating gradient glow' },
    { id: 'stardust', name: 'Stardust', description: 'Twinkling stars' },
    { id: 'orbit', name: 'Orbit', description: 'Spinning circles' },
];

// Get settings from localStorage
function getCursorSettings() {
    const enabled = localStorage.getItem('nexus-cursor-effect');
    const effect = localStorage.getItem('nexus-cursor-type') || 'ring';
    return {
        enabled: enabled === null ? true : enabled === 'true',
        effect
    };
}

// Export helper functions for Settings
export function toggleCursorEffect(enabled) {
    localStorage.setItem('nexus-cursor-effect', enabled.toString());
    window.dispatchEvent(new Event('cursor-setting-changed'));
}

export function setCursorEffectType(type) {
    localStorage.setItem('nexus-cursor-type', type);
    window.dispatchEvent(new Event('cursor-setting-changed'));
}

// === EFFECT COMPONENTS ===

// Neon Ring (default)
function RingEffect({ smoothX, smoothY }) {
    return (
        <motion.div
            className="fixed pointer-events-none"
            style={{ x: smoothX, y: smoothY, zIndex: 1 }}
        >
            <div
                style={{
                    width: 36, height: 36,
                    marginLeft: -18, marginTop: -18,
                    borderRadius: '50%',
                    border: '1.5px solid rgba(14, 165, 233, 0.25)',
                    boxShadow: '0 0 12px rgba(14, 165, 233, 0.15), 0 0 4px rgba(139, 92, 246, 0.1)',
                }}
            />
        </motion.div>
    );
}

// Particles
function ParticleEffect({ mouseX, mouseY }) {
    const [particles, setParticles] = useState([]);
    const idRef = useRef(0);
    const lastPos = useRef({ x: 0, y: 0 });

    useEffect(() => {
        const unsub = mouseX.on('change', (x) => {
            const y = mouseY.get();
            if (Math.hypot(x - lastPos.current.x, y - lastPos.current.y) > 15) {
                lastPos.current = { x, y };
                idRef.current += 1;
                setParticles(prev => [...prev.slice(-10), { id: idRef.current, x, y, size: Math.random() * 3 + 2 }]);
            }
        });
        return () => unsub();
    }, [mouseX, mouseY]);

    useEffect(() => {
        const cleanup = setInterval(() => setParticles(prev => prev.slice(1)), 80);
        return () => clearInterval(cleanup);
    }, []);

    return (
        <svg className="fixed inset-0 pointer-events-none w-full h-full" style={{ zIndex: 1 }}>
            {particles.map((p, i) => (
                <circle key={p.id} cx={p.x} cy={p.y} r={p.size} fill={`rgba(14, 165, 233, ${((i + 1) / particles.length) * 0.25})`} />
            ))}
        </svg>
    );
}

// Ribbon
function RibbonEffect({ mouseX, mouseY }) {
    const [points, setPoints] = useState([]);
    const idRef = useRef(0);

    useEffect(() => {
        const unsub = mouseX.on('change', (x) => {
            const y = mouseY.get();
            idRef.current += 1;
            setPoints(prev => [...prev.slice(-12), { x, y, id: idRef.current }]);
        });
        return () => unsub();
    }, [mouseX, mouseY]);

    useEffect(() => {
        const cleanup = setInterval(() => setPoints(prev => prev.slice(1)), 60);
        return () => clearInterval(cleanup);
    }, []);

    if (points.length < 2) return null;

    return (
        <svg className="fixed inset-0 pointer-events-none w-full h-full" style={{ zIndex: 1 }}>
            {points.slice(0, -1).map((point, i) => (
                <line key={point.id} x1={point.x} y1={point.y} x2={points[i + 1].x} y2={points[i + 1].y}
                    stroke={`rgba(139, 92, 246, ${((i + 1) / points.length) * 0.2})`} strokeWidth="1.5" strokeLinecap="round" />
            ))}
        </svg>
    );
}

// Aurora
function AuroraEffect({ smoothX, smoothY }) {
    return (
        <motion.div className="fixed pointer-events-none" style={{ x: smoothX, y: smoothY, zIndex: 1 }}>
            <motion.div
                className="relative -translate-x-1/2 -translate-y-1/2 w-14 h-14 rounded-full opacity-20"
                animate={{ rotate: 360 }}
                transition={{ duration: 6, repeat: Infinity, ease: 'linear' }}
                style={{
                    background: 'conic-gradient(from 0deg, rgba(14,165,233,0.4), rgba(139,92,246,0.4), rgba(14,165,233,0.4))',
                    filter: 'blur(8px)',
                }}
            />
        </motion.div>
    );
}

// Stardust
function StardustEffect({ mouseX, mouseY }) {
    const [stars, setStars] = useState([]);
    const idRef = useRef(0);

    useEffect(() => {
        const unsub = mouseX.on('change', (x) => {
            const y = mouseY.get();
            if (Math.random() > 0.7) {
                idRef.current += 1;
                setStars(prev => [...prev.slice(-8), {
                    id: idRef.current,
                    x: x + (Math.random() - 0.5) * 25,
                    y: y + (Math.random() - 0.5) * 25,
                }]);
            }
        });
        return () => unsub();
    }, [mouseX, mouseY]);

    useEffect(() => {
        const cleanup = setInterval(() => setStars(prev => prev.slice(1)), 100);
        return () => clearInterval(cleanup);
    }, []);

    return (
        <svg className="fixed inset-0 pointer-events-none w-full h-full" style={{ zIndex: 1 }}>
            {stars.map((star, i) => (
                <text key={star.id} x={star.x} y={star.y} fill={`rgba(14, 165, 233, ${((i + 1) / stars.length) * 0.3})`}
                    fontSize="10" textAnchor="middle" dominantBaseline="middle">✦</text>
            ))}
        </svg>
    );
}

// Orbit
function OrbitEffect({ smoothX, smoothY }) {
    return (
        <motion.div className="fixed pointer-events-none" style={{ x: smoothX, y: smoothY, zIndex: 1 }}>
            <motion.div
                className="relative -translate-x-1/2 -translate-y-1/2"
                animate={{ rotate: 360 }}
                transition={{ duration: 3, repeat: Infinity, ease: 'linear' }}
            >
                {[0, 1, 2].map((i) => (
                    <div key={i} className="absolute w-1 h-1 rounded-full bg-primary-400/30"
                        style={{ left: Math.cos(i * (Math.PI * 2 / 3)) * 10, top: Math.sin(i * (Math.PI * 2 / 3)) * 10 }} />
                ))}
            </motion.div>
        </motion.div>
    );
}

// Main Component
export default function CursorFollower() {
    const [settings, setSettings] = useState(getCursorSettings);

    const mouseX = useMotionValue(-100);
    const mouseY = useMotionValue(-100);

    const springConfig = { damping: 25, stiffness: 180, mass: 0.6 };
    const smoothX = useSpring(mouseX, springConfig);
    const smoothY = useSpring(mouseY, springConfig);

    useEffect(() => {
        const handleChange = () => setSettings(getCursorSettings());
        window.addEventListener('cursor-setting-changed', handleChange);
        window.addEventListener('storage', handleChange);
        return () => {
            window.removeEventListener('cursor-setting-changed', handleChange);
            window.removeEventListener('storage', handleChange);
        };
    }, []);

    useEffect(() => {
        if (!settings.enabled || 'ontouchstart' in window) return;
        const move = (e) => { mouseX.set(e.clientX); mouseY.set(e.clientY); };
        window.addEventListener('mousemove', move);
        return () => window.removeEventListener('mousemove', move);
    }, [mouseX, mouseY, settings.enabled]);

    if (!settings.enabled) return null;

    switch (settings.effect) {
        case 'particles': return <ParticleEffect mouseX={mouseX} mouseY={mouseY} />;
        case 'ribbon': return <RibbonEffect mouseX={mouseX} mouseY={mouseY} />;
        case 'aurora': return <AuroraEffect smoothX={smoothX} smoothY={smoothY} />;
        case 'stardust': return <StardustEffect mouseX={mouseX} mouseY={mouseY} />;
        case 'orbit': return <OrbitEffect smoothX={smoothX} smoothY={smoothY} />;
        default: return <RingEffect smoothX={smoothX} smoothY={smoothY} />;
    }
}
