import { useState, useEffect } from 'react'
import { AlertTriangle, Shield, Sliders, Save, Power } from 'lucide-react'

function Settings() {
    const [settings, setSettings] = useState({
        mode: 'assist',
        killSwitch: false,
        thresholds: {
            auto_assign: 85,
            auto_categorize: 80,
            auto_remediate: 95
        }
    })
    const [saving, setSaving] = useState(false)
    const [saved, setSaved] = useState(false)

    useEffect(() => {
        fetchSettings()
    }, [])

    const fetchSettings = async () => {
        try {
            const statusRes = await fetch('/api/status')
            const thresholdsRes = await fetch('/api/governance/thresholds')

            if (statusRes.ok && thresholdsRes.ok) {
                const status = await statusRes.json()
                const thresholds = await thresholdsRes.json()

                setSettings({
                    mode: status.mode || 'assist',
                    killSwitch: status.kill_switch_active || false,
                    thresholds: thresholds.thresholds || settings.thresholds
                })
            }
        } catch (err) {
            // Use defaults
        }
    }

    const saveSettings = async () => {
        setSaving(true)
        try {
            // Save mode
            await fetch('/api/governance/mode', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ mode: settings.mode, reason: 'Updated from admin portal' })
            })

            setSaved(true)
            setTimeout(() => setSaved(false), 3000)
        } catch (err) {
            console.error('Failed to save settings')
        } finally {
            setSaving(false)
        }
    }

    const toggleKillSwitch = async () => {
        const action = settings.killSwitch ? 'enable' : 'disable'

        if (!settings.killSwitch) {
            const confirmed = window.confirm(
                '⚠️ EMERGENCY STOP\n\nThis will halt ALL AI processing immediately.\n\nAre you sure you want to activate the kill switch?'
            )
            if (!confirmed) return
        }

        try {
            const response = await fetch('/api/governance/killswitch', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    action,
                    reason: 'Toggled from admin portal settings',
                    operator: 'admin@aegis.local'
                })
            })

            if (response.ok) {
                // Update local state only on success
                setSettings(prev => ({ ...prev, killSwitch: !prev.killSwitch }))
            } else {
                const err = await response.json()
                alert(`Failed to toggle kill switch: ${err.detail || 'Unknown error'}`)
            }
        } catch (err) {
            console.error(err)
            alert('Error toggling kill switch. Check console/logs.')
        }
    }

    return (
        <div>
            <div className="page-header">
                <div>
                    <h1 className="page-title">Settings</h1>
                    <p className="page-subtitle">Governance controls and system configuration</p>
                </div>
                <button
                    className="btn btn-primary"
                    onClick={saveSettings}
                    disabled={saving}
                >
                    <Save size={16} />
                    {saving ? 'Saving...' : saved ? 'Saved!' : 'Save Changes'}
                </button>
            </div>

            {/* Kill Switch */}
            <div className="card" style={{ marginBottom: '24px' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
                    <div style={{
                        width: '56px',
                        height: '56px',
                        borderRadius: '12px',
                        background: settings.killSwitch ? 'rgba(239, 68, 68, 0.15)' : 'rgba(34, 197, 94, 0.15)',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center'
                    }}>
                        <Power size={28} color={settings.killSwitch ? 'var(--accent-danger)' : 'var(--accent-success)'} />
                    </div>
                    <div style={{ flex: 1 }}>
                        <h3 style={{ fontSize: '18px', fontWeight: '600' }}>Kill Switch</h3>
                        <p style={{ color: 'var(--text-secondary)', fontSize: '14px', marginTop: '4px' }}>
                            {settings.killSwitch
                                ? '🛑 ACTIVE - All AI processing is halted'
                                : '✅ System is processing normally'}
                        </p>
                    </div>
                    <button
                        className={`btn ${settings.killSwitch ? 'btn-primary' : 'btn-danger'}`}
                        onClick={toggleKillSwitch}
                    >
                        {settings.killSwitch ? 'Resume System' : 'Emergency Stop'}
                    </button>
                </div>
            </div>

            {/* Operating Mode */}
            <div className="card" style={{ marginBottom: '24px' }}>
                <div className="card-header">
                    <h3 className="card-title">
                        <Shield size={18} style={{ marginRight: '8px', verticalAlign: 'middle' }} />
                        Operating Mode
                    </h3>
                </div>
                <div style={{ display: 'flex', gap: '16px', marginTop: '16px' }}>
                    {['auto', 'assist', 'monitor'].map((mode) => (
                        <div
                            key={mode}
                            onClick={() => setSettings({ ...settings, mode })}
                            style={{
                                flex: 1,
                                padding: '20px',
                                border: `2px solid ${settings.mode === mode ? 'var(--accent-primary)' : 'var(--border-primary)'}`,
                                borderRadius: 'var(--border-radius)',
                                cursor: 'pointer',
                                background: settings.mode === mode ? 'rgba(99, 102, 241, 0.1)' : 'transparent'
                            }}
                        >
                            <div style={{ fontWeight: '600', fontSize: '16px', textTransform: 'capitalize', marginBottom: '8px' }}>
                                {mode === 'auto' && '🤖 '}
                                {mode === 'assist' && '🤝 '}
                                {mode === 'monitor' && '👁️ '}
                                {mode}
                            </div>
                            <div style={{ fontSize: '13px', color: 'var(--text-secondary)' }}>
                                {mode === 'auto' && 'AI acts automatically above confidence thresholds'}
                                {mode === 'assist' && 'AI recommends, human approves all actions'}
                                {mode === 'monitor' && 'AI observes only, no changes made'}
                            </div>
                        </div>
                    ))}
                </div>
            </div>

            {/* Confidence Thresholds */}
            <div className="card">
                <div className="card-header">
                    <h3 className="card-title">
                        <Sliders size={18} style={{ marginRight: '8px', verticalAlign: 'middle' }} />
                        Confidence Thresholds
                    </h3>
                </div>
                <p style={{ color: 'var(--text-secondary)', fontSize: '14px', marginBottom: '24px' }}>
                    Minimum AI confidence (%) required for automatic actions in Auto mode
                </p>

                {Object.entries(settings.thresholds).map(([key, value]) => (
                    <div key={key} style={{ marginBottom: '24px' }}>
                        <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8px' }}>
                            <label style={{ fontWeight: '500', textTransform: 'capitalize' }}>
                                {key.replace(/_/g, ' ')}
                            </label>
                            <span style={{
                                fontWeight: '600',
                                color: value >= 90 ? 'var(--accent-success)' : value >= 80 ? 'var(--accent-warning)' : 'var(--accent-danger)'
                            }}>
                                {value}%
                            </span>
                        </div>
                        <input
                            type="range"
                            min="50"
                            max="100"
                            value={value}
                            onChange={(e) => setSettings({
                                ...settings,
                                thresholds: { ...settings.thresholds, [key]: parseInt(e.target.value) }
                            })}
                            style={{
                                width: '100%',
                                height: '8px',
                                borderRadius: '4px',
                                background: `linear-gradient(to right, var(--accent-primary) ${value}%, var(--bg-tertiary) ${value}%)`,
                                appearance: 'none',
                                cursor: 'pointer'
                            }}
                        />
                    </div>
                ))}

                <div style={{
                    background: 'var(--bg-tertiary)',
                    padding: '16px',
                    borderRadius: '8px',
                    marginTop: '16px'
                }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '8px' }}>
                        <AlertTriangle size={16} color="var(--accent-warning)" />
                        <strong style={{ fontSize: '14px' }}>Important</strong>
                    </div>
                    <p style={{ fontSize: '13px', color: 'var(--text-secondary)' }}>
                        Higher thresholds require more confidence before AI takes automatic action.
                        Remediation should always have the highest threshold (95%+) for safety.
                    </p>
                </div>
            </div>
        </div>
    )
}

export default Settings
