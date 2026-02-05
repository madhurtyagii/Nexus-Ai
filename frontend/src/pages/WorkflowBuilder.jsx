/**
 * Nexus AI - Visual Workflow Builder
 * Drag-and-drop node-based workflow designer for agent orchestration
 */

import { useState, useCallback, useRef, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { agentsAPI, projectsAPI } from '../services/api';
import Navbar from '../components/layout/Navbar';
import Sidebar from '../components/layout/Sidebar';
import toast from 'react-hot-toast';

// Agent node colors
const agentColors = {
    'ResearchAgent': { bg: 'bg-blue-500/20', border: 'border-blue-500/50', text: 'text-blue-400' },
    'CodeAgent': { bg: 'bg-green-500/20', border: 'border-green-500/50', text: 'text-green-400' },
    'ContentAgent': { bg: 'bg-purple-500/20', border: 'border-purple-500/50', text: 'text-purple-400' },
    'DataAgent': { bg: 'bg-orange-500/20', border: 'border-orange-500/50', text: 'text-orange-400' },
    'QAAgent': { bg: 'bg-teal-500/20', border: 'border-teal-500/50', text: 'text-teal-400' },
    'MemoryAgent': { bg: 'bg-indigo-500/20', border: 'border-indigo-500/50', text: 'text-indigo-400' },
    'ManagerAgent': { bg: 'bg-yellow-500/20', border: 'border-yellow-500/50', text: 'text-yellow-400' },
};

const agentEmojis = {
    'ResearchAgent': '🔍',
    'CodeAgent': '💻',
    'ContentAgent': '✍️',
    'DataAgent': '📊',
    'QAAgent': '✅',
    'MemoryAgent': '🧠',
    'ManagerAgent': '📋',
};

export default function WorkflowBuilder() {
    const navigate = useNavigate();
    const canvasRef = useRef(null);
    const [agents, setAgents] = useState([]);
    const [nodes, setNodes] = useState([]);
    const [connections, setConnections] = useState([]);
    const [selectedNode, setSelectedNode] = useState(null);
    const [connecting, setConnecting] = useState(null);
    const [workflowName, setWorkflowName] = useState('New Workflow');
    const [dragging, setDragging] = useState(null);
    const [dragOffset, setDragOffset] = useState({ x: 0, y: 0 });

    useEffect(() => {
        loadAgents();
    }, []);

    const loadAgents = async () => {
        try {
            const response = await agentsAPI.list();
            setAgents(response.data);
        } catch (error) {
            console.error('Failed to load agents:', error);
        }
    };

    const handleDragStart = (agent, e) => {
        e.dataTransfer.setData('agent', JSON.stringify(agent));
    };

    const handleDrop = (e) => {
        e.preventDefault();
        const agentData = e.dataTransfer.getData('agent');
        if (!agentData) return;

        const agent = JSON.parse(agentData);
        const rect = canvasRef.current.getBoundingClientRect();
        const x = e.clientX - rect.left - 75;
        const y = e.clientY - rect.top - 40;

        const newNode = {
            id: `node-${Date.now()}`,
            agent: agent.name,
            x: Math.max(0, x),
            y: Math.max(0, y),
            config: { prompt: '' }
        };

        setNodes([...nodes, newNode]);
    };

    const handleDragOver = (e) => {
        e.preventDefault();
    };

    const handleNodeMouseDown = (node, e) => {
        if (e.target.classList.contains('node-handle')) return;

        const rect = e.currentTarget.getBoundingClientRect();
        setDragging(node.id);
        setDragOffset({
            x: e.clientX - rect.left,
            y: e.clientY - rect.top
        });
        setSelectedNode(node.id);
    };

    const handleMouseMove = (e) => {
        if (!dragging) return;

        const rect = canvasRef.current.getBoundingClientRect();
        const x = e.clientX - rect.left - dragOffset.x;
        const y = e.clientY - rect.top - dragOffset.y;

        setNodes(nodes.map(n =>
            n.id === dragging ? { ...n, x: Math.max(0, x), y: Math.max(0, y) } : n
        ));
    };

    const handleMouseUp = () => {
        setDragging(null);
    };

    const handleConnectStart = (nodeId) => {
        setConnecting(nodeId);
    };

    const handleConnectEnd = (nodeId) => {
        if (connecting && connecting !== nodeId) {
            // Check for duplicate
            const exists = connections.some(c => c.from === connecting && c.to === nodeId);
            if (!exists) {
                setConnections([...connections, { id: `conn-${Date.now()}`, from: connecting, to: nodeId }]);
            }
        }
        setConnecting(null);
    };

    const deleteNode = (nodeId) => {
        setNodes(nodes.filter(n => n.id !== nodeId));
        setConnections(connections.filter(c => c.from !== nodeId && c.to !== nodeId));
        setSelectedNode(null);
    };

    const updateNodeConfig = (nodeId, config) => {
        setNodes(nodes.map(n => n.id === nodeId ? { ...n, config: { ...n.config, ...config } } : n));
    };

    const saveWorkflow = async () => {
        try {
            // Create a project with the workflow definition
            const workflowData = {
                name: workflowName,
                description: `Visual workflow with ${nodes.length} agents`,
                workflow_definition: JSON.stringify({ nodes, connections })
            };
            const response = await projectsAPI.createProject(workflowData);
            toast.success('Workflow saved as project!');
            navigate(`/projects/${response.data.id}`);
        } catch (error) {
            toast.error('Failed to save workflow');
        }
    };

    const getNodeCenter = (node, isOutput = false) => {
        return {
            x: node.x + 75,
            y: isOutput ? node.y + 80 : node.y
        };
    };

    return (
        <div className="min-h-screen bg-dark-900">
            <Navbar />
            <div className="flex">
                <Sidebar />
                <main className="flex-1 p-6 lg:p-8">
                    {/* Header */}
                    <div className="mb-6 flex items-center justify-between">
                        <div>
                            <input
                                type="text"
                                value={workflowName}
                                onChange={(e) => setWorkflowName(e.target.value)}
                                className="text-2xl font-bold bg-transparent text-white border-none outline-none focus:border-b-2 focus:border-primary-500"
                            />
                            <p className="text-dark-400">Drag agents onto the canvas to build your workflow</p>
                        </div>
                        <div className="flex gap-3">
                            <button
                                onClick={() => { setNodes([]); setConnections([]); }}
                                className="px-4 py-2 bg-dark-700 hover:bg-dark-600 text-white rounded-lg transition-colors"
                            >
                                Clear
                            </button>
                            <button
                                onClick={saveWorkflow}
                                disabled={nodes.length === 0}
                                className="btn-primary disabled:opacity-50"
                            >
                                💾 Save Workflow
                            </button>
                        </div>
                    </div>

                    <div className="flex gap-6">
                        {/* Agent Palette */}
                        <div className="w-48 flex-shrink-0">
                            <div className="card sticky top-6">
                                <h3 className="text-sm font-medium text-dark-400 mb-3">AGENTS</h3>
                                <div className="space-y-2">
                                    {agents.map(agent => {
                                        const colors = agentColors[agent.name] || { bg: 'bg-gray-500/20', border: 'border-gray-500/50', text: 'text-gray-400' };
                                        return (
                                            <div
                                                key={agent.id}
                                                draggable
                                                onDragStart={(e) => handleDragStart(agent, e)}
                                                className={`p-3 rounded-lg ${colors.bg} border ${colors.border} cursor-grab active:cursor-grabbing hover:scale-105 transition-all`}
                                            >
                                                <div className="flex items-center gap-2">
                                                    <span>{agentEmojis[agent.name] || '🤖'}</span>
                                                    <span className={`text-sm font-medium ${colors.text}`}>
                                                        {agent.name.replace('Agent', '')}
                                                    </span>
                                                </div>
                                            </div>
                                        );
                                    })}
                                </div>
                            </div>
                        </div>

                        {/* Canvas */}
                        <div
                            ref={canvasRef}
                            onDrop={handleDrop}
                            onDragOver={handleDragOver}
                            onMouseMove={handleMouseMove}
                            onMouseUp={handleMouseUp}
                            onMouseLeave={handleMouseUp}
                            className="flex-1 h-[600px] bg-dark-800 rounded-2xl border border-dark-700 relative overflow-hidden"
                            style={{
                                backgroundImage: 'radial-gradient(circle, #374151 1px, transparent 1px)',
                                backgroundSize: '20px 20px'
                            }}
                        >
                            {/* Empty State */}
                            {nodes.length === 0 && (
                                <div className="absolute inset-0 flex items-center justify-center text-dark-500">
                                    <div className="text-center">
                                        <div className="text-4xl mb-2">🎯</div>
                                        <p>Drag agents here to start building</p>
                                    </div>
                                </div>
                            )}

                            {/* Connections SVG */}
                            <svg className="absolute inset-0 w-full h-full pointer-events-none">
                                {connections.map(conn => {
                                    const fromNode = nodes.find(n => n.id === conn.from);
                                    const toNode = nodes.find(n => n.id === conn.to);
                                    if (!fromNode || !toNode) return null;

                                    const from = getNodeCenter(fromNode, true);
                                    const to = getNodeCenter(toNode, false);

                                    return (
                                        <g key={conn.id}>
                                            <path
                                                d={`M ${from.x} ${from.y} C ${from.x} ${from.y + 50}, ${to.x} ${to.y - 50}, ${to.x} ${to.y}`}
                                                fill="none"
                                                stroke="url(#gradient)"
                                                strokeWidth="3"
                                                strokeDasharray="8,4"
                                            />
                                            <circle cx={to.x} cy={to.y} r="4" fill="#8b5cf6" />
                                        </g>
                                    );
                                })}
                                <defs>
                                    <linearGradient id="gradient" x1="0%" y1="0%" x2="100%" y2="100%">
                                        <stop offset="0%" stopColor="#8b5cf6" />
                                        <stop offset="100%" stopColor="#06b6d4" />
                                    </linearGradient>
                                </defs>
                            </svg>

                            {/* Nodes */}
                            {nodes.map(node => {
                                const colors = agentColors[node.agent] || { bg: 'bg-gray-500/20', border: 'border-gray-500/50', text: 'text-gray-400' };
                                return (
                                    <div
                                        key={node.id}
                                        onMouseDown={(e) => handleNodeMouseDown(node, e)}
                                        className={`absolute w-[150px] p-3 rounded-xl ${colors.bg} border-2 ${selectedNode === node.id ? 'border-primary-500' : colors.border
                                            } cursor-move shadow-lg transition-all`}
                                        style={{ left: node.x, top: node.y }}
                                    >
                                        {/* Input Handle */}
                                        <div
                                            className="node-handle absolute -top-2 left-1/2 transform -translate-x-1/2 w-4 h-4 bg-dark-600 border-2 border-dark-400 rounded-full cursor-pointer hover:bg-primary-500 hover:border-primary-500 transition-colors"
                                            onClick={() => handleConnectEnd(node.id)}
                                        />

                                        <div className="flex items-center gap-2 mb-2">
                                            <span className="text-lg">{agentEmojis[node.agent] || '🤖'}</span>
                                            <span className={`font-medium ${colors.text} text-sm truncate`}>
                                                {node.agent.replace('Agent', '')}
                                            </span>
                                            <button
                                                onClick={(e) => { e.stopPropagation(); deleteNode(node.id); }}
                                                className="ml-auto text-dark-500 hover:text-red-400 text-xs"
                                            >
                                                ✕
                                            </button>
                                        </div>

                                        {/* Output Handle */}
                                        <div
                                            className="node-handle absolute -bottom-2 left-1/2 transform -translate-x-1/2 w-4 h-4 bg-primary-500 border-2 border-primary-400 rounded-full cursor-pointer hover:scale-125 transition-transform"
                                            onClick={() => handleConnectStart(node.id)}
                                        />
                                    </div>
                                );
                            })}
                        </div>

                        {/* Node Config Panel */}
                        {selectedNode && (
                            <div className="w-64 flex-shrink-0">
                                <div className="card sticky top-6">
                                    <h3 className="text-sm font-medium text-dark-400 mb-3">NODE CONFIG</h3>
                                    {(() => {
                                        const node = nodes.find(n => n.id === selectedNode);
                                        if (!node) return null;
                                        const colors = agentColors[node.agent] || { text: 'text-gray-400' };
                                        return (
                                            <div className="space-y-4">
                                                <div className="flex items-center gap-2">
                                                    <span className="text-xl">{agentEmojis[node.agent] || '🤖'}</span>
                                                    <span className={`font-semibold ${colors.text}`}>{node.agent}</span>
                                                </div>
                                                <div>
                                                    <label className="block text-xs text-dark-400 mb-1">Custom Prompt</label>
                                                    <textarea
                                                        value={node.config.prompt || ''}
                                                        onChange={(e) => updateNodeConfig(node.id, { prompt: e.target.value })}
                                                        placeholder="Optional: Add specific instructions..."
                                                        rows={3}
                                                        className="w-full input-field text-sm"
                                                    />
                                                </div>
                                            </div>
                                        );
                                    })()}
                                </div>
                            </div>
                        )}
                    </div>
                </main>
            </div>
        </div>
    );
}
