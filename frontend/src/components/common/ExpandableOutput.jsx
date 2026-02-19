import { useState, useRef, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import MarkdownRenderer from './MarkdownRenderer';
import './ExpandableOutput.css';

/**
 * ExpandableOutput — Premium collapsible output viewer
 * 
 * Features:
 * - Collapsed preview with gradient fade
 * - Show More / Show Less toggle
 * - Fullscreen modal for deep reading
 * - Copy-all button
 * - Smooth animations
 * 
 * @param {string} content - Markdown content to render
 * @param {string} title - Title for fullscreen modal header  
 * @param {number} collapsedHeight - Max height when collapsed (default 300)
 * @param {string} className - Additional CSS classes
 */
export default function ExpandableOutput({
    content,
    title = 'Output',
    collapsedHeight = 300,
    className = ''
}) {
    const [isExpanded, setIsExpanded] = useState(false);
    const [isFullscreen, setIsFullscreen] = useState(false);
    const [copied, setCopied] = useState(false);
    const [needsExpand, setNeedsExpand] = useState(false);
    const contentRef = useRef(null);

    // Check if content overflows the collapsed height
    useEffect(() => {
        if (!contentRef.current) return;

        const checkOverflow = () => {
            if (contentRef.current) {
                const hasOverflow = contentRef.current.scrollHeight > collapsedHeight + 5;
                setNeedsExpand(hasOverflow);
            }
        };

        // Initial check
        const timer = setTimeout(checkOverflow, 100);

        // Observe content changes (e.g., as markdown renders or images load)
        const observer = new ResizeObserver(checkOverflow);
        observer.observe(contentRef.current);

        return () => {
            clearTimeout(timer);
            observer.disconnect();
        };
    }, [content, collapsedHeight]);

    const handleCopyAll = async () => {
        try {
            await navigator.clipboard.writeText(content || '');
            setCopied(true);
            setTimeout(() => setCopied(false), 2000);
        } catch (err) {
            console.error('Failed to copy:', err);
        }
    };

    // Close fullscreen on Escape key
    useEffect(() => {
        const handleKey = (e) => {
            if (e.key === 'Escape' && isFullscreen) {
                setIsFullscreen(false);
            }
        };
        if (isFullscreen) {
            document.addEventListener('keydown', handleKey);
            document.body.style.overflow = 'hidden';
        }
        return () => {
            document.removeEventListener('keydown', handleKey);
            document.body.style.overflow = '';
        };
    }, [isFullscreen]);

    if (!content) return null;

    return (
        <>
            <div className={`expandable-output ${className}`}>
                {/* Content */}
                <div
                    ref={contentRef}
                    className={`expandable-output-content ${isExpanded ? 'expanded' : 'collapsed'}`}
                    style={!isExpanded ? { maxHeight: `${collapsedHeight}px` } : undefined}
                >
                    <MarkdownRenderer content={content} />
                </div>

                {/* Gradient Fade (only when collapsed and content overflows) */}
                {needsExpand && !isExpanded && (
                    <div className="expandable-output-fade" />
                )}

                {/* Controls */}
                <div className="expandable-output-controls">
                    {needsExpand && (
                        <button
                            className={`expand-toggle-btn ${isExpanded ? 'expanded' : ''}`}
                            onClick={() => setIsExpanded(!isExpanded)}
                        >
                            <span className="expand-icon">▼</span>
                            {isExpanded ? 'Show Less' : 'Show More'}
                        </button>
                    )}

                    <button
                        className="fullscreen-btn"
                        onClick={() => setIsFullscreen(true)}
                        title="Open in fullscreen"
                    >
                        ⛶
                    </button>

                    <button
                        className={`copy-all-btn ${copied ? 'copied' : ''}`}
                        onClick={handleCopyAll}
                        title={copied ? 'Copied!' : 'Copy all content'}
                    >
                        {copied ? '✓' : '📋'}
                    </button>
                </div>
            </div>

            {/* Fullscreen Modal */}
            <AnimatePresence>
                {isFullscreen && (
                    <motion.div
                        className="expandable-fullscreen-overlay"
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        exit={{ opacity: 0 }}
                        onClick={(e) => {
                            if (e.target === e.currentTarget) setIsFullscreen(false);
                        }}
                    >
                        <motion.div
                            className="expandable-fullscreen-modal"
                            initial={{ opacity: 0, y: 30, scale: 0.95 }}
                            animate={{ opacity: 1, y: 0, scale: 1 }}
                            exit={{ opacity: 0, y: 30, scale: 0.95 }}
                            transition={{ type: 'spring', stiffness: 300, damping: 25 }}
                        >
                            <div className="fullscreen-header">
                                <h3>📄 {title}</h3>
                                <button
                                    className="fullscreen-close-btn"
                                    onClick={() => setIsFullscreen(false)}
                                >
                                    ✕
                                </button>
                            </div>
                            <div className="fullscreen-body">
                                <MarkdownRenderer content={content} />
                            </div>
                        </motion.div>
                    </motion.div>
                )}
            </AnimatePresence>
        </>
    );
}
