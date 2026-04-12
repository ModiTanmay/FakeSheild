import axios from 'axios';

const API_BASE_URL = 'http://localhost:8001/api';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  // Real scraping can take tens of seconds depending on Apify/Mongo latency.
  timeout: 300000,
});

export const api = {
  
  healthCheck: async () => {
    try {
      const response = await fetch('http://localhost:8001/api/health', {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
      });
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      const data = await response.json();
      console.log('Health check successful:', data);
      return data;
    } catch (error) {
      console.error('Health check failed:', error);
      throw error;
    }
  },

  scanProfile: async (profileUrl, platforms = ['instagram', 'twitter']) => {
    try {
      const response = await apiClient.post('/detect-impersonation', {
        profile_url: profileUrl,
        platforms: platforms,
      });
      return response.data;
    } catch (error) {
      console.error('Scan failed:', error);
      throw error;
    }
  },

  getHistory: async () => {
    try {
      const response = await apiClient.get('/history');
      return response.data;
    } catch (error) {
      console.error('Failed to get history:', error);
      throw error;
    }
  },

  getResults: async (scanId) => {
    try {
      const response = await apiClient.get(`/results/${scanId}`);
      return response.data;
    } catch (error) {
      console.error('Failed to get results:', error);
      throw error;
    }
  },

  reportAccount: async (username, platform, reason) => {
    try {
      const response = await apiClient.post('/report', {
        username: username,
        platform: platform,
        reason: reason,
      });
      return response.data;
    } catch (error) {
      console.error('Report failed:', error);
      throw error;
    }
  },
};

export default api;