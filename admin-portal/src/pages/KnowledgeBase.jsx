import { useState, useEffect } from 'react'
import {
    Upload,
    Database,
    Search,
    Settings,
    FileText,
    Trash2,
    RefreshCw,
    CheckCircle,
    AlertCircle,
    Eye,
    X
} from 'lucide-react'

function KnowledgeBase() {
    const [activeTab, setActiveTab] = useState('upload')
    const [collections, setCollections] = useState({
        'idx:kb': { name: 'Knowledge Base', count: 0 },
        'idx:tickets': { name: 'Ticket History', count: 0 },
        'idx:sop': { name: 'SOP Documents', count: 0 }
    })
    const [selectedCollection, setSelectedCollection] = useState('kb')
    const [testQuery, setTestQuery] = useState('')
    const [testResults, setTestResults] = useState([])
    const [isSearching, setIsSearching] = useState(false)
    const [uploadStatus, setUploadStatus] = useState(null)
    const [chunkPreview, setChunkPreview] = useState([])
    const [settings, setSettings] = useState({
        chunkSize: 512,
        chunkOverlap: 50,
        similarityThreshold: 0.7
    })

    useEffect(() => {
        fetchCollectionStats()
    }, [])

    const fetchCollectionStats = async () => {
        try {
            const response = await fetch('/api/rag/stats')
            if (response.ok) {
                const data = await response.json()
                if (data.collections) {
                    setCollections(prev => ({
                        ...prev,
                        'idx:kb': { ...prev['idx:kb'], count: data.collections['idx:kb'] || 0 },
                        'idx:tickets': { ...prev['idx:tickets'], count: data.collections['idx:tickets'] || 0 },
                        'idx:sop': { ...prev['idx:sop'], count: data.collections['idx:sop'] || 0 }
                    }))
                }
            }
        } catch (err) {
            console.error('Failed to fetch stats:', err)
        }
    }

    const handleFileUpload = async (e) => {
        const file = e.target.files[0]
        if (!file) return

        setUploadStatus({ status: 'uploading', message: `Uploading ${file.name}...` })

        const formData = new FormData()
        formData.append('file', file)
        formData.append('collection', selectedCollection)
        formData.append('chunk_size', settings.chunkSize)
        formData.append('chunk_overlap', settings.chunkOverlap)

        try {
            const response = await fetch('/api/rag/upload', {
                method: 'POST',
                body: formData
            })

            if (response.ok) {
                const data = await response.json()
                setUploadStatus({ status: 'success', message: `Uploaded ${data.chunks_created} chunks` })
                setChunkPreview(data.preview || [])
                fetchCollectionStats()
            } else {
                setUploadStatus({ status: 'error', message: 'Upload failed' })
            }
        } catch (err) {
            setUploadStatus({ status: 'error', message: err.message })
        }
    }

    const handleTestQuery = async () => {
        if (!testQuery.trim()) return

        setIsSearching(true)
        try {
            const response = await fetch('/api/rag/search', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    query: testQuery,
                    collection: selectedCollection === 'kb' ? 'kb_articles' : selectedCollection === 'tickets' ? 'incidents' : 'sop',
                    top_k: 5
                })
            })

            if (response.ok) {
                const data = await response.json()
                setTestResults(data.results || [])
            }
        } catch (err) {
            console.error('Search failed:', err)
        } finally {
            setIsSearching(false)
        }
    }

    return (
        <div>
            <div className="page-header">
                <div>
                    <h1 className="page-title">Knowledge Base</h1>
                    <p className="page-subtitle">Manage RAG embeddings and test retrieval</p>
                </div>
                <button className="btn btn-secondary" onClick={fetchCollectionStats}>
                    <RefreshCw size={16} style={{ marginRight: '6px' }} />
                    Refresh
                </button>
            </div>

            {/* Collection Stats */}
            <div className="stats-grid" style={{ marginBottom: '24px' }}>
                {Object.entries(collections).map(([key, col]) => (
                    <div key={key} className="stat-card">
                        <div className="stat-card-header">
                            <div className="stat-card-icon purple">
                                <Database size={22} />
                            </div>
                        </div>
                        <div className="stat-card-value">{col.count}</div>
                        <div className="stat-card-label">{col.name}</div>
                    </div>
                ))}
            </div>

            {/* Tab Navigation */}
            <div className="card" style={{ marginBottom: '24px' }}>
                <div style={{ display: 'flex', gap: '8px', borderBottom: '1px solid var(--border-color)', padding: '12px 16px' }}>
                    {[
                        { id: 'upload', icon: Upload, label: 'Upload' },
                        { id: 'search', icon: Search, label: 'Test Query' },
                        { id: 'settings', icon: Settings, label: 'Settings' }
                    ].map(tab => (
                        <button
                            key={tab.id}
                            className={`btn ${activeTab === tab.id ? 'btn-primary' : 'btn-secondary'}`}
                            onClick={() => setActiveTab(tab.id)}
                        >
                            <tab.icon size={16} style={{ marginRight: '6px' }} />
                            {tab.label}
                        </button>
                    ))}
                </div>

                <div style={{ padding: '24px' }}>
                    {/* Upload Tab */}
                    {activeTab === 'upload' && (
                        <div>
                            <div style={{ marginBottom: '16px' }}>
                                <label style={{ display: 'block', marginBottom: '8px', fontWeight: 500 }}>Target Collection</label>
                                <select
                                    className="input-field"
                                    value={selectedCollection}
                                    onChange={e => setSelectedCollection(e.target.value)}
                                    style={{ maxWidth: '300px' }}
                                >
                                    <option value="kb">Knowledge Base</option>
                                    <option value="tickets">Ticket History</option>
                                    <option value="sop">SOP Documents</option>
                                </select>
                            </div>

                            <div
                                style={{
                                    border: '2px dashed var(--border-color)',
                                    borderRadius: '12px',
                                    padding: '48px',
                                    textAlign: 'center',
                                    cursor: 'pointer',
                                    transition: 'all 0.2s'
                                }}
                                onClick={() => document.getElementById('file-upload').click()}
                            >
                                <input
                                    type="file"
                                    id="file-upload"
                                    accept=".pdf,.txt,.md,.json"
                                    style={{ display: 'none' }}
                                    onChange={handleFileUpload}
                                />
                                <Upload size={48} style={{ color: 'var(--accent-primary)', marginBottom: '16px' }} />
                                <h3 style={{ margin: '0 0 8px' }}>Drop files here or click to upload</h3>
                                <p style={{ color: 'var(--text-muted)', margin: 0 }}>Supports PDF, TXT, MD, JSON</p>
                            </div>

                            {uploadStatus && (
                                <div style={{
                                    marginTop: '16px',
                                    padding: '12px 16px',
                                    borderRadius: '8px',
                                    display: 'flex',
                                    alignItems: 'center',
                                    gap: '8px',
                                    background: uploadStatus.status === 'success' ? 'rgba(34, 197, 94, 0.1)' :
                                        uploadStatus.status === 'error' ? 'rgba(239, 68, 68, 0.1)' :
                                            'rgba(99, 102, 241, 0.1)'
                                }}>
                                    {uploadStatus.status === 'success' ? <CheckCircle color="#22c55e" size={20} /> :
                                        uploadStatus.status === 'error' ? <AlertCircle color="#ef4444" size={20} /> :
                                            <RefreshCw className="spin" color="#6366f1" size={20} />}
                                    <span>{uploadStatus.message}</span>
                                </div>
                            )}

                            {chunkPreview.length > 0 && (
                                <div style={{ marginTop: '24px' }}>
                                    <h4 style={{ marginBottom: '12px' }}>📄 Chunk Preview</h4>
                                    <div style={{ maxHeight: '200px', overflow: 'auto', background: 'var(--bg-base)', padding: '16px', borderRadius: '8px' }}>
                                        {chunkPreview.slice(0, 3).map((chunk, i) => (
                                            <div key={i} style={{ marginBottom: '12px', padding: '8px', background: 'var(--bg-card)', borderRadius: '4px' }}>
                                                <span className="badge badge-primary" style={{ marginBottom: '4px' }}>Chunk {i + 1}</span>
                                                <p style={{ margin: 0, fontSize: '13px', color: 'var(--text-muted)' }}>{chunk.substring(0, 150)}...</p>
                                            </div>
                                        ))}
                                    </div>
                                </div>
                            )}
                        </div>
                    )}

                    {/* Test Query Tab */}
                    {activeTab === 'search' && (
                        <div>
                            <div style={{ display: 'flex', gap: '12px', marginBottom: '16px' }}>
                                <input
                                    type="text"
                                    className="input-field"
                                    placeholder="Enter test query..."
                                    value={testQuery}
                                    onChange={e => setTestQuery(e.target.value)}
                                    onKeyPress={e => e.key === 'Enter' && handleTestQuery()}
                                    style={{ flex: 1 }}
                                />
                                <select
                                    className="input-field"
                                    value={selectedCollection}
                                    onChange={e => setSelectedCollection(e.target.value)}
                                    style={{ width: '180px' }}
                                >
                                    <option value="kb">Knowledge Base</option>
                                    <option value="tickets">Tickets</option>
                                    <option value="sop">SOPs</option>
                                </select>
                                <button className="btn btn-primary" onClick={handleTestQuery} disabled={isSearching}>
                                    <Search size={16} style={{ marginRight: '6px' }} />
                                    {isSearching ? 'Searching...' : 'Search'}
                                </button>
                            </div>

                            {testResults.length > 0 && (
                                <div className="table-container">
                                    <table className="table">
                                        <thead>
                                            <tr>
                                                <th>#</th>
                                                <th>Title</th>
                                                <th>Score</th>
                                                <th>Preview</th>
                                            </tr>
                                        </thead>
                                        <tbody>
                                            {testResults.map((result, i) => (
                                                <tr key={i}>
                                                    <td>{i + 1}</td>
                                                    <td>{result.metadata?.title || result.metadata?.doc_id || 'N/A'}</td>
                                                    <td>
                                                        <span className={`badge ${result.score >= 0.8 ? 'badge-success' : result.score >= 0.6 ? 'badge-warning' : 'badge-danger'}`}>
                                                            {(result.score * 100).toFixed(1)}%
                                                        </span>
                                                    </td>
                                                    <td style={{ maxWidth: '300px', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                                                        {result.content?.substring(0, 100)}...
                                                    </td>
                                                </tr>
                                            ))}
                                        </tbody>
                                    </table>
                                </div>
                            )}

                            {testResults.length === 0 && testQuery && !isSearching && (
                                <div style={{ textAlign: 'center', padding: '48px', color: 'var(--text-muted)' }}>
                                    <Search size={48} style={{ marginBottom: '16px', opacity: 0.5 }} />
                                    <p>No results found</p>
                                </div>
                            )}
                        </div>
                    )}

                    {/* Settings Tab */}
                    {activeTab === 'settings' && (
                        <div style={{ maxWidth: '400px' }}>
                            <div style={{ marginBottom: '20px' }}>
                                <label style={{ display: 'block', marginBottom: '8px', fontWeight: 500 }}>Chunk Size (tokens)</label>
                                <input
                                    type="number"
                                    className="input-field"
                                    value={settings.chunkSize}
                                    onChange={e => setSettings({ ...settings, chunkSize: parseInt(e.target.value) })}
                                />
                                <p style={{ fontSize: '13px', color: 'var(--text-muted)', marginTop: '4px' }}>Recommended: 512 tokens</p>
                            </div>

                            <div style={{ marginBottom: '20px' }}>
                                <label style={{ display: 'block', marginBottom: '8px', fontWeight: 500 }}>Chunk Overlap (tokens)</label>
                                <input
                                    type="number"
                                    className="input-field"
                                    value={settings.chunkOverlap}
                                    onChange={e => setSettings({ ...settings, chunkOverlap: parseInt(e.target.value) })}
                                />
                                <p style={{ fontSize: '13px', color: 'var(--text-muted)', marginTop: '4px' }}>Recommended: 50 tokens</p>
                            </div>

                            <div style={{ marginBottom: '20px' }}>
                                <label style={{ display: 'block', marginBottom: '8px', fontWeight: 500 }}>Similarity Threshold</label>
                                <input
                                    type="number"
                                    step="0.1"
                                    min="0"
                                    max="1"
                                    className="input-field"
                                    value={settings.similarityThreshold}
                                    onChange={e => setSettings({ ...settings, similarityThreshold: parseFloat(e.target.value) })}
                                />
                                <p style={{ fontSize: '13px', color: 'var(--text-muted)', marginTop: '4px' }}>Minimum match score (0-1)</p>
                            </div>

                            <button className="btn btn-primary">
                                <CheckCircle size={16} style={{ marginRight: '6px' }} />
                                Save Settings
                            </button>
                        </div>
                    )}
                </div>
            </div>
        </div>
    )
}

export default KnowledgeBase
