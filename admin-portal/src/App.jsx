import { useState, useEffect } from 'react'
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import Sidebar from './components/Sidebar'
import Dashboard from './pages/Dashboard'
import Agents from './pages/Agents'
import Connectors from './pages/Connectors'
import Logs from './pages/Logs'
import Settings from './pages/Settings'
import KnowledgeBase from './pages/KnowledgeBase'
import Login from './pages/Login'

function App() {
    const [isAuthenticated, setIsAuthenticated] = useState(false)
    const [user, setUser] = useState(null)

    useEffect(() => {
        // Check for existing session
        const token = localStorage.getItem('aegis_token')
        const savedUser = localStorage.getItem('aegis_user')
        if (token && savedUser) {
            setIsAuthenticated(true)
            setUser(JSON.parse(savedUser))
        }
    }, [])

    const handleLogin = (userData) => {
        setIsAuthenticated(true)
        setUser(userData)
        localStorage.setItem('aegis_token', userData.token)
        localStorage.setItem('aegis_user', JSON.stringify(userData))
    }

    const handleLogout = () => {
        setIsAuthenticated(false)
        setUser(null)
        localStorage.removeItem('aegis_token')
        localStorage.removeItem('aegis_user')
    }

    if (!isAuthenticated) {
        return <Login onLogin={handleLogin} />
    }

    return (
        <BrowserRouter>
            <div className="app-container">
                <Sidebar user={user} onLogout={handleLogout} />
                <main className="main-content">
                    <Routes>
                        <Route path="/" element={<Dashboard />} />
                        <Route path="/agents" element={<Agents />} />
                        <Route path="/connectors" element={<Connectors />} />
                        <Route path="/logs" element={<Logs />} />
                        <Route path="/knowledge-base" element={<KnowledgeBase />} />
                        <Route path="/settings" element={<Settings />} />
                        <Route path="*" element={<Navigate to="/" replace />} />
                    </Routes>
                </main>
            </div>
        </BrowserRouter>
    )
}

export default App
