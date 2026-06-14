import React from 'react';

export default function Navbar({ connectionStatus, connectionName }) {
  return (
    <nav className="navbar navbar-expand-lg navbar-premium py-3">
      <div className="container px-4 d-flex justify-content-between align-items-center">
        <a className="navbar-brand brand-title m-0" href="#">
          <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round" className="lucide lucide-database text-primary">
            <ellipse cx="12" cy="5" rx="9" ry="3"/>
            <path d="M3 5V19A9 3 0 0 0 21 19V5"/>
            <path d="M3 12A9 3 0 0 0 21 12"/>
          </svg>
          SQL Agent
        </a>
        <div className="d-flex align-items-center">
          {connectionStatus ? (
            <span className="connection-badge connected">
              <span className="spinner-grow spinner-grow-sm" style={{ width: '8px', height: '8px' }} role="status"></span>
              Connected: {connectionName}
            </span>
          ) : (
            <span className="connection-badge disconnected">
              ● Disconnected
            </span>
          )}
        </div>
      </div>
    </nav>
  );
}
