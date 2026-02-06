import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import {
    Book,
    Rocket,
    Bot,
    Brain,
    Cpu,
    Files,
    Layout,
    Settings,
    Command,
    MousePointer2,
    Moon,
    Workflow,
    ChevronRight,
    Search,
    Lightbulb,
    Zap
} from 'lucide-react';
import Navbar from '../components/layout/Navbar';
import Sidebar from '../components/layout/Sidebar';
import './Help.css';

const HELP_CATEGORIES = [
    {
        id: 'getting-started',
        title: 'Quick Start',
        icon: Rocket,
        description: 'Master the basics of Nexus AI in minutes.',
        items: [
            {
                title: 'Intelligence v2.1 Overview',
                content: 'Nexus AI is an autonomous multi-agent workspace designed for high-performance orchestration. Scale your productivity by managing specialized AI agents.',
                icon: Zap
            },
            {
                title: 'Command Palette (Ctrl + K)',
                content: 'The fastest way to navigate. Use Ctrl+K to open the search bar and jump to any project, task, or setting instantly.',
                icon: Command
            },
            {
                title: 'Dashboard Insights',
                content: 'Monitor real-time system health, active agents, and quick-access metrics directly from your command center.',
                icon: Layout
            }
        ]
    },
    {
        id: 'agent-force',
        title: 'Agent Workforce',
        icon: Bot,
        description: 'Understand your specialized team of AI agents.',
        items: [
            {
                title: '7 Specialized Roles',
                content: 'From the Manager who orchestrates to the QA Analyst who verifies, each agent has unique capabilities and focus areas.',
                icon: Cpu
            },
            {
                title: 'Direct Agent Chat',
                content: 'Need to talk to a specific agent? Use the Agent page to start a 1-on-1 direct conversation with any team member.',
                icon: Bot
            },
            {
                title: 'Semantic Memory',
                content: 'Agents share a long-term memory system (RAG) that allows them to learn from past projects and your uploaded files.',
                icon: Brain
            }
        ]
    },
    {
        id: 'projects',
        title: 'Orchestration',
        icon: Workflow,
        description: 'How to manage complex project lifecycles.',
        items: [
            {
                title: 'AI Planning vs Templates',
                content: 'Use industry-standard templates for quick setup, or let the Manager agent brainstorm a custom multi-phase plan for you.',
                icon: Lightbulb
            },
            {
                title: 'Live Task Mirroring',
                content: 'Watch execution in real-time. Tasks marked with "Live" are actively being processed by the agent workforce.',
                icon: Zap
            },
            {
                title: 'Workflow Builder',
                content: 'The visual drag-and-drop tool for orchestrating agent connections and data flows between tasks.',
                icon: Workflow
            }
        ]
    },
    {
        id: 'memory-rag',
        title: 'Memory & RAG',
        icon: Files,
        description: 'Leverage your data with semantic intelligence.',
        items: [
            {
                title: 'Ask Your Files',
                content: 'Upload any PDF, CSV, or document and use semantic search to extract insights across your entire knowledge base.',
                icon: Search
            },
            {
                title: 'Automatic Indexing',
                content: 'When you upload files to a project, Nexus AI automatically vectorizes them for RAG-powered agent awareness.',
                icon: Files
            }
        ]
    },
    {
        id: 'customization',
        title: 'Customization',
        icon: Settings,
        description: 'Tailor the workspace to your neural preference.',
        items: [
            {
                title: 'Global Themes',
                content: 'Switch between Deep Space (Dark) and Pure Light themes with beautiful radial transitions.',
                icon: Moon
            },
            {
                title: 'Cursor Glow Effects',
                content: 'Choose from 6 premium cursor trails (Ring, Particles, Aurora, etc.) in the Appearance settings.',
                icon: MousePointer2
            }
        ]
    }
];

