import React from 'react';
import './LoadingSpinner.css';

const LoadingSpinner = () => {
  return (
    <div className="loading-container">
      <div className="spinner-wrapper">
        <div className="spinner"></div>
        <div className="loading-text">
          <h2>Analyzing Comments...</h2>
          <p>Scraping Instagram data and performing AI analysis</p>
          <div className="loading-steps">
            <div className="step">
              <div className="step-icon">📥</div>
              <span>Fetching comments</span>
            </div>
            <div className="step">
              <div className="step-icon">🤖</div>
              <span>AI Sentiment Analysis</span>
            </div>
            <div className="step">
              <div className="step-icon">🏷️</div>
              <span>Topic Classification</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default LoadingSpinner;
