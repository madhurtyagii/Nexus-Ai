import { useState, useRef, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Sparkles, Send, Loader2 } from 'lucide-react';
import './FloatingRefinementBar.css';

const FloatingRefinementBar = ({
    onRefine,
    isLoading,
    placeholder = "Steer your project with natural language...",
    title = "Smart Refinement",
    subtitle = "Ask to add phases, change scope, or adjust tasks."
}) => {
    const [input, setInput] = useState('');
    const textareaRef = useRef(null);

    // Auto-expand textarea
    useEffect(() => {
        if (textareaRef.current) {
            textareaRef.current.style.height = 'auto';
            textareaRef.current.style.height = `${Math.min(textareaRef.current.scrollHeight, 120)}px`;
        }
    }, [input]);

    const handleSubmit = () => {
        if (!input.trim() || isLoading) return;
        onRefine(input);
        setInput('');
    };

    const handleKeyDown = (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            handleSubmit();
        }
    };

    return (
        <AnimatePresence>
            <motion.div
                className="floating-refinement-container"
                initial={{ y: 100, x: '-50%', opacity: 0 }}
                animate={{ y: 0, x: '-50%', opacity: 1 }}
                exit={{ y: 100, x: '-50%', opacity: 0 }}
                transition={{ type: 'spring', damping: 25, stiffness: 200 }}
            >
                <div className="floating-refinement-bar glass">
                    <div className="refinement-header">
                        <div className="flex items-center gap-2">
                            <div className="sparkle-icon">
                                <Sparkles className="w-4 h-4 text-primary-400" />
                            </div>
                            <div>
                                <h3 className="refinement-title">{title}</h3>
                                <p className="refinement-subtitle">{subtitle}</p>
                            </div>
                        </div>
                    </div>

                    <div className="refinement-input-wrapper">
                        <textarea
                            ref={textareaRef}
                            value={input}
                            onChange={(e) => setInput(e.target.value)}
                            onKeyDown={handleKeyDown}
                            placeholder={placeholder}
                            rows={1}
                            className="refinement-textarea-floating"
                        />
                        <button
                            className={`refinement-send-btn ${input.trim() ? 'active' : ''}`}
                            onClick={handleSubmit}
                            disabled={!input.trim() || isLoading}
                        >
                            {isLoading ? (
                                <Loader2 className="w-5 h-5 animate-spin" />
                            ) : (
                                <Send className="w-5 h-5" />
                            )}
                        </button>
                    </div>
                </div>
            </motion.div>
        </AnimatePresence>
    );
};

export default FloatingRefinementBar;
