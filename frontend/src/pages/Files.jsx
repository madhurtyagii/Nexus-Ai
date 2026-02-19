import { useState, useEffect, useMemo, useRef } from 'react';
import { filesAPI } from '../services/api';
import Navbar from '../components/layout/Navbar';
import Sidebar from '../components/layout/Sidebar';
import MarkdownRenderer from '../components/common/MarkdownRenderer';
import toast from 'react-hot-toast';
import { Upload, Plus, FileUp, Loader2, Sparkles, MessageSquare, Bot, Search, Info, Database } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

export default function Files() {
    const [files, setFiles] = useState([]);
    const [loading, setLoading] = useState(true);
    const [searchQuery, setSearchQuery] = useState('');
    const [typeFilter, setTypeFilter] = useState('all');
    const [sortOrder, setSortOrder] = useState('newest');
    const [deleting, setDeleting] = useState(null);
    const [previewFile, setPreviewFile] = useState(null);
    // RAG state
    const [ragQuery, setRagQuery] = useState('');
    const [ragChatAnswer, setRagChatAnswer] = useState('');
    const [ragSources, setRagSources] = useState([]);
    const [ragLoading, setRagLoading] = useState(false);
    const [indexing, setIndexing] = useState(null);
    const [indexedFiles, setIndexedFiles] = useState(new Set());
    const [uploading, setUploading] = useState(false);
    const fileInputRef = useRef(null);

    useEffect(() => {
        loadFiles();
    }, []);

    const loadFiles = async () => {
        try {
            const response = await filesAPI.list({ limit: 100 });
            setFiles(response.data);
        } catch (error) {
            console.error('Failed to load files:', error);
        } finally {
            setLoading(false);
        }
    };

    const handleUpload = async (e) => {
        const file = e.target.files?.[0];
        if (!file) return;

        // Simple validation
        const maxSize = 100 * 1024 * 1024; // 100MB client limit (backend has its own)
        if (file.size > maxSize) {
            toast.error('File exceeds size limit.');
            return;
        }

        const formData = new FormData();
        formData.append('file', file);

        setUploading(true);
        const toastId = toast.loading(`Uploading ${file.name}...`);

        try {
            await filesAPI.upload(formData);
            toast.success('File uploaded successfully!', { id: toastId });
            loadFiles(); // Refresh list
        } catch (error) {
            console.error('Upload failed:', error);
            const detail = error.response?.data?.detail;
            toast.error(detail || 'Failed to upload file.', { id: toastId });
        } finally {
            setUploading(false);
            if (fileInputRef.current) fileInputRef.current.value = '';
        }
    };

    const handleDownload = async (file, e) => {
        e.stopPropagation();
        try {
            const response = await filesAPI.download(file.id);
            const url = window.URL.createObjectURL(new Blob([response.data]));
            const link = document.createElement('a');
            link.href = url;
            link.setAttribute('download', file.filename);
            document.body.appendChild(link);
            link.click();
            link.remove();
            window.URL.revokeObjectURL(url);
            toast.success('Download started');
        } catch (error) {
            toast.error('Failed to download file');
        }
    };

    const handleDelete = async (fileId, e) => {
        e.stopPropagation();
        if (!confirm('Are you sure you want to delete this file?')) return;

        setDeleting(fileId);
        try {
            await filesAPI.delete(fileId);
            toast.success('File deleted');
            setFiles(files.filter(f => f.id !== fileId));
        } catch (error) {
            toast.error('Failed to delete file');
        } finally {
            setDeleting(null);
        }
    };

    const handleIndex = async (fileId, e) => {
        e.stopPropagation();
        setIndexing(fileId);
        try {
            const response = await filesAPI.index(fileId);
            if (response.data.status === 'indexed') {
                toast.success(`Indexed! ${response.data.chunks_indexed} chunks`);
                setIndexedFiles(prev => new Set([...prev, fileId]));
            } else {
                toast.error(response.data.message || 'Could not index file');
            }
        } catch (error) {
            toast.error('Failed to index file');
        } finally {
            setIndexing(null);
        }
    };

    const handleRagSearch = async () => {
        if (!ragQuery.trim()) return;
        setRagLoading(true);
        setRagChatAnswer('');
        setRagSources([]);

        try {
            const response = await filesAPI.chat({ query: ragQuery });
            setRagChatAnswer(response.data.answer);
            setRagSources(response.data.sources || []);

            if (!response.data.answer || response.data.answer.includes("haven't indexed any files")) {
                toast('No context found. Try indexing more files.', { icon: '🔍' });
            }
        } catch (error) {
            console.error('RAG Chat failed:', error);
            toast.error('Nexus Intelligence is currently unavailable.');
        } finally {
            setRagLoading(false);
        }
    };

    const getFileIcon = (filename) => {
        const ext = filename?.split('.').pop()?.toLowerCase();
        const icons = {
            pdf: '📄',
            doc: '📝', docx: '📝',
            txt: '📃',
            csv: '📊', xlsx: '📊', xls: '📊',
            png: '🖼️', jpg: '🖼️', jpeg: '🖼️', gif: '🖼️', webp: '🖼️',
            mp4: '🎬', mov: '🎬', avi: '🎬',
            mp3: '🎵', wav: '🎵',
            zip: '📦', rar: '📦',
            json: '📋', xml: '📋',
            py: '🐍', js: '💛', ts: '💙', html: '🌐', css: '🎨'
        };
        return icons[ext] || '📁';
    };

    const getFileType = (filename) => {
        const ext = filename?.split('.').pop()?.toLowerCase();
        const types = {
            pdf: 'document', doc: 'document', docx: 'document', txt: 'document',
            csv: 'data', xlsx: 'data', xls: 'data', json: 'data',
            png: 'image', jpg: 'image', jpeg: 'image', gif: 'image', webp: 'image',
            mp4: 'video', mov: 'video', avi: 'video',
            mp3: 'audio', wav: 'audio',
            zip: 'archive', rar: 'archive',
            py: 'code', js: 'code', ts: 'code', html: 'code', css: 'code'
        };
        return types[ext] || 'other';
    };

    const formatBytes = (bytes) => {
        if (!bytes || bytes === 0) return '0 B';
        const k = 1024;
        const sizes = ['B', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i];
    };

    const filteredAndSortedFiles = useMemo(() => {
        let result = [...files];

        // Filter by type
        if (typeFilter !== 'all') {
            result = result.filter(f => getFileType(f.filename) === typeFilter);
        }

        // Filter by search
        if (searchQuery.trim()) {
            const query = searchQuery.toLowerCase();
            result = result.filter(f =>
                f.filename?.toLowerCase().includes(query)
            );
        }

        // Sort
        result.sort((a, b) => {
            if (sortOrder === 'newest') {
                return new Date(b.created_at) - new Date(a.created_at);
            } else if (sortOrder === 'oldest') {
                return new Date(a.created_at) - new Date(b.created_at);
            } else if (sortOrder === 'largest') {
                return (b.size || 0) - (a.size || 0);
            } else if (sortOrder === 'smallest') {
                return (a.size || 0) - (b.size || 0);
            } else if (sortOrder === 'name') {
                return (a.filename || '').localeCompare(b.filename || '');
            }
            return 0;
        });

        return result;
    }, [files, typeFilter, searchQuery, sortOrder]);

    const totalStorage = useMemo(() => {
        return files.reduce((acc, f) => acc + (f.size || 0), 0);
    }, [files]);

    const typeOptions = [
        { value: 'all', label: 'All Types' },
        { value: 'document', label: 'Documents' },
        { value: 'image', label: 'Images' },
        { value: 'data', label: 'Data Files' },
        { value: 'code', label: 'Code' },
        { value: 'video', label: 'Videos' },
        { value: 'other', label: 'Other' }
    ];

    return (
        <div className="min-h-screen bg-bg-primary">
            <Navbar />
            <div className="flex">
                <Sidebar />
                <main className="flex-1 p-6 lg:p-8">
                    {/* Header */}
                    <div className="flex flex-col md:flex-row md:items-center justify-between gap-6 mb-8">
                        <div>
                            <h1 className="text-3xl font-black text-text-primary tracking-tight italic uppercase">
                                📁 Files
                            </h1>
                            <p className="text-dark-400 font-medium">Manage all your uploaded files across projects.</p>
                        </div>

                        <div className="flex items-center gap-3">
                            <input
                                type="file"
                                ref={fileInputRef}
                                onChange={handleUpload}
                                className="hidden"
                            />
                            <button
                                onClick={() => fileInputRef.current?.click()}
                                disabled={uploading}
                                className="flex items-center gap-2 bg-primary-500 hover:bg-primary-400 text-white font-bold px-6 py-3 rounded-xl transition-all shadow-[0_10px_30px_rgba(14,165,233,0.3)] disabled:opacity-50"
                            >
                                {uploading ? (
                                    <Loader2 className="w-5 h-5 animate-spin" />
                                ) : (
                                    <Upload className="w-5 h-5" />
                                )}
                                <span>{uploading ? 'Uploading...' : 'Upload File'}</span>
                            </button>
                        </div>
                    </div>

                    {/* Storage Indicator */}
                    <div className="card p-5 mb-8 flex flex-col md:flex-row md:items-center justify-between gap-4">
                        <div className="flex items-center gap-3">
                            <div className="p-2.5 bg-primary-500/10 rounded-xl border border-primary-500/10">
                                <Database className="w-5 h-5 text-primary-500" />
                            </div>
                            <div>
                                <h3 className="text-sm font-black text-text-primary uppercase tracking-wider mb-0.5">Cloud Storage</h3>
                                <p className="text-dark-500 text-[11px] font-bold uppercase tracking-widest">{formatBytes(totalStorage)} Used of 100 MB</p>
                            </div>
                        </div>

                        <div className="flex-1 max-w-md w-full">
                            <div className="h-3 bg-dark-900/5 dark:bg-white/[0.04] rounded-full overflow-hidden border border-border/50 relative">
                                <motion.div
                                    initial={{ width: 0 }}
                                    animate={{ width: `${Math.min((totalStorage / (100 * 1024 * 1024)) * 100, 100)}%` }}
                                    transition={{ duration: 1, ease: 'easeOut' }}
                                    className="h-full bg-gradient-to-r from-primary-500 via-primary-400 to-purple-500 rounded-full relative"
                                    style={{ boxShadow: '0 0 15px rgba(14, 165, 233, 0.4)' }}
                                >
                                    <div className="absolute inset-0 bg-white/10" />
                                </motion.div>
                            </div>
                        </div>

                        <div className="hidden md:block">
                            <span className="text-xl font-black text-text-primary tabular-nums">
                                {Math.round((totalStorage / (100 * 1024 * 1024)) * 100)}%
                            </span>
                        </div>
                    </div>

                    {/* Filters */}
                    <div className="card p-5 mb-8">
                        <div className="flex flex-col gap-4">
                            {/* Search */}
                            <div className="relative">
                                <Search className="absolute left-4 top-1/2 -translate-y-1/2 w-4.5 h-4.5 text-dark-500" />
                                <input
                                    type="text"
                                    value={searchQuery}
                                    onChange={(e) => setSearchQuery(e.target.value)}
                                    placeholder="Search files..."
                                    className="w-full pl-12 pr-4 py-3.5 bg-bg-tertiary border border-border rounded-xl text-text-primary placeholder-dark-500 focus:outline-none focus:border-primary-500/50 transition-colors text-sm font-medium"
                                />
                            </div>

                            {/* Type + Sort */}
                            <div className="flex flex-wrap items-center gap-2">
                                {typeOptions.map(opt => (
                                    <button
                                        key={opt.value}
                                        onClick={() => setTypeFilter(opt.value)}
                                        className={`px-4 py-2 rounded-xl text-xs font-bold transition-all ${typeFilter === opt.value
                                            ? 'bg-primary-500 text-white shadow-[0_4px_12px_rgba(14,165,233,0.3)]'
                                            : 'bg-white/[0.03] text-dark-400 hover:text-white border border-white/5'
                                            }`}
                                    >
                                        {opt.label}
                                    </button>
                                ))}

                                <div className="w-px h-6 bg-white/10 mx-2 hidden md:block" />

                                {[
                                    { value: 'newest', label: 'Newest' },
                                    { value: 'oldest', label: 'Oldest' },
                                    { value: 'largest', label: 'Largest' },
                                    { value: 'smallest', label: 'Smallest' },
                                    { value: 'name', label: 'A-Z' },
                                ].map(opt => (
                                    <button
                                        key={opt.value}
                                        onClick={() => setSortOrder(opt.value)}
                                        className={`px-4 py-2 rounded-xl text-xs font-bold transition-all ${sortOrder === opt.value
                                            ? 'bg-purple-500/15 text-purple-400 border border-purple-500/20'
                                            : 'bg-white/[0.03] text-dark-500 hover:text-dark-300 border border-white/5'
                                            }`}
                                    >
                                        {opt.label}
                                    </button>
                                ))}
                            </div>
                        </div>
                    </div>

                    {/* Nexus Intelligence - RAG Chat */}
                    <div className="card mb-8 overflow-hidden relative" style={{ background: 'linear-gradient(135deg, var(--mesh-1), var(--mesh-2), var(--bg-card))' }}>
                        {/* Subtle glow */}
                        <div className="absolute top-0 left-0 w-72 h-72 bg-primary-500/10 rounded-full blur-3xl pointer-events-none" />
                        <div className="absolute bottom-0 right-0 w-48 h-48 bg-purple-500/8 rounded-full blur-3xl pointer-events-none" />

                        <div className="relative p-8">
                            <div className="flex items-center justify-between mb-6">
                                <div className="flex items-center gap-4">
                                    <div className="w-12 h-12 bg-gradient-to-br from-primary-500 to-primary-600 rounded-2xl flex items-center justify-center shadow-lg shadow-primary-500/25">
                                        <Bot className="w-6 h-6 text-white" />
                                    </div>
                                    <div>
                                        <h3 className="text-lg font-black text-text-primary flex items-center gap-2.5">
                                            Nexus Intelligence
                                            <span className="bg-primary-500/15 text-primary-400 text-[10px] px-2.5 py-0.5 rounded-full uppercase tracking-widest font-black border border-primary-500/20">RAG v2.0</span>
                                        </h3>
                                        <p className="text-dark-400 text-sm font-medium mt-0.5">Ask anything about your indexed files.</p>
                                    </div>
                                </div>
                                <div className="hidden md:flex items-center gap-2 text-xs text-dark-500">
                                    <Sparkles className="w-3.5 h-3.5 text-amber-400" />
                                    <span className="font-medium">Powered by Context Synthesis</span>
                                </div>
                            </div>

                            <div className="relative">
                                <div className="flex items-center gap-3 bg-bg-tertiary rounded-2xl px-5 py-1 border border-border focus-within:border-primary-500/30 transition-colors">
                                    <Search className="w-5 h-5 text-dark-500 flex-shrink-0" />
                                    <input
                                        type="text"
                                        value={ragQuery}
                                        onChange={(e) => setRagQuery(e.target.value)}
                                        onKeyDown={(e) => e.key === 'Enter' && handleRagSearch()}
                                        placeholder="Type your question (e.g., 'Summarize the roadmap PDF'...)"
                                        className="flex-1 bg-transparent py-3.5 text-text-primary font-medium placeholder-dark-500 focus:outline-none text-sm"
                                    />
                                    <button
                                        onClick={handleRagSearch}
                                        disabled={ragLoading || !ragQuery.trim()}
                                        className="px-5 py-2 bg-primary-500 hover:bg-primary-400 text-white rounded-xl font-bold transition-all shadow-lg shadow-primary-500/20 disabled:opacity-40 text-sm flex-shrink-0"
                                    >
                                        {ragLoading ? (
                                            <Loader2 className="w-4 h-4 animate-spin" />
                                        ) : (
                                            'Ask Nexus'
                                        )}
                                    </button>
                                </div>
                            </div>

                            <AnimatePresence mode="wait">
                                {ragLoading && (
                                    <motion.div
                                        initial={{ opacity: 0, y: 10 }}
                                        animate={{ opacity: 1, y: 0 }}
                                        exit={{ opacity: 0, y: -10 }}
                                        className="mt-6 flex items-start gap-4"
                                    >
                                        <div className="w-10 h-10 rounded-xl bg-white/[0.04] flex items-center justify-center">
                                            <Bot className="w-5 h-5 text-primary-500 animate-pulse" />
                                        </div>
                                        <div className="flex-1 space-y-3 py-1">
                                            <div className="h-4 bg-white/[0.04] rounded-lg w-1/4 animate-pulse"></div>
                                            <div className="h-4 bg-white/[0.04] rounded-lg w-3/4 animate-pulse"></div>
                                        </div>
                                    </motion.div>
                                )}

                                {ragChatAnswer && !ragLoading && (
                                    <motion.div
                                        initial={{ opacity: 0, y: 20 }}
                                        animate={{ opacity: 1, y: 0 }}
                                        className="mt-8 space-y-4"
                                    >
                                        <div className="flex items-start gap-4">
                                            <div className="w-10 h-10 rounded-xl bg-primary-500/10 border border-primary-500/20 flex items-center justify-center flex-shrink-0">
                                                <Bot className="w-5 h-5 text-primary-500" />
                                            </div>
                                            <div className="flex-1">
                                                <div className="prose prose-invert max-w-none text-sm">
                                                    <MarkdownRenderer content={ragChatAnswer} />
                                                </div>
                                            </div>
                                        </div>

                                        {ragSources.length > 0 && (
                                            <div className="flex flex-wrap gap-2 ml-14">
                                                {ragSources.map((source) => (
                                                    <div
                                                        key={source.id}
                                                        className="flex items-center gap-1.5 bg-white/[0.04] border border-white/[0.06] px-3 py-1.5 rounded-full text-[10px] text-dark-400 font-bold uppercase tracking-wider"
                                                    >
                                                        <Info className="w-3 h-3 text-primary-500" />
                                                        {source.name}
                                                    </div>
                                                ))}
                                            </div>
                                        )}
                                    </motion.div>
                                )}
                            </AnimatePresence>
                        </div>
                    </div>

                    {/* File List */}
                    {loading ? (
                        <div className="text-center py-16">
                            <div className="animate-spin w-10 h-10 border-2 border-primary-500 border-t-transparent rounded-full mx-auto mb-4"></div>
                            <p className="text-dark-400 font-medium">Loading files...</p>
                        </div>
                    ) : filteredAndSortedFiles.length === 0 ? (
                        <div className="card p-16 text-center">
                            <div className="w-20 h-20 bg-white/[0.03] border border-white/[0.06] rounded-3xl flex items-center justify-center mx-auto mb-6">
                                <span className="text-4xl">📁</span>
                            </div>
                            <h3 className="text-xl font-bold text-text-primary mb-2">No Files Found</h3>
                            <p className="text-dark-400 font-medium">
                                {searchQuery || typeFilter !== 'all'
                                    ? 'Try adjusting your filters.'
                                    : 'Upload files to see them here.'}
                            </p>
                            {!searchQuery && typeFilter === 'all' && (
                                <button
                                    onClick={() => fileInputRef.current?.click()}
                                    className="mt-8 flex items-center gap-2 bg-white/5 hover:bg-white/10 text-white font-bold px-8 py-3.5 rounded-xl border border-white/10 transition-all mx-auto"
                                >
                                    <Upload className="w-5 h-5" />
                                    <span>Upload First File</span>
                                </button>
                            )}
                        </div>
                    ) : (
                        <div className="space-y-3">
                            {filteredAndSortedFiles.map((file) => (
                                <motion.div
                                    key={file.id}
                                    initial={{ opacity: 0, y: 8 }}
                                    animate={{ opacity: 1, y: 0 }}
                                    className="card p-5 hover:border-primary-500/30 transition-all cursor-pointer group"
                                    onClick={() => setPreviewFile(file)}
                                    whileHover={{ y: -2, scale: 1.005 }}
                                >
                                    <div className="flex items-center gap-5">
                                        {/* Icon */}
                                        <div className="w-14 h-14 bg-white/[0.04] border border-white/[0.06] rounded-2xl flex items-center justify-center text-2xl flex-shrink-0">
                                            {getFileIcon(file.filename)}
                                        </div>

                                        {/* Info */}
                                        <div className="flex-1 min-w-0">
                                            <h3 className="text-text-primary font-bold text-[15px] truncate group-hover:text-primary-400 transition-colors mb-1">
                                                {file.filename}
                                            </h3>
                                            <div className="flex items-center gap-3 text-sm text-dark-500 font-medium">
                                                <span>{formatBytes(file.size)}</span>
                                                <span className="text-dark-700">•</span>
                                                <span>{new Date(file.created_at).toLocaleDateString()}</span>
                                                {file.project_name && (
                                                    <>
                                                        <span className="text-dark-700">•</span>
                                                        <span className="truncate text-dark-400">{file.project_name}</span>
                                                    </>
                                                )}
                                            </div>
                                        </div>

                                        {/* Actions */}
                                        <div className="flex items-center gap-2.5 flex-shrink-0">
                                            <button
                                                onClick={(e) => handleIndex(file.id, e)}
                                                disabled={indexing === file.id || indexedFiles.has(file.id)}
                                                className={`px-4 py-2 text-sm font-bold rounded-xl transition-all ${indexedFiles.has(file.id)
                                                    ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 cursor-default'
                                                    : 'bg-purple-500/10 hover:bg-purple-500/20 text-purple-400 border border-purple-500/20'
                                                    } disabled:opacity-50`}
                                            >
                                                {indexing === file.id ? '...' : indexedFiles.has(file.id) ? '✓ Indexed' : '📥 Index'}
                                            </button>
                                            <button
                                                onClick={(e) => handleDownload(file, e)}
                                                className="px-4 py-2 text-sm font-bold bg-white/[0.04] hover:bg-white/[0.08] text-white rounded-xl border border-white/[0.06] transition-all"
                                            >
                                                Download
                                            </button>
                                            <button
                                                onClick={(e) => handleDelete(file.id, e)}
                                                disabled={deleting === file.id}
                                                className="px-4 py-2 text-sm font-bold bg-red-500/5 hover:bg-red-500/15 text-red-400/70 hover:text-red-400 rounded-xl border border-red-500/10 hover:border-red-500/20 transition-all disabled:opacity-50"
                                            >
                                                {deleting === file.id ? '...' : 'Delete'}
                                            </button>
                                        </div>
                                    </div>
                                </motion.div>
                            ))}
                        </div>
                    )}

                    {/* Stats */}
                    <div className="mt-10 grid grid-cols-2 md:grid-cols-4 gap-4">
                        <div className="card p-6 text-center">
                            <div className="text-3xl font-black text-white tabular-nums">{files.length}</div>
                            <p className="text-dark-500 text-xs font-bold uppercase tracking-wider mt-1">Total Files</p>
                        </div>
                        <div className="card p-6 text-center">
                            <div className="text-3xl font-black text-blue-400 tabular-nums">
                                {files.filter(f => getFileType(f.filename) === 'document').length}
                            </div>
                            <p className="text-dark-500 text-xs font-bold uppercase tracking-wider mt-1">Documents</p>
                        </div>
                        <div className="card p-6 text-center">
                            <div className="text-3xl font-black text-green-400 tabular-nums">
                                {files.filter(f => getFileType(f.filename) === 'image').length}
                            </div>
                            <p className="text-dark-500 text-xs font-bold uppercase tracking-wider mt-1">Images</p>
                        </div>
                        <div className="card p-6 text-center">
                            <div className="text-3xl font-black text-purple-400 tabular-nums">
                                {files.filter(f => getFileType(f.filename) === 'data').length}
                            </div>
                            <p className="text-dark-500 text-xs font-bold uppercase tracking-wider mt-1">Data Files</p>
                        </div>
                    </div>
                </main>
            </div>

            {/* File Preview Modal */}
            <AnimatePresence>
                {previewFile && (
                    <motion.div
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        exit={{ opacity: 0 }}
                        className="fixed inset-0 bg-black/60 backdrop-blur-sm flex items-center justify-center z-50 p-4"
                        onClick={() => setPreviewFile(null)}
                    >
                        <motion.div
                            initial={{ opacity: 0, scale: 0.9, y: 20 }}
                            animate={{ opacity: 1, scale: 1, y: 0 }}
                            exit={{ opacity: 0, scale: 0.9, y: 20 }}
                            transition={{ type: 'spring', stiffness: 300, damping: 25 }}
                            onClick={(e) => e.stopPropagation()}
                            className="glass rounded-3xl border border-white/10 w-full max-w-lg overflow-hidden"
                        >
                            <div className="p-6 border-b border-white/5 flex items-center justify-between">
                                <h2 className="text-lg font-bold text-white tracking-tight">File Details</h2>
                                <button
                                    onClick={() => setPreviewFile(null)}
                                    className="p-1.5 rounded-lg text-dark-400 hover:text-white hover:bg-white/5 transition-colors"
                                >
                                    ✕
                                </button>
                            </div>
                            <div className="p-6">
                                <div className="flex items-center gap-4 mb-6">
                                    <div className="w-14 h-14 bg-white/[0.03] border border-white/[0.06] rounded-2xl flex items-center justify-center text-3xl">
                                        {getFileIcon(previewFile.filename)}
                                    </div>
                                    <div>
                                        <h3 className="text-base font-bold text-white">{previewFile.filename}</h3>
                                        <p className="text-dark-400 text-sm">{formatBytes(previewFile.size)}</p>
                                    </div>
                                </div>
                                <div className="space-y-3 text-sm">
                                    <div className="flex justify-between p-3 rounded-xl bg-white/[0.02] border border-white/[0.04]">
                                        <span className="text-dark-400 font-medium">Type</span>
                                        <span className="text-white capitalize font-bold">{getFileType(previewFile.filename)}</span>
                                    </div>
                                    <div className="flex justify-between p-3 rounded-xl bg-white/[0.02] border border-white/[0.04]">
                                        <span className="text-dark-400 font-medium">Uploaded</span>
                                        <span className="text-white font-bold">{new Date(previewFile.created_at).toLocaleString()}</span>
                                    </div>
                                    {previewFile.project_name && (
                                        <div className="flex justify-between p-3 rounded-xl bg-white/[0.02] border border-white/[0.04]">
                                            <span className="text-dark-400 font-medium">Project</span>
                                            <span className="text-white font-bold">{previewFile.project_name}</span>
                                        </div>
                                    )}
                                </div>
                            </div>
                            <div className="p-6 border-t border-white/5 flex justify-end gap-3">
                                <motion.button
                                    onClick={(e) => {
                                        handleDownload(previewFile, e);
                                        setPreviewFile(null);
                                    }}
                                    className="btn-primary text-sm"
                                    whileHover={{ scale: 1.03 }}
                                    whileTap={{ scale: 0.97 }}
                                >
                                    Download
                                </motion.button>
                                <button
                                    onClick={() => setPreviewFile(null)}
                                    className="px-4 py-2 bg-white/[0.03] hover:bg-white/[0.06] text-dark-300 rounded-xl border border-white/5 transition-colors text-sm font-bold"
                                >
                                    Close
                                </button>
                            </div>
                        </motion.div>
                    </motion.div>
                )}
            </AnimatePresence>
        </div>
    );
}
