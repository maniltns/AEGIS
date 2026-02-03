import { useState, useEffect } from 'react'
import { Search, Filter, RefreshCw, Download, Clock } from 'lucide-react'

function Logs() {
    const [logs, setLogs] = useState([])
    const [filter, setFilter] = useState('all')
    const [searchQuery, setSearchQuery] = useState('')
    const [loading, setLoading] = useState(false)

    useEffect(() => {
        fetchLogs()
    }, [filter])

    const fetchLogs = async () => {
        setLoading(true)
        try {
            const response = await fetch(`/api/admin/logs?filter=${filter}&limit=50`)
            if (response.ok) {
                const data = await response.json()
                setLogs(data.logs || [])
            }
        } catch (err) {
            // Demo data
            setLogs(generateDemoLogs())
        } finally {
            setLoading(false)
        }
    }

    const generateDemoLogs = () => {
        const agents = ['GUARDIAN', 'SCOUT', 'SHERLOCK', 'ROUTER', 'ARBITER', 'HERALD', 'SCRIBE', 'BRIDGE', 'JANITOR']
        const actions = [
            'Triaged incident (94% confidence)',
            'Blocked duplicate incident',
            'Enriched with CMDB data',
            'Assigned to L2-Network',
            'Sent Teams notification',
            'Logged decision to audit',
            'Converted Case to Incident',
            'Executed print spooler restart',
            'Approved by governance rules'
        ]
        const levels = ['info', 'warning', 'error', 'success']

        return Array(30).fill().map((_, i) => ({
            id: i + 1,
            timestamp: new Date(Date.now() - i * 120000).toISOString(),
            agent: agents[Math.floor(Math.random() * agents.length)],
            incident: `INC00${12345 - i}`,
            action: actions[Math.floor(Math.random() * actions.length)],
            level: levels[Math.floor(Math.random() * levels.length)],
            details: 'Lorem ipsum dolor sit amet'
        }))
    }

    const formatTime = (iso) => {
        const date = new Date(iso)
        return date.toLocaleString('en-US', {
            month: 'short',
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit',
            second: '2-digit'
        })
    }

    const getLevelBadge = (level) => {
        const classes = {
            info: 'badge-info',
            warning: 'badge-warning',
            error: 'badge-danger',
            success: 'badge-success'
        }
        return classes[level] || 'badge-info'
    }

    const filteredLogs = logs.filter(log =>
        searchQuery === '' ||
        log.incident?.toLowerCase().includes(searchQuery.toLowerCase()) ||
        log.agent?.toLowerCase().includes(searchQuery.toLowerCase()) ||
        log.action?.toLowerCase().includes(searchQuery.toLowerCase())
    )

    return (
        <div>
            <div className="page-header">
                <div>
                    <h1 className="page-title">Logs</h1>
                    <p className="page-subtitle">Real-time audit trail and activity logs</p>
                </div>
                <div className="flex gap-2">
                    <button className="btn btn-secondary" onClick={fetchLogs}>
                        <RefreshCw size={16} className={loading ? 'spinning' : ''} />
                        Refresh
                    </button>
                    <button className="btn btn-secondary">
                        <Download size={16} />
                        Export
                    </button>
                </div>
            </div>

            <div style={{ display: 'flex', gap: '16px', marginBottom: '24px' }}>
                <div className="search-box" style={{ flex: 1, maxWidth: 'none' }}>
                    <Search size={18} className="search-icon" />
                    <input
                        className="input"
                        placeholder="Search logs by incident, agent, or action..."
                        value={searchQuery}
                        onChange={e => setSearchQuery(e.target.value)}
                    />
                </div>
                <select
                    className="input"
                    style={{ width: '200px' }}
                    value={filter}
                    onChange={e => setFilter(e.target.value)}
                >
                    <option value="all">All Levels</option>
                    <option value="info">Info</option>
                    <option value="warning">Warning</option>
                    <option value="error">Error</option>
                    <option value="success">Success</option>
                </select>
            </div>

            <div className="table-container">
                <table className="table">
                    <thead>
                        <tr>
                            <th style={{ width: '180px' }}>Timestamp</th>
                            <th style={{ width: '100px' }}>Level</th>
                            <th style={{ width: '120px' }}>Agent</th>
                            <th style={{ width: '120px' }}>Incident</th>
                            <th>Action</th>
                        </tr>
                    </thead>
                    <tbody>
                        {filteredLogs.map((log) => (
                            <tr key={log.id}>
                                <td style={{ color: 'var(--text-muted)', fontSize: '13px' }}>
                                    <Clock size={14} style={{ marginRight: '6px', verticalAlign: 'middle' }} />
                                    {formatTime(log.timestamp)}
                                </td>
                                <td>
                                    <span className={`badge ${getLevelBadge(log.level)}`}>
                                        {log.level}
                                    </span>
                                </td>
                                <td>
                                    <span className="badge badge-primary">{log.agent}</span>
                                </td>
                                <td style={{ fontFamily: 'monospace', fontSize: '13px' }}>
                                    {log.incident}
                                </td>
                                <td>{log.action}</td>
                            </tr>
                        ))}
                    </tbody>
                </table>
            </div>

            <div style={{
                display: 'flex',
                justifyContent: 'space-between',
                alignItems: 'center',
                marginTop: '16px',
                color: 'var(--text-muted)',
                fontSize: '14px'
            }}>
                <span>Showing {filteredLogs.length} logs</span>
                <div className="flex gap-2">
                    <button className="btn btn-secondary" style={{ padding: '6px 12px' }} disabled>Previous</button>
                    <button className="btn btn-secondary" style={{ padding: '6px 12px' }}>Next</button>
                </div>
            </div>

            <style>{`
        .spinning {
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

export default Logs
