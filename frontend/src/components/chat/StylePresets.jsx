import React from 'react';
import { motion } from 'framer-motion';

const STYLES = [
    { id: 'Photorealistic', emoji: '📸', label: 'Photo' },
    { id: 'Digital Art', emoji: '🎨', label: 'Digital' },
    { id: 'Anime', emoji: '🎌', label: 'Anime' },
    { id: '3D Render', emoji: '🧊', label: '3D' },
    { id: 'Sketch', emoji: '✏️', label: 'Sketch' },
    { id: 'Cyberpunk', emoji: '🦾', label: 'Cyber' },
    { id: 'Minimalist', emoji: '⚪', label: 'Minimal' }
];

export default function StylePresets({ selectedStyle, onSelectStyle }) {
    return (
        <div className="flex flex-col gap-2 mb-3">
            <span className="text-[10px] font-bold uppercase tracking-wider text-dark-500 ml-1">
                Style Presets
            </span>
            <div className="flex gap-2 overflow-x-auto pb-2 scrollbar-hide no-scrollbar">
                {STYLES.map((style) => (
                    <motion.button
                        key={style.id}
                        whileHover={{ scale: 1.05 }}
                        whileTap={{ scale: 0.95 }}
                        onClick={() => onSelectStyle(selectedStyle === style.id ? null : style.id)}
                        className={`flex items-center gap-2 px-3 py-1.5 rounded-full border whitespace-nowrap transition-all duration-300 ${selectedStyle === style.id
                                ? 'bg-primary-500/20 border-primary-500 text-white shadow-lg shadow-primary-500/10'
                                : 'bg-dark-800/50 border-dark-700 text-dark-400 hover:border-dark-600 hover:bg-dark-700/50'
                            }`}
                    >
                        <span className="text-sm">{style.emoji}</span>
                        <span className="text-xs font-medium">{style.label}</span>
                    </motion.button>
                ))}
            </div>
        </div>
    );
}
