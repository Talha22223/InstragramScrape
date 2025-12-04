import React, { useState } from 'react';
import './UrlInput.css';
import { FaInstagram, FaFacebook, FaSearch, FaCalendar, FaUser } from 'react-icons/fa';

const UrlInput = ({ onAnalyze }) => {
  const [platform, setPlatform] = useState('instagram'); // 'instagram' or 'facebook'
  const [mode, setMode] = useState('single'); // 'single' or 'profile'
  const [url, setUrl] = useState('');
  const [profileUrl, setProfileUrl] = useState('');
  const [fromDate, setFromDate] = useState('');
  const [maxPosts, setMaxPosts] = useState(20);
  const [error, setError] = useState('');

  const validateInstagramPostUrl = (url) => {
    const instagramRegex = /^https?:\/\/(www\.)?instagram\.com\/(p|reel)\/[\w-]+\/?/;
    return instagramRegex.test(url);
  };

  const validateInstagramProfileUrl = (url) => {
    const profileRegex = /^https?:\/\/(www\.)?instagram\.com\/[\w.]+\/?$/;
    return profileRegex.test(url);
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    setError('');

    if (mode === 'single') {
      if (!url.trim()) {
        setError('Please enter an Instagram URL');
        return;
      }

      if (!validateInstagramPostUrl(url)) {
        setError('Please enter a valid Instagram post or reel URL');
        return;
      }

      onAnalyze({ type: 'single', url });
    } else {
      if (!profileUrl.trim()) {
        setError('Please enter an Instagram profile URL');
        return;
      }

      if (!validateInstagramProfileUrl(profileUrl)) {
        setError('Please enter a valid Instagram profile URL (e.g., https://www.instagram.com/username/)');
        return;
      }

      if (!fromDate) {
        setError('Please select a start date');
        return;
      }

      onAnalyze({ 
        type: 'profile', 
        profile_url: profileUrl, 
        from_date: fromDate,
        max_posts: maxPosts 
      });
    }
  };

  return (
    <div className="url-input-container">
      <div className="url-input-card">
        <div className={`card-icon ${platform === 'instagram' ? 'insta-logo' : 'fb-logo'}`}>
          {platform === 'instagram' ? <FaInstagram /> : <FaFacebook />}
        </div>
        
        <h2>Analyze {platform === 'instagram' ? 'Instagram' : 'Facebook'} Comments</h2>
        <p className="subtitle">
          Choose platform and analysis mode
        </p>

        {/* Platform Selection */}
        <div className="mode-selector">
          <button 
            type="button"
            className={`mode-btn ${platform === 'instagram' ? 'active' : ''}`}
            onClick={() => {
              setPlatform('instagram');
              setUrl('');
              setProfileUrl('');
              setError('');
            }}
          >
            <FaInstagram /> Instagram
          </button>
          <button 
            type="button"
            className={`mode-btn ${platform === 'facebook' ? 'active' : ''}`}
            onClick={() => {
              setPlatform('facebook');
              setUrl('');
              setProfileUrl('');
              setError('');
            }}
          >
            <FaFacebook /> Facebook
          </button>
        </div>

        {/* Mode Selection */}
        <div className="mode-selector">
          <button 
            type="button"
            className={`mode-btn ${mode === 'single' ? 'active' : ''}`}
            onClick={() => setMode('single')}
          >
            {platform === 'instagram' ? <FaInstagram /> : <FaFacebook />} Single Post
          </button>
          <button 
            type="button"
            className={`mode-btn ${mode === 'profile' ? 'active' : ''}`}
            onClick={() => setMode('profile')}
          >
            <FaUser /> {platform === 'instagram' ? 'Profile' : 'Group/Page'} (Bulk)
          </button>
        </div>

        <form onSubmit={handleSubmit} className="url-form">
          {mode === 'single' ? (
            <div className="input-wrapper">
              {platform === 'instagram' ? <FaInstagram className="input-icon" /> : <FaFacebook className="input-icon" />}
              <input
                type="text"
                value={url}
                onChange={(e) => setUrl(e.target.value)}
                placeholder={platform === 'instagram' 
                  ? "https://www.instagram.com/p/xxxxx or /reel/xxxxx"
                  : "https://www.facebook.com/post-url"}
                className={error ? 'input-error' : ''}
              />
            </div>
          ) : (
            <>
              <div className="input-wrapper">
                <FaUser className="input-icon" />
                <input
                  type="text"
                  value={profileUrl}
                  onChange={(e) => setProfileUrl(e.target.value)}
                  placeholder={platform === 'instagram'
                    ? "https://www.instagram.com/username/"
                    : "https://www.facebook.com/group-or-page-url"}
                  className={error ? 'input-error' : ''}
                />
              </div>
              
              <div className="date-posts-row">
                <div className="input-wrapper date-input">
                  <FaCalendar className="input-icon" />
                  <input
                    type="date"
                    value={fromDate}
                    onChange={(e) => setFromDate(e.target.value)}
                    max={new Date().toISOString().split('T')[0]}
                    className={error ? 'input-error' : ''}
                  />
                  <label className="input-label">From Date</label>
                </div>
                
                <div className="input-wrapper posts-input">
                  <input
                    type="number"
                    value={maxPosts}
                    onChange={(e) => setMaxPosts(Math.max(1, Math.min(50, parseInt(e.target.value) || 20)))}
                    min="1"
                    max="50"
                    className="small-input"
                  />
                  <label className="input-label">Max Posts</label>
                </div>
              </div>
            </>
          )}

          {error && <div className="error-message">{error}</div>}

          <button type="submit" className="analyze-button">
            <FaSearch />
            <span>{mode === 'single' ? 'Analyze Post' : 'Analyze Profile'}</span>
          </button>
        </form>

        <div className="info-section">
          <h3>What we analyze:</h3>
          <ul className="features-list">
            <li>✓ Sentiment Analysis (Positive/Negative/Neutral)</li>
            <li>✓ Topic Classification for Negative Comments</li>
            <li>✓ {mode === 'profile' ? 'Bulk analysis of all posts from date' : 'Single post analysis'}</li>
            <li>✓ {platform === 'instagram' ? 'Instagram' : 'Facebook'} posts and comments</li>
            <li>✓ Beautiful Visual Dashboard</li>
          </ul>
        </div>
      </div>
    </div>
  );
};

export default UrlInput;
