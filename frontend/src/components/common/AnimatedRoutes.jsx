import { motion, AnimatePresence } from 'framer-motion';
import { useLocation } from 'react-router-dom';

/**
 * AnimatedRoutes — Wraps React Router with smooth page transitions
 * Provides a crossfade + subtle slide animation between routes.
 * 
 * Usage:
 *   <AnimatedRoutes>
 *     <Routes>
 *       <Route ... />
 *     </Routes>
 *   </AnimatedRoutes>
 */

const pageVariants = {
    initial: {
        opacity: 0,
        y: 8,
        filter: 'blur(4px)',
    },
    enter: {
        opacity: 1,
        y: 0,
        filter: 'blur(0px)',
        transition: {
            duration: 0.3,
            ease: [0.25, 0.4, 0.25, 1],
        },
    },
    exit: {
        opacity: 0,
        y: -8,
        filter: 'blur(4px)',
        transition: {
            duration: 0.2,
            ease: [0.4, 0, 1, 1],
        },
    },
};

export default function AnimatedRoutes({ children }) {
    const location = useLocation();

    return (
        <AnimatePresence mode="wait" initial={false}>
            <motion.div
                key={location.pathname}
                variants={pageVariants}
                initial="initial"
                animate="enter"
                exit="exit"
                style={{ minHeight: '100vh' }}
            >
                {children}
            </motion.div>
        </AnimatePresence>
    );
}
