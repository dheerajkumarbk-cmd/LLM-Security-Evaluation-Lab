import React, { useState } from 'react';
import { liveTest } from '../api/client';

export default function LiveTest() {
  const [model, setModel] = useState('gpt-4');
  const [systemPrompt, setSystemPrompt] = useState('');
  const [prompt, setPrompt] = useState('');
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleTest = () => {
    if (!prompt) return;
    setLoading(true);
    setError(null);
    liveTest({ model, system_prompt: systemPrompt, prompt })
      .then(setResult)
      .catch(e => setError(e.message))
      .finally(() => setLoading(false));
  };

  return (
    <div>
      <h2>Live Test</h2>
      <div className="grid-2">
        <div className="card">
          <h3>Input</h3>
          <select value={model} onChange={e => setModel(e.target.value)}>
            <option value="gpt-4">GPT-4</option>
            <option value="claude-3">Claude 3</option>
            <option value="llama-3">Llama 3</option>
          </select>
          <textarea 
            placeholder="System Prompt (optional)" 
            value={systemPrompt} 
            onChange={e => setSystemPrompt(e.target.value)} 
            rows={3}
          />
          <textarea 
            placeholder="User Prompt" 
            value={prompt} 
            onChange={e => setPrompt(e.target.value)} 
            rows={5}
          />
          <button onClick={handleTest} disabled={loading || !prompt}>
            {loading ? 'Running...' : 'Send'}
          </button>
          {error && <div className="text-fail mt-4">{error}</div>}
        </div>
        <div className="card">
          <h3>Result</h3>
          {loading && <div className="spinner"></div>}
          {result && (
             <div>
               <h4>Response</h4>
               <p style={{ backgroundColor: 'rgba(0,0,0,0.2)', padding: '10px', borderRadius: '4px' }}>
                 {result.response}
               </p>
               
               <div className="grid-2 mt-4">
                 <div>
                   <h4>Heuristic Score</h4>
                   <div className="value">{result.heuristic_score}</div>
                   <ul style={{ paddingLeft: '20px' }}>
                     {result.heuristic_details?.map((h, i) => (
                       <li key={i} className={h.passed ? 'text-pass' : 'text-fail'}>
                         {h.check_type}: {h.passed ? 'Pass' : 'Fail'}
                       </li>
                     ))}
                   </ul>
                 </div>
                 <div>
                   <h4>Judge Score</h4>
                   <div className="value">{result.judge_result?.score}</div>
                   <div className={`badge ${result.judge_result?.verdict.toLowerCase()}`}>{result.judge_result?.verdict}</div>
                   <p className="text-secondary mt-4" style={{ fontSize: '0.8rem' }}>{result.judge_result?.reasoning}</p>
                 </div>
               </div>
               
               <div className="mt-4 text-secondary" style={{ fontSize: '0.8rem' }}>
                 Latency: {result.latency_ms}ms | Tokens: {result.input_tokens} in, {result.output_tokens} out
               </div>
             </div>
          )}
        </div>
      </div>
    </div>
  );
}
