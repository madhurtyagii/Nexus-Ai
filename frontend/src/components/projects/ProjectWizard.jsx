import { useState } from 'react';
import api from '../../services/api';
import './ProjectWizard.css';

/**
 * ProjectWizard - Multi-step project creation wizard
 * Guides users through creating complex AI projects
 */
function ProjectWizard({ onComplete, onCancel }) {
    const [step, setStep] = useState(1);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);

    const [formData, setFormData] = useState({
        name: '',
        description: '',
        objectives: [],
        complexity: 'auto',
        preferredAgents: [],
        addQA: true,
        timeline: 'normal'
    });

    const totalSteps = 4;

    const handleNext = () => {
        if (step < totalSteps) setStep(step + 1);
    };

    const handleBack = () => {
        if (step > 1) setStep(step - 1);
    };

    const handleSubmit = async () => {
        setLoading(true);
        setError(null);

        try {
            const response = await api.post('/projects/', {
                name: formData.name,
                description: buildDescription(),
                complexity: formData.complexity
            });
            onComplete(response.data);
        } catch (err) {
            setError(err.response?.data?.detail || 'Failed to create project');
            setLoading(false);
        }
    };

    const buildDescription = () => {
        let desc = formData.description;
        if (formData.objectives.length > 0) {
            desc += '\n\nObjectives:\n' + formData.objectives.map(o => `- ${o}`).join('\n');
        }
        if (formData.preferredAgents.length > 0) {
            desc += '\n\nPreferred Agents: ' + formData.preferredAgents.join(', ');
        }
        return desc;
    };

    const updateField = (field, value) => {
        setFormData({ ...formData, [field]: value });
    };

    const addObjective = (objective) => {
        if (objective.trim() && !formData.objectives.includes(objective)) {
            updateField('objectives', [...formData.objectives, objective.trim()]);
        }
    };

    const removeObjective = (index) => {
        updateField('objectives', formData.objectives.filter((_, i) => i !== index));
    };

    const toggleAgent = (agent) => {
        const agents = formData.preferredAgents.includes(agent)
            ? formData.preferredAgents.filter(a => a !== agent)
            : [...formData.preferredAgents, agent];
        updateField('preferredAgents', agents);
    };

    return (
        <div className="wizard-overlay" onClick={onCancel}>
            <div className="wizard-container" onClick={(e) => e.stopPropagation()}>
                {/* Progress Bar */}
                <div className="wizard-progress">
                    {[1, 2, 3, 4].map((s) => (
                        <div
                            key={s}
                            className={`progress-step ${s <= step ? 'active' : ''} ${s < step ? 'completed' : ''}`}
                        >
                            <div className="step-circle">
                                {s < step ? '✓' : s}
                            </div>
                            <span className="step-label">
                                {s === 1 && 'Basics'}
                                {s === 2 && 'Objectives'}
                                {s === 3 && 'Agents'}
                                {s === 4 && 'Review'}
                            </span>
                        </div>
                    ))}
                    <div className="progress-line">
                        <div
                            className="progress-fill"
                            style={{ width: `${((step - 1) / (totalSteps - 1)) * 100}%` }}
                        />
                    </div>
                </div>

                {/* Step Content */}
                <div className="wizard-content">
                    {step === 1 && (
                        <div className="step-content">
                            <h2>🚀 Project Basics</h2>
                            <p>What would you like to build?</p>

                            <div className="form-group">
                                <label>Project Name</label>
                                <input
                                    type="text"
                                    value={formData.name}
                                    onChange={(e) => updateField('name', e.target.value)}
                                    placeholder="e.g., AI-Powered Blog Platform"
                                />
                            </div>

                            <div className="form-group">
                                <label>Description</label>
                                <textarea
                                    value={formData.description}
                                    onChange={(e) => updateField('description', e.target.value)}
                                    placeholder="Describe your project in detail. The more specific, the better the AI planning will be..."
                                    rows={5}
                                />
                            </div>

                            <div className="form-group">
                                <label>Complexity</label>
                                <div className="option-cards">
                                    {[
                                        { value: 'auto', icon: '🤖', label: 'Auto-detect', desc: 'AI determines complexity' },
                                        { value: 'low', icon: '🟢', label: 'Simple', desc: '1-2 tasks, quick execution' },
                                        { value: 'medium', icon: '🟡', label: 'Medium', desc: 'Multiple phases' },
                                        { value: 'high', icon: '🔴', label: 'Complex', desc: 'Full workflow with QA' }
                                    ].map((opt) => (
                                        <button
                                            key={opt.value}
                                            type="button"
                                            className={`option-card ${formData.complexity === opt.value ? 'selected' : ''}`}
                                            onClick={() => updateField('complexity', opt.value)}
                                        >
                                            <span className="option-icon">{opt.icon}</span>
                                            <span className="option-label">{opt.label}</span>
                                            <span className="option-desc">{opt.desc}</span>
                                        </button>
                                    ))}
                                </div>
                            </div>
                        </div>
                    )}

                    {step === 2 && (
                        <div className="step-content">
                            <h2>🎯 Project Objectives</h2>
                            <p>What are the key goals for this project?</p>

                            <div className="objectives-input">
                                <input
                                    type="text"
                                    placeholder="Add an objective and press Enter..."
                                    onKeyPress={(e) => {
                                        if (e.key === 'Enter') {
                                            addObjective(e.target.value);
                                            e.target.value = '';
                                        }
                                    }}
                                />
                            </div>

                            <div className="objectives-list">
                                {formData.objectives.length === 0 ? (
                                    <p className="empty-text">No objectives added yet. Add some to help the AI understand your goals.</p>
                                ) : (
                                    formData.objectives.map((obj, i) => (
                                        <div key={i} className="objective-item">
                                            <span className="objective-icon">🎯</span>
                                            <span className="objective-text">{obj}</span>
                                            <button onClick={() => removeObjective(i)}>&times;</button>
                                        </div>
                                    ))
                                )}
                            </div>

                            <div className="suggested-objectives">
                                <h4>Suggested Objectives</h4>
                                <div className="suggestions">
                                    {['High quality content', 'Well-researched sources', 'Clean code', 'Comprehensive documentation', 'Data-driven insights'].map((sug) => (
                                        <button
                                            key={sug}
                                            className="suggestion-btn"
                                            onClick={() => addObjective(sug)}
                                            disabled={formData.objectives.includes(sug)}
                                        >
                                            + {sug}
                                        </button>
                                    ))}
                                </div>
                            </div>
                        </div>
                    )}

                    {step === 3 && (
                        <div className="step-content">
                            <h2>🤖 Preferred Agents</h2>
                            <p>Select which agents you'd like involved (optional)</p>

                            <div className="agents-grid">
                                {[
                                    { name: 'ResearchAgent', icon: '🔍', desc: 'Web research & information gathering' },
                                    { name: 'CodeAgent', icon: '💻', desc: 'Code generation & debugging' },
                                    { name: 'ContentAgent', icon: '✍️', desc: 'Writing blogs, docs, content' },
                                    { name: 'DataAgent', icon: '📊', desc: 'Data analysis & visualization' },
                                    { name: 'QAAgent', icon: '✅', desc: 'Quality assurance & validation' },
                                    { name: 'ManagerAgent', icon: '📋', desc: 'Project planning & coordination' }
                                ].map((agent) => (
                                    <div
                                        key={agent.name}
                                        className={`agent-card ${formData.preferredAgents.includes(agent.name) ? 'selected' : ''}`}
                                        onClick={() => toggleAgent(agent.name)}
                                    >
                                        <span className="agent-icon">{agent.icon}</span>
                                        <span className="agent-name">{agent.name}</span>
                                        <span className="agent-desc">{agent.desc}</span>
                                        {formData.preferredAgents.includes(agent.name) && (
                                            <span className="check-mark">✓</span>
                                        )}
                                    </div>
                                ))}
                            </div>

                            <p className="agents-hint">
                                💡 Leave empty to let the ManagerAgent automatically select the best team
                            </p>
                        </div>
                    )}

                    {step === 4 && (
                        <div className="step-content">
                            <h2>📋 Review & Create</h2>
                            <p>Review your project configuration</p>

                            <div className="review-section">
                                <h4>Project Details</h4>
                                <div className="review-item">
                                    <span className="review-label">Name:</span>
                                    <span className="review-value">{formData.name || 'Not specified'}</span>
                                </div>
                                <div className="review-item">
                                    <span className="review-label">Complexity:</span>
                                    <span className="review-value">{formData.complexity}</span>
                                </div>
                            </div>

                            <div className="review-section">
                                <h4>Description</h4>
                                <p className="review-description">{formData.description || 'No description'}</p>
                            </div>

                            {formData.objectives.length > 0 && (
                                <div className="review-section">
                                    <h4>Objectives ({formData.objectives.length})</h4>
                                    <ul className="review-list">
                                        {formData.objectives.map((obj, i) => (
                                            <li key={i}>🎯 {obj}</li>
                                        ))}
                                    </ul>
                                </div>
                            )}

                            {formData.preferredAgents.length > 0 && (
                                <div className="review-section">
                                    <h4>Selected Agents</h4>
                                    <div className="review-agents">
                                        {formData.preferredAgents.map((a) => (
                                            <span key={a} className="agent-tag">{a}</span>
                                        ))}
                                    </div>
                                </div>
                            )}

                            {error && <div className="error-message">{error}</div>}
                        </div>
                    )}
                </div>

                {/* Footer */}
                <div className="wizard-footer">
                    <button
                        className="btn-secondary"
                        onClick={step === 1 ? onCancel : handleBack}
                    >
                        {step === 1 ? 'Cancel' : '← Back'}
                    </button>

                    {step < totalSteps ? (
                        <button
                            className="btn-primary"
                            onClick={handleNext}
                            disabled={step === 1 && !formData.name.trim()}
                        >
                            Next →
                        </button>
                    ) : (
                        <button
                            className="btn-primary"
                            onClick={handleSubmit}
                            disabled={loading || !formData.name.trim()}
                        >
                            {loading ? (
                                <>
                                    <span className="mini-spinner"></span>
                                    Creating...
                                </>
                            ) : (
                                '🚀 Create Project'
                            )}
                        </button>
                    )}
                </div>
            </div>
        </div>
    );
}

export default ProjectWizard;
