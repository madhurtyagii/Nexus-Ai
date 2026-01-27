import { useState } from 'react';

const API_BASE = 'http://localhost:8000';

export default function TaskFeedback({ taskId, token, onFeedbackSubmitted }) {
    const [rating, setRating] = useState(0);
    const [hoverRating, setHoverRating] = useState(0);
    const [feedback, setFeedback] = useState('');
    const [aspects, setAspects] = useState({
        accuracy: null,
        speed: null,
        detail: null,
        creativity: null
    });
    const [loading, setLoading] = useState(false);
    const [submitted, setSubmitted] = useState(false);

    const handleSubmit = async () => {
        if (rating === 0) return;

        setLoading(true);

        try {
            const response = await fetch(`${API_BASE}/tasks/${taskId}/feedback`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    Authorization: `Bearer ${token}`
                },
                body: JSON.stringify({
                    rating,
                    feedback: feedback || null,
                    aspects: Object.fromEntries(
                        Object.entries(aspects).filter(([_, v]) => v !== null)
                    )
                })
            });

            if (response.ok) {
                setSubmitted(true);
                onFeedbackSubmitted?.();
            }
        } catch (error) {
            console.error('Failed to submit feedback:', error);
        } finally {
            setLoading(false);
        }
    };

    const toggleAspect = (aspect) => {
        setAspects(prev => ({
            ...prev,
            [aspect]: prev[aspect] === null ? true : prev[aspect] === true ? false : null
        }));
    };

    if (submitted) {
        return (
            <div className="feedback-success">
                <div className="success-icon">✨</div>
                <h4>Thank you for your feedback!</h4>
                <p>This helps us learn your preferences</p>

                <style jsx>{`
          .feedback-success {
            text-align: center;
            padding: 24px;
            background: rgba(16, 185, 129, 0.1);
            border-radius: 12px;
            color: #10b981;
          }
          .success-icon {
            font-size: 2rem;
            margin-bottom: 8px;
          }
          .feedback-success h4 {
            margin: 0 0 4px 0;
          }
          .feedback-success p {
            margin: 0;
            font-size: 0.85rem;
            opacity: 0.8;
          }
        `}</style>
            </div>
        );
    }

    return (
        <div className="task-feedback">
            <h4>📝 Rate this result</h4>

            <div className="rating-section">
                <div className="star-rating">
                    {[1, 2, 3, 4, 5].map((star) => (
                        <button
                            key={star}
                            className={`star-btn ${(hoverRating || rating) >= star ? 'active' : ''}`}
                            onMouseEnter={() => setHoverRating(star)}
                            onMouseLeave={() => setHoverRating(0)}
                            onClick={() => setRating(star)}
                        >
                            ★
                        </button>
                    ))}
                </div>
                <span className="rating-text">
                    {rating === 1 && 'Poor'}
                    {rating === 2 && 'Fair'}
                    {rating === 3 && 'Good'}
                    {rating === 4 && 'Very Good'}
                    {rating === 5 && 'Excellent'}
                </span>
            </div>

            <div className="aspects-section">
                <p className="aspects-label">What did you think about:</p>
                <div className="aspects-grid">
                    {Object.entries(aspects).map(([aspect, value]) => (
                        <button
                            key={aspect}
                            className={`aspect-btn ${value === true ? 'liked' : value === false ? 'disliked' : ''}`}
                            onClick={() => toggleAspect(aspect)}
                        >
                            <span className="aspect-icon">
                                {value === true ? '👍' : value === false ? '👎' : '•'}
                            </span>
                            <span className="aspect-name">{aspect}</span>
                        </button>
                    ))}
                </div>
            </div>

            <div className="feedback-section">
                <textarea
                    className="feedback-input"
                    placeholder="Any additional feedback? (optional)"
                    value={feedback}
                    onChange={(e) => setFeedback(e.target.value)}
                    rows={3}
                />
            </div>

            <button
                className="submit-btn"
                onClick={handleSubmit}
                disabled={rating === 0 || loading}
            >
                {loading ? 'Submitting...' : 'Submit Feedback'}
            </button>

            <style jsx>{`
        .task-feedback {
          background: rgba(255, 255, 255, 0.05);
          border: 1px solid rgba(255, 255, 255, 0.1);
          border-radius: 12px;
          padding: 20px;
          margin-top: 16px;
        }
        .task-feedback h4 {
          margin: 0 0 16px 0;
          color: #fff;
        }
        .rating-section {
          display: flex;
          align-items: center;
          gap: 16px;
          margin-bottom: 20px;
        }
        .star-rating {
          display: flex;
          gap: 4px;
        }
        .star-btn {
          background: none;
          border: none;
          font-size: 1.75rem;
          color: #444;
          cursor: pointer;
          transition: all 0.2s ease;
          padding: 0;
        }
        .star-btn:hover, .star-btn.active {
          color: #fbbf24;
          transform: scale(1.1);
        }
        .rating-text {
          color: #fbbf24;
          font-weight: 500;
        }
        .aspects-section {
          margin-bottom: 16px;
        }
        .aspects-label {
          color: #888;
          font-size: 0.85rem;
          margin: 0 0 8px 0;
        }
        .aspects-grid {
          display: flex;
          flex-wrap: wrap;
          gap: 8px;
        }
        .aspect-btn {
          display: flex;
          align-items: center;
          gap: 6px;
          padding: 8px 14px;
          background: rgba(255, 255, 255, 0.05);
          border: 1px solid rgba(255, 255, 255, 0.1);
          border-radius: 20px;
          color: #a0a0a0;
          cursor: pointer;
          transition: all 0.2s ease;
          text-transform: capitalize;
        }
        .aspect-btn:hover {
          background: rgba(255, 255, 255, 0.1);
        }
        .aspect-btn.liked {
          background: rgba(16, 185, 129, 0.1);
          border-color: #10b981;
          color: #10b981;
        }
        .aspect-btn.disliked {
          background: rgba(239, 68, 68, 0.1);
          border-color: #ef4444;
          color: #ef4444;
        }
        .feedback-section {
          margin-bottom: 16px;
        }
        .feedback-input {
          width: 100%;
          padding: 12px;
          background: rgba(255, 255, 255, 0.05);
          border: 1px solid rgba(255, 255, 255, 0.1);
          border-radius: 8px;
          color: #fff;
          font-family: inherit;
          font-size: 0.9rem;
          resize: vertical;
        }
        .feedback-input:focus {
          outline: none;
          border-color: #667eea;
        }
        .feedback-input::placeholder {
          color: #666;
        }
        .submit-btn {
          width: 100%;
          padding: 12px;
          background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
          border: none;
          border-radius: 8px;
          color: white;
          font-weight: 500;
          cursor: pointer;
          transition: all 0.2s ease;
        }
        .submit-btn:hover:not(:disabled) {
          transform: translateY(-2px);
          box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
        }
        .submit-btn:disabled {
          opacity: 0.5;
          cursor: not-allowed;
        }
      `}</style>
        </div>
    );
}
