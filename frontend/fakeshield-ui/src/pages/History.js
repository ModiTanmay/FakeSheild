

import React from 'react';
import '../styles/pages.css';

function History({ history, onViewResult, onBackHome }) {
  const formatDate = (timestamp) => {
    const date = new Date(timestamp);
    return date.toLocaleDateString() + ' ' + date.toLocaleTimeString();
  };

  return (
    <div className="history-page">
      <div className="history-container">
        <div className="history-header">
          <h1>Scan History</h1>
          <p>Your previous scans and results</p>
          <button className="back-button" onClick={onBackHome}>
            ← Back to Home
          </button>
        </div>

        {history.length === 0 ? (
          <div className="empty-history">
            <div className="empty-icon">📋</div>
            <h2>No scans yet</h2>
            <p>Start scanning profiles to build your history</p>
            <button className="start-scan-button" onClick={onBackHome}>
              Start Your First Scan
            </button>
          </div>
        ) : (
          <div className="history-list">
            {history.map((scan, index) => (
              <div key={index} className="history-item">
                <div className="history-item-left">
                  <h3>{scan.profile_url}</h3>
                  <p className="scan-date">{formatDate(scan.timestamp)}</p>
                  <div className="platforms-tags">
                    {scan.platforms.map((platform) => (
                      <span key={platform} className="platform-tag">
                        {platform}
                      </span>
                    ))}
                  </div>
                </div>

                <div className="history-item-right">
                  <div className="results-summary">
                    <div className="summary-stat">
                      <span className="stat-label">Found</span>
                      <span className="stat-value">{scan.total_found}</span>
                    </div>
                  </div>

                  <button
                    className="view-button"
                    onClick={() => onViewResult(scan.scan_id)}
                  >
                    View Results →
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}

        <div className="history-actions">
          <button className="action-button" onClick={onBackHome}>
            Scan Another Profile
          </button>
          <button className="action-button clear-button">
            Clear History
          </button>
        </div>
      </div>
    </div>
  );
}

export default History;
