import { useState, useEffect } from 'react'
import { Check, AlertCircle, RefreshCw, Wifi, WifiOff, Settings } from 'lucide-react'
import api from '../api/client'

function Connectors() {
    const [connectors, setConnectors] = useState([])
    const [loading, setLoading] = useState(true)
    const [refreshing, setRefreshing] = useState(false)
    const [error, setError] = useState(null)
    const [showConfigModal, setShowConfigModal] = useState(false)
    const [selectedConnector, setSelectedConnector] = useState(null)

    // Fetch connectors from API
    const fetchConnectors = async (isRefresh = false) => {
        try {
            if (isRefresh) setRefreshing(true)
            else setLoading(true)

            const response = await api.getConnectors()
            setConnectors(response.connectors || [])
            setError(null)
        } catch (err) {
            console.error('Failed to fetch connectors:', err)
            setError('Failed to load connector status')
        } finally {
            setLoading(false)
            setRefreshing(false)
        }
    }

    useEffect(() => {
        fetchConnectors()
        // Refresh every 30 seconds
        const interval = setInterval(() => fetchConnectors(true), 30000)
        return () => clearInterval(interval)
    }, [])

    const openConfig = (connector) => {
        setSelectedConnector(connector)
        setShowConfigModal(true)
    }

    const getStatusIcon = (status) => {
        switch (status) {
            case 'connected':
                return <Check size={14} className="status-icon connected" />
            case 'error':
                return <AlertCircle size={14} className="status-icon error" />
            case 'disconnected':
            default:
                return <WifiOff size={14} className="status-icon disconnected" />
        }
    }

    const getStatusColor = (status) => {
        switch (status) {
            case 'connected':
                return 'var(--success)'
            case 'error':
                return 'var(--danger)'
            case 'disconnected':
            default:
                return 'var(--text-tertiary)'
        }
    }

    if (loading) {
        return (
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', height: '50vh' }}>
                <RefreshCw size={32} className="spin" style={{ color: 'var(--primary)' }} />
            </div>
        )
    }

    const connectedConnectors = connectors.filter(c => c.status === 'connected')
    const otherConnectors = connectors.filter(c => c.status !== 'connected')

    return (
        <div>
            <div className="page-header">
                <div>
                    <h1 className="page-title">Connectors</h1>
                    <p className="page-subtitle">Real-time integration status</p>
                </div>
                <button
                    className="btn btn-secondary"
                    onClick={() => fetchConnectors(true)}
                    disabled={refreshing}
                    style={{ display: 'flex', alignItems: 'center', gap: '8px' }}
                >
                    <RefreshCw size={16} className={refreshing ? 'spin' : ''} />
                    Refresh
                </button>
            </div>

            {error && (
                <div style={{
                    background: 'rgba(239, 68, 68, 0.1)',
                    border: '1px solid var(--danger)',
                    borderRadius: '8px',
                    padding: '12px 16px',
                    marginBottom: '24px',
                    color: 'var(--danger)'
                }}>
                    {error}
                </div>
            )}

            {connectedConnectors.length > 0 && (
                <div style={{ marginBottom: '32px' }}>
                    <h3 style={{ fontSize: '16px', fontWeight: '600', marginBottom: '16px', display: 'flex', alignItems: 'center', gap: '8px' }}>
                        <Wifi size={18} style={{ color: 'var(--success)' }} />
                        Connected ({connectedConnectors.length})
                    </h3>
                    <div className="connector-grid">
                        {connectedConnectors.map((connector) => (
                            <div key={connector.id} className="connector-card" onClick={() => openConfig(connector)}>
                                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                                    <div className="connector-logo">{connector.logo}</div>
                                    <span className="connector-badge connected">
                                        {getStatusIcon(connector.status)}
                                        <span style={{ marginLeft: '4px' }}>Connected</span>
                                    </span>
                                </div>
                                <div>
                                    <div className="connector-name">{connector.name}</div>
                                    <div className="connector-description">{connector.description}</div>
                                    <div style={{ fontSize: '12px', color: 'var(--success)', marginTop: '4px' }}>
                                        {connector.message}
                                    </div>
                                </div>
                                <div style={{ display: 'flex', flexWrap: 'wrap', gap: '6px' }}>
                                    {connector.features?.map((feature, i) => (
                                        <span key={i} className="badge badge-primary" style={{ fontSize: '11px' }}>
                                            {feature}
                                        </span>
                                    ))}
                                </div>
                            </div>
                        ))}
                    </div>
                </div>
            )}

            {otherConnectors.length > 0 && (
                <div>
                    <h3 style={{ fontSize: '16px', fontWeight: '600', marginBottom: '16px', display: 'flex', alignItems: 'center', gap: '8px' }}>
                        <WifiOff size={18} style={{ color: 'var(--text-tertiary)' }} />
                        Disconnected / Error ({otherConnectors.length})
                    </h3>
                    <div className="connector-grid">
                        {otherConnectors.map((connector) => (
                            <div key={connector.id} className="connector-card" onClick={() => openConfig(connector)}>
                                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                                    <div className="connector-logo">{connector.logo}</div>
                                    <span className="connector-badge" style={{
                                        background: connector.status === 'error' ? 'rgba(239, 68, 68, 0.1)' : 'var(--bg-tertiary)',
                                        color: getStatusColor(connector.status)
                                    }}>
                                        {getStatusIcon(connector.status)}
                                        <span style={{ marginLeft: '4px' }}>
                                            {connector.status === 'error' ? 'Error' : 'Disconnected'}
                                        </span>
                                    </span>
                                </div>
                                <div>
                                    <div className="connector-name">{connector.name}</div>
                                    <div className="connector-description">{connector.description}</div>
                                    <div style={{
                                        fontSize: '12px',
                                        color: connector.status === 'error' ? 'var(--danger)' : 'var(--text-tertiary)',
                                        marginTop: '4px'
                                    }}>
                                        {connector.message}
                                    </div>
                                </div>
                                <div style={{ display: 'flex', flexWrap: 'wrap', gap: '6px' }}>
                                    {connector.features?.map((feature, i) => (
                                        <span key={i} className="badge" style={{ fontSize: '11px', background: 'var(--bg-tertiary)' }}>
                                            {feature}
                                        </span>
                                    ))}
                                </div>
                            </div>
                        ))}
                    </div>
                </div>
            )}

            {showConfigModal && selectedConnector && (
                <div className="modal-overlay" onClick={() => setShowConfigModal(false)}>
                    <div className="modal" onClick={e => e.stopPropagation()}>
                        <div className="modal-header">
                            <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                                <span style={{ fontSize: '28px' }}>{selectedConnector.logo}</span>
                                <div>
                                    <h3 className="modal-title">{selectedConnector.name}</h3>
                                    <span style={{
                                        fontSize: '12px',
                                        color: getStatusColor(selectedConnector.status)
                                    }}>
                                        {selectedConnector.message}
                                    </span>
                                </div>
                            </div>
                            <button className="modal-close" onClick={() => setShowConfigModal(false)}>✕</button>
                        </div>

                        <div style={{
                            background: 'var(--bg-tertiary)',
                            padding: '16px',
                            borderRadius: '8px',
                            marginBottom: '16px'
                        }}>
                            <div style={{ display: 'grid', gap: '12px' }}>
                                <div>
                                    <span style={{ fontSize: '12px', color: 'var(--text-tertiary)' }}>Status</span>
                                    <div style={{
                                        display: 'flex',
                                        alignItems: 'center',
                                        gap: '8px',
                                        color: getStatusColor(selectedConnector.status),
                                        fontWeight: '600'
                                    }}>
                                        {getStatusIcon(selectedConnector.status)}
                                        {selectedConnector.status.charAt(0).toUpperCase() + selectedConnector.status.slice(1)}
                                    </div>
                                </div>
                                {selectedConnector.instance && (
                                    <div>
                                        <span style={{ fontSize: '12px', color: 'var(--text-tertiary)' }}>Instance</span>
                                        <div>{selectedConnector.instance}</div>
                                    </div>
                                )}
                            </div>
                        </div>

                        <div style={{
                            background: 'var(--bg-tertiary)',
                            padding: '12px 16px',
                            borderRadius: '8px',
                            fontSize: '13px',
                            color: 'var(--text-secondary)'
                        }}>
                            <strong>Features:</strong> {selectedConnector.features?.join(', ')}
                        </div>

                        <div style={{ marginTop: '16px', fontSize: '13px', color: 'var(--text-tertiary)' }}>
                            <Settings size={14} style={{ marginRight: '6px', verticalAlign: 'middle' }} />
                            Configure this connector in the <code>.env</code> file and restart containers.
                        </div>

                        <div style={{ display: 'flex', gap: '12px', marginTop: '24px' }}>
                            <button className="btn btn-secondary" style={{ flex: 1 }} onClick={() => setShowConfigModal(false)}>
                                Close
                            </button>
                            <button className="btn btn-primary" style={{ flex: 1 }} onClick={() => fetchConnectors(true)}>
                                <RefreshCw size={14} style={{ marginRight: '6px' }} />
                                Refresh Status
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
                .status-icon.connected { color: var(--success); }
                .status-icon.error { color: var(--danger); }
                .status-icon.disconnected { color: var(--text-tertiary); }
            `}</style>
        </div>
    )
}

export default Connectors
