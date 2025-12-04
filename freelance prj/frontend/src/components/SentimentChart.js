import React from 'react';
import { PieChart, Pie, Cell, ResponsiveContainer, Legend, Tooltip } from 'recharts';

const SentimentChart = ({ data }) => {
  const chartData = [
    { name: 'Positive', value: data.positive, color: '#27ae60' },
    { name: 'Negative', value: data.negative, color: '#e74c3c' },
    { name: 'Neutral', value: data.neutral, color: '#95a5a6' }
  ];

  const CustomTooltip = ({ active, payload }) => {
    if (active && payload && payload.length) {
      return (
        <div style={{
          background: 'rgba(255, 255, 255, 0.95)',
          padding: '10px',
          borderRadius: '8px',
          boxShadow: '0 4px 12px rgba(0,0,0,0.15)'
        }}>
          <p style={{ margin: 0, fontWeight: 'bold' }}>{payload[0].name}</p>
          <p style={{ margin: 0, color: payload[0].payload.color }}>
            {payload[0].value} comments
          </p>
        </div>
      );
    }
    return null;
  };

  // Generate unique key based on data to force re-render
  const chartKey = `sentiment-${data.positive}-${data.negative}-${data.neutral}-${Date.now()}`;

  return (
    <ResponsiveContainer width="100%" height={300} key={chartKey}>
      <PieChart>
        <Pie
          data={chartData}
          cx="50%"
          cy="50%"
          labelLine={false}
          label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(0)}%`}
          outerRadius={100}
          fill="#8884d8"
          dataKey="value"
        >
          {chartData.map((entry, index) => (
            <Cell key={`cell-${index}`} fill={entry.color} />
          ))}
        </Pie>
        <Tooltip content={<CustomTooltip />} />
        <Legend />
      </PieChart>
    </ResponsiveContainer>
  );
};

export default SentimentChart;
