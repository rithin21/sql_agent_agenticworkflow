import React, { useState, useRef, useEffect } from 'react';

export default function Querypage(props) {
    const [prompt, setPrompt] = useState("");
    const [chatHistory, setChatHistory] = useState([
        {
            role: 'assistant',
            content: `Database connection established! I am connected to: "${props.ConnectionName}". You can ask me anything about the database tables, schema, or request to execute SQL queries.`
        }
    ]);
    const [loading, setLoading] = useState(false);
    const chatEndRef = useRef(null);

    const scrollToBottom = () => {
        chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    };

    useEffect(() => {
        scrollToBottom();
    }, [chatHistory, loading]);

    const handleSend = async (textToSend) => {
        const queryText = textToSend || prompt;
        if (!queryText.trim()) return;

        setLoading(true);
        if (!textToSend) setPrompt("");

        // Add user query to history
        setChatHistory(prev => [...prev, { role: 'user', content: queryText }]);

        try {
            const res = await fetch('http://localhost:8000/process_query', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    prompt: queryText,
                    connectionString: props.ConnectionString
                })
            });

            const data = await res.json();
            
            // Add assistant answer to history
            setChatHistory(prev => [...prev, { 
                role: 'assistant', 
                content: data.answer, 
                tableData: data.data 
            }]);
        }
        catch (err) {
            console.error(err);
            setChatHistory(prev => [...prev, { 
                role: 'assistant', 
                content: "Error: Failed to process the query. Please check if the backend FastAPI server is running." 
            }]);
        }
        finally {
            setLoading(false);
        }
    };

    const handleKeyDown = (e) => {
        if (e.key === 'Enter') {
            handleSend();
        }
    };

    const suggestions = [
        "What tables are in the database?",
        "Show columns and schema for all tables",
        "Select the first 5 records from users"
    ];

    return (
        <div className="container py-4" style={{ maxWidth: '950px' }}>
            <div className="card-query-page p-4 mb-4">
                <div className="d-flex align-items-center gap-3">
                    <div className="p-2 bg-primary-subtle rounded-3">
                        <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="var(--primary-color)" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="lucide lucide-terminal">
                          <polyline points="4 17 10 11 4 5"/>
                          <line x1="12" x2="20" y1="19" y2="19"/>
                        </svg>
                    </div>
                    <div>
                        <h4 className="mb-0 fw-bold">SQL Chat Assistant</h4>
                        <p className="text-muted mb-0" style={{ fontSize: '0.9rem' }}>
                            Ask natural language questions to generate and run SQL queries against <strong>{props.ConnectionName}</strong>.
                        </p>
                    </div>
                </div>
            </div>

            {/* Chat History View */}
            <div className="chat-history shadow-sm mb-4">
                {chatHistory.map((msg, index) => (
                    <div 
                        key={index} 
                        className={`chat-bubble ${msg.role === 'user' ? 'chat-bubble-user' : 'chat-bubble-assistant'}`}
                    >
                        {/* Message Text */}
                        <p className="mb-0 fw-medium" style={{ whiteSpace: 'pre-line', fontSize: '0.95rem' }}>
                            {msg.content}
                        </p>

                        {/* Executed Data Table (if available) */}
                        {Array.isArray(msg.tableData) && (
                            msg.tableData.length > 0 ? (
                                <div className="table-responsive mt-3">
                                    <table className="table table-premium mb-0">
                                        <thead>
                                            <tr>
                                                {Object.keys(msg.tableData[0]).map(key => (
                                                    <th key={key}>{key}</th>
                                                ))}
                                            </tr>
                                        </thead>
                                        <tbody>
                                            {msg.tableData.map((row, rowIndex) => (
                                                <tr key={rowIndex}>
                                                    {Object.values(row).map((val, cellIndex) => (
                                                        <td key={cellIndex}>
                                                            {val !== null && val !== undefined ? String(val) : <em className="text-muted">NULL</em>}
                                                        </td>
                                                    ))}
                                                </tr>
                                            ))}
                                        </tbody>
                                    </table>
                                </div>
                            ) : (
                                <div className="alert alert-light mt-3 mb-0 py-2 border text-dark" style={{ fontSize: '0.85rem', borderRadius: '8px' }}>
                                    ✓ Query executed successfully. No records were returned.
                                </div>
                            )
                        )}
                    </div>
                ))}
                
                {/* Loading indicator inside history */}
                {loading && (
                    <div className="chat-bubble chat-bubble-assistant align-self-start d-flex align-items-center gap-2">
                        <span className="spinner-grow spinner-grow-sm text-primary" role="status" aria-hidden="true"></span>
                        <span className="text-muted" style={{ fontSize: '0.9rem' }}>Thinking & running SQL...</span>
                    </div>
                )}
                <div ref={chatEndRef} />
            </div>

            {/* Quick Prompt Suggestions */}
            <div className="mb-3 px-2">
                <span className="text-muted me-2" style={{ fontSize: '0.85rem', fontWeight: '500' }}>Suggestions:</span>
                <div className="chip-container d-inline-flex gap-2">
                    {suggestions.map((s, idx) => (
                        <button 
                            key={idx} 
                            className="chip-suggestion" 
                            onClick={() => handleSend(s)}
                            disabled={loading}
                        >
                            {s}
                        </button>
                    ))}
                </div>
            </div>

            {/* Chat Input controls */}
            <div className="d-flex gap-2">
                <input
                    type="text"
                    className="form-control input-premium flex-grow-1 shadow-sm"
                    placeholder="Ask standard questions or type SQL (e.g. Find users with email containing bob)..."
                    value={prompt}
                    onChange={(e) => setPrompt(e.target.value)}
                    onKeyDown={handleKeyDown}
                    disabled={loading}
                />
                <button
                    className="btn btn-premium px-4 shadow-sm"
                    onClick={() => handleSend()}
                    disabled={loading || !prompt.trim()}
                >
                    <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round" className="lucide lucide-send">
                        <line x1="22" x2="11" y1="2" y2="13"/>
                        <polygon points="22 2 15 22 11 13 2 9 22 2"/>
                    </svg>
                </button>
            </div>
        </div>
    );
}