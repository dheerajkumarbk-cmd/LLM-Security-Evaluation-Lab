import React, { useState, useEffect } from 'react';
import { fetchRuns } from '../api/client';
import { LineChart, Line, XAxis, YAxis, Tooltip, CartesianGrid, ResponsiveContainer } from 'recharts';

export default function History() {
  const [runs, setRuns] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchRuns().then(data => {
      setRuns(data);
      setLoading(false);
    }).catch(console.error);
  }, []);

  if (loading) return <div className="spinner"></div>;

  const chartData = [...runs].reverse().map(r => ({
    name: new Date(r.started_at).toLocaleDateString(),
    score: r.overall_risk_score,
    model: r.model_id
  }));

  return (
    <div>
      <h2>History</h2>
      <div className="card mb-4">
        <h3>Risk Score Over Time</h3>
        <div style={{ width: '100%', height: 300 }}>
          <ResponsiveContainer>
            <LineChart data={chartData} margin={{ top: 5, right: 30, left: 20, bottom: 5 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="var(--card-border)" />
              <XAxis dataKey="name" stroke="var(--text-secondary)" />
              <YAxis domain={[0, 100]} stroke="var(--text-secondary)" />
              <Tooltip contentStyle={{ backgroundColor: 'var(--card-bg)', border: '1px solid var(--card-border)' }} />
              <Line type="monotone" dataKey="score" stroke="#3b82f6" activeDot={{ r: 8 }} />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </div>
      <div className="card">
        <h3>All Runs</h3>
        <table>
          <thead>
            <tr>
              <th>Model</th>
              <th>Date</th>
              <th>Total Tests</th>
              <th>Risk Score</th>
            </tr>
          </thead>
          <tbody>
            {runs.map(r => (
              <tr key={r.id}>
                <td>{r.model_id}</td>
                <td>{new Date(r.started_at).toLocaleString()}</td>
                <td>{r.total_tests}</td>
                <td>{r.overall_risk_score?.toFixed(1)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
