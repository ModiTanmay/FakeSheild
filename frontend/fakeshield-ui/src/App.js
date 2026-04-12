import React, { useState, useEffect } from 'react';
import './styles/App.css';
import './styles/pages.css';
import './styles/components.css';
import api from './services/api';
import Home from './pages/Home';
import Scan from './pages/Scan';
import Results from './pages/Results';
import History from './pages/History';
import Navigation from './components/Navigation';

function App() {
  const [currentPage, setCurrentPage] = useState('home');
  const [scanResults, setScanResults] = useState(null);
  const [scanHistory, setScanHistory] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [backendStatus, setBackendStatus] = useState(false);

  useEffect(() => {
    checkBackendStatus();
    loadHistory();
  }, []);

  // Check backend status every 3 seconds
  useEffect(() => {
    const interval = setInterval(() => {
      checkBackendStatus();
    }, 3000);
    
    return () => clearInterval(interval);
  }, []);

  const checkBackendStatus = async () => {
    try {
      console.log('Checking backend health...');
      
      const response = await fetch('http://localhost:8001/api/health', {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
      });
      
      if (response.ok) {
        const data = await response.json();
        console.log('✅ Backend is healthy:', data);
        setBackendStatus(true);
      } else {
        console.log('❌ Backend responded with error:', response.status);
        setBackendStatus(false);
      }
    } catch (error) {
      console.log('❌ Backend health check failed:', error.message);
      setBackendStatus(false);
    }
  };

  const loadHistory = async () => {
    try {
      const response = await api.getHistory();
      if (response.success) {
        setScanHistory(response.data);
      }
    } catch (error) {
      console.error('Failed to load history:', error);
    }
  };

  const handleScan = async (profileUrl, platforms) => {
    setLoading(true);
    setError(null);
    
    try {
      const response = await api.scanProfile(profileUrl, platforms);
      
      if (response.success) {
        setScanResults(response);
        setCurrentPage('results');
        
        setScanHistory([
          {
            scan_id: response.scan_id,
            profile_url: profileUrl,
            timestamp: response.timestamp,
            total_found: response.summary.total_accounts_found,
            platforms: platforms
          },
          ...scanHistory
        ]);
      } else {
        setError(response.error || 'Scan failed');
      }
    } catch (error) {
      console.error('Scan error:', error);
      if (error.code === 'ECONNABORTED') {
        setError('Scan timed out. Please try again or scan a different username.');
      } else if (error.response?.data?.error) {
        setError(error.response.data.error);
      } else {
        setError('Failed to scan. Please check backend logs and try again.');
      }
    } finally {
      setLoading(false);
    }
  };

  const handleNavigate = (page) => {
    setCurrentPage(page);
  };

  const handleViewResult = async (scanId) => {
    setLoading(true);
    setError(null);

    try {
      const response = await api.getResults(scanId);
      if (response.success && response.data) {
        setScanResults(response.data);
        setCurrentPage('results');
      } else {
        setError(response.error || 'Result not found for this scan.');
      }
    } catch (error) {
      console.error('View result error:', error);
      if (error.response?.data?.error) {
        setError(error.response.data.error);
      } else {
        setError('Failed to load scan details. Please try again.');
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="App">
      <Navigation 
        currentPage={currentPage} 
        onNavigate={handleNavigate}
        backendStatus={backendStatus}
      />
      
      {error && (
        <div className="error-banner">
          <p>{error}</p>
          <button onClick={() => setError(null)}>Dismiss</button>
        </div>
      )}
      
      {loading && (
        <div className="loading-overlay">
          <div className="spinner"></div>
          <p>Scanning profile...</p>
        </div>
      )}

      {currentPage === 'home' && (
        <Home onStartScan={() => handleNavigate('scan')} />
      )}

      {currentPage === 'scan' && (
        <Scan 
          onScan={handleScan} 
          loading={loading}
        />
      )}

      {currentPage === 'results' && scanResults && (
        <Results 
          results={scanResults}
          onBackHome={() => handleNavigate('home')}
        />
      )}

      {currentPage === 'history' && (
        <History 
          history={scanHistory}
          onViewResult={handleViewResult}
          onBackHome={() => handleNavigate('home')}
        />
      )}
    </div>
  );
}

export default App;