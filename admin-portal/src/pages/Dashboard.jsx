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
        active_agents: 9,
        success_rate: 94
    })
    const [status, setStatus] = useState({
        operational: true,
        mode: 'assist',
        kill_switch_active: false
    })
    const [recentLogs, setRecentLogs] = useState([])

    useEffect(() => {
        fetchStatus()
        fetchRecentLogs()
        const interval = setInterval(fetchStatus, 30000)
        return () => clearInterval(interval)
    }, [])

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
        } catch (err) {
            // Demo data
            setStats({
                processed_today: 127,
                blocked_today: 12,
                active_agents: 9,
                success_rate: 94
            })
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
                { timestamp: new Date().toISOString(), agent: 'SHERLOCK', incident: 'INC0012345', action: 'Triaged (94%)' },
                { timestamp: new Date(Date.now() - 60000).toISOString(), agent: 'GUARDIAN', incident: 'INC0012346', action: 'Blocked (Duplicate)' },
                { timestamp: new Date(Date.now() - 120000).toISOString(), agent: 'ROUTER', incident: 'INC0012345', action: 'Assigned to L2-Network' },
                { timestamp: new Date(Date.now() - 180000).toISOString(), agent: 'HERALD', incident: 'INC0012344', action: 'Teams Notification Sent' },
                { timestamp: new Date(Date.now() - 240000).toISOString(), agent: 'SCOUT', incident: 'INC0012343', action: 'Enriched (CMDB + User)' },
            ])
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
                    <div className="stat-card-value">{stats.active_agents}</div>
                    <div className="stat-card-label">Active Agents</div>
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
                                <th>Agent</th>
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
        </div>
    )
}

export default Dashboard
