import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell } from 'recharts';
import { fetchRuns } from '../api/client';

export default function Dashboard() {
  const [runs, setRuns] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchRuns()
      .then((data) => {
        setRuns(data || []);
        setLoading(false);
      })
      .catch((err) => {
        console.error(err);
        setError('Failed to load runs');
        setLoading(false);
      });
  }, []);

  if (loading) return <div className="spinner"></div>;
  if (error) return <div className="text-fail">{error}</div>;

  const latestRun = runs.length > 0 ? runs[0] : null;

  const categoryData = latestRun ? Object.entries(latestRun.category_scores).map(([name, score], index) => ({
    name,
    score: score * 100,
    fill: `var(--color-cat${(index % 8) + 1})`
  })) : [];

  return (
    <div>
      <h2>Dashboard</h2>
      {latestRun ? (
        <>
          <div className="grid-4">
            <div className="card">
              <h3>Total Tests</h3>
              <div className="value">{latestRun.total_tests}</div>
            </div>
            <div className="card">
              <h3>Passed</h3>
              <div className="value text-pass">{latestRun.passed}</div>
            </div>
            <div className="card">
              <h3>Failed</h3>
              <div className="value text-fail">{latestRun.failed}</div>
            </div>
            <div className="card">
              <h3>Risk Score</h3>
              <div className="value">{latestRun.overall_risk_score?.toFixed(1)}/100</div>
            </div>
          </div>

          <div className="grid-2">
            <div className="card">
              <h3>Category Breakdown</h3>
              <div style={{ width: '100%', height: 300 }}>
                <ResponsiveContainer>
                  <BarChart data={categoryData} layout="vertical" margin={{ top: 5, right: 30, left: 20, bottom: 5 }}>
                    <XAxis type="number" domain={[0, 100]} />
                    <YAxis dataKey="name" type="category" width={100} />
                    <Tooltip contentStyle={{ backgroundColor: 'var(--card-bg)', border: '1px solid var(--card-border)' }} />
                    <Bar dataKey="score">
                      {categoryData.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={entry.fill} />
                      ))}
                    </Bar>
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </div>
            <div className="card">
              <h3>Recent Runs</h3>
              <table>
                <thead>
                  <tr>
                    <th>Model</th>
                    <th>Date</th>
                    <th>Risk Score</th>
                    <th>Action</th>
                  </tr>
                </thead>
                <tbody>
                  {runs.slice(0, 5).map(run => (
                    <tr key={run.id}>
                      <td>{run.model_id}</td>
                      <td>{new Date(run.started_at).toLocaleDateString()}</td>
                      <td>{run.overall_risk_score?.toFixed(1)}</td>
                      <td>
                        <Link to={`/runs/${run.id}`} className="text-pass">View</Link>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </>
      ) : (
        <p>No runs found. Start a test to see results here.</p>
      )}
    </div>
  );
}
