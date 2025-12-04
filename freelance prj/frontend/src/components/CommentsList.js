import React from 'react';
import './CommentsList.css';
import { FaHeart, FaUser, FaTag } from 'react-icons/fa';
import { motion } from 'framer-motion';

const CommentsList = ({ comments }) => {
  const getSentimentColor = (sentiment) => {
    switch (sentiment) {
      case 'positive':
        return '#27ae60';
      case 'negative':
        return '#e74c3c';
      default:
        return '#95a5a6';
    }
  };

  const getSentimentEmoji = (sentiment) => {
    switch (sentiment) {
      case 'positive':
        return '😊';
      case 'negative':
        return '😞';
      default:
        return '😐';
    }
  };

  const containerVariants = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: {
        staggerChildren: 0.05
      }
    }
  };

  const itemVariants = {
    hidden: { x: -20, opacity: 0 },
    visible: {
      x: 0,
      opacity: 1
    }
  };

  return (
    <motion.div 
      className="comments-list"
      initial="hidden"
      animate="visible"
      variants={containerVariants}
    >
      {comments.length === 0 ? (
        <div className="no-comments">
          <p>No comments to display</p>
        </div>
      ) : (
        comments.map((comment, index) => (
          <motion.div 
            key={comment.id || index} 
            className="comment-card"
            variants={itemVariants}
            whileHover={{ scale: 1.02 }}
          >
            <div className="comment-header">
              <div className="comment-user">
                <FaUser className="user-icon" />
                <span className="username">@{comment.username}</span>
              </div>
              <div className="comment-meta">
                {comment.likes > 0 && (
                  <span className="likes">
                    <FaHeart /> {comment.likes}
                  </span>
                )}
              </div>
            </div>
            
            <div className="comment-text">
              {comment.text}
            </div>

            <div className="comment-footer">
              <div 
                className="sentiment-badge"
                style={{ 
                  background: `${getSentimentColor(comment.sentiment)}20`,
                  color: getSentimentColor(comment.sentiment)
                }}
              >
                <span className="sentiment-emoji">
                  {getSentimentEmoji(comment.sentiment)}
                </span>
                <span>{comment.sentiment}</span>
                {comment.confidence && (
                  <span className="confidence">
                    ({Math.round(comment.confidence * 100)}%)
                  </span>
                )}
              </div>

              {comment.sentiment === 'negative' && (
                <div className="topic-badge">
                  <FaTag />
                  <span>{comment.topic || 'Other'}</span>
                </div>
              )}
            </div>
          </motion.div>
        ))
      )}
    </motion.div>
  );
};

export default CommentsList;
