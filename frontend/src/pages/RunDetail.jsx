import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import { fetchRun, fetchResults, downloadReport } from '../api/client';

export default function RunDetail() {
  const { id } = useParams();
  const [run, setRun] = useState(null);
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(true);
  const [expandedId, setExpandedId] = useState(null);

  useEffect(() => {
    Promise.all([fetchRun(id), fetchResults(id)])
      .then(([runData, resultsData]) => {
        setRun(runData);
        setResults(resultsData);
        setLoading(false);
      })
      .catch(console.error);
  }, [id]);

  if (loading) return <div className="spinner"></div>;
  if (!run) return <div>Run not found</div>;

  return (
    <div>
      <div className="flex justify-between items-center mb-4">
        <h2>Run: {run.model_id}</h2>
        <div>
          <button onClick={() => downloadReport(id, 'pdf')} style={{ marginRight: '10px' }}>Download PDF</button>
          <button onClick={() => downloadReport(id, 'markdown')}>Download MD</button>
        </div>
      </div>
      
      <div className="grid-4">
         <div className="card"><h3>Passed</h3><div className="value text-pass">{run.passed}</div></div>
         <div className="card"><h3>Failed</h3><div className="value text-fail">{run.failed}</div></div>
         <div className="card"><h3>Partial</h3><div className="value text-partial">{run.partial}</div></div>
         <div className="card"><h3>Risk Score</h3><div className="value">{run.overall_risk_score?.toFixed(1)}</div></div>
      </div>

      <div className="card mt-4">
        <h3>Results</h3>
        <table>
          <thead>
            <tr>
              <th>Test ID</th>
              <th>Category</th>
              <th>Severity</th>
              <th>Verdict</th>
              <th>Score</th>
              <th>Action</th>
            </tr>
          </thead>
          <tbody>
            {results.map(res => (
              <React.Fragment key={res.id}>
                <tr>
                  <td>{res.test_id}</td>
                  <td>{res.category}</td>
                  <td><span className={`badge ${res.severity.toLowerCase()}`}>{res.severity}</span></td>
                  <td><span className={`badge ${res.verdict.toLowerCase()}`}>{res.verdict}</span></td>
                  <td>{res.final_score.toFixed(2)}</td>
                  <td>
                    <button onClick={() => setExpandedId(expandedId === res.id ? null : res.id)}>
                      {expandedId === res.id ? 'Hide' : 'View'}
                    </button>
                  </td>
                </tr>
                {expandedId === res.id && (
                  <tr>
                    <td colSpan="6" style={{ backgroundColor: 'rgba(0,0,0,0.2)' }}>
                      <div style={{ padding: '15px' }}>
                        <h4>Prompt</h4>
                        <pre style={{ whiteSpace: 'pre-wrap', fontSize: '0.8rem' }}>{JSON.stringify(res.prompt_data, null, 2)}</pre>
                        <h4>Response</h4>
                        <p>{res.response_text}</p>
                        <h4>Judge Reasoning</h4>
                        <p>{res.judge_reasoning}</p>
                      </div>
                    </td>
                  </tr>
                )}
              </React.Fragment>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
