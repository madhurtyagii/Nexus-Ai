import { useState, useEffect, useMemo } from 'react';
import { filesAPI } from '../services/api';
import Navbar from '../components/layout/Navbar';
import Sidebar from '../components/layout/Sidebar';
import toast from 'react-hot-toast';

export default function Files() {
    const [files, setFiles] = useState([]);
    const [loading, setLoading] = useState(true);
    const [searchQuery, setSearchQuery] = useState('');
    const [typeFilter, setTypeFilter] = useState('all');
    const [sortOrder, setSortOrder] = useState('newest');
    const [deleting, setDeleting] = useState(null);
    const [previewFile, setPreviewFile] = useState(null);

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
                    <div className="mb-8">
                        <h1 className="text-3xl font-bold text-white mb-2">📁 Files</h1>
                        <p className="text-dark-400">Manage all your uploaded files across projects.</p>
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
                                    : 'Upload files from a project to see them here.'}
                            </p>
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
