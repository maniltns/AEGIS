import { useState, useEffect } from 'react'
import {
    Shield,
    Search,
    Brain,
    Zap,
    Plus,
    Settings,
    GitBranch,
    RefreshCw
} from 'lucide-react'
import api from '../api/client'

// Icon mapping for node IDs
const ICON_MAP = {
    guardrails: Shield,
    enrichment: Search,
    triage_llm: Brain,
    executor: Zap
}

function Agents() {
    const [nodes, setNodes] = useState([])
    const [loading, setLoading] = useState(true)
    const [showAddModal, setShowAddModal] = useState(false)
    const [newNode, setNewNode] = useState({ name: '', role: '', description: '' })
    const [saving, setSaving] = useState(false)

    // Fetch nodes from API
    const fetchNodes = async () => {
        try {
            setLoading(true)
            const response = await api.getAgents()
            const agents = response.agents || []
            // Add icon component to each node
            const nodesWithIcons = agents.map(node => ({
                ...node,
                icon: ICON_MAP[node.id] || Settings
            }))
            setNodes(nodesWithIcons)
        } catch (err) {
            console.error('Failed to fetch nodes:', err)
            // Fallback to demo data
            setNodes([
                { id: 'guardrails', name: 'GUARDRAILS', role: 'Security & Dedup', description: 'PII scrubbing + Vector dedup', icon: Shield, color: '#6366f1', active: true, order: 1 },
                { id: 'enrichment', name: 'ENRICHMENT', role: 'Context Gathering', description: 'KB search, user info, CMDB', icon: Search, color: '#22c55e', active: true, order: 2 },
                { id: 'triage_llm', name: 'TRIAGE_LLM', role: 'AI Classification', description: 'Single LLM call for triage', icon: Brain, color: '#f59e0b', active: true, order: 3 },
                { id: 'executor', name: 'EXECUTOR', role: 'Action Engine', description: 'ServiceNow update, Teams', icon: Zap, color: '#8b5cf6', active: true, order: 4 },
            ])
        } finally {
            setLoading(false)
        }
    }

    useEffect(() => {
        fetchNodes()
    }, [])

    const toggleNode = async (id) => {
        const node = nodes.find(n => n.id === id)
        if (!node) return

        const newState = !node.active

        // Optimistic update
        setNodes(nodes.map(n =>
            n.id === id ? { ...n, active: newState } : n
        ))

        try {
            await api.toggleAgent(id, newState)
        } catch (err) {
            // Revert on error
            setNodes(nodes.map(n =>
                n.id === id ? { ...n, active: !newState } : n
            ))
            console.error('Failed to toggle node:', err)
        }
    }

    const handleAddNode = async () => {
        if (!newNode.name || !newNode.role) return

        setSaving(true)
        try {
            const response = await api.addAgent({
                name: newNode.name,
                role: newNode.role,
                description: newNode.description
            })

            if (response.success) {
                // Add the new node with icon
                const addedNode = {
                    ...response.agent,
                    icon: Settings
                }
                setNodes([...nodes, addedNode])
                setNewNode({ name: '', role: '', description: '' })
                setShowAddModal(false)
            }
        } catch (err) {
            console.error('Failed to add node:', err)
            alert('Failed to add node. Please try again.')
        } finally {
            setSaving(false)
        }
    }

    if (loading) {
        return (
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', height: '50vh' }}>
                <RefreshCw size={32} className="spin" style={{ color: 'var(--primary)' }} />
            </div>
        )
    }

    return (
        <div>
            <div className="page-header">
                <div>
                    <h1 className="page-title">Pipeline Nodes</h1>
                    <p className="page-subtitle">LangGraph v2.1 triage pipeline configuration</p>
                </div>
                <div style={{ display: 'flex', gap: '12px' }}>
                    <button className="btn btn-secondary" onClick={fetchNodes}>
                        <RefreshCw size={16} />
                        Refresh
                    </button>
                    <button className="btn btn-primary" onClick={() => setShowAddModal(true)}>
                        <Plus size={18} />
                        Add Node
                    </button>
                </div>
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
                                background: `${node.color || '#6366f1'}15`,
                                border: `2px solid ${node.active ? (node.color || '#6366f1') : '#666'}`,
                                borderRadius: '12px',
                                padding: '12px 20px',
                                textAlign: 'center',
                                opacity: node.active ? 1 : 0.5
                            }}>
                                <node.icon size={20} color={node.color || '#6366f1'} />
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
                                style={{ background: `${node.color || '#6366f1'}20`, color: node.color || '#6366f1' }}
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
                            <button
                                className="btn btn-primary"
                                style={{ flex: 1 }}
                                onClick={handleAddNode}
                                disabled={saving || !newNode.name || !newNode.role}
                            >
                                {saving ? 'Adding...' : 'Add Node'}
                            </button>
                        </div>
                    </div>
                </div>
            )}

            <style>{`
                .spin {
                    animation: spin 1s linear infinite;
                }
                @keyframes spin {
                    from { transform: rotate(0deg); }
                    to { transform: rotate(360deg); }
                }
            `}</style>
        </div>
    )
}

export default Agents
