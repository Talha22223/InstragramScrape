import React, { useState } from 'react';
import './App.css';
import UrlInput from './components/UrlInput';
import Dashboard from './components/Dashboard';
import LoadingSpinner from './components/LoadingSpinner';
import { ToastContainer, toast } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';
import { FaInstagram } from 'react-icons/fa';

function App() {
  const [analysisData, setAnalysisData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [analysisType, setAnalysisType] = useState('single'); // 'single' or 'profile'

  const handleAnalyze = async (data) => {
    setLoading(true);
    setAnalysisData(null);
    setAnalysisType(data.type);

    try {
      const API_BASE_URL = process.env.REACT_APP_API_URL || '';
      let endpoint = `${API_BASE_URL}/api/analyze`;
      let body = {};

      if (data.type === 'single') {
        endpoint = `${API_BASE_URL}/api/analyze`;
        body = { url: data.url };
      } else {
        endpoint = `${API_BASE_URL}/api/analyze-profile`;
        body = {
          profile_url: data.profile_url,
          from_date: data.from_date,
          max_posts: data.max_posts
        };
      }

      const response = await fetch(endpoint, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(body),
      });

      const result = await response.json();

      if (result.success) {
        setAnalysisData({ ...result.data, type: data.type });
        toast.success(data.type === 'profile' 
          ? `Analysis completed! Analyzed ${result.data.total_posts} posts with ${result.data.total_comments} comments.`
          : 'Analysis completed successfully!');
      } else {
        toast.error(result.error || 'Analysis failed');
      }
    } catch (error) {
      console.error('Error:', error);
      toast.error('Failed to connect to server. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleReset = () => {
    setAnalysisData(null);
  };

  return (
    <div className="App">
      <ToastContainer
        position="top-right"
        autoClose={3000}
        hideProgressBar={false}
        newestOnTop
        closeOnClick
        rtl={false}
        pauseOnFocusLoss
        draggable
        pauseOnHover
        theme="dark"
      />
      
      <header className="app-header">
        <div className="header-content">
          <FaInstagram className="header-icon" />
          <h1>Instagram Comment Analyzer</h1>
          <p>AI-Powered Sentiment Analysis & Topic Classification</p>
        </div>
      </header>

      <main className="app-main">
        {!analysisData && !loading && (
          <div className="input-section">
            <UrlInput onAnalyze={handleAnalyze} />
          </div>
        )}

        {loading && (
          <div className="loading-section">
            <LoadingSpinner />
          </div>
        )}

        {analysisData && !loading && (
          <div className="dashboard-section">
            <Dashboard data={analysisData} onReset={handleReset} />
          </div>
        )}
      </main>

      <footer className="app-footer">
        <p>Powered by BERT AI Model & Apify API</p>
      </footer>
    </div>
  );
}

export default App;
