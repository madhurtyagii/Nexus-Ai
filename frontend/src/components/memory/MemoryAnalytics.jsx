import { useState, useEffect } from 'react';

const API_BASE = 'http://localhost:8000';

export default function MemoryAnalytics({ token }) {
    const [analytics, setAnalytics] = useState(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        fetchAnalytics();
    }, []);

    const fetchAnalytics = async () => {
        try {
            const response = await fetch(`${API_BASE}/memory/analytics`, {
                headers: { Authorization: `Bearer ${token}` }
            });
            if (response.ok) {
                setAnalytics(await response.json());
            }
        } catch (error) {
            console.error('Failed to fetch analytics:', error);
        } finally {
            setLoading(false);
        }
    };

    if (loading) {
        return (
            <div className="loading-state">
                <div className="spinner"></div>
                <p>Loading analytics...</p>
            </div>
        );
    }

    if (!analytics) {
        return (
            <div className="empty-state">
                <div className="empty-state-icon">📊</div>
                <p>No analytics available yet</p>
            </div>
        );
    }

    const { statistics, popular_topics, quality_score, cleanup_suggestions } = analytics;

    return (
        <div className="memory-analytics">
            {/* Stats Cards */}
            <div className="stats-grid">
                <div className="stat-card">
                    <div className="stat-icon">🧠</div>
                    <div className="stat-value">{statistics?.total_memories || 0}</div>
                    <div className="stat-label">Total Memories</div>
                </div>

                <div className="stat-card">
                    <div className="stat-icon">💬</div>
                    <div className="stat-value">
                        {statistics?.by_collection?.conversation_history || 0}
                    </div>
                    <div className="stat-label">Conversations</div>
                </div>

                <div className="stat-card">
                    <div className="stat-icon">🤖</div>
                    <div className="stat-value">
                        {statistics?.by_collection?.agent_outputs || 0}
                    </div>
                    <div className="stat-label">Agent Outputs</div>
                </div>

                <div className="stat-card quality">
                    <div className="stat-icon">⭐</div>
                    <div className="stat-value">{quality_score?.overall_score || 0}</div>
                    <div className="stat-label">Quality Score</div>
                </div>
            </div>

            {/* Agent Usage */}
            {statistics?.by_agent && Object.keys(statistics.by_agent).length > 0 && (
                <div className="section">
                    <h3>🤖 Agent Usage</h3>
                    <div className="bar-chart">
                        {Object.entries(statistics.by_agent)
                            .sort(([, a], [, b]) => b - a)
                            .slice(0, 5)
                            .map(([agent, count]) => {
                                const maxCount = Math.max(...Object.values(statistics.by_agent));
                                const percentage = (count / maxCount) * 100;

                                return (
                                    <div key={agent} className="bar-item">
                                        <div className="bar-label">{agent.replace('Agent', '')}</div>
                                        <div className="bar-container">
                                            <div
                                                className="bar-fill"
                                                style={{ width: `${percentage}%` }}
                                            ></div>
                                        </div>
                                        <div className="bar-value">{count}</div>
                                    </div>
                                );
                            })}
                    </div>
                </div>
            )}

            {/* Popular Topics */}
            {popular_topics?.length > 0 && (
                <div className="section">
                    <h3>🔥 Popular Topics</h3>
                    <div className="topics-cloud">
                        {popular_topics.slice(0, 15).map((topic, index) => (
                            <span
                                key={topic.topic}
                                className="topic-chip"
                                style={{
                                    fontSize: `${Math.max(0.75, 1 - index * 0.03)}rem`,
                                    opacity: Math.max(0.5, 1 - index * 0.05)
                                }}
                            >
                                {topic.topic}
                                <span className="topic-count">{topic.count}</span>
                            </span>
                        ))}
                    </div>
                </div>
            )}

            {/* Quality Breakdown */}
            {quality_score?.breakdown && (
                <div className="section">
                    <h3>📊 Quality Breakdown</h3>
                    <div className="quality-metrics">
                        {Object.entries(quality_score.breakdown).map(([metric, value]) => (
                            <div key={metric} className="quality-metric">
                                <div className="metric-header">
                                    <span className="metric-label">
                                        {metric.replace(/_/g, ' ')}
                                    </span>
                                    <span className="metric-value">{value}%</span>
                                </div>
                                <div className="metric-bar">
                                    <div
                                        className="metric-fill"
                                        style={{ width: `${value}%` }}
                                    ></div>
                                </div>
                            </div>
                        ))}
                    </div>
                </div>
            )}

            {/* Recommendations */}
            {quality_score?.recommendations?.length > 0 && (
                <div className="section recommendations">
                    <h3>💡 Recommendations</h3>
                    <ul className="recommendation-list">
                        {quality_score.recommendations.map((rec, index) => (
                            <li key={index}>{rec}</li>
                        ))}
                    </ul>
                </div>
            )}

            {/* Cleanup Suggestions */}
            {cleanup_suggestions?.recommendations?.length > 0 && (
                <div className="section cleanup">
                    <h3>🧹 Cleanup Suggestions</h3>
                    <ul className="suggestion-list">
                        {cleanup_suggestions.recommendations.map((sug, index) => (
                            <li key={index}>{sug}</li>
                        ))}
                    </ul>
                </div>
            )}

            <style jsx>{`
        .memory-analytics {
          padding: 8px;
        }
        .stats-grid {
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
          gap: 16px;
          margin-bottom: 24px;
        }
        .stat-card {
          background: rgba(255, 255, 255, 0.05);
          border: 1px solid rgba(255, 255, 255, 0.1);
          border-radius: 12px;
          padding: 16px;
          text-align: center;
        }
        .stat-card.quality {
          background: linear-gradient(135deg, rgba(102, 126, 234, 0.1) 0%, rgba(118, 75, 162, 0.1) 100%);
          border-color: rgba(102, 126, 234, 0.3);
        }
        .stat-icon {
          font-size: 1.5rem;
          margin-bottom: 8px;
        }
        .stat-value {
          font-size: 1.75rem;
          font-weight: 700;
          color: #fff;
        }
        .stat-label {
          font-size: 0.8rem;
          color: #888;
          margin-top: 4px;
        }
        .section {
          background: rgba(255, 255, 255, 0.03);
          border-radius: 12px;
          padding: 16px;
          margin-bottom: 16px;
        }
        .section h3 {
          margin: 0 0 16px 0;
          color: #fff;
          font-size: 1rem;
        }
        .bar-chart {
          display: flex;
          flex-direction: column;
          gap: 12px;
        }
        .bar-item {
          display: flex;
          align-items: center;
          gap: 12px;
        }
        .bar-label {
          width: 80px;
          font-size: 0.85rem;
          color: #a0a0a0;
        }
        .bar-container {
          flex: 1;
          height: 20px;
          background: rgba(255, 255, 255, 0.05);
          border-radius: 10px;
          overflow: hidden;
        }
        .bar-fill {
          height: 100%;
          background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
          border-radius: 10px;
          transition: width 0.5s ease;
        }
        .bar-value {
          width: 40px;
          text-align: right;
          font-size: 0.85rem;
          color: #667eea;
        }
        .topics-cloud {
          display: flex;
          flex-wrap: wrap;
          gap: 8px;
        }
        .topic-chip {
          background: rgba(102, 126, 234, 0.1);
          color: #a0a0f0;
          padding: 6px 12px;
          border-radius: 20px;
          display: inline-flex;
          align-items: center;
          gap: 6px;
        }
        .topic-count {
          background: rgba(255, 255, 255, 0.1);
          padding: 2px 6px;
          border-radius: 10px;
          font-size: 0.7rem;
        }
        .quality-metrics {
          display: flex;
          flex-direction: column;
          gap: 12px;
        }
        .quality-metric {
          padding: 8px 0;
        }
        .metric-header {
          display: flex;
          justify-content: space-between;
          margin-bottom: 6px;
        }
        .metric-label {
          color: #a0a0a0;
          font-size: 0.85rem;
          text-transform: capitalize;
        }
        .metric-value {
          color: #667eea;
          font-weight: 600;
        }
        .metric-bar {
          height: 8px;
          background: rgba(255, 255, 255, 0.05);
          border-radius: 4px;
          overflow: hidden;
        }
        .metric-fill {
          height: 100%;
          background: linear-gradient(135deg, #10b981 0%, #059669 100%);
          border-radius: 4px;
          transition: width 0.5s ease;
        }
        .recommendations, .cleanup {
          border-left: 3px solid #667eea;
        }
        .recommendation-list, .suggestion-list {
          margin: 0;
          padding-left: 20px;
          color: #a0a0a0;
          font-size: 0.9rem;
          line-height: 1.6;
        }
        .cleanup {
          border-left-color: #fbbf24;
        }
      `}</style>
        </div>
    );
}
