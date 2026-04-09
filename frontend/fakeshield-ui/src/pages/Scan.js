

import React, { useState } from 'react';
import '../styles/pages.css';

function Scan({ onScan, loading }) {
  const [profileUrl, setProfileUrl] = useState('');
  const [platforms, setPlatforms] = useState({
    instagram: true,
    twitter: false,
    linkedin: false,
  });
  const [error, setError] = useState('');

  const handlePlatformChange = (platform) => {
    setPlatforms({
      ...platforms,
      [platform]: !platforms[platform],
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');

    if (!profileUrl.trim()) {
      setError('Please enter an Instagram username or URL');
      return;
    }

    const selectedPlatforms = Object.keys(platforms).filter(
      (platform) => platforms[platform]
    );

    if (selectedPlatforms.length === 0) {
      setError('Please select at least one platform');
      return;
    }

    await onScan(profileUrl.trim(), selectedPlatforms);
  };

  return (
    <div className="scan-page">
      <div className="scan-container">
        <div className="scan-header">
          <h1>Scan for Fake Accounts</h1>
          <p>Enter an Instagram username or profile URL to get started</p>
        </div>

        <form onSubmit={handleSubmit} className="scan-form">
          <div className="form-group">
            <label htmlFor="profileUrl">Instagram Username or URL</label>
            <input
              id="profileUrl"
              type="text"
              placeholder="Enter username (e.g., @john_doe) or URL"
              value={profileUrl}
              onChange={(e) => setProfileUrl(e.target.value)}
              disabled={loading}
              className="form-input"
            />
            <small className="form-hint">
              You can enter a username like @john_doe or a full URL like instagram.com/john_doe
            </small>
          </div>

          <div className="form-group">
            <label>Select Platforms to Scan</label>
            <div className="platforms-list">
              <div className="platform-checkbox">
                <input
                  id="instagram"
                  type="checkbox"
                  checked={platforms.instagram}
                  onChange={() => handlePlatformChange('instagram')}
                  disabled={loading}
                />
                <label htmlFor="instagram">Instagram</label>
              </div>

              <div className="platform-checkbox">
                <input
                  id="twitter"
                  type="checkbox"
                  checked={platforms.twitter}
                  onChange={() => handlePlatformChange('twitter')}
                  disabled={loading}
                />
                <label htmlFor="twitter">Twitter</label>
              </div>

              <div className="platform-checkbox">
                <input
                  id="linkedin"
                  type="checkbox"
                  checked={platforms.linkedin}
                  onChange={() => handlePlatformChange('linkedin')}
                  disabled={loading}
                />
                <label htmlFor="linkedin">LinkedIn</label>
              </div>
            </div>
          </div>

          {error && <div className="form-error">{error}</div>}

          <button
            type="submit"
            className="submit-button"
            disabled={loading}
          >
            {loading ? 'Scanning...' : 'Scan for Fakes'}
          </button>
        </form>

        <div className="scan-info">
          <h3>How the scan works:</h3>
          <ol>
            <li>Enter your Instagram username or profile URL</li>
            <li>Select which platforms you want to scan</li>
            <li>Click "Scan for Fakes" to start the analysis</li>
            <li>Get detailed results about suspicious accounts</li>
            <li>View risk levels and reasons for each finding</li>
          </ol>
        </div>
      </div>
    </div>
  );
}

export default Scan;
