import { useState } from 'react';

const API_BASE = 'http://localhost:8000';

/**
 * RelatedTasks Component
 * 
 * Allows users to search for similar past tasks across their history 
 * using semantic similarity search.
 * 
 * @component
 * @param {Object} props - Component props.
 * @param {string} props.token - JWT authentication token.
 */
export default function RelatedTasks({ token }) {
  const [searchQuery, setSearchQuery] = useState('');
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [hasSearched, setHasSearched] = useState(false);

  const handleSearch = async () => {
    if (!searchQuery.trim()) return;

    setLoading(true);
    setHasSearched(true);

    try {
      const response = await fetch(
        `${API_BASE}/memory/related?prompt=${encodeURIComponent(searchQuery)}&limit=10`,
        { headers: { Authorization: `Bearer ${token}` } }
      );
      if (response.ok) {
        const data = await response.json();
        setResults(data.related_tasks || []);
      }
    } catch (error) {
      console.error('Search failed:', error);
    } finally {
      setLoading(false);
    }
  };

  const formatTimestamp = (timestamp) => {
    if (!timestamp) return '';
    const date = new Date(timestamp);
    return date.toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric'
    });
  };

  const getSimilarityColor = (similarity) => {
    if (similarity >= 0.8) return '#10b981';
    if (similarity >= 0.6) return '#fbbf24';
    return '#ef4444';
  };

  return (
    <div className="related-tasks">
      <div className="search-section">
        <h3>🔍 Find Similar Past Tasks</h3>
        <p className="subtitle">Search for tasks you've done before that are related to a topic</p>

        <div className="search-box">
          <input
            type="text"
            className="search-input"
            placeholder="Describe what you're looking for..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
          />
          <button
            className="btn-primary"
            onClick={handleSearch}
            disabled={loading}
          >
            {loading ? 'Searching...' : 'Find Related'}
          </button>
        </div>
      </div>

      <div className="results-section">
        {loading ? (
          <div className="loading-state">
            <div className="spinner"></div>
            <p>Searching memories...</p>
          </div>
        ) : hasSearched && results.length === 0 ? (
          <div className="empty-state">
            <div className="empty-state-icon">🔍</div>
            <p>No related tasks found</p>
            <p className="text-sm text-muted">Try a different search query</p>
          </div>
        ) : results.length > 0 ? (
          <div className="results-list">
            {results.map((result, index) => (
              <div key={result.id || index} className="result-card">
                <div className="result-header">
                  <div className="similarity-badge" style={{
                    background: `${getSimilarityColor(result.similarity)}20`,
                    color: getSimilarityColor(result.similarity)
                  }}>
                    {Math.round((result.similarity || 0) * 100)}% match
                  </div>
                  <span className="result-date">
                    {formatTimestamp(result.metadata?.timestamp)}
                  </span>
                </div>

                <div className="result-content">
                  {result.content}
                </div>

                {result.metadata?.task_id && (
                  <div className="result-meta">
                    Task #{result.metadata.task_id}
                    {result.metadata?.agent_name && (
                      <span className="agent-tag">{result.metadata.agent_name}</span>
                    )}
                  </div>
                )}
              </div>
            ))}
          </div>
        ) : (
          <div className="hint-section">
            <div className="hint-card">
              <div className="hint-icon">💡</div>
              <h4>How to use</h4>
              <p>Enter a description of what you're looking for to find similar past tasks.
                This helps you build on previous work and avoid duplication.</p>

              <div className="example-queries">
                <span className="example-label">Example queries:</span>
                <ul>
                  <li>"Python API authentication"</li>
                  <li>"Blog post about machine learning"</li>
                  <li>"Data analysis visualization"</li>
                </ul>
              </div>
            </div>
          </div>
        )}
      </div>

      <style jsx>{`
        .related-tasks {
          padding: 8px;
        }
        .search-section {
          margin-bottom: 24px;
        }
        .search-section h3 {
          margin: 0 0 8px 0;
          color: #fff;
        }
        .subtitle {
          color: #888;
          margin: 0 0 16px 0;
          font-size: 0.9rem;
        }
        .results-section {
          min-height: 200px;
        }
        .results-list {
          display: flex;
          flex-direction: column;
          gap: 12px;
        }
        .result-card {
          background: rgba(255, 255, 255, 0.05);
          border: 1px solid rgba(255, 255, 255, 0.1);
          border-radius: 12px;
          padding: 16px;
          transition: all 0.3s ease;
        }
        .result-card:hover {
          border-color: rgba(102, 126, 234, 0.3);
        }
        .result-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: 12px;
        }
        .similarity-badge {
          padding: 4px 12px;
          border-radius: 20px;
          font-size: 0.8rem;
          font-weight: 600;
        }
        .result-date {
          color: #666;
          font-size: 0.8rem;
        }
        .result-content {
          color: #d0d0d0;
          line-height: 1.5;
          margin-bottom: 12px;
        }
        .result-meta {
          font-size: 0.8rem;
          color: #888;
          display: flex;
          align-items: center;
          gap: 8px;
        }
        .agent-tag {
          background: rgba(16, 185, 129, 0.1);
          color: #10b981;
          padding: 2px 8px;
          border-radius: 12px;
        }
        .hint-section {
          display: flex;
          justify-content: center;
          padding: 20px;
        }
        .hint-card {
          background: rgba(255, 255, 255, 0.03);
          border: 1px solid rgba(255, 255, 255, 0.1);
          border-radius: 16px;
          padding: 24px;
          max-width: 400px;
          text-align: center;
        }
        .hint-icon {
          font-size: 2rem;
          margin-bottom: 12px;
        }
        .hint-card h4 {
          margin: 0 0 8px 0;
          color: #fff;
        }
        .hint-card p {
          color: #888;
          margin: 0 0 16px 0;
          font-size: 0.9rem;
        }
        .example-queries {
          text-align: left;
          background: rgba(102, 126, 234, 0.1);
          padding: 12px;
          border-radius: 8px;
        }
        .example-label {
          font-size: 0.8rem;
          color: #667eea;
          font-weight: 500;
        }
        .example-queries ul {
          margin: 8px 0 0 0;
          padding-left: 20px;
          color: #a0a0a0;
          font-size: 0.85rem;
        }
        .text-sm { font-size: 0.875rem; }
        .text-muted { color: #666; }
      `}</style>
    </div>
  );
}
