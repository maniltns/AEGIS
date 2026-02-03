import { useState } from 'react'
import { Shield, Eye, EyeOff } from 'lucide-react'

function Login({ onLogin }) {
    const [username, setUsername] = useState('')
    const [password, setPassword] = useState('')
    const [showPassword, setShowPassword] = useState(false)
    const [error, setError] = useState('')
    const [loading, setLoading] = useState(false)

    const handleSubmit = async (e) => {
        e.preventDefault()
        setError('')
        setLoading(true)

        try {
            const response = await fetch('/api/auth/login', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ username, password })
            })

            if (response.ok) {
                const data = await response.json()
                onLogin(data)
            } else {
                const errorData = await response.json()
                setError(errorData.detail || 'Invalid credentials')
            }
        } catch (err) {
            // For demo/dev mode, allow default credentials
            if (username === 'admin' && password === 'aegis2026') {
                onLogin({
                    username: 'admin',
                    token: 'demo-token-' + Date.now(),
                    role: 'admin'
                })
            } else {
                setError('Invalid username or password')
            }
        } finally {
            setLoading(false)
        }
    }

    return (
        <div className="login-container">
            <div className="login-card">
                <div className="login-logo">
                    <div className="login-logo-icon">
                        <Shield size={32} color="white" />
                    </div>
                    <div className="login-logo-text">AEGIS</div>
                    <div className="login-subtitle">Admin Portal</div>
                </div>

                {error && <div className="login-error">{error}</div>}

                <form onSubmit={handleSubmit}>
                    <div className="form-group">
                        <label className="form-label">Username</label>
                        <input
                            type="text"
                            className="input"
                            value={username}
                            onChange={(e) => setUsername(e.target.value)}
                            placeholder="Enter username"
                            required
                            autoFocus
                        />
                    </div>

                    <div className="form-group">
                        <label className="form-label">Password</label>
                        <div style={{ position: 'relative' }}>
                            <input
                                type={showPassword ? 'text' : 'password'}
                                className="input"
                                value={password}
                                onChange={(e) => setPassword(e.target.value)}
                                placeholder="Enter password"
                                required
                                style={{ paddingRight: '48px' }}
                            />
                            <button
                                type="button"
                                onClick={() => setShowPassword(!showPassword)}
                                style={{
                                    position: 'absolute',
                                    right: '12px',
                                    top: '50%',
                                    transform: 'translateY(-50%)',
                                    background: 'none',
                                    border: 'none',
                                    color: 'var(--text-muted)',
                                    cursor: 'pointer'
                                }}
                            >
                                {showPassword ? <EyeOff size={20} /> : <Eye size={20} />}
                            </button>
                        </div>
                    </div>

                    <button
                        type="submit"
                        className="btn btn-primary"
                        style={{ width: '100%', marginTop: '8px' }}
                        disabled={loading}
                    >
                        {loading ? 'Signing in...' : 'Sign In'}
                    </button>
                </form>

                <div style={{
                    marginTop: '24px',
                    padding: '16px',
                    background: 'var(--bg-tertiary)',
                    borderRadius: '8px',
                    fontSize: '13px',
                    color: 'var(--text-secondary)'
                }}>
                    <strong>Default credentials:</strong><br />
                    Username: admin<br />
                    Password: aegis2026
                </div>
            </div>
        </div>
    )
}

export default Login
