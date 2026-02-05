import { useState, useEffect, useRef, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import {
    Search,
    Command,
    LayoutDashboard,
    ListTodo,
    FolderKanban,
    Users,
    Settings,
    FileText,
    HelpCircle,
    GitBranch,
    ArrowRight,
    Sparkles
} from 'lucide-react';

const pages = [
    { name: 'Dashboard', path: '/dashboard', icon: LayoutDashboard, description: 'Home overview' },
    { name: 'Tasks', path: '/tasks', icon: ListTodo, description: 'Manage AI tasks' },
    { name: 'Projects', path: '/projects', icon: FolderKanban, description: 'Multi-phase projects' },
    { name: 'Agents', path: '/agents', icon: Users, description: 'AI agent fleet' },
    { name: 'Workflow Builder', path: '/workflow-builder', icon: GitBranch, description: 'Visual automation' },
    { name: 'Files', path: '/files', icon: FileText, description: 'File management' },
    { name: 'Settings', path: '/settings', icon: Settings, description: 'Configuration' },
    { name: 'Help', path: '/help', icon: HelpCircle, description: 'Documentation' },
];

export default function CommandPalette() {
    const [isOpen, setIsOpen] = useState(false);
    const [query, setQuery] = useState('');
    const [selectedIndex, setSelectedIndex] = useState(0);
    const inputRef = useRef(null);
    const navigate = useNavigate();

    const filteredPages = pages.filter((page) =>
        page.name.toLowerCase().includes(query.toLowerCase()) ||
        page.description.toLowerCase().includes(query.toLowerCase())
    );

    const handleKeyDown = useCallback((e) => {
        // Open command palette
        if ((e.metaKey || e.ctrlKey) && e.key === 'k') {
            e.preventDefault();
            setIsOpen(true);
            setQuery('');
            setSelectedIndex(0);
        }

        // Close on escape
        if (e.key === 'Escape') {
            setIsOpen(false);
        }
    }, []);

    const handleNavigateKeyDown = (e) => {
        if (e.key === 'ArrowDown') {
            e.preventDefault();
            setSelectedIndex((prev) => Math.min(prev + 1, filteredPages.length - 1));
        } else if (e.key === 'ArrowUp') {
            e.preventDefault();
            setSelectedIndex((prev) => Math.max(prev - 1, 0));
        } else if (e.key === 'Enter' && filteredPages[selectedIndex]) {
            navigate(filteredPages[selectedIndex].path);
            setIsOpen(false);
        }
    };

    useEffect(() => {
        document.addEventListener('keydown', handleKeyDown);
        return () => document.removeEventListener('keydown', handleKeyDown);
    }, [handleKeyDown]);

    useEffect(() => {
        if (isOpen && inputRef.current) {
            inputRef.current.focus();
        }
    }, [isOpen]);

    useEffect(() => {
        setSelectedIndex(0);
    }, [query]);

    const handleSelect = (path) => {
        navigate(path);
        setIsOpen(false);
    };

    return (
        <AnimatePresence>
            {isOpen && (
                <motion.div
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    exit={{ opacity: 0 }}
                    className="fixed inset-0 bg-black/60 backdrop-blur-sm z-[100] flex items-start justify-center pt-[15vh]"
                    onClick={() => setIsOpen(false)}
                >
                    <motion.div
                        initial={{ opacity: 0, scale: 0.95, y: -20 }}
                        animate={{ opacity: 1, scale: 1, y: 0 }}
                        exit={{ opacity: 0, scale: 0.95, y: -20 }}
                        transition={{ type: "spring", stiffness: 400, damping: 30 }}
                        onClick={(e) => e.stopPropagation()}
                        className="w-full max-w-xl glass rounded-2xl border border-white/10 overflow-hidden shadow-2xl"
                    >
                        {/* Search Input */}
                        <div className="flex items-center gap-3 px-5 py-4 border-b border-white/5">
                            <Search className="w-5 h-5 text-dark-400" />
                            <input
                                ref={inputRef}
                                type="text"
                                value={query}
                                onChange={(e) => setQuery(e.target.value)}
                                onKeyDown={handleNavigateKeyDown}
                                placeholder="Search pages, commands..."
                                className="flex-1 bg-transparent border-none text-white text-lg placeholder-dark-500 focus:outline-none focus:ring-0"
                            />
                            <div className="flex items-center gap-1 px-2 py-1 rounded-lg bg-white/5 border border-white/10">
                                <Command className="w-3 h-3 text-dark-400" />
                                <span className="text-xs text-dark-400 font-medium">K</span>
                            </div>
                        </div>

                        {/* Results */}
                        <div className="max-h-80 overflow-y-auto p-2">
                            {filteredPages.length === 0 ? (
                                <div className="flex flex-col items-center justify-center py-12 text-dark-400">
                                    <Sparkles className="w-8 h-8 mb-3 opacity-50" />
                                    <p className="text-sm font-medium">No results found</p>
                                    <p className="text-xs text-dark-500 mt-1">Try a different search term</p>
                                </div>
                            ) : (
                                filteredPages.map((page, index) => (
                                    <motion.button
                                        key={page.path}
                                        onClick={() => handleSelect(page.path)}
                                        className={`w-full flex items-center gap-4 px-4 py-3 rounded-xl transition-all group ${index === selectedIndex
                                                ? 'bg-primary-500/10 text-white'
                                                : 'text-dark-300 hover:bg-white/5 hover:text-white'
                                            }`}
                                        whileHover={{ x: 4 }}
                                    >
                                        <div className={`p-2 rounded-lg transition-colors ${index === selectedIndex
                                                ? 'bg-primary-500/20 text-primary-400'
                                                : 'bg-white/5 text-dark-400 group-hover:text-white'
                                            }`}>
                                            <page.icon className="w-5 h-5" />
                                        </div>
                                        <div className="flex-1 text-left">
                                            <p className="font-bold text-sm">{page.name}</p>
                                            <p className="text-xs text-dark-500">{page.description}</p>
                                        </div>
                                        <ArrowRight className={`w-4 h-4 transition-opacity ${index === selectedIndex ? 'opacity-100' : 'opacity-0 group-hover:opacity-50'
                                            }`} />
                                    </motion.button>
                                ))
                            )}
                        </div>

                        {/* Footer */}
                        <div className="flex items-center justify-between px-5 py-3 border-t border-white/5 text-xs text-dark-500">
                            <div className="flex items-center gap-4">
                                <span className="flex items-center gap-1">
                                    <kbd className="px-1.5 py-0.5 rounded bg-white/5 border border-white/10">↑</kbd>
                                    <kbd className="px-1.5 py-0.5 rounded bg-white/5 border border-white/10">↓</kbd>
                                    <span className="ml-1">Navigate</span>
                                </span>
                                <span className="flex items-center gap-1">
                                    <kbd className="px-1.5 py-0.5 rounded bg-white/5 border border-white/10">↵</kbd>
                                    <span className="ml-1">Select</span>
                                </span>
                            </div>
                            <span className="flex items-center gap-1">
                                <kbd className="px-1.5 py-0.5 rounded bg-white/5 border border-white/10">Esc</kbd>
                                <span className="ml-1">Close</span>
                            </span>
                        </div>
                    </motion.div>
                </motion.div>
            )}
        </AnimatePresence>
    );
}
