
import React from 'react';
import '../styles/components.css';

function Navigation({ currentPage, onNavigate, backendStatus }) {
  return (
    <nav className="navbar">
      <div className="nav-container">
        <div className="nav-brand">
          <div className="nav-logo">🛡️</div>
          <h1 className="nav-title">FakeShield</h1>
        </div>

        <ul className="nav-menu">
          <li className="nav-item">
            <button
              className={`nav-link ${currentPage === 'home' ? 'active' : ''}`}
              onClick={() => onNavigate('home')}
            >
              Home
            </button>
          </li>

          <li className="nav-item">
            <button
              className={`nav-link ${currentPage === 'scan' ? 'active' : ''}`}
              onClick={() => onNavigate('scan')}
            >
              Scan
            </button>
          </li>

          <li className="nav-item">
            <button
              className={`nav-link ${currentPage === 'history' ? 'active' : ''}`}
              onClick={() => onNavigate('history')}
            >
              History
            </button>
          </li>
        </ul>

        <div className="nav-status">
          <div className={`status-indicator ${backendStatus ? 'online' : 'offline'}`}>
            <span className="status-dot"></span>
            <span className="status-text">
              {backendStatus ? 'Online' : 'Offline'}
            </span>
          </div>
        </div>
      </div>
    </nav>
  );
}

export default Navigation;
