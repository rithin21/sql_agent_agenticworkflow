import React, { useState } from 'react';

export default function Mainpage(props) {
    const [showinput, setShowinput] = useState(false);
    const [connectionString, setConnectionString] = useState("");
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState("");

    const handleConnect = async () => {
        setLoading(true);
        setError("");
        try {
            const res = await fetch('http://localhost:8000/verifyconnection', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ connection_link: connectionString })
            });

            const data = await res.json();

            if (res.status === 200) {
                props.setConnectionstatus(true);
                props.setConnectionName(data.connection_name || "Database");
                props.setConnectionURL(connectionString);
            } else {
                setError(data.detail || "Failed to establish a connection to the database.");
            }
        } catch (err) {
            setError("Could not connect to the backend server. Make sure the FastAPI app is running.");
        } finally {
            setLoading(false);
        }
    };

    const handleUsePreset = (preset) => {
        setConnectionString(preset);
        setShowinput(true);
    };

    return (
        <div className="container py-5 d-flex flex-column align-items-center justify-content-center" style={{ minHeight: 'calc(100vh - 80px)' }}>
            <div className="card-landing-page text-center">
                <div className="d-flex justify-content-center mb-4">
                    <div className="p-3 bg-light rounded-circle shadow-sm" style={{ width: '80px', height: '80px', display: 'flex', alignItems: 'center', justify: 'center' }}>
                        <svg xmlns="http://www.w3.org/2000/svg" width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="#4f46e5" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="lucide lucide-bot">
                          <path d="M12 8V4H8"/>
                          <rect width="16" height="12" x="4" y="8" rx="2"/>
                          <path d="M2 14h2"/>
                          <path d="M20 14h2"/>
                          <path d="M15 13v2"/>
                          <path d="M9 13v2"/>
                        </svg>
                    </div>
                </div>
                <h1 className="display-5 fw-bold mb-3" style={{ color: 'var(--secondary-color)' }}>Connect to Your Database</h1>
                <p className="lead text-muted mb-4 mx-auto" style={{ maxWidth: '600px' }}>
                    Welcome to SQL Agent. Simply hook up your SQLite or PostgreSQL connection string, and chat with your database to get insights, query columns, or list schemas in real-time.
                </p>

                <div className="chip-container justify-content-center mb-4">
                    <span className="text-muted align-self-center me-2" style={{ fontSize: '0.85rem' }}>Presets:</span>
                    <button className="chip-suggestion" onClick={() => handleUsePreset("sqlite:///test_agent.db")}>SQLite (Local Test)</button>
                    <button className="chip-suggestion" onClick={() => handleUsePreset("postgresql://postgres:21wdspvabd@localhost:5432/sql_agent_demo")}>PostgreSQL</button>
                </div>

                {!showinput ? (
                    <button className="btn btn-premium btn-lg" onClick={() => setShowinput(true)}>
                        Get Started
                    </button>
                ) : (
                    <div className="w-100 mx-auto" style={{ maxWidth: '550px' }}>
                        <div className="input-group shadow-sm">
                            <input 
                                type="text" 
                                className="form-control input-premium border-end-0" 
                                placeholder="e.g. sqlite:///test_agent.db" 
                                value={connectionString} 
                                onChange={(e) => setConnectionString(e.target.value)}
                                disabled={loading}
                            />
                            <button 
                                className="btn btn-premium px-4" 
                                onClick={handleConnect}
                                disabled={loading || !connectionString.trim()}
                            >
                                {loading ? (
                                    <>
                                        <span className="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>
                                        Connecting...
                                    </>
                                ) : 'Connect'}
                            </button>
                        </div>
                        {error && (
                            <div className="alert alert-danger mt-3 text-start border-0 shadow-sm" role="alert" style={{ fontSize: '0.9rem', borderRadius: '10px' }}>
                                <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="lucide lucide-alert-circle me-2 align-text-bottom">
                                    <circle cx="12" cy="12" r="10"/>
                                    <line x1="12" x2="12" y1="8" y2="12"/>
                                    <line x1="12" x2="12" y1="16" y2="16"/>
                                </svg>
                                {error}
                            </div>
                        )}
                    </div>
                )}
            </div>
        </div>
    );
}
