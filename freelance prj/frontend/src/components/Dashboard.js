import React, { useState } from 'react';
import './Dashboard.css';
import StatCard from './StatCard';
import SentimentChart from './SentimentChart';
import TopicChart from './TopicChart';
import CommentsList from './CommentsList';
import { FaChartPie, FaComments, FaSmile, FaFrown, FaMeh, FaRedo } from 'react-icons/fa';
import { motion } from 'framer-motion';

const Dashboard = ({ data, onReset }) => {
  const [activeTab, setActiveTab] = useState('all');
  
  const isProfileAnalysis = data.type === 'profile';
  const { sentiment_stats, topic_stats, total_comments } = data;
  
  // Handle both single and profile analysis
  const comments = data.all_comments || data.comments || { positive: [], negative: [], neutral: [] };

  const getCommentsForTab = () => {
    switch (activeTab) {
      case 'positive':
        return comments.positive || [];
      case 'negative':
        return comments.negative || [];
      case 'neutral':
        return comments.neutral || [];
      default:
        return [
          ...(comments.positive || []),
          ...(comments.negative || []),
          ...(comments.neutral || [])
        ].sort((a, b) => (b.likes || 0) - (a.likes || 0));
    }
  };

  const containerVariants = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: {
        staggerChildren: 0.1
      }
    }
  };

  const itemVariants = {
    hidden: { y: 20, opacity: 0 },
    visible: {
      y: 0,
      opacity: 1
    }
  };

  return (
    <motion.div 
      className="dashboard-container"
      initial="hidden"
      animate="visible"
      variants={containerVariants}
    >
      <motion.div className="dashboard-header" variants={itemVariants}>
        <h2>Analysis Results</h2>
        {isProfileAnalysis && (
          <div className="profile-info">
            <p><strong>Profile:</strong> {data.profile_url}</p>
            <p><strong>From Date:</strong> {data.from_date}</p>
            <p><strong>Posts Analyzed:</strong> {data.total_posts}</p>
          </div>
        )}
        <button onClick={onReset} className="reset-button">
          <FaRedo /> {isProfileAnalysis ? 'Analyze Another Profile' : 'Analyze Another Post'}
        </button>
      </motion.div>

      <motion.div className="stats-grid" variants={itemVariants}>
        <StatCard
          icon={<FaComments />}
          title="Total Comments"
          value={total_comments}
          color="#667eea"
        />
        <StatCard
          icon={<FaSmile />}
          title="Positive"
          value={`${sentiment_stats.positive_percentage}%`}
          subtitle={`${sentiment_stats.positive} comments`}
          color="#27ae60"
        />
        <StatCard
          icon={<FaFrown />}
          title="Negative"
          value={`${sentiment_stats.negative_percentage}%`}
          subtitle={`${sentiment_stats.negative} comments`}
          color="#e74c3c"
        />
        <StatCard
          icon={<FaMeh />}
          title="Neutral"
          value={`${sentiment_stats.neutral_percentage}%`}
          subtitle={`${sentiment_stats.neutral} comments`}
          color="#95a5a6"
        />
      </motion.div>

      <motion.div className="charts-section" variants={itemVariants}>
        <div className="chart-container">
          <div className="chart-header">
            <FaChartPie />
            <h3>Sentiment Distribution</h3>
          </div>
          <SentimentChart data={sentiment_stats} />
        </div>

        {Object.keys(topic_stats).length > 0 && (
          <div className="chart-container">
            <div className="chart-header">
              <FaChartPie />
              <h3>Negative Comment Topics</h3>
            </div>
            <TopicChart data={topic_stats} />
          </div>
        )}
      </motion.div>

      <motion.div className="comments-section" variants={itemVariants}>
        <div className="comments-header">
          <h3>Comments Details</h3>
          <div className="tabs">
            <button
              className={activeTab === 'all' ? 'active' : ''}
              onClick={() => setActiveTab('all')}
            >
              All ({total_comments})
            </button>
            <button
              className={activeTab === 'positive' ? 'active' : ''}
              onClick={() => setActiveTab('positive')}
            >
              Positive ({sentiment_stats.positive})
            </button>
            <button
              className={activeTab === 'negative' ? 'active' : ''}
              onClick={() => setActiveTab('negative')}
            >
              Negative ({sentiment_stats.negative})
            </button>
            <button
              className={activeTab === 'neutral' ? 'active' : ''}
              onClick={() => setActiveTab('neutral')}
            >
              Neutral ({sentiment_stats.neutral})
            </button>
          </div>
        </div>
        <CommentsList comments={getCommentsForTab()} />
      </motion.div>
    </motion.div>
  );
};

export default Dashboard;
