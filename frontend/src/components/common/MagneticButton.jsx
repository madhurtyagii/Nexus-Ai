import { useRef, useState } from 'react';
import { motion } from 'framer-motion';

/**
 * MagneticButton — Button that attracts toward cursor on hover
 * Creates a subtle magnetic pull effect similar to macOS dock icons.
 * 
 * Usage:
 *   <MagneticButton>
 *     <button className="btn-primary">Click Me</button>
 *   </MagneticButton>
 */
export default function MagneticButton({ children, strength = 0.3, className = '' }) {
    const ref = useRef(null);
    const [position, setPosition] = useState({ x: 0, y: 0 });

    const handleMouseMove = (e) => {
        if (!ref.current) return;
        const rect = ref.current.getBoundingClientRect();
        const centerX = rect.left + rect.width / 2;
        const centerY = rect.top + rect.height / 2;
        setPosition({
            x: (e.clientX - centerX) * strength,
            y: (e.clientY - centerY) * strength,
        });
    };

    const handleMouseLeave = () => {
        setPosition({ x: 0, y: 0 });
    };

    return (
        <motion.div
            ref={ref}
            onMouseMove={handleMouseMove}
            onMouseLeave={handleMouseLeave}
            animate={{ x: position.x, y: position.y }}
            transition={{ type: 'spring', stiffness: 200, damping: 15, mass: 0.2 }}
            className={`inline-block ${className}`}
        >
            {children}
        </motion.div>
    );
}
