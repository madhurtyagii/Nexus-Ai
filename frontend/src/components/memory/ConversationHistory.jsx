import { useState, useEffect } from 'react';

const API_BASE = 'http://localhost:8000';

/**
 * ConversationHistory Component
 * 
 * Displays a searchable and paginated history of user-AI interactions 
 * stored in the semantic memory system.
 * 
 * @component
 * @param {Object} props - Component props.
 * @param {string} props.token - JWT authentication token.
 */
export default function ConversationHistory({ token }) {
    const [conversations, setConversations] = useState([]);
    const [loading, setLoading] = useState(true);
    const [searchQuery, setSearchQuery] = useState('');
    const [expandedId, setExpandedId] = useState(null);

    useEffect(() => {
        fetchConversations();
    }, []);

    const fetchConversations = async () => {
        try {
            const response = await fetch(`${API_BASE}/memory/conversations?limit=50`, {
                headers: { Authorization: `Bearer ${token}` }
            });
            if (response.ok) {
                const data = await response.json();
                setConversations(data.conversations || []);
            }
        } catch (error) {
            console.error('Failed to fetch conversations:', error);
        } finally {
            setLoading(false);
        }
    };

    const handleSearch = async () => {
        if (!searchQuery.trim()) {
            fetchConversations();
            return;
        }

        setLoading(true);
        try {
            const response = await fetch(
                `${API_BASE}/memory/search?query=${encodeURIComponent(searchQuery)}&limit=20`,
                { headers: { Authorization: `Bearer ${token}` } }
            );
            if (response.ok) {
                const data = await response.json();
                setConversations(data.results || []);
            }
        } catch (error) {
            console.error('Search failed:', error);
        } finally {
            setLoading(false);
        }
    };

    const handleDelete = async (memoryId, collection) => {
        if (!confirm('Delete this memory?')) return;

        try {
            const response = await fetch(
                `${API_BASE}/memory/${memoryId}?collection=${collection}`,
                {
                    method: 'DELETE',
                    headers: { Authorization: `Bearer ${token}` }
                }
            );
            if (response.ok) {
                setConversations(prev => prev.filter(c => c.id !== memoryId));
            }
        } catch (error) {
            console.error('Delete failed:', error);
        }
    };

    const formatTimestamp = (timestamp) => {
        if (!timestamp) return '';
        const date = new Date(timestamp);
        return date.toLocaleDateString('en-US', {
            month: 'short',
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        });
    };

    const toggleExpand = (id) => {
        setExpandedId(expandedId === id ? null : id);
    };

    if (loading) {
        return (
            <div className="loading-state">
                <div className="spinner"></div>
                <p>Loading conversations...</p>
            </div>
        );
    }

    return (
        <div className="conversation-history">
            <div className="search-box">
                <input
                    type="text"
                    className="search-input"
                    placeholder="Search your conversation history..."
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
                />
                <button className="btn-primary" onClick={handleSearch}>
                    Search
                </button>
            </div>

            {conversations.length === 0 ? (
                <div className="empty-state">
                    <div className="empty-state-icon">💬</div>
                    <p>No conversation history yet</p>
                    <p className="text-sm text-muted">Your task prompts and agent responses will appear here</p>
                </div>
            ) : (
                <div className="memory-list">
                    {conversations.map((conv) => (
                        <div
                            key={conv.id}
                            className={`memory-item ${expandedId === conv.id ? 'expanded' : ''}`}
                            onClick={() => toggleExpand(conv.id)}
                        >
                            <div className="memory-item-header">
                                <span className={`role-badge ${conv.metadata?.role || 'user'}`}>
                                    {conv.metadata?.role === 'agent' ? '🤖' : '👤'}
                                    {conv.metadata?.role === 'agent' ? conv.metadata?.agent_name : 'You'}
                                </span>
                                <div className="memory-item-meta">
                                    {conv.metadata?.task_id && (
                                        <span>Task #{conv.metadata.task_id}</span>
                                    )}
                                    <span>{formatTimestamp(conv.metadata?.timestamp)}</span>
                                </div>
                            </div>

                            <div className="memory-item-content">
                                {expandedId === conv.id
                                    ? conv.content
                                    : conv.content?.substring(0, 200) + (conv.content?.length > 200 ? '...' : '')
                                }
                            </div>

                            {expandedId === conv.id && (
                                <div className="memory-item-actions">
                                    <button
                                        className="btn-small btn-danger"
                                        onClick={(e) => {
                                            e.stopPropagation();
                                            handleDelete(conv.id, conv.collection || 'conversation_history');
                                        }}
                                    >
                                        🗑️ Delete
                                    </button>
                                </div>
                            )}
                        </div>
                    ))}
                </div>
            )}

            <style jsx>{`
        .role-badge {
          padding: 4px 12px;
          border-radius: 20px;
          font-size: 0.85rem;
          font-weight: 500;
        }
        .role-badge.user {
          background: rgba(59, 130, 246, 0.2);
          color: #3b82f6;
        }
        .role-badge.agent {
          background: rgba(16, 185, 129, 0.2);
          color: #10b981;
        }
        .memory-item.expanded {
          border-color: rgba(102, 126, 234, 0.5);
        }
        .text-sm { font-size: 0.875rem; }
        .text-muted { color: #666; }
      `}</style>
        </div>
    );
}
