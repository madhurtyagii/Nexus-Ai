import { useState, useEffect, useMemo, useRef } from 'react';
import { filesAPI } from '../services/api';
import Navbar from '../components/layout/Navbar';
import Sidebar from '../components/layout/Sidebar';
import MarkdownRenderer from '../components/common/MarkdownRenderer';
import toast from 'react-hot-toast';
import { Upload, Plus, FileUp, Loader2, Sparkles, MessageSquare, Bot, Search, Info } from 'lucide-react';
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
        <div className="min-h-screen bg-dark-900">
            <Navbar />
            <div className="flex">
                <Sidebar />
                <main className="flex-1 p-6 lg:p-8">
                    {/* Header */}
                    <div className="flex flex-col md:flex-row md:items-center justify-between gap-6 mb-8">
                        <div>
                            <h1 className="text-3xl font-black text-white tracking-tight italic uppercase">
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

                    {/* Storage Bar */}
                    <div className="card mb-6">
                        <div className="flex items-center justify-between mb-2">
                            <span className="text-white font-medium">Storage Used</span>
                            <span className="text-dark-400">{formatBytes(totalStorage)} / 100 MB</span>
                        </div>
                        <div className="h-3 bg-dark-700 rounded-full overflow-hidden">
                            <div
                                className="h-full bg-gradient-to-r from-primary-500 to-purple-500 rounded-full transition-all"
                                style={{ width: `${Math.min((totalStorage / (100 * 1024 * 1024)) * 100, 100)}%` }}
                            ></div>
                        </div>
                    </div>

                    {/* Filters */}
                    <div className="card mb-6">
                        <div className="flex flex-col md:flex-row gap-4">
                            <div className="flex-1">
                                <input
                                    type="text"
                                    value={searchQuery}
                                    onChange={(e) => setSearchQuery(e.target.value)}
                                    placeholder="Search files..."
                                    className="w-full input-field"
                                />
                            </div>
                            <select
                                value={typeFilter}
                                onChange={(e) => setTypeFilter(e.target.value)}
                                className="input-field md:w-40"
                            >
                                {typeOptions.map(opt => (
                                    <option key={opt.value} value={opt.value}>{opt.label}</option>
                                ))}
                            </select>
                            <select
                                value={sortOrder}
                                onChange={(e) => setSortOrder(e.target.value)}
                                className="input-field md:w-40"
                            >
                                <option value="newest">Newest First</option>
                                <option value="oldest">Oldest First</option>
                                <option value="largest">Largest First</option>
                                <option value="smallest">Smallest First</option>
                                <option value="name">By Name</option>
                            </select>
                        </div>
                    </div>

                    {/* Nexus Intelligence - RAG Chat */}
                    <div className="card mb-6 overflow-hidden border-primary-500/20 shadow-[0_0_50px_rgba(14,165,233,0.1)]">
                        <div className="bg-gradient-to-r from-primary-500/10 via-purple-500/10 to-transparent p-6">
                            <div className="flex items-center justify-between mb-4">
                                <div className="flex items-center gap-3">
                                    <div className="w-10 h-10 bg-primary-500 rounded-xl flex items-center justify-center shadow-lg shadow-primary-500/30">
                                        <Bot className="w-6 h-6 text-white" />
                                    </div>
                                    <div>
                                        <h3 className="text-xl font-bold text-white flex items-center gap-2">
                                            Nexus Intelligence
                                            <span className="bg-primary-500/20 text-primary-400 text-[10px] px-2 py-0.5 rounded-full uppercase tracking-widest font-black">RAG v2.0</span>
                                        </h3>
                                        <p className="text-dark-400 text-sm">Ask anything about your indexed files.</p>
                                    </div>
                                </div>
                                <div className="hidden md:flex items-center gap-2 text-xs text-dark-500">
                                    <Sparkles className="w-3 h-3 text-yellow-500" />
                                    <span>Powered by Context Synthesis</span>
                                </div>
                            </div>

                            <div className="relative group">
                                <Search className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-dark-500 group-focus-within:text-primary-400 transition-colors" />
                                <input
                                    type="text"
                                    value={ragQuery}
                                    onChange={(e) => setRagQuery(e.target.value)}
                                    onKeyDown={(e) => e.key === 'Enter' && handleRagSearch()}
                                    placeholder="Type your question (e.g., 'Summarize the roadmap PDF'...)"
                                    className="w-full bg-dark-900/50 border border-dark-700 focus:border-primary-500 pl-12 pr-32 py-4 rounded-2xl text-white font-medium transition-all"
                                />
                                <button
                                    onClick={handleRagSearch}
                                    disabled={ragLoading || !ragQuery.trim()}
                                    className="absolute right-2 top-1/2 -translate-y-1/2 px-6 py-2 bg-primary-500 hover:bg-primary-400 text-white rounded-xl font-bold transition-all shadow-lg shadow-primary-500/20 disabled:opacity-50"
                                >
                                    {ragLoading ? (
                                        <Loader2 className="w-5 h-5 animate-spin mx-auto" />
                                    ) : (
                                        'Ask Nexus'
                                    )}
                                </button>
                            </div>

                            <AnimatePresence mode="wait">
                                {ragLoading && (
                                    <motion.div
                                        initial={{ opacity: 0, y: 10 }}
                                        animate={{ opacity: 1, y: 0 }}
                                        exit={{ opacity: 0, y: -10 }}
                                        className="mt-6 flex items-start gap-4"
                                    >
                                        <div className="w-8 h-8 rounded-lg bg-dark-800 flex items-center justify-center">
                                            <Bot className="w-4 h-4 text-primary-500 animate-pulse" />
                                        </div>
                                        <div className="flex-1 space-y-2">
                                            <div className="h-4 bg-dark-800 rounded w-1/4 animate-pulse"></div>
                                            <div className="h-4 bg-dark-800 rounded w-3/4 animate-pulse"></div>
                                        </div>
                                    </motion.div>
                                )}

                                {ragChatAnswer && !ragLoading && (
                                    <motion.div
                                        initial={{ opacity: 0, y: 20 }}
                                        animate={{ opacity: 1, y: 0 }}
                                        className="mt-6 space-y-4"
                                    >
                                        <div className="flex items-start gap-4">
                                            <div className="w-10 h-10 rounded-xl bg-primary-500/10 border border-primary-500/20 flex items-center justify-center flex-shrink-0">
                                                <Bot className="w-6 h-6 text-primary-500" />
                                            </div>
                                            <div className="flex-1">
                                                <div className="prose prose-invert max-w-none">
                                                    <MarkdownRenderer content={ragChatAnswer} />
                                                </div>
                                            </div>
                                        </div>

                                        {ragSources.length > 0 && (
                                            <div className="flex flex-wrap gap-2 ml-14">
                                                {ragSources.map((source) => (
                                                    <div
                                                        key={source.id}
                                                        className="flex items-center gap-1.5 bg-dark-800/80 border border-dark-700 px-3 py-1 rounded-full text-[10px] text-dark-400 font-bold uppercase tracking-wider"
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
                        <div className="text-center py-12">
                            <div className="animate-spin w-8 h-8 border-2 border-primary-500 border-t-transparent rounded-full mx-auto mb-4"></div>
                            <p className="text-dark-400">Loading files...</p>
                        </div>
                    ) : filteredAndSortedFiles.length === 0 ? (
                        <div className="card text-center py-12">
                            <div className="w-16 h-16 bg-dark-700 rounded-full flex items-center justify-center mx-auto mb-4">
                                <span className="text-3xl">📁</span>
                            </div>
                            <h3 className="text-xl font-semibold text-white mb-2">No Files Found</h3>
                            <p className="text-dark-400">
                                {searchQuery || typeFilter !== 'all'
                                    ? 'Try adjusting your filters.'
                                    : 'Upload files to see them here.'}
                            </p>
                            {!searchQuery && typeFilter === 'all' && (
                                <button
                                    onClick={() => fileInputRef.current?.click()}
                                    className="mt-6 flex items-center gap-2 bg-white/5 hover:bg-white/10 text-white font-bold px-6 py-3 rounded-xl border border-white/10 transition-all mx-auto"
                                >
                                    <Upload className="w-5 h-5" />
                                    <span>Upload First File</span>
                                </button>
                            )}
                        </div>
                    ) : (
                        <div className="space-y-3">
                            {filteredAndSortedFiles.map((file) => (
                                <div
                                    key={file.id}
                                    className="card hover:border-primary-500/50 transition-all cursor-pointer group"
                                    onClick={() => setPreviewFile(file)}
                                >
                                    <div className="flex items-center gap-4">
                                        {/* Icon */}
                                        <div className="w-12 h-12 bg-dark-700 rounded-lg flex items-center justify-center text-2xl flex-shrink-0">
                                            {getFileIcon(file.filename)}
                                        </div>

                                        {/* Info */}
                                        <div className="flex-1 min-w-0">
                                            <h3 className="text-white font-medium truncate group-hover:text-primary-400 transition-colors">
                                                {file.filename}
                                            </h3>
                                            <div className="flex items-center gap-3 text-sm text-dark-400">
                                                <span>{formatBytes(file.size)}</span>
                                                <span>•</span>
                                                <span>{new Date(file.created_at).toLocaleDateString()}</span>
                                                {file.project_name && (
                                                    <>
                                                        <span>•</span>
                                                        <span className="truncate">{file.project_name}</span>
                                                    </>
                                                )}
                                            </div>
                                        </div>

                                        {/* Actions */}
                                        <div className="flex items-center gap-2 flex-shrink-0">
                                            <button
                                                onClick={(e) => handleIndex(file.id, e)}
                                                disabled={indexing === file.id || indexedFiles.has(file.id)}
                                                className={`px-3 py-1.5 text-sm rounded-lg transition-colors ${indexedFiles.has(file.id)
                                                    ? 'bg-green-500/10 text-green-400 cursor-default'
                                                    : 'bg-purple-500/10 hover:bg-purple-500/20 text-purple-400'
                                                    } disabled:opacity-50`}
                                            >
                                                {indexing === file.id ? '...' : indexedFiles.has(file.id) ? '✓ Indexed' : '📥 Index'}
                                            </button>
                                            <button
                                                onClick={(e) => handleDownload(file, e)}
                                                className="px-3 py-1.5 text-sm bg-dark-700 hover:bg-dark-600 text-white rounded-lg transition-colors"
                                            >
                                                Download
                                            </button>
                                            <button
                                                onClick={(e) => handleDelete(file.id, e)}
                                                disabled={deleting === file.id}
                                                className="px-3 py-1.5 text-sm bg-red-500/10 hover:bg-red-500/20 text-red-400 rounded-lg transition-colors disabled:opacity-50"
                                            >
                                                {deleting === file.id ? '...' : 'Delete'}
                                            </button>
                                        </div>
                                    </div>
                                </div>
                            ))}
                        </div>
                    )}

                    {/* Stats */}
                    <div className="mt-8 grid grid-cols-2 md:grid-cols-4 gap-4">
                        <div className="card text-center py-4">
                            <div className="text-2xl font-bold text-white">{files.length}</div>
                            <p className="text-dark-400 text-sm">Total Files</p>
                        </div>
                        <div className="card text-center py-4">
                            <div className="text-2xl font-bold text-blue-400">
                                {files.filter(f => getFileType(f.filename) === 'document').length}
                            </div>
                            <p className="text-dark-400 text-sm">Documents</p>
                        </div>
                        <div className="card text-center py-4">
                            <div className="text-2xl font-bold text-green-400">
                                {files.filter(f => getFileType(f.filename) === 'image').length}
                            </div>
                            <p className="text-dark-400 text-sm">Images</p>
                        </div>
                        <div className="card text-center py-4">
                            <div className="text-2xl font-bold text-purple-400">
                                {files.filter(f => getFileType(f.filename) === 'data').length}
                            </div>
                            <p className="text-dark-400 text-sm">Data Files</p>
                        </div>
                    </div>
                </main>
            </div>

            {/* File Preview Modal */}
            {previewFile && (
                <div className="fixed inset-0 bg-black/70 backdrop-blur-sm flex items-center justify-center z-50 p-4">
                    <div className="bg-dark-800 rounded-2xl border border-dark-700 w-full max-w-lg">
                        <div className="p-6 border-b border-dark-700 flex items-center justify-between">
                            <h2 className="text-xl font-semibold text-white">File Details</h2>
                            <button
                                onClick={() => setPreviewFile(null)}
                                className="text-dark-400 hover:text-white text-2xl"
                            >
                                ×
                            </button>
                        </div>
                        <div className="p-6">
                            <div className="flex items-center gap-4 mb-6">
                                <div className="w-16 h-16 bg-dark-700 rounded-lg flex items-center justify-center text-3xl">
                                    {getFileIcon(previewFile.filename)}
                                </div>
                                <div>
                                    <h3 className="text-lg font-medium text-white">{previewFile.filename}</h3>
                                    <p className="text-dark-400">{formatBytes(previewFile.size)}</p>
                                </div>
                            </div>
                            <div className="space-y-3 text-sm">
                                <div className="flex justify-between">
                                    <span className="text-dark-400">Type</span>
                                    <span className="text-white capitalize">{getFileType(previewFile.filename)}</span>
                                </div>
                                <div className="flex justify-between">
                                    <span className="text-dark-400">Uploaded</span>
                                    <span className="text-white">{new Date(previewFile.created_at).toLocaleString()}</span>
                                </div>
                                {previewFile.project_name && (
                                    <div className="flex justify-between">
                                        <span className="text-dark-400">Project</span>
                                        <span className="text-white">{previewFile.project_name}</span>
                                    </div>
                                )}
                            </div>
                        </div>
                        <div className="p-6 border-t border-dark-700 flex justify-end gap-3">
                            <button
                                onClick={(e) => {
                                    handleDownload(previewFile, e);
                                    setPreviewFile(null);
                                }}
                                className="btn-primary"
                            >
                                Download
                            </button>
                            <button
                                onClick={() => setPreviewFile(null)}
                                className="px-4 py-2 bg-dark-700 hover:bg-dark-600 text-white rounded-lg transition-colors"
                            >
                                Close
                            </button>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
}
