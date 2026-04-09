
import React from 'react';
import '../styles/pages.css';

function Home({ onStartScan }) {
  return (
    <div className="home-page">
      <div className="home-container">
        <div className="hero-section">
          <div className="logo-container">
            <div className="shield-icon">🛡️</div>
          </div>
          
          <h1 className="hero-title">FAKESHIELD</h1>
          <p className="hero-subtitle">Detect Fake Instagram Accounts</p>
          
          <button 
            className="cta-button"
            onClick={onStartScan}
          >
            Start Scanning Now
          </button>
        </div>

        <div className="features-section">
          <div className="feature-card">
            <div className="feature-icon">🔍</div>
            <h3>What is FakeShield?</h3>
            <p>Advanced AI-powered detector for fake Instagram accounts. Protect your identity and find impersonators instantly.</p>
          </div>

          <div className="feature-card">
            <div className="feature-icon">⚙️</div>
            <h3>How it Works?</h3>
            <p>Analyzes account data using machine learning algorithms to detect suspicious patterns and fake accounts.</p>
          </div>

          <div className="feature-card">
            <div className="feature-icon">✓</div>
            <h3>100% Safe</h3>
            <p>No login required. Your data is secure and private. We never store personal information.</p>
          </div>
        </div>

        <div className="info-section">
          <h2>Why Use FakeShield?</h2>
          <ul className="info-list">
            <li>Instant detection of impersonation accounts</li>
            <li>Check multiple social media platforms</li>
            <li>Get detailed risk analysis for each account</li>
            <li>Free and completely private</li>
            <li>No technical knowledge required</li>
          </ul>
        </div>
      </div>
    </div>
  );
}

export default Home;
