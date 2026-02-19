import { motion } from 'framer-motion';

/**
 * ScrollReveal — Scroll-triggered stagger reveal animation
 * Wraps children with a fade-up animation that triggers when scrolled into view.
 * 
 * Usage:
 *   <ScrollReveal>
 *     <h2>This will animate in</h2>
 *   </ScrollReveal>
 * 
 *   <ScrollReveal delay={0.2} direction="left">
 *     <p>Slides in from left</p>
 *   </ScrollReveal>
 */
const directions = {
    up: { y: 40, x: 0 },
    down: { y: -40, x: 0 },
    left: { y: 0, x: -40 },
    right: { y: 0, x: 40 },
};

export default function ScrollReveal({
    children,
    direction = 'up',
    delay = 0,
    duration = 0.6,
    className = '',
    once = true,
}) {
    const offset = directions[direction] || directions.up;

    return (
        <motion.div
            initial={{
                opacity: 0,
                x: offset.x,
                y: offset.y,
                filter: 'blur(8px)',
            }}
            whileInView={{
                opacity: 1,
                x: 0,
                y: 0,
                filter: 'blur(0px)',
            }}
            viewport={{ once, margin: '-50px' }}
            transition={{
                duration,
                delay,
                ease: [0.25, 0.4, 0.25, 1],
            }}
            className={className}
        >
            {children}
        </motion.div>
    );
}

/**
 * StaggerContainer — Container that staggers children animations
 * Use with ScrollReveal children for beautiful cascade reveals.
 */
export function StaggerContainer({
    children,
    staggerDelay = 0.1,
    className = '',
}) {
    return (
        <motion.div
            initial="hidden"
            whileInView="visible"
            viewport={{ once: true, margin: '-50px' }}
            variants={{
                hidden: {},
                visible: {
                    transition: {
                        staggerChildren: staggerDelay,
                    },
                },
            }}
            className={className}
        >
            {children}
        </motion.div>
    );
}

/**
 * StaggerItem — Individual item within a StaggerContainer
 */
export function StaggerItem({ children, className = '' }) {
    return (
        <motion.div
            variants={{
                hidden: { opacity: 0, y: 30, filter: 'blur(6px)' },
                visible: {
                    opacity: 1,
                    y: 0,
                    filter: 'blur(0px)',
                    transition: {
                        duration: 0.5,
                        ease: [0.25, 0.4, 0.25, 1],
                    },
                },
            }}
            className={className}
        >
            {children}
        </motion.div>
    );
}
