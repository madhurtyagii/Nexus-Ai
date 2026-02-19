import { useState, useEffect, useCallback } from 'react';

/**
 * TypingPlaceholder — Cycles through example prompts with typing animation
 * Shows a blinking cursor and smooth type/delete effect
 */
const PROMPTS = [
    "Research latest React patterns...",
    "Generate a marketing email...",
    "Analyze my sales data...",
    "Build a REST API endpoint...",
    "Debug this Python script...",
    "Write unit tests for...",
    "Create a dashboard widget...",
    "Summarize this document...",
];

export default function TypingPlaceholder({ isActive, actualValue }) {
    const [displayText, setDisplayText] = useState('');
    const [promptIndex, setPromptIndex] = useState(0);
    const [isDeleting, setIsDeleting] = useState(false);
    const [showCursor, setShowCursor] = useState(true);

    // Blink cursor
    useEffect(() => {
        const cursorInterval = setInterval(() => {
            setShowCursor(prev => !prev);
        }, 530);
        return () => clearInterval(cursorInterval);
    }, []);

    // Typing effect
    useEffect(() => {
        // Don't animate when user is actively typing
        if (isActive || actualValue) return;

        const currentPrompt = PROMPTS[promptIndex];
        let timeout;

        if (!isDeleting) {
            if (displayText.length < currentPrompt.length) {
                timeout = setTimeout(() => {
                    setDisplayText(currentPrompt.slice(0, displayText.length + 1));
                }, 60 + Math.random() * 40); // Variable speed for natural feel
            } else {
                // Pause at end before deleting
                timeout = setTimeout(() => setIsDeleting(true), 2000);
            }
        } else {
            if (displayText.length > 0) {
                timeout = setTimeout(() => {
                    setDisplayText(displayText.slice(0, -1));
                }, 30);
            } else {
                setIsDeleting(false);
                setPromptIndex((prev) => (prev + 1) % PROMPTS.length);
            }
        }

        return () => clearTimeout(timeout);
    }, [displayText, isDeleting, promptIndex, isActive, actualValue]);

    // Don't show when user is typing
    if (isActive || actualValue) return null;

    return (
        <span className="pointer-events-none select-none text-dark-600 font-medium flex items-center">
            {displayText}
            <span
                className="inline-block w-0.5 h-5 ml-0.5 bg-primary-400/60"
                style={{ opacity: showCursor ? 1 : 0, transition: 'opacity 0.1s' }}
            />
        </span>
    );
}
