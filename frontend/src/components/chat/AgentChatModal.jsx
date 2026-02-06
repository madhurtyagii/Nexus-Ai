/**
 * Nexus AI - Agent Chat Modal
 * Direct chat interface for communicating with specific agents
 */

import { useState, useRef, useEffect, useCallback } from 'react';
import { useAuth } from '../../context/AuthContext';
import { useWebSocket, EventType } from '../../hooks/useWebSocket';
import api from '../../services/api';
import MarkdownRenderer from '../common/MarkdownRenderer';

export default function AgentChatModal({ isOpen, onClose, agent }) {
    const { token } = useAuth();
    const [messages, setMessages] = useState([]);
    const [input, setInput] = useState('');
    const [isLoading, setIsLoading] = useState(false);
    const messagesEndRef = useRef(null);
    const inputRef = useRef(null);

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

    // Focus input when modal opens
    useEffect(() => {
        if (isOpen) {
            setTimeout(() => inputRef.current?.focus(), 100);
            // Clear history for new session
            setMessages([{
                role: 'system',
                content: `You're now chatting with ${agent?.name}. Ask anything!`,
                timestamp: new Date().toISOString()
            }]);
        }
    }, [isOpen, agent?.name]);

    const handleSend = async () => {
        if (!input.trim() || isLoading) return;

        const userMessage = input.trim();
        setInput('');
        setMessages(prev => [...prev, {
            role: 'user',
            content: userMessage,
            timestamp: new Date().toISOString()
        }]);
        setIsLoading(true);

        try {
            // Build conversation history for context (exclude system messages)
            const history = messages
                .filter(m => m.role === 'user' || m.role === 'agent')
                .map(m => ({
                    role: m.role,
                    content: m.content
                }));

            // Send via REST API with history for context
            const response = await api.post('/agents/chat', {
                agent_name: agent?.name,
                message: userMessage,
                history: history  // Include conversation history
            });

            // Handle direct REST response if no WebSocket
            if (response.data?.response) {
                setMessages(prev => [...prev, {
                    role: 'agent',
                    content: response.data.response,
                    timestamp: new Date().toISOString()
                }]);
                setIsLoading(false);
            }
        } catch (error) {
            console.error('Chat error:', error);
            setMessages(prev => [...prev, {
                role: 'agent',
                content: `Sorry, I encountered an error. Please try again.`,
                timestamp: new Date().toISOString()
            }]);
            setIsLoading(false);
        }
    };

    const handleKeyDown = (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            handleSend();
        }
    };

    if (!isOpen) return null;

    const agentEmojis = {
        'ResearchAgent': '🔍',
        'CodeAgent': '💻',
        'ContentAgent': '✍️',
        'DataAgent': '📊',
        'QAAgent': '✅',
        'MemoryAgent': '🧠',
        'ManagerAgent': '📋',
    };

    return (
        <div className="fixed inset-0 bg-black/70 backdrop-blur-sm flex items-center justify-center z-50 p-4">
            <div className="bg-dark-800 rounded-2xl border border-dark-700 w-full max-w-2xl h-[600px] flex flex-col overflow-hidden shadow-2xl">
                {/* Header */}
                <div className="p-4 border-b border-dark-700 flex items-center justify-between bg-dark-800/80">
                    <div className="flex items-center gap-3">
                        <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-primary-500 to-purple-600 flex items-center justify-center text-xl">
                            {agentEmojis[agent?.name] || '🤖'}
                        </div>
                        <div>
                            <h2 className="text-lg font-semibold text-white">{agent?.name}</h2>
                            <p className="text-xs text-dark-400">Direct Chat</p>
                        </div>
                    </div>
                    <button
                        onClick={onClose}
                        className="w-8 h-8 flex items-center justify-center rounded-lg hover:bg-dark-700 text-dark-400 hover:text-white transition-colors"
                    >
                        ✕
                    </button>
                </div>

                {/* Messages */}
                <div className="flex-1 overflow-y-auto p-4 space-y-4">
                    {messages.map((msg, idx) => (
                        <div
                            key={idx}
                            className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
                        >
                            <div
                                className={`max-w-[80%] px-4 py-2.5 rounded-2xl ${msg.role === 'user'
                                    ? 'bg-primary-500 text-white rounded-br-sm'
                                    : msg.role === 'system'
                                        ? 'bg-dark-700/50 text-dark-400 text-sm italic'
                                        : 'bg-dark-700 text-white rounded-bl-sm'
                                    }`}
                            >
                                {msg.role === 'agent' ? (
                                    <MarkdownRenderer content={msg.content} />
                                ) : (
                                    <p className="whitespace-pre-wrap">{msg.content}</p>
                                )}
                            </div>
                        </div>
                    ))}
                    {isLoading && (
                        <div className="flex justify-start">
                            <div className="bg-dark-700 text-dark-400 px-4 py-3 rounded-2xl rounded-bl-sm">
                                <div className="flex gap-1.5">
                                    <span className="w-2 h-2 bg-dark-500 rounded-full animate-bounce" style={{ animationDelay: '0ms' }}></span>
                                    <span className="w-2 h-2 bg-dark-500 rounded-full animate-bounce" style={{ animationDelay: '150ms' }}></span>
                                    <span className="w-2 h-2 bg-dark-500 rounded-full animate-bounce" style={{ animationDelay: '300ms' }}></span>
                                </div>
                            </div>
                        </div>
                    )}
                    <div ref={messagesEndRef} />
                </div>

                {/* Input */}
                <div className="p-4 border-t border-dark-700 bg-dark-800/80">
                    <div className="flex gap-3">
                        <textarea
                            ref={inputRef}
                            value={input}
                            onChange={(e) => setInput(e.target.value)}
                            onKeyDown={handleKeyDown}
                            placeholder={`Ask ${agent?.name} anything...`}
                            rows={1}
                            className="flex-1 bg-dark-700 border border-dark-600 rounded-xl px-4 py-3 text-white placeholder-dark-500 focus:outline-none focus:border-primary-500 resize-none"
                        />
                        <button
                            onClick={handleSend}
                            disabled={!input.trim() || isLoading}
                            className="px-5 py-3 bg-gradient-to-r from-primary-500 to-purple-600 text-white rounded-xl font-medium hover:shadow-lg hover:shadow-primary-500/25 transition-all disabled:opacity-50 disabled:cursor-not-allowed"
                        >
                            Send
                        </button>
                    </div>
                </div>
            </div>
        </div>
    );
}
