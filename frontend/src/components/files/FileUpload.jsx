import React, { useState, useRef } from 'react';
import toast from 'react-hot-toast';
import { filesAPI } from '../../services/api';
import './FileUpload.css';

/**
 * FileUpload Component
 * 
 * A button and hidden input that handles file selection and 
 * asynchronous upload to the backend.
 * 
 * @component
 * @param {Object} props - Component props.
 * @param {number} [props.projectId] - Associate upload with a project.
 * @param {number} [props.taskId] - Associate upload with a task.
 * @param {Function} [props.onUploadSuccess] - Callback after successful upload.
 */
const FileUpload = ({ projectId, taskId, onUploadSuccess }) => {
    const [uploading, setUploading] = useState(false);
    const [progress, setProgress] = useState(0);
    const [error, setError] = useState(null);
    const fileInputRef = useRef(null);

    const handleFileChange = async (e) => {
        const file = e.target.files[0];
        if (!file) return;

        setUploading(true);
        setError(null);
        setProgress(0);

        const formData = new FormData();
        formData.append('file', file);

        const params = {};
        if (projectId) params.project_id = projectId;
        if (taskId) params.task_id = taskId;

        try {
            const response = await filesAPI.upload(formData, params);
            setUploading(false);
            toast.success('File uploaded successfully');
            if (onUploadSuccess) onUploadSuccess(response.data);
            if (fileInputRef.current) fileInputRef.current.value = '';
        } catch (err) {
            setUploading(false);
            setError(err.response?.data?.detail || 'Upload failed');
            toast.error('Upload failed');
            console.error('File upload error:', err);
        }
    };

    return (
        <div className="file-upload-container">
            <input
                type="file"
                onChange={handleFileChange}
                style={{ display: 'none' }}
                ref={fileInputRef}
            />
            <button
                className={`upload-button ${uploading ? 'uploading' : ''}`}
                onClick={() => fileInputRef.current?.click()}
                disabled={uploading}
            >
                {uploading ? (
                    <span>Uploading...</span>
                ) : (
                    <>
                        <span className="icon">📁</span>
                        <span>Upload File</span>
                    </>
                )}
            </button>
            {error && <p className="upload-error">{error}</p>}
        </div>
    );
};

export default FileUpload;
