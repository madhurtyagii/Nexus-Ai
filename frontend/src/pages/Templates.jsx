import React from 'react';
import { useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { ArrowLeft, Bot, Sparkles, Rocket } from 'lucide-react';
import Navbar from '../components/layout/Navbar';
import Sidebar from '../components/layout/Sidebar';

export default function Templates() {
    const navigate = useNavigate();

    return (
        <div className="min-h-screen selection:bg-primary-500/30">
            <Navbar />
            <div className="flex">
                <Sidebar />
                <main className="flex-1 p-6 lg:p-8">
                    <motion.div
                        className="max-w-4xl mx-auto"
                        initial={{ opacity: 0, y: 12 }}
                        animate={{ opacity: 1, y: 0 }}
                    >
                        {/* Back */}
                        <motion.button
                            onClick={() => navigate(-1)}
                            className="flex items-center gap-2 text-dark-400 hover:text-white mb-8 transition-colors text-sm font-medium group"
                            whileHover={{ x: -4 }}
                        >
                            <ArrowLeft className="w-4 h-4 group-hover:text-primary-400 transition-colors" />
                            Back
                        </motion.button>

                        {/* Header */}
                        <div className="mb-10">
                            <h1 className="text-3xl font-black text-white tracking-tight mb-2">Agent Templates</h1>
                            <p className="text-dark-400 font-medium">Browse and manage specialized AI agent configurations.</p>
                        </div>

                        {/* Coming Soon Card */}
                        <motion.div
                            className="card p-16 text-center relative overflow-hidden"
                            initial={{ opacity: 0, scale: 0.95 }}
                            animate={{ opacity: 1, scale: 1 }}
                            transition={{ delay: 0.15, type: 'spring', stiffness: 200, damping: 20 }}
                        >
                            {/* Background glow */}
                            <div className="absolute inset-0 bg-gradient-to-br from-primary-500/5 via-purple-500/5 to-transparent pointer-events-none" />

                            <motion.div
                                className="w-24 h-24 bg-white/[0.03] border border-white/[0.06] rounded-3xl flex items-center justify-center mx-auto mb-8 relative"
                                animate={{ rotate: [0, 8, -8, 0] }}
                                transition={{ duration: 4, repeat: Infinity, repeatDelay: 2, ease: 'easeInOut' }}
                            >
                                <Bot className="w-12 h-12 text-primary-400" />
                                <motion.div
                                    className="absolute -top-2 -right-2"
                                    animate={{ scale: [1, 1.3, 1] }}
                                    transition={{ duration: 2, repeat: Infinity }}
                                >
                                    <Sparkles className="w-5 h-5 text-amber-400" />
                                </motion.div>
                            </motion.div>

                            <h2 className="text-2xl font-black text-white mb-3 tracking-tight relative z-10">Coming Soon</h2>
                            <p className="text-dark-400 max-w-md mx-auto mb-8 leading-relaxed relative z-10">
                                We're building a library of pre-configured agent templates to help you get started faster with specialized AI workflows.
                            </p>

                            <motion.button
                                onClick={() => navigate('/agents')}
                                className="inline-flex items-center gap-2 px-6 py-3 bg-primary-500/10 hover:bg-primary-500/20 text-primary-400 border border-primary-500/20 rounded-xl transition-all text-sm font-bold relative z-10"
                                whileHover={{ scale: 1.03 }}
                                whileTap={{ scale: 0.97 }}
                            >
                                <Rocket className="w-4 h-4" />
                                Explore Agents
                            </motion.button>
                        </motion.div>
                    </motion.div>
                </main>
            </div>
        </div>
    );
}
