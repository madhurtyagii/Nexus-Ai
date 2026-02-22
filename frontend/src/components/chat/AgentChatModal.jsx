/**
 * Nexus AI - Agent Chat Modal
 * Direct chat interface for communicating with specific agents
 * Features: Expand/Collapse, Image Download, Markdown rendering
 */

import { useState, useRef, useEffect, useCallback } from 'react';
import { useAuth } from '../../context/AuthContext';
import { useWebSocket, EventType } from '../../hooks/useWebSocket';
import api, { agentsAPI } from '../../services/api';
import MarkdownRenderer from '../common/MarkdownRenderer';
import StylePresets from './StylePresets';
import ImageLightbox from '../common/ImageLightbox';

export default function AgentChatModal({ isOpen, onClose, agent }) {
    const { token } = useAuth();
    const [messages, setMessages] = useState([]);
    const [input, setInput] = useState('');
    const [selectedStyle, setSelectedStyle] = useState(null);
    const [lightboxImage, setLightboxImage] = useState(null);
    const [isLoading, setIsLoading] = useState(false);
    const [isExpanded, setIsExpanded] = useState(false);
    const [currentRequestId, setCurrentRequestId] = useState(null);
    const [abortController, setAbortController] = useState(null);
    const [attachedFile, setAttachedFile] = useState(null);
    const [isUploading, setIsUploading] = useState(false);
    const [history, setHistory] = useState([]);
    const [showHistory, setShowHistory] = useState(false);
    const [currentConversationId, setCurrentConversationId] = useState(null);
    const [editingConversationId, setEditingConversationId] = useState(null);
    const [editTitleValue, setEditTitleValue] = useState('');
    const messagesEndRef = useRef(null);
    const inputRef = useRef(null);
    const fileInputRef = useRef(null);

    // WebSocket for receiving agent responses
    const handleWebSocketMessage = useCallback((message) => {
        if (message.event_type === EventType.AGENT_MESSAGE && message.data?.agent_name === agent?.name) {
            setMessages(prev => [...prev, {
                role: 'agent',
                content: message.data.message || message.data.response,
                timestamp: new Date().toISOString()
            }]);
            setIsLoading(false);
        }
    }, [agent?.name]);

    const { sendMessage } = useWebSocket(token, {
        onMessage: handleWebSocketMessage,
        autoConnect: isOpen && !!token
    });

    // Auto-scroll to bottom
    useEffect(() => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    }, [messages]);

    // Fetch history for this agent
    const fetchHistory = useCallback(async () => {
        if (!agent?.name) return;
        try {
            const response = await agentsAPI.getAgentConversations(agent.name);
            setHistory(response.data || []);
        } catch (error) {
            console.error('Failed to fetch chat history:', error);
        }
    }, [agent?.name]);

    // Focus input and fetch history when modal opens
    useEffect(() => {
        if (isOpen) {
            setTimeout(() => inputRef.current?.focus(), 100);
            if (messages.length === 0) {
                setMessages([{
                    role: 'system',
                    content: `You're now chatting with ${agent?.name}. Ask anything!`,
                    timestamp: new Date().toISOString()
                }]);
            }
            fetchHistory();
        }
    }, [isOpen, agent?.name, fetchHistory, messages.length]);

    const loadConversation = async (convId) => {
        setIsLoading(true);
        try {
            const response = await agentsAPI.getConversationHistory(convId);
            setMessages(response.data || []);
            setCurrentConversationId(convId);
        } catch (error) {
            console.error('Failed to load conversation:', error);
        } finally {
            setIsLoading(false);
        }
    };

    const handleRenameConversation = async (convId, newTitle) => {
        if (!newTitle.trim()) return;
        try {
            await agentsAPI.updateConversation(convId, newTitle);
            setHistory(prev => prev.map(c => c.id === convId ? { ...c, title: newTitle } : c));
            setEditingConversationId(null);
        } catch (error) {
            console.error('Failed to rename conversation:', error);
        }
    };

    const handleDeleteConversation = async (convId) => {
        if (!window.confirm('Are you sure you want to delete this conversation?')) return;
        try {
            await agentsAPI.deleteConversation(convId);
            setHistory(prev => prev.filter(c => c.id !== convId));
            if (currentConversationId === convId) {
                startNewChat();
            }
        } catch (error) {
            console.error('Failed to delete conversation:', error);
        }
    };

    const startNewChat = () => {
        setMessages([{
            role: 'system',
            content: `You're now chatting with ${agent?.name}. Ask anything!`,
            timestamp: new Date().toISOString()
        }]);
        setCurrentConversationId(null);
    };

    // Close on Escape
    useEffect(() => {
        const handleKey = (e) => {
            if (e.key === 'Escape') {
                if (isExpanded) {
                    setIsExpanded(false);
                } else {
                    onClose();
                }
            }
        };
        if (isOpen) document.addEventListener('keydown', handleKey);
        return () => document.removeEventListener('keydown', handleKey);
    }, [isOpen, isExpanded, onClose]);

    const handleFileUpload = async (e) => {
        const file = e.target.files[0];
        if (!file) return;

        // Check if it's an image
        if (!file.type.startsWith('image/')) {
            alert('Please select an image file (PNG, JPG, etc.)');
            return;
        }

        setIsUploading(true);
        const formData = new FormData();
        formData.append('file', file);

        try {
            const response = await api.post('/files/upload', formData, {
                headers: { 'Content-Type': 'multipart/form-data' }
            });

            setAttachedFile({
                id: response.data.id,
                name: file.name,
                url: URL.createObjectURL(file)
            });
        } catch (error) {
            console.error('Upload error:', error);
            alert('Failed to upload image. Please try again.');
        } finally {
            setIsUploading(false);
            // Reset input so same file can be selected again
            if (fileInputRef.current) fileInputRef.current.value = '';
        }
    };

    const removeAttachment = () => {
        if (attachedFile?.url) URL.revokeObjectURL(attachedFile.url);
        setAttachedFile(null);
    };

    const handleSend = async () => {
        if ((!input.trim() && !attachedFile) || isLoading || isUploading) return;

        const userMessage = input.trim();
        const fileId = attachedFile?.id;

        setInput('');
        setMessages(prev => [...prev, {
            role: 'user',
            content: userMessage || (fileId ? `[Uploaded Image: ${attachedFile.name}]` : ''),
            timestamp: new Date().toISOString(),
            attachedImage: attachedFile?.url
        }]);

        // Clear attachment immediately for UI
        const currentAttachment = attachedFile;
        setAttachedFile(null);
        setIsLoading(true);

        const requestId = `req_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
        setCurrentRequestId(requestId);

        const controller = new AbortController();
        setAbortController(controller);

        try {
            // Only send history if it's a fresh manual send (backend now handles persistent history retrieval)
            // But we keep this for initial context if needed
            const historyPayload = messages
                .filter(m => m.role === 'user' || m.role === 'agent')
                .map(m => ({ role: m.role, content: m.content }));

            const response = await api.post('/agents/chat', {
                agent_name: agent?.name,
                message: userMessage,
                history: historyPayload,
                request_id: requestId,
                style: selectedStyle,
                file_id: fileId,
                conversation_id: currentConversationId
            }, {
                signal: controller.signal
            });

            if (response.data?.response) {
                setMessages(prev => [...prev, {
                    role: 'agent',
                    content: response.data.response,
                    timestamp: new Date().toISOString()
                }]);

                if (response.data.conversation_id && !currentConversationId) {
                    setCurrentConversationId(response.data.conversation_id);
                    fetchHistory();
                }

                setIsLoading(false);
                setCurrentRequestId(null);
                setAbortController(null);
            }
        } catch (error) {
            if (error.name === 'AbortError') {
                console.log('Request aborted');
                return;
            }
            console.error('Chat error:', error);
            setMessages(prev => [...prev, {
                role: 'agent',
                content: `Sorry, I encountered an error. Please try again.`,
                timestamp: new Date().toISOString()
            }]);
            setIsLoading(false);
            setCurrentRequestId(null);
            setAbortController(null);
        }
    };

    // Reset state when modal closes
    useEffect(() => {
        if (!isOpen) {
            setMessages([]);
            setInput('');
            setSelectedStyle(null);
            setIsLoading(false);
            setCurrentRequestId(null);
            setAttachedFile(null);
            setIsUploading(false);
            setHistory([]);
            setCurrentConversationId(null);
        }
    }, [isOpen]);

    const handleStop = async () => {
        if (!currentRequestId) return;

        // 1. Optimistic UI update - don't wait for backend
        setIsLoading(false);
        const reqIdToStop = currentRequestId;
        setCurrentRequestId(null);

        // 2. Abort local fetch immediately
        if (abortController) {
            abortController.abort();
            setAbortController(null);
        }

        setMessages(prev => [...prev, {
            role: 'system',
            content: '🛑 Request stopped by user.',
            timestamp: new Date().toISOString()
        }]);

        try {
            // 3. Notify backend in the background
            await api.post('/agents/stop', { request_id: reqIdToStop });
            console.log('✅ Backend notified of stop:', reqIdToStop);
        } catch (error) {
            console.error('Failed to notify backend of stop:', error);
        }
    };

    const handleKeyDown = (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            handleSend();
        }
    };

    // Download image from markdown image syntax
    const handleImageDownload = (content) => {
        const match = content.match(/!\[.*?\]\((.*?)\)/);
        if (match && match[1]) {
            const baseUrl = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000';
            const imgUrl = match[1].startsWith('/') ? `${baseUrl}${match[1]}` : match[1];
            const link = document.createElement('a');
            link.href = imgUrl;
            link.download = match[1].split('/').pop() || 'nexus-image.png';
            link.target = '_blank';
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
        }
    };

    // Check if message contains an image
    const hasImage = (content) => /!\[.*?\]\(.*?\)/.test(content);

    if (!isOpen) return null;

    const agentEmojis = {
        'ResearchAgent': '🔍',
        'CodeAgent': '💻',
        'ContentAgent': '✍️',
        'DataAgent': '📊',
        'QAAgent': '✅',
        'MemoryAgent': '🧠',
        'ManagerAgent': '📋',
        'VisualAgent': '🎨',
    };

    return (
        <div className="fixed inset-0 bg-black/70 backdrop-blur-sm flex items-center justify-center z-[100] p-4">
            <div
                className={`bg-dark-800 rounded-2xl border border-dark-700 flex flex-row overflow-hidden shadow-2xl transition-all duration-500 ease-in-out ${isExpanded
                    ? 'fixed inset-4 md:inset-6 w-auto h-auto'
                    : 'relative w-full max-w-4xl h-[650px]'
                    }`}
            >
                {/* History Sidebar */}
                <div className={`transition-all duration-300 border-r border-dark-700 bg-dark-900/50 flex flex-col ${showHistory || isExpanded ? 'w-64' : 'w-0 overflow-hidden border-none'}`}>
                    <div className="p-4 border-b border-dark-700 flex items-center justify-between">
                        <span className="text-xs font-bold uppercase tracking-wider text-dark-400">History</span>
                        <button
                            onClick={startNewChat}
                            className="p-1.5 rounded-lg bg-primary-500/10 text-primary-400 hover:bg-primary-500 hover:text-white transition-all text-xs flex items-center gap-1"
                        >
                            <span>+</span> New Chat
                        </button>
                    </div>
                    <div className="flex-1 overflow-y-auto p-2 space-y-1">
                        {history.length === 0 ? (
                            <div className="p-4 text-center text-dark-500 text-xs mt-10">
                                No previous chats.
                            </div>
                        ) : (
                            history.map((conv) => (
                                <div key={conv.id} className="group relative">
                                    {editingConversationId === conv.id ? (
                                        <div className="p-2 space-y-2 bg-dark-700/50 rounded-xl border border-primary-500/30">
                                            <input
                                                autoFocus
                                                value={editTitleValue}
                                                onChange={(e) => setEditTitleValue(e.target.value)}
                                                onKeyDown={(e) => {
                                                    if (e.key === 'Enter') handleRenameConversation(conv.id, editTitleValue);
                                                    if (e.key === 'Escape') setEditingConversationId(null);
                                                }}
                                                className="w-full bg-dark-800 border border-dark-600 rounded-lg px-2 py-1 text-xs text-white focus:outline-none focus:border-primary-500"
                                            />
                                            <div className="flex justify-end gap-1">
                                                <button
                                                    onClick={() => setEditingConversationId(null)}
                                                    className="p-1 px-2 text-[10px] text-dark-400 hover:text-white"
                                                >
                                                    Cancel
                                                </button>
                                                <button
                                                    onClick={() => handleRenameConversation(conv.id, editTitleValue)}
                                                    className="p-1 px-2 text-[10px] bg-primary-500 text-white rounded-md"
                                                >
                                                    Save
                                                </button>
                                            </div>
                                        </div>
                                    ) : (
                                        <>
                                            <button
                                                onClick={() => loadConversation(conv.id)}
                                                className={`w-full text-left p-2.5 rounded-xl transition-all relative overflow-hidden ${currentConversationId === conv.id ? 'bg-primary-500/20 text-primary-400' : 'text-dark-300 hover:bg-dark-700'}`}
                                            >
                                                <div className="text-sm font-medium truncate pr-10">{conv.title}</div>
                                                <div className="text-[10px] text-dark-500 mt-1">{new Date(conv.updated_at).toLocaleDateString()}</div>
                                                {currentConversationId === conv.id && (
                                                    <div className="absolute left-0 top-0 bottom-0 w-1 bg-primary-500" />
                                                )}
                                            </button>
                                            <div className="absolute right-2 top-2.5 flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
                                                <button
                                                    onClick={(e) => {
                                                        e.stopPropagation();
                                                        setEditingConversationId(conv.id);
                                                        setEditTitleValue(conv.title);
                                                    }}
                                                    className="p-1.5 rounded-md hover:bg-dark-600 text-dark-400 hover:text-primary-400 transition-all"
                                                    title="Rename"
                                                >
                                                    <svg className="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15.232 5.232l3.536 3.536m-2.036-5.036a2.5 2.5 0 113.536 3.536L6.5 21.036H3v-3.572L16.732 3.732z" />
                                                    </svg>
                                                </button>
                                                <button
                                                    onClick={(e) => {
                                                        e.stopPropagation();
                                                        handleDeleteConversation(conv.id);
                                                    }}
                                                    className="p-1.5 rounded-md hover:bg-dark-600 text-dark-400 hover:text-red-400 transition-all"
                                                    title="Delete"
                                                >
                                                    <svg className="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                                                    </svg>
                                                </button>
                                            </div>
                                        </>
                                    )}
                                </div>
                            ))
                        )}
                    </div>
                </div>

                {/* Main Chat Area */}
                <div className="flex-1 flex flex-col bg-dark-800 relative">
                    {/* Header */}
                    <div className="p-4 border-b border-dark-700 flex items-center justify-between bg-dark-800/80">
                        <div className="flex items-center gap-3">
                            <button
                                onClick={() => setShowHistory(!showHistory)}
                                className={`p-2 rounded-lg hover:bg-dark-700 transition-colors ${showHistory ? 'text-primary-400' : 'text-dark-400'}`}
                            >
                                <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
                                </svg>
                            </button>
                            <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-primary-500 to-purple-600 flex items-center justify-center text-xl">
                                {agentEmojis[agent?.name] || '🤖'}
                            </div>
                            <div>
                                <h1 className="text-lg font-semibold text-white">{agent?.name}</h1>
                                <p className="text-xs text-dark-400">
                                    {isExpanded ? 'Full Chat Mode' : 'Direct Chat'}
                                </p>
                            </div>
                        </div>
                        <div className="flex items-center gap-2">
                            {/* Expand / Collapse button */}
                            <button
                                onClick={() => setIsExpanded(!isExpanded)}
                                className="w-8 h-8 flex items-center justify-center rounded-lg hover:bg-dark-700 text-dark-400 hover:text-white transition-colors"
                                title={isExpanded ? 'Collapse' : 'Expand to full chat'}
                            >
                                {isExpanded ? '⊡' : '⛶'}
                            </button>
                            {/* Close button */}
                            <button
                                onClick={onClose}
                                className="w-8 h-8 flex items-center justify-center rounded-lg hover:bg-dark-700 text-dark-400 hover:text-white transition-colors"
                            >
                                ✕
                            </button>
                        </div>
                    </div>

                    {/* Messages */}
                    <div className="flex-1 overflow-y-auto p-6 space-y-6">
                        {messages.map((msg, idx) => (
                            <div
                                key={idx}
                                className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
                            >
                                <div
                                    className={`flex flex-col ${msg.role === 'user' ? 'items-end' : 'items-start'} ${isExpanded ? 'max-w-[75%]' : 'max-w-[90%]'}`}
                                >
                                    <div
                                        className={`px-4 py-2.5 rounded-2xl ${msg.role === 'user'
                                            ? 'bg-primary-500 text-white rounded-br-none shadow-lg shadow-primary-500/10'
                                            : msg.role === 'system'
                                                ? 'bg-dark-700/50 text-dark-400 text-xs italic border border-dark-600/50'
                                                : 'bg-dark-700 text-dark-100 rounded-bl-none border border-dark-600'
                                            }`}
                                    >
                                        {msg.attachedImage && (
                                            <div className="mb-2 rounded-lg overflow-hidden border border-white/10">
                                                <img
                                                    src={msg.attachedImage.startsWith('blob:') ? msg.attachedImage : `${import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000'}${msg.attachedImage}`}
                                                    alt="Attached"
                                                    className="max-h-48 object-contain cursor-pointer"
                                                    onClick={() => setLightboxImage(msg.attachedImage)}
                                                />
                                            </div>
                                        )}
                                        {msg.role === 'agent' ? (
                                            <div className="min-w-0 max-w-full overflow-hidden">
                                                <MarkdownRenderer
                                                    content={msg.content}
                                                    onImageClick={setLightboxImage}
                                                />
                                                {/* Download button for images */}
                                                {hasImage(msg.content) && (
                                                    <button
                                                        onClick={() => handleImageDownload(msg.content)}
                                                        className="mt-3 flex items-center gap-1.5 text-xs text-primary-400 hover:text-primary-300 bg-primary-500/10 hover:bg-primary-500/20 px-3 py-1.5 rounded-lg transition-all"
                                                    >
                                                        ⬇ Download Image
                                                    </button>
                                                )}
                                            </div>
                                        ) : (
                                            <p className="whitespace-pre-wrap">{msg.content}</p>
                                        )}
                                    </div>
                                    <span className="text-[10px] text-dark-500 mt-1 px-1">
                                        {msg.timestamp ? new Date(msg.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) : ''}
                                    </span>
                                </div>
                            </div>
                        ))}
                        {isLoading && (
                            <div className="flex justify-start">
                                <div className="bg-dark-700 text-dark-400 px-4 py-3 rounded-2xl rounded-bl-none border border-dark-600">
                                    <div className="flex items-center gap-4">
                                        <div className="flex gap-1.5">
                                            <span className="w-1.5 h-1.5 bg-primary-500 rounded-full animate-bounce" style={{ animationDelay: '0ms' }}></span>
                                            <span className="w-1.5 h-1.5 bg-primary-500 rounded-full animate-bounce" style={{ animationDelay: '150ms' }}></span>
                                            <span className="w-1.5 h-1.5 bg-primary-500 rounded-full animate-bounce" style={{ animationDelay: '300ms' }}></span>
                                        </div>
                                        <button
                                            onClick={handleStop}
                                            className="text-[10px] font-bold uppercase tracking-wider text-red-400 hover:text-red-300 transition-colors border border-red-400/30 px-2 py-0.5 rounded-md hover:bg-red-400/10"
                                        >
                                            🛑 Stop
                                        </button>
                                    </div>
                                </div>
                            </div>
                        )}
                        <div ref={messagesEndRef} />
                    </div>

                    {/* Input Area */}
                    <div className="p-4 border-t border-dark-700 bg-dark-800/80">
                        {/* Image Preview */}
                        {attachedFile && (
                            <div className="mb-3 flex items-center gap-3 p-2 bg-dark-700 rounded-xl border border-primary-500/30 w-fit">
                                <img src={attachedFile.url} className="w-12 h-12 rounded-lg object-cover" alt="Preview" />
                                <div className="flex flex-col">
                                    <span className="text-xs text-white font-medium truncate max-w-[150px]">{attachedFile.name}</span>
                                    <span className="text-[10px] text-primary-400">Ready to upload</span>
                                </div>
                                <button
                                    onClick={removeAttachment}
                                    className="w-6 h-6 flex items-center justify-center rounded-full bg-dark-600 text-dark-400 hover:text-white hover:bg-red-500/20 transition-all font-bold text-xs"
                                >
                                    ✕
                                </button>
                            </div>
                        )}

                        {agent?.name === 'VisualAgent' && (
                            <StylePresets
                                selectedStyle={selectedStyle}
                                onSelectStyle={setSelectedStyle}
                            />
                        )}
                        <div className="flex gap-3">
                            {agent?.name === 'VisualAgent' && (
                                <>
                                    <input
                                        type="file"
                                        ref={fileInputRef}
                                        onChange={handleFileUpload}
                                        className="hidden"
                                        accept="image/*"
                                    />
                                    <button
                                        onClick={() => fileInputRef.current?.click()}
                                        disabled={isLoading || isUploading || attachedFile}
                                        className={`w-12 h-12 flex items-center justify-center rounded-xl border border-dark-600 text-dark-400 hover:text-white hover:border-primary-500 transition-all flex-shrink-0 ${attachedFile ? 'bg-primary-500/20 border-primary-500 text-primary-400' : 'bg-dark-700'}`}
                                        title="Attach Image"
                                    >
                                        {isUploading ? (
                                            <div className="w-5 h-5 border-2 border-primary-500 border-t-transparent rounded-full animate-spin"></div>
                                        ) : (
                                            <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15.172 7l-6.586 6.586a2 2 0 102.828 2.828l6.414-6.586a4 4 0 00-5.656-5.656l-6.415 6.585a6 6 0 108.486 8.486L20.5 13" />
                                            </svg>
                                        )}
                                    </button>
                                </>
                            )}
                            <textarea
                                ref={inputRef}
                                value={input}
                                onChange={(e) => setInput(e.target.value)}
                                onKeyDown={handleKeyDown}
                                placeholder={attachedFile ? `Describe what to do with this image...` : `Ask ${agent?.name} anything...`}
                                rows={isExpanded ? 2 : 1}
                                className="flex-1 bg-dark-700 border border-dark-600 rounded-xl px-4 py-3 text-white placeholder-dark-500 focus:outline-none focus:border-primary-500 resize-none max-h-32"
                            />
                            <button
                                onClick={handleSend}
                                disabled={(!input.trim() && !attachedFile) || isLoading || isUploading}
                                className="px-5 py-3 bg-gradient-to-r from-primary-500 to-purple-600 text-white rounded-xl font-medium hover:shadow-lg hover:shadow-primary-500/25 transition-all disabled:opacity-50 disabled:cursor-not-allowed h-12"
                            >
                                Send
                            </button>
                        </div>
                    </div>
                </div>
            </div>

            <ImageLightbox
                isOpen={!!lightboxImage}
                imageUrl={lightboxImage}
                onClose={() => setLightboxImage(null)}
            />
        </div>
    );
}

