import { useState } from 'react'
import {
    Shield,
    Search,
    Brain,
    Zap,
    Plus,
    Settings,
    GitBranch
} from 'lucide-react'

const PIPELINE_NODES = [
    {
        id: 'guardrails',
        name: 'GUARDRAILS',
        role: 'Security & Dedup',
        description: 'PII scrubbing (Presidio) + Vector duplicate detection (90% similarity)',
        icon: Shield,
        color: '#6366f1',
        active: true,
        order: 1
    },
    {
        id: 'enrichment',
        name: 'ENRICHMENT',
        role: 'Context Gathering',
        description: 'KB article search, user info, CMDB CI details',
        icon: Search,
        color: '#22c55e',
        active: true,
        order: 2
    },
    {
        id: 'triage_llm',
        name: 'TRIAGE LLM',
        role: 'AI Classification',
        description: 'Single LLM call for classification, priority, routing, action',
        icon: Brain,
        color: '#f59e0b',
        active: true,
        order: 3
    },
    {
        id: 'executor',
        name: 'EXECUTOR',
        role: 'Action Engine',
        description: 'ServiceNow update, Teams notification, SSM auto-heal',
        icon: Zap,
        color: '#8b5cf6',
        active: true,
        order: 4
    },
]

function Agents() {
    const [nodes, setNodes] = useState(PIPELINE_NODES)
    const [showAddModal, setShowAddModal] = useState(false)
    const [newNode, setNewNode] = useState({ name: '', role: '', description: '' })

    const toggleNode = (id) => {
        setNodes(nodes.map(node =>
            node.id === id ? { ...node, active: !node.active } : node
        ))
    }

    const handleAddNode = () => {
        if (newNode.name && newNode.role) {
            setNodes([...nodes, {
                id: newNode.name.toLowerCase().replace(/\s/g, '_'),
                name: newNode.name.toUpperCase(),
                role: newNode.role,
                description: newNode.description || 'Custom pipeline node',
                icon: Settings,
                color: '#6366f1',
                active: true,
                order: nodes.length + 1
            }])
            setNewNode({ name: '', role: '', description: '' })
            setShowAddModal(false)
        }
    }

    return (
        <div>
            <div className="page-header">
                <div>
                    <h1 className="page-title">Pipeline Nodes</h1>
                    <p className="page-subtitle">LangGraph v2.1 triage pipeline configuration</p>
                </div>
                <button className="btn btn-primary" onClick={() => setShowAddModal(true)}>
                    <Plus size={18} />
                    Add Node
                </button>
            </div>

            {/* Pipeline Flow Diagram */}
            <div className="card" style={{ marginBottom: '24px', padding: '20px' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '16px' }}>
                    <GitBranch size={20} color="var(--accent-primary)" />
                    <h3 style={{ margin: 0, fontSize: '16px' }}>Pipeline Flow</h3>
                </div>
                <div style={{
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    gap: '12px',
                    flexWrap: 'wrap'
                }}>
                    {nodes.sort((a, b) => a.order - b.order).map((node, index) => (
                        <div key={node.id} style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                            <div style={{
                                background: `${node.color}15`,
                                border: `2px solid ${node.active ? node.color : '#666'}`,
                                borderRadius: '12px',
                                padding: '12px 20px',
                                textAlign: 'center',
                                opacity: node.active ? 1 : 0.5
                            }}>
                                <node.icon size={20} color={node.color} />
                                <div style={{ fontSize: '12px', fontWeight: 600, marginTop: '4px' }}>
                                    {node.name}
                                </div>
                            </div>
                            {index < nodes.length - 1 && (
                                <span style={{ color: 'var(--text-muted)', fontSize: '20px' }}>→</span>
                            )}
                        </div>
                    ))}
                </div>
            </div>

            <div className="agent-grid">
                {nodes.map((node) => (
                    <div key={node.id} className="agent-card">
                        <div className="agent-card-header">
                            <div
                                className="agent-icon"
                                style={{ background: `${node.color}20`, color: node.color }}
                            >
                                <node.icon size={24} />
                            </div>
                            <div className="agent-info">
                                <div className="agent-name">{node.name}</div>
                                <div className="agent-role">{node.role}</div>
                            </div>
                        </div>
                        <p style={{ fontSize: '14px', color: 'var(--text-secondary)', marginTop: '12px' }}>
                            {node.description}
                        </p>
                        <div style={{
                            fontSize: '12px',
                            color: 'var(--text-muted)',
                            marginTop: '8px',
                            padding: '8px 12px',
                            background: 'var(--bg-tertiary)',
                            borderRadius: '6px'
                        }}>
                            Order: {node.order} of {nodes.length}
                        </div>
                        <div className="agent-status">
                            <div
                                className={`toggle ${node.active ? 'active' : ''}`}
                                onClick={() => toggleNode(node.id)}
                            />
                            <span className="status-text">
                                {node.active ? 'Active' : 'Bypassed'}
                            </span>
                            <button
                                className="btn btn-secondary"
                                style={{ marginLeft: 'auto', padding: '6px 12px', fontSize: '12px' }}
                            >
                                Configure
                            </button>
                        </div>
                    </div>
                ))}
            </div>

            {showAddModal && (
                <div className="modal-overlay" onClick={() => setShowAddModal(false)}>
                    <div className="modal" onClick={e => e.stopPropagation()}>
                        <div className="modal-header">
                            <h3 className="modal-title">Add New Pipeline Node</h3>
                            <button className="modal-close" onClick={() => setShowAddModal(false)}>✕</button>
                        </div>
                        <div className="form-group">
                            <label className="form-label">Node Name</label>
                            <input
                                className="input"
                                placeholder="e.g. VALIDATOR"
                                value={newNode.name}
                                onChange={e => setNewNode({ ...newNode, name: e.target.value })}
                            />
                        </div>
                        <div className="form-group">
                            <label className="form-label">Role</label>
                            <input
                                className="input"
                                placeholder="e.g. Output Validation"
                                value={newNode.role}
                                onChange={e => setNewNode({ ...newNode, role: e.target.value })}
                            />
                        </div>
                        <div className="form-group">
                            <label className="form-label">Description</label>
                            <input
                                className="input"
                                placeholder="What does this node do?"
                                value={newNode.description}
                                onChange={e => setNewNode({ ...newNode, description: e.target.value })}
                            />
                        </div>
                        <div style={{ display: 'flex', gap: '12px', marginTop: '24px' }}>
                            <button className="btn btn-secondary" style={{ flex: 1 }} onClick={() => setShowAddModal(false)}>
                                Cancel
                            </button>
                            <button className="btn btn-primary" style={{ flex: 1 }} onClick={handleAddNode}>
                                Add Node
                            </button>
                        </div>
                    </div>
                </div>
            )}
        </div>
    )
}

export default Agents
