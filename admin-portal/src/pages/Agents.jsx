import { useState } from 'react'
import {
    Shield,
    Search,
    Crosshair,
    RotateCcw,
    Gavel,
    Bell,
    FileText,
    ArrowRightLeft,
    Wrench,
    Plus,
    Power,
    Settings
} from 'lucide-react'

const AGENTS = [
    {
        id: 'guardian',
        name: 'GUARDIAN',
        role: 'Storm Shield',
        description: 'Duplicate detection & storm suppression',
        icon: Shield,
        color: '#6366f1',
        active: true
    },
    {
        id: 'scout',
        name: 'SCOUT',
        role: 'Enrichment',
        description: 'Context gathering from CMDB, users, KB',
        icon: Search,
        color: '#8b5cf6',
        active: true
    },
    {
        id: 'sherlock',
        name: 'SHERLOCK',
        role: 'AI Triage',
        description: 'Classification, RCA, KB matching',
        icon: Crosshair,
        color: '#22c55e',
        active: true
    },
    {
        id: 'router',
        name: 'ROUTER',
        role: 'Assignment',
        description: 'Team workload & skills matching',
        icon: RotateCcw,
        color: '#f59e0b',
        active: true
    },
    {
        id: 'arbiter',
        name: 'ARBITER',
        role: 'Governance',
        description: 'Kill switch, thresholds, approvals',
        icon: Gavel,
        color: '#ef4444',
        active: true
    },
    {
        id: 'herald',
        name: 'HERALD',
        role: 'Notifications',
        description: 'Teams cards, swarm channels',
        icon: Bell,
        color: '#3b82f6',
        active: true
    },
    {
        id: 'scribe',
        name: 'SCRIBE',
        role: 'Audit',
        description: 'Decision logging, compliance',
        icon: FileText,
        color: '#ec4899',
        active: true
    },
    {
        id: 'bridge',
        name: 'BRIDGE',
        role: 'Case→Incident',
        description: 'Case analysis & conversion',
        icon: ArrowRightLeft,
        color: '#14b8a6',
        active: true
    },
    {
        id: 'janitor',
        name: 'JANITOR',
        role: 'Remediation',
        description: 'Standard changes, rollback',
        icon: Wrench,
        color: '#a855f7',
        active: true
    },
]

function Agents() {
    const [agents, setAgents] = useState(AGENTS)
    const [showAddModal, setShowAddModal] = useState(false)
    const [newAgent, setNewAgent] = useState({ name: '', role: '', description: '' })

    const toggleAgent = (id) => {
        setAgents(agents.map(agent =>
            agent.id === id ? { ...agent, active: !agent.active } : agent
        ))
    }

    const handleAddAgent = () => {
        if (newAgent.name && newAgent.role) {
            setAgents([...agents, {
                id: newAgent.name.toLowerCase(),
                name: newAgent.name.toUpperCase(),
                role: newAgent.role,
                description: newAgent.description || 'Custom agent',
                icon: Settings,
                color: '#6366f1',
                active: true
            }])
            setNewAgent({ name: '', role: '', description: '' })
            setShowAddModal(false)
        }
    }

    return (
        <div>
            <div className="page-header">
                <div>
                    <h1 className="page-title">Agents</h1>
                    <p className="page-subtitle">Manage your AI agent swarm</p>
                </div>
                <button className="btn btn-primary" onClick={() => setShowAddModal(true)}>
                    <Plus size={18} />
                    Add Agent
                </button>
            </div>

            <div className="agent-grid">
                {agents.map((agent) => (
                    <div key={agent.id} className="agent-card">
                        <div className="agent-card-header">
                            <div
                                className="agent-icon"
                                style={{ background: `${agent.color}20`, color: agent.color }}
                            >
                                <agent.icon size={24} />
                            </div>
                            <div className="agent-info">
                                <div className="agent-name">{agent.name}</div>
                                <div className="agent-role">{agent.role}</div>
                            </div>
                        </div>
                        <p style={{ fontSize: '14px', color: 'var(--text-secondary)', marginTop: '12px' }}>
                            {agent.description}
                        </p>
                        <div className="agent-status">
                            <div
                                className={`toggle ${agent.active ? 'active' : ''}`}
                                onClick={() => toggleAgent(agent.id)}
                            />
                            <span className="status-text">
                                {agent.active ? 'Active' : 'Inactive'}
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
                            <h3 className="modal-title">Add New Agent</h3>
                            <button className="modal-close" onClick={() => setShowAddModal(false)}>✕</button>
                        </div>
                        <div className="form-group">
                            <label className="form-label">Agent Name</label>
                            <input
                                className="input"
                                placeholder="e.g. ANALYZER"
                                value={newAgent.name}
                                onChange={e => setNewAgent({ ...newAgent, name: e.target.value })}
                            />
                        </div>
                        <div className="form-group">
                            <label className="form-label">Role</label>
                            <input
                                className="input"
                                placeholder="e.g. Data Analysis"
                                value={newAgent.role}
                                onChange={e => setNewAgent({ ...newAgent, role: e.target.value })}
                            />
                        </div>
                        <div className="form-group">
                            <label className="form-label">Description</label>
                            <input
                                className="input"
                                placeholder="What does this agent do?"
                                value={newAgent.description}
                                onChange={e => setNewAgent({ ...newAgent, description: e.target.value })}
                            />
                        </div>
                        <div style={{ display: 'flex', gap: '12px', marginTop: '24px' }}>
                            <button className="btn btn-secondary" style={{ flex: 1 }} onClick={() => setShowAddModal(false)}>
                                Cancel
                            </button>
                            <button className="btn btn-primary" style={{ flex: 1 }} onClick={handleAddAgent}>
                                Add Agent
                            </button>
                        </div>
                    </div>
                </div>
            )}
        </div>
    )
}

export default Agents
