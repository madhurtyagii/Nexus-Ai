import { useState, useEffect } from 'react';

const API_BASE = 'http://localhost:8000';

/**
 * PreferencesPanel Component
 * 
 * Displays user preferences learned by the AI, such as communication tone, 
 * detail level, and preferred agents.
 * 
 * @component
 * @param {Object} props - Component props.
 * @param {string} props.token - JWT authentication token.
 */
export default function PreferencesPanel({ token }) {
  const [preferences, setPreferences] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchPreferences();
  }, []);

  const fetchPreferences = async () => {
    try {
      const response = await fetch(`${API_BASE}/memory/preferences`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      if (response.ok) {
        const data = await response.json();
        setPreferences(data.preferences || {});
      }
    } catch (error) {
      console.error('Failed to fetch preferences:', error);
    } finally {
      setLoading(false);
    }
  };

  const preferenceCategories = [
    {
      id: 'tone',
      label: '🎭 Communication Tone',
      description: 'How you prefer responses to be written',
      options: ['formal', 'professional', 'casual', 'friendly']
    },
    {
      id: 'detail_level',
      label: '📊 Detail Level',
      description: 'How much detail you prefer in responses',
      options: ['concise', 'moderate', 'detailed', 'comprehensive']
    },
    {
      id: 'content_length',
      label: '📏 Content Length',
      description: 'Preferred length of generated content',
      options: ['short', 'medium', 'long']
    },
    {
      id: 'response_speed',
      label: '⚡ Response Priority',
      description: 'Speed vs thoroughness preference',
      options: ['quick', 'balanced', 'thorough']
    }
  ];

  if (loading) {
    return (
      <div className="loading-state">
        <div className="spinner"></div>
        <p>Loading preferences...</p>
      </div>
    );
  }

  return (
    <div className="preferences-panel">
      <div className="preferences-header">
        <h3>Learned Preferences</h3>
        <p className="subtitle">These preferences are learned from your interaction patterns</p>
      </div>

      <div className="preferences-grid">
        {preferenceCategories.map(category => {
          const currentValue = preferences?.[category.id] || 'Not learned yet';

          return (
            <div key={category.id} className="preference-card">
              <div className="preference-label">{category.label}</div>
              <div className="preference-description">{category.description}</div>

              <div className="preference-value">
                <span className="current-value">{currentValue}</span>
              </div>

              <div className="preference-options">
                {category.options.map(option => (
                  <span
                    key={option}
                    className={`option-chip ${currentValue === option ? 'active' : ''}`}
                  >
                    {option}
                  </span>
                ))}
              </div>
            </div>
          );
        })}
      </div>

      {preferences?.preferred_agents?.length > 0 && (
        <div className="preferred-agents-section">
          <h4>🤖 Preferred Agents</h4>
          <div className="agent-chips">
            {preferences.preferred_agents.map(agent => (
              <span key={agent} className="agent-chip">{agent}</span>
            ))}
          </div>
        </div>
      )}

      {preferences?.avg_satisfaction && (
        <div className="satisfaction-section">
          <h4>⭐ Average Satisfaction</h4>
          <div className="satisfaction-score">
            {[1, 2, 3, 4, 5].map(star => (
              <span
                key={star}
                className={`star ${star <= preferences.avg_satisfaction ? 'filled' : ''}`}
              >
                ★
              </span>
            ))}
            <span className="score-text">
              {preferences.avg_satisfaction?.toFixed(1)} / 5
            </span>
          </div>
        </div>
      )}

      <div className="preferences-footer">
        <p className="help-text">
          💡 Tip: Provide feedback on tasks to help improve these preferences
        </p>
      </div>

      <style jsx>{`
        .preferences-panel {
          padding: 8px;
        }
        .preferences-header {
          margin-bottom: 24px;
        }
        .preferences-header h3 {
          margin: 0 0 8px 0;
          color: #fff;
        }
        .subtitle {
          color: #888;
          margin: 0;
          font-size: 0.9rem;
        }
        .preferences-grid {
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
          gap: 16px;
          margin-bottom: 24px;
        }
        .preference-card {
          background: rgba(255, 255, 255, 0.05);
          border: 1px solid rgba(255, 255, 255, 0.1);
          border-radius: 12px;
          padding: 16px;
        }
        .preference-label {
          font-weight: 600;
          color: #fff;
          margin-bottom: 4px;
        }
        .preference-description {
          font-size: 0.8rem;
          color: #888;
          margin-bottom: 12px;
        }
        .preference-value {
          margin-bottom: 12px;
        }
        .current-value {
          background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
          -webkit-background-clip: text;
          -webkit-text-fill-color: transparent;
          background-clip: text;
          font-weight: 600;
          font-size: 1.1rem;
          text-transform: capitalize;
        }
        .preference-options {
          display: flex;
          flex-wrap: wrap;
          gap: 8px;
        }
        .option-chip {
          padding: 4px 10px;
          border-radius: 20px;
          font-size: 0.75rem;
          background: rgba(255, 255, 255, 0.05);
          color: #888;
          text-transform: capitalize;
        }
        .option-chip.active {
          background: rgba(102, 126, 234, 0.2);
          color: #667eea;
        }
        .preferred-agents-section, .satisfaction-section {
          margin-top: 24px;
          padding: 16px;
          background: rgba(255, 255, 255, 0.03);
          border-radius: 12px;
        }
        .preferred-agents-section h4, .satisfaction-section h4 {
          margin: 0 0 12px 0;
          color: #fff;
        }
        .agent-chips {
          display: flex;
          flex-wrap: wrap;
          gap: 8px;
        }
        .agent-chip {
          background: rgba(16, 185, 129, 0.2);
          color: #10b981;
          padding: 6px 14px;
          border-radius: 20px;
          font-size: 0.85rem;
        }
        .satisfaction-score {
          display: flex;
          align-items: center;
          gap: 4px;
        }
        .star {
          font-size: 1.5rem;
          color: #444;
        }
        .star.filled {
          color: #fbbf24;
        }
        .score-text {
          margin-left: 12px;
          color: #888;
        }
        .preferences-footer {
          margin-top: 24px;
          text-align: center;
        }
        .help-text {
          color: #666;
          font-size: 0.85rem;
          margin: 0;
        }
      `}</style>
    </div>
  );
}
