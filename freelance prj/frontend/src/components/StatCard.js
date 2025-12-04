import React from 'react';
import './StatCard.css';
import { motion } from 'framer-motion';

const StatCard = ({ icon, title, value, subtitle, color }) => {
  return (
    <motion.div 
      className="stat-card"
      whileHover={{ scale: 1.05 }}
      whileTap={{ scale: 0.95 }}
    >
      <div className="stat-icon" style={{ color }}>
        {icon}
      </div>
      <div className="stat-content">
        <h4>{title}</h4>
        <p className="stat-value" style={{ color }}>{value}</p>
        {subtitle && <span className="stat-subtitle">{subtitle}</span>}
      </div>
    </motion.div>
  );
};

export default StatCard;
