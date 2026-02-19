import { useRef, useState } from 'react';
import { motion } from 'framer-motion';

/**
 * SpotlightCard — Premium card with cursor-tracking radial spotlight
 * Inspired by Linear/Stripe. The glow follows the mouse within the card.
 * 
 * Usage:
 *   <SpotlightCard className="p-6" spotlightColor="rgba(14, 165, 233, 0.08)">
 *     <h3>Content</h3>
 *   </SpotlightCard>
 */
export default function SpotlightCard({
    children,
    className = '',
    spotlightColor = 'rgba(14, 165, 233, 0.06)',
    borderColor = 'rgba(14, 165, 233, 0.15)',
    as: Component = 'div',
    onClick,
    ...props
}) {
    const cardRef = useRef(null);
    const [position, setPosition] = useState({ x: 0, y: 0 });
    const [isHovered, setIsHovered] = useState(false);
    const [opacity, setOpacity] = useState(0);

    const handleMouseMove = (e) => {
        if (!cardRef.current) return;
        const rect = cardRef.current.getBoundingClientRect();
        setPosition({
            x: e.clientX - rect.left,
            y: e.clientY - rect.top,
        });
    };

    const handleMouseEnter = () => {
        setIsHovered(true);
        setOpacity(1);
    };

    const handleMouseLeave = () => {
        setIsHovered(false);
        setOpacity(0);
    };

    return (
        <Component
            ref={cardRef}
            onMouseMove={handleMouseMove}
            onMouseEnter={handleMouseEnter}
            onMouseLeave={handleMouseLeave}
            onClick={onClick}
            className={`relative overflow-hidden rounded-2xl transition-all duration-300 ${className}`}
            style={{
                background: 'var(--bg-card)',
                backdropFilter: 'blur(16px) saturate(150%)',
                WebkitBackdropFilter: 'blur(16px) saturate(150%)',
                border: `1px solid ${isHovered ? borderColor : 'var(--border)'}`,
                boxShadow: isHovered
                    ? `var(--shadow-elevated), var(--shadow-inset-hover)`
                    : `var(--shadow-card), var(--shadow-inset)`,
                cursor: onClick ? 'pointer' : 'default',
            }}
            {...props}
        >
            {/* Spotlight radial gradient that follows cursor */}
            <div
                className="pointer-events-none absolute inset-0 transition-opacity duration-300"
                style={{
                    opacity,
                    background: `radial-gradient(350px circle at ${position.x}px ${position.y}px, ${spotlightColor}, transparent 70%)`,
                }}
            />

            {/* Top edge highlight */}
            <div
                className="pointer-events-none absolute inset-x-0 top-0 h-px transition-opacity duration-500"
                style={{
                    opacity: isHovered ? 1 : 0,
                    background: `radial-gradient(ellipse at ${position.x}px 0px, ${borderColor}, transparent 60%)`,
                }}
            />

            {/* Content */}
            <div className="relative z-10">{children}</div>
        </Component>
    );
}
