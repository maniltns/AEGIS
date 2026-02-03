import { NavLink } from 'react-router-dom'
import {
    LayoutDashboard,
    Bot,
    Plug,
    ScrollText,
    Settings,
    LogOut,
    Shield
} from 'lucide-react'

function Sidebar({ user, onLogout }) {
    const navItems = [
        { path: '/', icon: LayoutDashboard, label: 'Dashboard' },
        { path: '/agents', icon: Bot, label: 'Agents' },
        { path: '/connectors', icon: Plug, label: 'Connectors' },
        { path: '/logs', icon: ScrollText, label: 'Logs' },
        { path: '/settings', icon: Settings, label: 'Settings' },
    ]

    return (
        <aside className="sidebar">
            <div className="sidebar-logo">
                <div className="sidebar-logo-icon">
                    <Shield size={24} color="white" />
                </div>
                <span className="sidebar-logo-text">AEGIS</span>
            </div>

            <nav className="sidebar-nav">
                <div className="nav-section">
                    <div className="nav-section-title">Main</div>
                    {navItems.map((item) => (
                        <NavLink
                            key={item.path}
                            to={item.path}
                            className={({ isActive }) =>
                                `nav-item ${isActive ? 'active' : ''}`
                            }
                            end={item.path === '/'}
                        >
                            <item.icon size={20} className="nav-item-icon" />
                            <span className="nav-item-text">{item.label}</span>
                        </NavLink>
                    ))}
                </div>
            </nav>

            <div style={{ padding: '16px 12px', borderTop: '1px solid var(--border-primary)' }}>
                <div style={{
                    display: 'flex',
                    alignItems: 'center',
                    gap: '12px',
                    padding: '12px',
                    marginBottom: '8px'
                }}>
                    <div style={{
                        width: '36px',
                        height: '36px',
                        borderRadius: '8px',
                        background: 'var(--gradient-primary)',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        color: 'white',
                        fontWeight: '600',
                        fontSize: '14px'
                    }}>
                        {user?.username?.[0]?.toUpperCase() || 'A'}
                    </div>
                    <div style={{ flex: 1 }}>
                        <div style={{ fontSize: '14px', fontWeight: '500' }}>{user?.username || 'Admin'}</div>
                        <div style={{ fontSize: '12px', color: 'var(--text-muted)' }}>Administrator</div>
                    </div>
                </div>
                <button
                    className="nav-item"
                    onClick={onLogout}
                    style={{ width: '100%', border: 'none', background: 'transparent' }}
                >
                    <LogOut size={20} className="nav-item-icon" />
                    <span className="nav-item-text">Logout</span>
                </button>
            </div>
        </aside>
    )
}

export default Sidebar
