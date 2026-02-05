import { useState, useEffect } from 'react'
import {
    Activity,
    AlertTriangle,
    CheckCircle,
    Clock,
    TrendingUp,
    Shield,
    Bot,
    Zap
} from 'lucide-react'

function Dashboard() {
    const [stats, setStats] = useState({
        processed_today: 0,
        blocked_today: 0,
        active_nodes: 4,
        success_rate: 94,
        approval_rate: 0
    })
    const [status, setStatus] = useState({
        operational: true,
        mode: 'assist',
        kill_switch_active: false
    })
    const [recentLogs, setRecentLogs] = useState([])
    const [showFeedback, setShowFeedback] = useState(false)
    const [feedbackDetails, setFeedbackDetails] = useState([])

    useEffect(() => {
        fetchStatus()
        fetchRecentLogs()
        const interval = setInterval(fetchStatus, 30000)
        return () => clearInterval(interval)
    }, [])

    useEffect(() => {
        if (showFeedback) {
            fetchFeedbackDetails()
        }
    }, [showFeedback])

    const fetchStatus = async () => {
        try {
            const response = await fetch('/api/status')
            if (response.ok) {
                const data = await response.json()
                setStatus(data)
                setStats(prev => ({
                    ...prev,
                    processed_today: data.stats?.processed_today || 0,
                    blocked_today: data.stats?.blocked_today || 0
                }))
            }
            // Fetch feedback stats
            const fbResponse = await fetch('/api/feedback/stats')
            if (fbResponse.ok) {
                const fbData = await fbResponse.json()
                setStats(prev => ({ ...prev, approval_rate: fbData.approval_rate || 0 }))
            }
        } catch (err) {
            // Demo data
            setStats({
                processed_today: 127,
                blocked_today: 12,
                active_nodes: 4,
                success_rate: 94,
                approval_rate: 85
            })
        }
    }

    const fetchFeedbackDetails = async () => {
        try {
            const response = await fetch('/api/feedback/details?limit=10')
            if (response.ok) {
                const data = await response.json()
                setFeedbackDetails(data.feedback || [])
            }
        } catch (err) {
            setFeedbackDetails([])
        }
    }

    const fetchRecentLogs = async () => {
        try {
            const response = await fetch('/api/admin/logs?limit=5')
            if (response.ok) {
                const data = await response.json()
                setRecentLogs(data.logs || [])
            }
        } catch (err) {
            // Demo data
            setRecentLogs([
                { timestamp: new Date().toISOString(), agent: 'TRIAGE_LLM', incident: 'INC0012345', action: 'Classified (94%)' },
                { timestamp: new Date(Date.now() - 60000).toISOString(), agent: 'GUARDRAILS', incident: 'INC0012346', action: 'Blocked (Duplicate)' },
                { timestamp: new Date(Date.now() - 120000).toISOString(), agent: 'EXECUTOR', incident: 'INC0012345', action: 'Assigned to L2-Network' },
                { timestamp: new Date(Date.now() - 180000).toISOString(), agent: 'EXECUTOR', incident: 'INC0012344', action: 'Teams Card Sent' },
                { timestamp: new Date(Date.now() - 240000).toISOString(), agent: 'ENRICHMENT', incident: 'INC0012343', action: 'KB + User Context Added' },
            ])
        }
    }

    const toggleKillSwitch = async () => {
        if (!confirm('Are you sure you want to toggle the system kill switch?')) return

        try {
            // If kill switch is ACTIVE (System Disabled), we want to ENABLE system
            // If kill switch is INACTIVE (System Enabled), we want to DISABLE system
            const action = status.kill_switch_active ? 'enable' : 'disable'

            const response = await fetch('/api/governance/killswitch', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    action: action,
                    reason: 'Manual toggle from Dashboard',
                    operator: 'admin@aegis.local'
                })
            })

            if (response.ok) {
                fetchStatus()
            } else {
                alert('Failed to toggle kill switch')
            }
        } catch (err) {
            console.error(err)
            alert('Error toggling kill switch')
        }
    }

    const formatTime = (iso) => {
        const date = new Date(iso)
        return date.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' })
    }

    return (
        <div>
            <div className="page-header">
                <div>
                    <h1 className="page-title">Dashboard</h1>
                    <p className="page-subtitle">System overview and real-time monitoring</p>
                </div>
                <div className="flex items-center gap-4">
                    <button
                        className={`btn ${status.kill_switch_active ? 'btn-success' : 'btn-danger'}`}
                        onClick={toggleKillSwitch}
                        style={{ padding: '8px 16px', fontSize: '13px', display: 'flex', alignItems: 'center', gap: '6px' }}
                    >
                        <Zap size={16} />
                        {status.kill_switch_active ? 'Enable System' : 'Disable System'}
                    </button>

                    <div className={`badge ${status.operational ? 'badge-success' : 'badge-danger'}`}>
                        <span style={{
                            width: '8px',
                            height: '8px',
                            borderRadius: '50%',
                            background: 'currentColor',
                            marginRight: '6px'
                        }}></span>
                        {status.operational ? 'System Online' : 'System Offline'}
                    </div>
                    <div className="badge badge-primary">
                        Mode: {status.mode?.toUpperCase()}
                    </div>
                </div>
            </div>

            {status.kill_switch_active && (
                <div style={{
                    background: 'rgba(239, 68, 68, 0.1)',
                    border: '1px solid var(--accent-danger)',
                    borderRadius: 'var(--border-radius)',
                    padding: '16px 20px',
                    marginBottom: '24px',
                    display: 'flex',
                    alignItems: 'center',
                    gap: '12px'
                }}>
                    <AlertTriangle color="var(--accent-danger)" />
                    <span><strong>Kill Switch Active:</strong> All AI processing is halted</span>
                </div>
            )}

            <div className="stats-grid">
                <div className="stat-card">
                    <div className="stat-card-header">
                        <div className="stat-card-icon purple">
                            <Activity size={22} />
                        </div>
                    </div>
                    <div className="stat-card-value">{stats.processed_today}</div>
                    <div className="stat-card-label">Processed Today</div>
                </div>

                <div className="stat-card">
                    <div className="stat-card-header">
                        <div className="stat-card-icon orange">
                            <Shield size={22} />
                        </div>
                    </div>
                    <div className="stat-card-value">{stats.blocked_today}</div>
                    <div className="stat-card-label">Blocked (Duplicates)</div>
                </div>

                <div className="stat-card">
                    <div className="stat-card-header">
                        <div className="stat-card-icon green">
                            <Bot size={22} />
                        </div>
                    </div>
                    <div className="stat-card-value">{stats.active_nodes}</div>
                    <div className="stat-card-label">Pipeline Nodes</div>
                </div>

                <div className="stat-card">
                    <div className="stat-card-header">
                        <div className="stat-card-icon blue">
                            <TrendingUp size={22} />
                        </div>
                    </div>
                    <div className="stat-card-value">{stats.success_rate}%</div>
                    <div className="stat-card-label">Success Rate</div>
                </div>

                <div className="stat-card" style={{ cursor: 'pointer' }} onClick={() => setShowFeedback(true)}>
                    <div className="stat-card-header">
                        <div className="stat-card-icon" style={{ background: stats.approval_rate >= 80 ? 'rgba(34, 197, 94, 0.15)' : 'rgba(251, 146, 60, 0.15)' }}>
                            <CheckCircle size={22} style={{ color: stats.approval_rate >= 80 ? '#22c55e' : '#f97316' }} />
                        </div>
                    </div>
                    <div className="stat-card-value">{stats.approval_rate || 0}%</div>
                    <div className="stat-card-label">👍 Approval Rate</div>
                </div>
            </div>

            <div className="card">
                <div className="card-header">
                    <h3 className="card-title">Recent Activity</h3>
                    <a href="/logs" style={{ color: 'var(--accent-primary)', fontSize: '14px', textDecoration: 'none' }}>
                        View All →
                    </a>
                </div>
                <div className="table-container" style={{ border: 'none' }}>
                    <table className="table">
                        <thead>
                            <tr>
                                <th>Time</th>
                                <th>Node</th>
                                <th>Incident</th>
                                <th>Action</th>
                            </tr>
                        </thead>
                        <tbody>
                            {recentLogs.map((log, index) => (
                                <tr key={index}>
                                    <td style={{ color: 'var(--text-muted)' }}>
                                        <Clock size={14} style={{ marginRight: '6px', verticalAlign: 'middle' }} />
                                        {formatTime(log.timestamp)}
                                    </td>
                                    <td>
                                        <span className="badge badge-primary">{log.agent}</span>
                                    </td>
                                    <td style={{ fontFamily: 'monospace' }}>{log.incident}</td>
                                    <td>{log.action}</td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>
            </div>

            {/* Feedback Drill-down Modal */}
            {showFeedback && (
                <div className="modal-overlay" style={{
                    position: 'fixed', top: 0, left: 0, right: 0, bottom: 0,
                    background: 'rgba(0,0,0,0.7)', display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 1000
                }} onClick={() => setShowFeedback(false)}>
                    <div className="modal-content" style={{
                        background: 'var(--bg-card)', borderRadius: '12px', padding: '24px', width: '600px', maxHeight: '80vh', overflow: 'auto'
                    }} onClick={e => e.stopPropagation()}>
                        <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '16px' }}>
                            <h3 style={{ margin: 0 }}>👍 Feedback Details</h3>
                            <button className="btn btn-secondary" onClick={() => setShowFeedback(false)}>✕</button>
                        </div>
                        <div style={{ marginBottom: '16px' }}>
                            <span className="badge badge-success" style={{ marginRight: '8px' }}>
                                👍 {feedbackDetails.filter(f => f.feedback === 'positive').length}
                            </span>
                            <span className="badge badge-danger">
                                👎 {feedbackDetails.filter(f => f.feedback === 'negative').length}
                            </span>
                        </div>
                        <table className="table" style={{ fontSize: '14px' }}>
                            <thead>
                                <tr>
                                    <th>Incident</th>
                                    <th>Classification</th>
                                    <th>Feedback</th>
                                </tr>
                            </thead>
                            <tbody>
                                {feedbackDetails.map((fb, i) => (
                                    <tr key={i}>
                                        <td style={{ fontFamily: 'monospace' }}>{fb.incident_number}</td>
                                        <td>{fb.classification}</td>
                                        <td>{fb.feedback === 'positive' ? '👍' : '👎'}</td>
                                    </tr>
                                ))}
                                {feedbackDetails.length === 0 && (
                                    <tr><td colSpan={3} style={{ textAlign: 'center', color: 'var(--text-muted)' }}>No feedback yet</td></tr>
                                )}
                            </tbody>
                        </table>
                    </div>
                </div>
            )}
        </div>
    )
}

export default Dashboard
