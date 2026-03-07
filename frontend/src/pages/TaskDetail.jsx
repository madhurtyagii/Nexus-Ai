import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import {
    ArrowLeft,
    CheckCircle2,
    Loader2,
    AlertCircle,
    Clock,
    Trash2,
    RotateCcw,
    Upload,
    FolderOpen
} from 'lucide-react';
import api from '../services/api';
import Navbar from '../components/layout/Navbar';
import Sidebar from '../components/layout/Sidebar';
import MarkdownRenderer from '../components/common/MarkdownRenderer';
import ExpandableOutput from '../components/common/ExpandableOutput';
import ImageLightbox from '../components/common/ImageLightbox';
import { AgentActivityPanelPolling } from '../components/agents/AgentActivityPanel';
import FileUpload from '../components/files/FileUpload';
import FloatingRefinementBar from '../components/common/FloatingRefinementBar';


function TaskDetail() {
    const { taskId } = useParams();
    const navigate = useNavigate();
    const [task, setTask] = useState(null);
    const [progress, setProgress] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [lightboxImage, setLightboxImage] = useState(null);
    const [isPolling, setIsPolling] = useState(false);
    const [fileRefreshTrigger, setFileRefreshTrigger] = useState(0);

    const fetchTask = async () => {
        try {
            const response = await api.get(`/tasks/${taskId}`);
            setTask(response.data);
            setError(null);
        } catch (err) {
            setError('Failed to load task');
            console.error(err);
        } finally {
            setLoading(false);
        }
    };

    const fetchProgress = async () => {
        try {
            const response = await api.get(`/tasks/${taskId}/status`);
            setProgress(response.data);
            if (response.data.status === 'completed' || response.data.status === 'failed') {
                setIsPolling(false);
                fetchTask();
            }
        } catch (err) {
            console.error('Progress fetch error:', err);
        }
    };

    useEffect(() => {
        fetchTask();
        fetchProgress();
    }, [taskId]);

    useEffect(() => {
        let interval;
        if (task?.status === 'in_progress' || task?.status === 'queued') {
            setIsPolling(true);
            interval = setInterval(fetchProgress, 3000);
        }
        return () => { if (interval) clearInterval(interval); };
    }, [task?.status]);

    const [followupInput, setFollowupInput] = useState('');
    const [isSendingFollowup, setIsSendingFollowup] = useState(false);

    const handleFollowup = async () => {
        if (!followupInput.trim() || isSendingFollowup) return;
        setIsSendingFollowup(true);
        try {
            await api.post(`/tasks/${taskId}/followup`, {
                followup_prompt: followupInput
            });
            setFollowupInput('');
            // Switch back to polling to see new subtasks
            setIsPolling(true);
            fetchTask();
            fetchProgress();
        } catch (err) {
            console.error('Follow-up failed:', err);
            alert('Failed to send follow-up instructions.');
        } finally {
            setIsSendingFollowup(false);
        }
    };

    const handleRetry = async () => {
        try {
            await api.post(`/tasks/${taskId}/retry`);
            fetchTask();
            fetchProgress();
        } catch (err) {
            console.error('Retry failed:', err);
        }
    };

    const handleDelete = async () => {
        if (window.confirm('Are you sure you want to delete this task?')) {
            try {
                await api.delete(`/tasks/${taskId}`);
                navigate('/dashboard');
            } catch (err) {
                console.error('Delete failed:', err);
            }
        }
    };

    const getStatusConfig = (status) => {
        switch (status?.toLowerCase()) {
            case 'completed': return { color: 'text-emerald-400', bg: 'bg-emerald-400/10', border: 'border-emerald-400/20', icon: CheckCircle2, label: 'Completed' };
            case 'in_progress': return { color: 'text-blue-400', bg: 'bg-blue-400/10', border: 'border-blue-400/20', icon: Loader2, label: 'In Progress' };
            case 'queued': return { color: 'text-amber-400', bg: 'bg-amber-400/10', border: 'border-amber-400/20', icon: Clock, label: 'Queued' };
            case 'failed': return { color: 'text-red-400', bg: 'bg-red-400/10', border: 'border-red-400/20', icon: AlertCircle, label: 'Failed' };
            default: return { color: 'text-dark-400', bg: 'bg-dark-400/10', border: 'border-dark-400/20', icon: Clock, label: status || 'Unknown' };
        }
    };

    const formatDate = (dateString) => {
        if (!dateString) return '';
        let adjustedString = dateString;
        if (typeof dateString === 'string' && !dateString.includes('Z') && !dateString.includes('+')) {
            adjustedString = dateString + 'Z';
        }
        const date = new Date(adjustedString);
        if (isNaN(date.getTime())) return dateString;
        return date.toLocaleString(undefined, { month: 'short', day: 'numeric', year: 'numeric', hour: '2-digit', minute: '2-digit' });
    };

    const renderOutput = (output) => {
        if (!output) return null;

        const formatDictAsMarkdown = (obj) => {
            if (obj.summary && obj.key_findings) {
                const summaryText = typeof obj.summary === 'object'
                    ? (obj.summary.summary || obj.summary.text || JSON.stringify(obj.summary))
                    : obj.summary;
                const findings = Array.isArray(obj.key_findings)
                    ? obj.key_findings.map(f => `- ${f}`).join('\n')
                    : String(obj.key_findings);
                return `### Summary\n${summaryText}\n\n### Key Findings\n${findings}`;
            }
            return Object.entries(obj)
                .filter(([key]) => !['status', 'agent_name', 'timestamp', 'execution_time_seconds', 'tokens_used', 'confidence_score', 'query', 'researched_at'].includes(key))
                .map(([key, value]) => {
                    const cleanKey = key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
                    if (Array.isArray(value)) return `**${cleanKey}:**\n${value.map(v => `- ${v}`).join('\n')}`;
                    if (typeof value === 'object') return `**${cleanKey}:** ${value?.summary || value?.text || '(complex data)'}`;
                    return `**${cleanKey}:** ${value}`;
                })
                .join('\n\n');
        };

        if (typeof output === 'string') {
            const jsonMatch = output.match(/\{\s*"(summary|key_findings|content|code|body)":/);
            if (jsonMatch) {
                try {
                    const jsonStart = output.indexOf('{');
                    const prefix = jsonStart > 0 ? output.substring(0, jsonStart).trim() : '';
                    const jsonStr = output.substring(jsonStart);
                    const parsed = JSON.parse(jsonStr);
                    const formatted = formatDictAsMarkdown(parsed);
                    const finalContent = prefix ? `${prefix}\n\n${formatted}` : formatted;
                    return <MarkdownRenderer content={finalContent} onImageClick={setLightboxImage} />;
                } catch (e) {
                    return <MarkdownRenderer content={output} onImageClick={setLightboxImage} />;
                }
            }
            return <MarkdownRenderer content={output} />;
        }

        if (typeof output === 'object') {
            try {
                const markdown = formatDictAsMarkdown(output);
                return <MarkdownRenderer content={markdown} onImageClick={setLightboxImage} />;
            } catch (e) {
                return <pre className="text-dark-200 whitespace-pre-wrap">{JSON.stringify(output, null, 2)}</pre>;
            }
        }

        return <pre className="text-dark-200 whitespace-pre-wrap">{JSON.stringify(output, null, 2)}</pre>;
    };

    if (loading) {
        return (
            <div className="min-h-screen selection:bg-primary-500/30">
                <Navbar />
                <div className="flex items-center justify-center h-96">
                    <motion.div
                        className="w-10 h-10 border-2 border-primary-500 border-t-transparent rounded-full"
                        animate={{ rotate: 360 }}
                        transition={{ duration: 1, repeat: Infinity, ease: 'linear' }}
                    />
                </div>
            </div>
        );
    }

    if (error) {
        return (
            <div className="min-h-screen selection:bg-primary-500/30">
                <Navbar />
                <div className="max-w-4xl mx-auto px-6 py-8">
                    <div className="card p-8 text-center border-red-500/20">
                        <AlertCircle className="w-10 h-10 text-red-400 mx-auto mb-3" />
                        <p className="text-red-400 font-medium mb-4">{error}</p>
                        <motion.button
                            onClick={() => navigate('/dashboard')}
                            className="btn-primary text-sm"
                            whileHover={{ scale: 1.03 }}
                            whileTap={{ scale: 0.97 }}
                        >
                            Back to Dashboard
                        </motion.button>
                    </div>
                </div>
            </div>
        );
    }

    const statusConf = getStatusConfig(task?.status);
    const StatusIcon = statusConf.icon;

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
                        transition={{ duration: 0.4 }}
                    >
                        {/* Back */}
                        <motion.button
                            onClick={() => navigate(-1)}
                            className="flex items-center gap-2 text-dark-400 hover:text-white mb-6 transition-colors text-sm font-medium group"
                            whileHover={{ x: -4 }}
                        >
                            <ArrowLeft className="w-4 h-4 group-hover:text-primary-400 transition-colors" />
                            Back
                        </motion.button>

                        {/* Header Card */}
                        <div className="card p-6 mb-6">
                            <div className="flex items-start justify-between gap-4 mb-4">
                                <h1 className="text-xl font-bold text-white leading-relaxed flex-1">
                                    {task?.user_prompt}
                                </h1>
                                <span className={`flex-shrink-0 inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-bold ${statusConf.bg} ${statusConf.color} border ${statusConf.border}`}>
                                    <StatusIcon className={`w-3.5 h-3.5 ${task?.status === 'in_progress' ? 'animate-spin' : ''}`} />
                                    {statusConf.label}
                                </span>
                            </div>

                            <div className="flex items-center gap-4 text-xs text-dark-500 font-medium">
                                <span>Created: {formatDate(task?.created_at)}</span>
                                {task?.completed_at && (
                                    <span>Completed: {formatDate(task?.completed_at)}</span>
                                )}
                            </div>

                            {/* Progress bar */}
                            {progress && (task?.status === 'in_progress' || task?.status === 'queued') && (
                                <div className="mt-5">
                                    <div className="flex items-center justify-between mb-2">
                                        <span className="text-xs text-dark-400 font-medium">
                                            {progress.current_agent ? `${progress.current_agent} working...` : 'Processing...'}
                                        </span>
                                        <span className="text-xs text-primary-400 font-bold tabular-nums">
                                            {progress.progress_percentage}%
                                        </span>
                                    </div>
                                    <div className="h-1.5 bg-dark-800 rounded-full overflow-hidden">
                                        <motion.div
                                            className="h-full bg-gradient-to-r from-primary-500 to-purple-500 rounded-full"
                                            initial={{ width: 0 }}
                                            animate={{ width: `${progress.progress_percentage}%` }}
                                            transition={{ duration: 0.6, ease: 'easeOut' }}
                                            style={{ boxShadow: '0 0 8px rgba(14, 165, 233, 0.3)' }}
                                        />
                                    </div>
                                    {isPolling && (
                                        <p className="text-[10px] text-dark-600 mt-1.5">Auto-refreshing every 3 seconds...</p>
                                    )}
                                </div>
                            )}
                        </div>

                        {/* Subtasks */}
                        {task?.subtasks && task.subtasks.length > 0 && (
                            <div className="card p-6 mb-6">
                                <h2 className="text-base font-bold text-white mb-4 tracking-tight">Subtasks</h2>
                                <div className="space-y-2">
                                    {task.subtasks.map((subtask) => {
                                        const st = getStatusConfig(subtask.status);
                                        const StIcon = st.icon;
                                        return (
                                            <div
                                                key={subtask.id}
                                                className="flex items-center justify-between p-3 rounded-xl bg-white/[0.02] border border-white/[0.04] hover:bg-white/[0.04] transition-colors"
                                            >
                                                <div className="flex items-center gap-3">
                                                    <StIcon className={`w-4 h-4 ${st.color} ${subtask.status === 'in_progress' ? 'animate-spin' : ''}`} />
                                                    <span className="text-dark-200 text-sm font-medium">{subtask.assigned_agent}</span>
                                                </div>
                                                <span className={`text-[10px] uppercase font-bold tracking-wider px-2 py-0.5 rounded-md ${st.bg} ${st.color} border ${st.border}`}>
                                                    {subtask.status?.replace('_', ' ')}
                                                </span>
                                            </div>
                                        );
                                    })}
                                </div>
                            </div>
                        )}

                        {/* Agent Activity Panel */}
                        {task?.subtasks && task.subtasks.length > 0 && (
                            <div className="mb-6">
                                <AgentActivityPanelPolling
                                    subtasks={task.subtasks}
                                    status={task.status}
                                />
                            </div>
                        )}

                        {/* File Management */}
                        <div className="card p-6 mb-6">
                            <div className="flex items-center justify-between mb-4">
                                <h2 className="text-base font-bold text-white tracking-tight flex items-center gap-2">
                                    <FolderOpen className="w-4 h-4 text-primary-400" />
                                    Files
                                </h2>
                                <FileUpload
                                    taskId={taskId}
                                    onUploadSuccess={() => setFileRefreshTrigger(prev => prev + 1)}
                                />
                            </div>
                            <div className="card p-6 text-center bg-dark-800/20 border border-white/5 rounded-2xl mt-4">
                                <p className="text-dark-400 mb-4 text-sm">Files for this task are available in the central Files area.</p>
                                <button
                                    onClick={() => navigate('/files')}
                                    className="px-6 py-2 bg-primary-500/10 hover:bg-primary-500/20 text-primary-400 border border-primary-500/20 rounded-xl transition-all text-sm font-bold"
                                >
                                    Go to Files
                                </button>
                            </div>
                        </div>

                        {/* Output */}
                        {task?.output && (
                            <div className="card p-6 mb-6">
                                <h2 className="text-base font-bold text-white mb-4 tracking-tight">Output</h2>
                                <div className="rounded-xl bg-white/[0.02] border border-white/[0.04] p-4 mb-4">
                                    <ExpandableOutput
                                        content={typeof task.output === 'object' ? JSON.stringify(task.output, null, 2) : task.output}
                                        title="Task Output"
                                        collapsedHeight={300}
                                    />
                                </div>

                                {/* Inline Follow-up Bar - Centered and Smaller */}
                                <div className="mt-6 max-w-xl mx-auto border-t border-white/[0.04] pt-6 pb-2">
                                    <p className="text-xs text-dark-500 font-medium mb-3 text-center">Continue the conversation</p>
                                    <div className="flex items-center gap-2 p-2 rounded-xl bg-white/[0.03] border border-white/[0.06] hover:border-primary-500/20 focus-within:border-primary-500/40 transition-all shadow-inner">
                                        <input
                                            type="text"
                                            value={followupInput}
                                            onChange={(e) => setFollowupInput(e.target.value)}
                                            onKeyDown={(e) => e.key === 'Enter' && handleFollowup()}
                                            placeholder="Ask a follow-up... (e.g., 'Summarize results')"
                                            className="flex-1 bg-transparent text-sm text-dark-200 placeholder-dark-600 outline-none px-3 py-1.5"
                                        />
                                        <motion.button
                                            onClick={handleFollowup}
                                            disabled={!followupInput.trim() || isSendingFollowup}
                                            className="flex-shrink-0 px-4 py-2 bg-primary-500/10 hover:bg-primary-500/20 text-primary-400 border border-primary-500/20 rounded-lg text-xs font-bold transition-all disabled:opacity-40"
                                            whileHover={followupInput.trim() ? { scale: 1.03 } : {}}
                                            whileTap={followupInput.trim() ? { scale: 0.97 } : {}}
                                        >
                                            {isSendingFollowup ? (
                                                <Loader2 className="w-3.5 h-3.5 animate-spin" />
                                            ) : (
                                                'Send'
                                            )}
                                        </motion.button>
                                    </div>
                                </div>
                            </div>
                        )}


                        {/* Actions */}
                        <div className="flex gap-3 mb-10">
                            {task?.status === 'failed' && (
                                <motion.button
                                    onClick={handleRetry}
                                    className="flex items-center gap-2 px-5 py-2.5 bg-primary-500/10 hover:bg-primary-500/20 text-primary-400 border border-primary-500/20 rounded-xl transition-all text-sm font-bold"
                                    whileHover={{ scale: 1.03 }}
                                    whileTap={{ scale: 0.97 }}
                                >
                                    <RotateCcw className="w-4 h-4" />
                                    Retry Task
                                </motion.button>
                            )}
                            <motion.button
                                onClick={handleDelete}
                                className="flex items-center gap-2 px-5 py-2.5 bg-red-500/5 hover:bg-red-500/15 text-red-400/70 hover:text-red-400 border border-red-500/10 hover:border-red-500/20 rounded-xl transition-all text-sm font-bold"
                                whileHover={{ scale: 1.03 }}
                                whileTap={{ scale: 0.97 }}
                            >
                                <Trash2 className="w-4 h-4" />
                                Delete Task
                            </motion.button>
                        </div>


                    </motion.div>
                </main>
            </div>



            <ImageLightbox
                isOpen={!!lightboxImage}
                imageUrl={lightboxImage}
                onClose={() => setLightboxImage(null)}
            />
        </div>
    );
}

export default TaskDetail;
