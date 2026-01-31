import React, { useState, useEffect, useCallback } from 'react';
import toast from 'react-hot-toast';
import { filesAPI } from '../../services/api';
import './FileManager.css';

const formatSize = (bytes) => {
    if (!bytes) return '0 B';
    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB', 'TB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
};

/**
 * FileManager Component
 * 
 * Handles listing, downloading, and deleting files associated with 
 * a project or task.
 * 
 * @component
 * @param {Object} props - Component props.
 * @param {number} [props.projectId] - Filter files by project ID.
 * @param {number} [props.taskId] - Filter files by task ID.
 * @param {any} [props.refreshTrigger] - Trigger to re-fetch files.
 */
const FileManager = ({ projectId, taskId, refreshTrigger }) => {
    const [files, setFiles] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    const fetchFiles = useCallback(async () => {
        setLoading(true);
        try {
            const params = {};
            if (projectId) params.project_id = projectId;
            if (taskId) params.task_id = taskId;

            const response = await filesAPI.list(params);
            setFiles(response.data);
            setError(null);
        } catch (err) {
            setError('Failed to load files');
            console.error('Fetch files error:', err);
        } finally {
            setLoading(false);
        }
    }, [projectId, taskId]);

    useEffect(() => {
        fetchFiles();
    }, [fetchFiles, refreshTrigger]);

    const handleDownload = async (fileId, filename) => {
        try {
            const response = await filesAPI.download(fileId);
            const url = window.URL.createObjectURL(new Blob([response.data]));
            const link = document.createElement('a');
            link.href = url;
            link.setAttribute('download', filename);
            document.body.appendChild(link);
            link.click();
            link.remove();
            window.URL.revokeObjectURL(url);
            toast.success('Download started');
        } catch (err) {
            console.error('Download error:', err);
            toast.error('Failed to download file');
        }
    };

    const handleDelete = async (fileId) => {
        if (!window.confirm('Are you sure you want to delete this file?')) return;

        try {
            await filesAPI.delete(fileId);
            setFiles(files.filter(f => f.id !== fileId));
            toast.success('File deleted');
        } catch (err) {
            console.error('Delete error:', err);
            toast.error('Failed to delete file');
        }
    };

    const getFileIcon = (filename) => {
        if (!filename) return '📄';
        const ext = filename.split('.').pop().toLowerCase();
        switch (ext) {
            case 'pdf': return '📕';
            case 'csv':
            case 'xlsx': return '📗';
            case 'json': return '📙';
            case 'txt': return '📄';
            case 'png':
            case 'jpg':
            case 'jpeg': return '🖼️';
            default: return '📄';
        }
    };

    if (loading && files.length === 0) return (
        <div className="file-manager-loading">
            <div className="spinner-mini"></div>
            <span>Loading files...</span>
        </div>
    );

    return (
        <div className="file-manager-container">
            {files.length === 0 ? (
                <div className="no-files-card">
                    <p>No files uploaded yet.</p>
                </div>
            ) : (
                <div className="file-grid">
                    {files.map(file => (
                        <div key={file.id} className="file-card">
                            <div className="file-icon">{getFileIcon(file.original_filename)}</div>
                            <div className="file-main">
                                <span className="file-name" title={file.original_filename}>
                                    {file.original_filename}
                                </span>
                                <div className="file-metadata">
                                    <span>{formatSize(file.file_size)}</span>
                                    <span className="dot"></span>
                                    <span>{new Date(file.uploaded_at).toLocaleDateString()}</span>
                                </div>
                            </div>
                            <div className="file-item-actions">
                                <button
                                    className="action-btn-circle download"
                                    onClick={() => handleDownload(file.id, file.original_filename)}
                                    title="Download"
                                >
                                    📥
                                </button>
                                <button
                                    className="action-btn-circle delete"
                                    onClick={() => handleDelete(file.id)}
                                    title="Delete"
                                >
                                    🗑️
                                </button>
                            </div>
                        </div>
                    ))}
                </div>
            )}
            {error && <p className="file-manager-error">{error}</p>}
        </div>
    );
};

export default FileManager;
