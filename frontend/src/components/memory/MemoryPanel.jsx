import { useState, useEffect } from 'react';
import ConversationHistory from './ConversationHistory';
import PreferencesPanel from './PreferencesPanel';
import RelatedTasks from './RelatedTasks';
import MemoryAnalytics from './MemoryAnalytics';
import './MemoryPanel.css';

const API_BASE = 'http://localhost:8000';

export default function MemoryPanel({ token }) {
    const [activeTab, setActiveTab] = useState('history');
    const [stats, setStats] = useState(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        fetchStats();
    }, []);

    const fetchStats = async () => {
        try {
            const response = await fetch(`${API_BASE}/memory/stats`, {
                headers: { Authorization: `Bearer ${token}` }
            });
            if (response.ok) {
                setStats(await response.json());
            }
        } catch (error) {
            console.error('Failed to fetch memory stats:', error);
        } finally {
            setLoading(false);
        }
    };

    const tabs = [
        { id: 'history', label: '💬 Conversations', icon: '💬' },
        { id: 'preferences', label: '⚙️ Preferences', icon: '⚙️' },
        { id: 'related', label: '🔗 Related Tasks', icon: '🔗' },
        { id: 'analytics', label: '📊 Analytics', icon: '📊' },
    ];

    const renderTabContent = () => {
        switch (activeTab) {
            case 'history':
                return <ConversationHistory token={token} />;
            case 'preferences':
                return <PreferencesPanel token={token} />;
            case 'related':
                return <RelatedTasks token={token} />;
            case 'analytics':
                return <MemoryAnalytics token={token} />;
            default:
                return null;
        }
    };

    return (
        <div className="memory-panel">
            <div className="memory-header">
                <h2>🧠 Memory & Context</h2>
                {stats && (
                    <div className="memory-stats-summary">
                        <span className="stat-badge">
                            {stats.total_memories || 0} memories stored
                        </span>
                    </div>
                )}
            </div>

            <div className="memory-tabs">
                {tabs.map(tab => (
                    <button
                        key={tab.id}
                        className={`memory-tab ${activeTab === tab.id ? 'active' : ''}`}
                        onClick={() => setActiveTab(tab.id)}
                    >
                        <span className="tab-icon">{tab.icon}</span>
                        <span className="tab-label">{tab.label.split(' ').slice(1).join(' ')}</span>
                    </button>
                ))}
            </div>

            <div className="memory-content">
                {loading ? (
                    <div className="loading-state">
                        <div className="spinner"></div>
                        <p>Loading memory data...</p>
                    </div>
                ) : (
                    renderTabContent()
                )}
            </div>

            <div className="memory-footer">
                <p className="privacy-notice">
                    🔒 Your data is stored locally and never shared
                </p>
            </div>
        </div>
    );
}
