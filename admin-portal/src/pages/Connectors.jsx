import { useState } from 'react'
import { Plus, Check, Settings, ExternalLink } from 'lucide-react'

const CONNECTORS = [
    {
        id: 'servicenow',
        name: 'ServiceNow',
        description: 'ITSM platform for incidents, cases, RITMs, and knowledge base',
        logo: '🎟️',
        status: 'connected',
        features: ['Incidents', 'Cases', 'RITMs', 'Knowledge Base', 'CMDB']
    },
    {
        id: 'jira',
        name: 'Jira Service Management',
        description: 'Atlassian service desk for issue tracking and project management',
        logo: '🔷',
        status: 'available',
        features: ['Issues', 'Projects', 'Workflows', 'SLAs']
    },
    {
        id: 'zendesk',
        name: 'Zendesk',
        description: 'Customer service platform for tickets and help desk',
        logo: '💬',
        status: 'available',
        features: ['Tickets', 'Users', 'Organizations', 'Help Center']
    },
    {
        id: 'freshservice',
        name: 'Freshservice',
        description: 'Cloud-based ITSM solution by Freshworks',
        logo: '🟢',
        status: 'available',
        features: ['Tickets', 'Assets', 'Problems', 'Changes']
    },
    {
        id: 'remedy',
        name: 'BMC Remedy',
        description: 'Enterprise ITSM platform for large organizations',
        logo: '🔶',
        status: 'available',
        features: ['Incidents', 'Changes', 'Problems', 'Assets']
    },
    {
        id: 'teams',
        name: 'Microsoft Teams',
        description: 'Collaboration platform for notifications and approvals',
        logo: '💜',
        status: 'connected',
        features: ['Webhooks', 'Adaptive Cards', 'Channels']
    },
    {
        id: 'slack',
        name: 'Slack',
        description: 'Messaging platform for team notifications',
        logo: '💬',
        status: 'available',
        features: ['Messages', 'Channels', 'Bots']
    },
    {
        id: 'pagerduty',
        name: 'PagerDuty',
        description: 'Incident management and alerting platform',
        logo: '🚨',
        status: 'available',
        features: ['Incidents', 'Escalations', 'On-Call']
    },
]

function Connectors() {
    const [connectors, setConnectors] = useState(CONNECTORS)
    const [showConfigModal, setShowConfigModal] = useState(false)
    const [selectedConnector, setSelectedConnector] = useState(null)
    const [config, setConfig] = useState({ instance: '', user: '', password: '' })

    const openConfig = (connector) => {
        setSelectedConnector(connector)
        setShowConfigModal(true)
    }

    const saveConfig = () => {
        setConnectors(connectors.map(c =>
            c.id === selectedConnector.id ? { ...c, status: 'connected' } : c
        ))
        setShowConfigModal(false)
        setConfig({ instance: '', user: '', password: '' })
    }

    return (
        <div>
            <div className="page-header">
                <div>
                    <h1 className="page-title">Connectors</h1>
                    <p className="page-subtitle">Integrate with ITSM platforms and services</p>
                </div>
            </div>

            <div style={{ marginBottom: '32px' }}>
                <h3 style={{ fontSize: '16px', fontWeight: '600', marginBottom: '16px' }}>
                    Connected
                </h3>
                <div className="connector-grid">
                    {connectors.filter(c => c.status === 'connected').map((connector) => (
                        <div key={connector.id} className="connector-card" onClick={() => openConfig(connector)}>
                            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                                <div className="connector-logo">{connector.logo}</div>
                                <span className="connector-badge connected">
                                    <Check size={12} style={{ marginRight: '4px' }} />
                                    Connected
                                </span>
                            </div>
                            <div>
                                <div className="connector-name">{connector.name}</div>
                                <div className="connector-description">{connector.description}</div>
                            </div>
                            <div style={{ display: 'flex', flexWrap: 'wrap', gap: '6px' }}>
                                {connector.features.map((feature, i) => (
                                    <span key={i} className="badge badge-primary" style={{ fontSize: '11px' }}>
                                        {feature}
                                    </span>
                                ))}
                            </div>
                        </div>
                    ))}
                </div>
            </div>

            <div>
                <h3 style={{ fontSize: '16px', fontWeight: '600', marginBottom: '16px' }}>
                    Available Connectors
                </h3>
                <div className="connector-grid">
                    {connectors.filter(c => c.status === 'available').map((connector) => (
                        <div key={connector.id} className="connector-card" onClick={() => openConfig(connector)}>
                            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                                <div className="connector-logo">{connector.logo}</div>
                                <span className="connector-badge available">
                                    <Plus size={12} style={{ marginRight: '4px' }} />
                                    Add
                                </span>
                            </div>
                            <div>
                                <div className="connector-name">{connector.name}</div>
                                <div className="connector-description">{connector.description}</div>
                            </div>
                            <div style={{ display: 'flex', flexWrap: 'wrap', gap: '6px' }}>
                                {connector.features.map((feature, i) => (
                                    <span key={i} className="badge" style={{ fontSize: '11px', background: 'var(--bg-tertiary)' }}>
                                        {feature}
                                    </span>
                                ))}
                            </div>
                        </div>
                    ))}
                </div>
            </div>

            {showConfigModal && selectedConnector && (
                <div className="modal-overlay" onClick={() => setShowConfigModal(false)}>
                    <div className="modal" onClick={e => e.stopPropagation()}>
                        <div className="modal-header">
                            <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                                <span style={{ fontSize: '28px' }}>{selectedConnector.logo}</span>
                                <h3 className="modal-title">Configure {selectedConnector.name}</h3>
                            </div>
                            <button className="modal-close" onClick={() => setShowConfigModal(false)}>✕</button>
                        </div>

                        <div className="form-group">
                            <label className="form-label">Instance URL</label>
                            <input
                                className="input"
                                placeholder={`e.g. yourcompany.${selectedConnector.id}.com`}
                                value={config.instance}
                                onChange={e => setConfig({ ...config, instance: e.target.value })}
                            />
                        </div>
                        <div className="form-group">
                            <label className="form-label">Username / API User</label>
                            <input
                                className="input"
                                placeholder="Integration user"
                                value={config.user}
                                onChange={e => setConfig({ ...config, user: e.target.value })}
                            />
                        </div>
                        <div className="form-group">
                            <label className="form-label">Password / API Key</label>
                            <input
                                type="password"
                                className="input"
                                placeholder="••••••••"
                                value={config.password}
                                onChange={e => setConfig({ ...config, password: e.target.value })}
                            />
                        </div>

                        <div style={{
                            background: 'var(--bg-tertiary)',
                            padding: '12px 16px',
                            borderRadius: '8px',
                            marginTop: '16px',
                            fontSize: '13px',
                            color: 'var(--text-secondary)'
                        }}>
                            <strong>Features:</strong> {selectedConnector.features.join(', ')}
                        </div>

                        <div style={{ display: 'flex', gap: '12px', marginTop: '24px' }}>
                            <button className="btn btn-secondary" style={{ flex: 1 }} onClick={() => setShowConfigModal(false)}>
                                Cancel
                            </button>
                            <button className="btn btn-primary" style={{ flex: 1 }} onClick={saveConfig}>
                                {selectedConnector.status === 'connected' ? 'Update' : 'Connect'}
                            </button>
                        </div>
                    </div>
                </div>
            )}
        </div>
    )
}

export default Connectors
