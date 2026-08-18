import React, { useState, useEffect } from 'react';
import { fetchMethodology } from '../api/client';

export default function Methodology() {
  const [methodology, setMethodology] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchMethodology()
      .then(setMethodology)
      .catch(console.error)
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <div className="spinner"></div>;
  if (!methodology) return <div>Failed to load methodology</div>;

  return (
    <div>
      <h2>Scoring Methodology</h2>
      
      <div className="card mb-4">
        <h3>Formulas</h3>
        <p><strong>Per-test Score:</strong> {methodology.formulas.per_test}</p>
        <p><strong>Per-category Score:</strong> {methodology.formulas.per_category}</p>
        <p><strong>Overall Risk:</strong> {methodology.formulas.overall_risk}</p>
      </div>

      <div className="grid-2">
        <div className="card">
          <h3>Category Weights</h3>
          <table>
            <thead>
              <tr><th>Category</th><th>Weight</th></tr>
            </thead>
            <tbody>
              {Object.entries(methodology.scoring.category_weights).map(([cat, weight]) => (
                <tr key={cat}><td>{cat}</td><td>{weight}</td></tr>
              ))}
            </tbody>
          </table>
        </div>
        
        <div className="card">
          <h3>Severity Weights</h3>
          <table>
            <thead>
              <tr><th>Severity</th><th>Multiplier</th></tr>
            </thead>
            <tbody>
              {Object.entries(methodology.scoring.severity_weights).map(([sev, weight]) => (
                <tr key={sev}>
                  <td><span className={`badge ${sev.toLowerCase()}`}>{sev}</span></td>
                  <td>{weight}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
      
      <div className="card mt-4">
        <h3>Thresholds</h3>
        <p><strong>Pass:</strong> Score &ge; {methodology.scoring.pass_threshold}</p>
        <p><strong>Partial:</strong> Score &ge; {methodology.scoring.partial_threshold} and &lt; {methodology.scoring.pass_threshold}</p>
        <p><strong>Fail:</strong> Score &lt; {methodology.scoring.partial_threshold}</p>
      </div>
    </div>
  );
}