export default function Help() {
    const navigate = useNavigate();
    const [activeCat, setActiveCat] = useState('getting-started');
    const [searchQuery, setSearchQuery] = useState('');

    const activeCategory = HELP_CATEGORIES.find(c => c.id === activeCat);

    return (
        <div className="min-h-screen bg-dark-900">
            <Navbar />
            <div className="flex">
                <Sidebar />
                <main className="flex-1 p-6 lg:p-8">
                    <div className="max-w-6xl mx-auto">
                        {/* Header Section */}
                        <section className="mb-12">
                            <div className="flex flex-col md:flex-row md:items-end justify-between gap-6">
                                <div>
                                    <h1 className="text-4xl font-black text-white mb-3 tracking-tight italic uppercase">
                                        Nexus <span className="text-primary-500">Manual</span>
                                    </h1>
                                    <p className="text-dark-400 font-medium max-w-xl">
                                        Master the autonomous multi-agent workspace and unlock the full potential of Intelligence v2.1.
                                    </p>
                                </div>
                                <div className="relative group min-w-[300px]">
                                    <Search className="absolute left-4 top-1/2 -translate-y-1/2 w-4 h-4 text-dark-500 group-hover:text-primary-500 transition-colors" />
                                    <input
                                        type="text"
                                        placeholder="Search documentation..."
                                        value={searchQuery}
                                        onChange={(e) => setSearchQuery(e.target.value)}
                                        className="w-full bg-white/[0.03] border border-white/5 rounded-2xl py-4 pl-12 pr-4 text-white font-bold outline-none focus:border-primary-500/50 focus:bg-primary-500/5 transition-all"
                                    />
                                </div>
                            </div>
                        </section>

                        <div className="flex flex-col lg:flex-row gap-8">
                            {/* Category Sidebar */}
                            <aside className="lg:w-72 flex flex-col gap-2">
                                {HELP_CATEGORIES.map((cat) => {
                                    const Icon = cat.icon;
                                    const isActive = activeCat === cat.id;
                                    return (
                                        <button
                                            key={cat.id}
                                            onClick={() => setActiveCat(cat.id)}
                                            className={`flex items-center gap-4 p-4 rounded-2xl border transition-all text-left ${isActive
                                                    ? 'bg-primary-500/10 border-primary-500/50 text-white shadow-[0_10px_30px_rgba(14,165,233,0.15)]'
                                                    : 'bg-white/[0.02] border-white/5 text-dark-400 hover:border-white/20 hover:bg-white/[0.04]'
                                                }`}
                                        >
                                            <div className={`w-10 h-10 rounded-xl flex items-center justify-center ${isActive ? 'bg-primary-500 text-white' : 'bg-white/5 text-dark-400'}`}>
                                                <Icon className="w-5 h-5" />
                                            </div>
                                            <div className="flex-1">
                                                <p className="font-black text-sm uppercase tracking-tighter italic">{cat.title}</p>
                                            </div>
                                            {isActive && <ChevronRight className="w-4 h-4 text-primary-500" />}
                                        </button>
                                    );
                                })}
                            </aside>

                            {/* Content Display */}
                            <div className="flex-1">
                                <AnimatePresence mode="wait">
                                    <motion.div
                                        key={activeCat}
                                        initial={{ opacity: 0, x: 20 }}
                                        animate={{ opacity: 1, x: 0 }}
                                        exit={{ opacity: 0, x: -20 }}
                                        className="glass p-8 rounded-[2rem] border border-white/5 min-h-[500px]"
                                    >
                                        <div className="mb-10">
                                            <div className="flex items-center gap-4 mb-4">
                                                <div className="w-14 h-14 rounded-2xl bg-gradient-to-br from-primary-500 to-purple-600 flex items-center justify-center text-white shadow-2xl">
                                                    {activeCategory && <activeCategory.icon className="w-7 h-7" />}
                                                </div>
                                                <div>
                                                    <h2 className="text-2xl font-black text-white tracking-tighter italic uppercase">{activeCategory?.title}</h2>
                                                    <p className="text-dark-400 font-medium">{activeCategory?.description}</p>
                                                </div>
                                            </div>
                                            <div className="h-px w-full bg-gradient-to-r from-white/10 to-transparent" />
                                        </div>

                                        <div className="space-y-8">
                                            {activeCategory?.items.map((item, idx) => (
                                                <motion.div
                                                    key={idx}
                                                    initial={{ opacity: 0, y: 10 }}
                                                    animate={{ opacity: 1, y: 0 }}
                                                    transition={{ delay: idx * 0.1 }}
                                                    className="group"
                                                >
                                                    <div className="flex gap-6">
                                                        <div className="pt-1">
                                                            <div className="w-10 h-10 rounded-xl bg-white/[0.03] border border-white/5 flex items-center justify-center text-primary-400 group-hover:bg-primary-500 group-hover:text-white transition-all duration-300">
                                                                <item.icon className="w-5 h-5" />
                                                            </div>
                                                        </div>
                                                        <div>
                                                            <h3 className="text-lg font-black text-white mb-2 italic tracking-tight">{item.title}</h3>
                                                            <p className="text-dark-400 leading-relaxed font-medium">
                                                                {item.content}
                                                            </p>
                                                        </div>
                                                    </div>
                                                </motion.div>
                                            ))}
                                        </div>

                                        {/* Pro Tip Section */}
                                        <div className="mt-12 p-6 rounded-2xl bg-gradient-to-br from-primary-500/10 to-transparent border border-primary-500/20 relative overflow-hidden group">
                                            <div className="absolute top-0 right-0 p-4 opacity-10 group-hover:scale-110 transition-transform duration-500">
                                                <Lightbulb className="w-20 h-20 text-primary-500" />
                                            </div>
                                            <div className="relative z-10 flex gap-4">
                                                <div className="w-8 h-8 rounded-lg bg-primary-500 flex items-center justify-center text-white shrink-0">
                                                    <Lightbulb className="w-4 h-4" />
                                                </div>
                                                <div>
                                                    <p className="text-[10px] font-black text-primary-400 uppercase tracking-[0.2em] mb-1">Neural Secret</p>
                                                    <p className="text-white font-bold leading-snug">
                                                        Press <span className="bg-white/10 px-2 py-0.5 rounded-md text-primary-400">Ctrl + K</span> from anywhere to instantly search through your projects without leaving your current view.
                                                    </p>
                                                </div>
                                            </div>
                                        </div>
                                    </motion.div>
                                </AnimatePresence>
                            </div>
                        </div>

                        <div className="mt-12 flex justify-center">
                            <button
                                onClick={() => navigate('/dashboard')}
                                className="group flex items-center gap-3 px-8 py-4 rounded-2xl bg-white/[0.03] border border-white/5 text-white font-black uppercase tracking-widest text-xs hover:bg-white/[0.08] hover:border-white/20 transition-all italic"
                            >
                                Finish Resonance Study
                                <ChevronRight className="w-4 h-4 group-hover:translate-x-1 transition-transform" />
                            </button>
                        </div>
                    </div>
                </main>
            </div>
        </div>
    );
}
