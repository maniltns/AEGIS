const API_BASE = '/api'

export const api = {
    // Auth
    login: async (username, password) => {
        const res = await fetch(`${API_BASE}/auth/login`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username, password })
        })
        if (!res.ok) throw new Error('Login failed')
        return res.json()
    },

    // Status
    getStatus: async () => {
        const res = await fetch(`${API_BASE}/status`)
        if (!res.ok) throw new Error('Failed to fetch status')
        return res.json()
    },

    getHealth: async () => {
        const res = await fetch(`${API_BASE}/health`)
        if (!res.ok) throw new Error('Failed to fetch health')
        return res.json()
    },

    // Governance
    setMode: async (mode, reason) => {
        const res = await fetch(`${API_BASE}/governance/mode`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ mode, reason })
        })
        if (!res.ok) throw new Error('Failed to set mode')
        return res.json()
    },

    toggleKillSwitch: async (action, reason, operator) => {
        const res = await fetch(`${API_BASE}/governance/killswitch`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ action, reason, operator })
        })
        if (!res.ok) throw new Error('Failed to toggle kill switch')
        return res.json()
    },

    getThresholds: async () => {
        const res = await fetch(`${API_BASE}/governance/thresholds`)
        if (!res.ok) throw new Error('Failed to fetch thresholds')
        return res.json()
    },

    // Agents
    getAgents: async () => {
        const res = await fetch(`${API_BASE}/admin/agents`)
        if (!res.ok) throw new Error('Failed to fetch agents')
        return res.json()
    },

    toggleAgent: async (agentId, enabled) => {
        const res = await fetch(`${API_BASE}/admin/agents/${agentId}/toggle`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ enabled })
        })
        if (!res.ok) throw new Error('Failed to toggle agent')
        return res.json()
    },

    addAgent: async (agent) => {
        const res = await fetch(`${API_BASE}/admin/agents`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(agent)
        })
        if (!res.ok) throw new Error('Failed to add agent')
        return res.json()
    },

    // Logs
    getLogs: async (filter = 'all', limit = 50) => {
        const res = await fetch(`${API_BASE}/admin/logs?filter=${filter}&limit=${limit}`)
        if (!res.ok) throw new Error('Failed to fetch logs')
        return res.json()
    },

    // Connectors
    getConnectors: async () => {
        const res = await fetch(`${API_BASE}/admin/connectors`)
        if (!res.ok) throw new Error('Failed to fetch connectors')
        return res.json()
    },

    saveConnector: async (connectorId, config) => {
        const res = await fetch(`${API_BASE}/admin/connectors/${connectorId}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(config)
        })
        if (!res.ok) throw new Error('Failed to save connector')
        return res.json()
    }
}

export default api
