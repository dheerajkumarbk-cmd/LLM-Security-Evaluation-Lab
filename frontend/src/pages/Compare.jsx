import React, { useState, useEffect } from 'react';
import { fetchRuns, compareRuns } from '../api/client';
import { BarChart, Bar, XAxis, YAxis, Tooltip, Legend, ResponsiveContainer, CartesianGrid } from 'recharts';

export default function Compare() {
  const [runs, setRuns] = useState([]);
  const [run1, setRun1] = useState('');
  const [run2, setRun2] = useState('');
  const [compareData, setCompareData] = useState(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    fetchRuns().then(setRuns).catch(console.error);
  }, []);

  const handleCompare = () => {
    if (!run1 || !run2) return;
    setLoading(true);
    compareRuns(run1, run2)
      .then(setCompareData)
      .catch(console.error)
      .finally(() => setLoading(false));
  };

  const chartData = compareData ? Object.entries(compareData.category_deltas).map(([cat, data]) => ({
    name: cat,
    Run1: data.run1 * 100,
    Run2: data.run2 * 100,
  })) : [];

  return (
    <div>
      <h2>Compare Runs</h2>
      <div className="card mb-4">
        <div className="flex gap-2 items-center">
          <select value={run1} onChange={e => setRun1(e.target.value)}>
            <option value="">Select Run 1...</option>
            {runs.map(r => <option key={r.id} value={r.id}>{r.model_id} ({new Date(r.started_at).toLocaleDateString()})</option>)}
          </select>
          <select value={run2} onChange={e => setRun2(e.target.value)}>
            <option value="">Select Run 2...</option>
            {runs.map(r => <option key={r.id} value={r.id}>{r.model_id} ({new Date(r.started_at).toLocaleDateString()})</option>)}
          </select>
          <button onClick={handleCompare} disabled={!run1 || !run2}>Compare</button>
        </div>
      </div>

      {loading && <div className="spinner"></div>}

      {compareData && (
        <>
          <div className="card mb-4">
            <h3>Category Comparison</h3>
            <div style={{ width: '100%', height: 400 }}>
              <ResponsiveContainer>
                <BarChart data={chartData} margin={{ top: 20, right: 30, left: 20, bottom: 5 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="var(--card-border)" />
                  <XAxis dataKey="name" stroke="var(--text-secondary)" />
                  <YAxis stroke="var(--text-secondary)" />
                  <Tooltip contentStyle={{ backgroundColor: 'var(--card-bg)', border: '1px solid var(--card-border)' }} />
                  <Legend />
                  <Bar dataKey="Run1" fill="#3b82f6" />
                  <Bar dataKey="Run2" fill="#10b981" />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>
          
          <div className="card">
            <h3>Flipped Tests</h3>
            <table>
              <thead>
                <tr>
                  <th>Test ID</th>
                  <th>Run 1 Verdict</th>
                  <th>Run 2 Verdict</th>
                </tr>
              </thead>
              <tbody>
                {compareData.flipped.map((f, i) => (
                  <tr key={i}>
                    <td>{f.test_id}</td>
                    <td><span className={`badge ${f.run1_verdict.toLowerCase()}`}>{f.run1_verdict}</span></td>
                    <td><span className={`badge ${f.run2_verdict.toLowerCase()}`}>{f.run2_verdict}</span></td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </>
      )}
    </div>
  );
}
