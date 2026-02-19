import { motion, AnimatePresence } from 'framer-motion';

export default function ImageLightbox({ isOpen, imageUrl, onClose }) {
    if (!isOpen || !imageUrl) return null;

    return (
        <AnimatePresence>
            {isOpen && (
                <motion.div
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    exit={{ opacity: 0 }}
                    className="fixed inset-0 z-[200] flex items-center justify-center bg-black/95 backdrop-blur-md p-4 lg:p-10 cursor-zoom-out"
                    onClick={onClose}
                >
                    <motion.div
                        initial={{ scale: 0.9, opacity: 0, y: 20 }}
                        animate={{ scale: 1, opacity: 1, y: 0 }}
                        exit={{ scale: 0.9, opacity: 0, y: 20 }}
                        transition={{ type: 'spring', damping: 25, stiffness: 200 }}
                        className="relative max-w-full max-h-full overflow-hidden rounded-2xl shadow-2xl border border-white/10"
                        onClick={(e) => e.stopPropagation()}
                    >
                        <img
                            src={imageUrl}
                            alt="Expanded creation"
                            className="max-w-full max-h-[85vh] object-contain"
                        />

                        {/* Meta/Actions Bar */}
                        <div className="absolute top-4 right-4 flex gap-2">
                            <button
                                onClick={onClose}
                                className="w-10 h-10 flex items-center justify-center rounded-full bg-black/50 text-white hover:bg-white/20 backdrop-blur-md transition-all border border-white/10"
                                title="Close"
                            >
                                ✕
                            </button>
                        </div>

                        <div className="p-4 bg-dark-900/80 backdrop-blur-md border-t border-white/5 flex items-center justify-between">
                            <span className="text-xs font-bold text-dark-300 uppercase tracking-widest">Nexus AI Visual Engine</span>
                            <a
                                href={imageUrl}
                                download
                                className="text-xs font-bold text-primary-400 hover:text-white transition-colors"
                            >
                                DOWNLOAD ORIGINAL
                            </a>
                        </div>
                    </motion.div>
                </motion.div>
            )}
        </AnimatePresence>
    );
}
