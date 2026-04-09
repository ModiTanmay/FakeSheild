import React from 'react';
import '../styles/pages.css';

function Results({ results, onBackHome }) {
  if (!results) {
    return <div className="results-page">No results available</div>;
  }

  const { summary = {}, results: scanResults = {} } = results;

  const getRiskColor = (riskLevel) => {
    switch (riskLevel) {
      case 'HIGH':
        return '#FF6B6B';
      case 'MEDIUM':
        return '#FFA500';
      case 'LOW':
        return '#4CAF50';
      default:
        return '#999';
    }
  };

  return (
    <div className="results-page">
      <div className="results-container">
        <div className="results-header">
          <h1>Scan Results</h1>
          <p>Analysis complete - Review the findings below</p>
          <button className="back-button" onClick={onBackHome}>
            ← Back to Home
          </button>
        </div>

        <div className="summary-section">
          <h2>Summary</h2>
          <div className="summary-cards">
            <div className="summary-card">
              <div className="summary-number">{summary.total_accounts_found || 0}</div>
              <div className="summary-label">Total Found</div>
            </div>

            <div className="summary-card high-risk">
              <div className="summary-number">{summary.high_risk || 0}</div>
              <div className="summary-label">High Risk</div>
            </div>

            <div className="summary-card medium-risk">
              <div className="summary-number">{summary.medium_risk || 0}</div>
              <div className="summary-label">Medium Risk</div>
            </div>

            <div className="summary-card platforms">
              <div className="summary-number">{summary.platforms_scanned || 0}</div>
              <div className="summary-label">Platforms Scanned</div>
            </div>
          </div>
        </div>

        <div className="detailed-results">
          {scanResults && Object.entries(scanResults).length > 0 ? (
            Object.entries(scanResults).map(([platform, data]) => (
              <div key={platform} className="platform-section">
                <h3 className="platform-title">
                  {platform.charAt(0).toUpperCase() + platform.slice(1)}
                </h3>

                {!data || data.found === 0 ? (
                  <p className="no-results">No suspicious accounts found on {platform}</p>
                ) : (
                  <div className="accounts-list">
                    {data.fake_accounts && data.fake_accounts.map((account, index) => (
                      <div key={index} className="account-card">
                        <div className="account-header">
                          <div className="account-info">
                            <h4>{account.username}</h4>
                            <p className="followers">{account.followers} followers</p>
                          </div>
                          <div
                            className="risk-badge"
                            style={{ backgroundColor: getRiskColor(account.risk_level) }}
                          >
                            {account.risk_level}
                          </div>
                        </div>

                        <div className="confidence-bar">
                          <div className="confidence-fill" style={{
                            width: `${account.confidence}%`,
                            backgroundColor: getRiskColor(account.risk_level)
                          }}></div>
                          <span className="confidence-text">
                            {account.confidence}% confidence
                          </span>
                        </div>

                        <div className="reasons">
                          <h5>Why flagged:</h5>
                          <ul>
                            {account.reasons && account.reasons.map((reason, idx) => (
                              <li key={idx}>{reason}</li>
                            ))}
                          </ul>
                        </div>

                        {account.url && (
                          <a
                            href={account.url}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="view-account-link"
                          >
                            View Account →
                          </a>
                        )}
                      </div>
                    ))}
                  </div>
                )}
              </div>
            ))
          ) : (
            <p className="no-results">No detailed results available</p>
          )}
        </div>

        <div className="results-actions">
          <button className="action-button report-button">
            Report These Accounts
          </button>
          <button className="action-button download-button">
            Download Report
          </button>
          <button className="action-button scan-button" onClick={onBackHome}>
            Scan Another Profile
          </button>
        </div>
      </div>
    </div>
  );
}

export default Results;