import React from 'react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell } from 'recharts';

const TopicChart = ({ data }) => {
  const colors = [
    '#e74c3c', '#c0392b', '#e67e22', '#d35400', 
    '#f39c12', '#f1c40f', '#16a085', '#27ae60'
  ];

  const chartData = Object.entries(data).map(([topic, count], index) => ({
    topic,
    count,
    color: colors[index % colors.length]
  }));

  const CustomTooltip = ({ active, payload }) => {
    if (active && payload && payload.length) {
      return (
        <div style={{
          background: 'rgba(255, 255, 255, 0.95)',
          padding: '10px',
          borderRadius: '8px',
          boxShadow: '0 4px 12px rgba(0,0,0,0.15)'
        }}>
          <p style={{ margin: 0, fontWeight: 'bold' }}>{payload[0].payload.topic}</p>
          <p style={{ margin: 0, color: payload[0].payload.color }}>
            {payload[0].value} comments
          </p>
        </div>
      );
    }
    return null;
  };

  // Generate unique key based on data to force re-render
  const chartKey = `topic-${JSON.stringify(data)}-${Date.now()}`;

  return (
    <ResponsiveContainer width="100%" height={300} key={chartKey}>
      <BarChart data={chartData}>
        <CartesianGrid strokeDasharray="3 3" />
        <XAxis 
          dataKey="topic" 
          angle={-45}
          textAnchor="end"
          height={100}
          interval={0}
        />
        <YAxis />
        <Tooltip content={<CustomTooltip />} />
        <Bar dataKey="count" radius={[8, 8, 0, 0]}>
          {chartData.map((entry, index) => (
            <Cell key={`cell-${index}`} fill={entry.color} />
          ))}
        </Bar>
      </BarChart>
    </ResponsiveContainer>
  );
};

export default TopicChart;
