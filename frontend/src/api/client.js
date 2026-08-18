const BASE_URL = '/api';

async function request(endpoint, options = {}) {
  try {
    const response = await fetch(`${BASE_URL}${endpoint}`, {
      headers: {
        'Content-Type': 'application/json',
      },
      ...options,
    });
    if (!response.ok) {
      throw new Error(`API error: ${response.status} ${response.statusText}`);
    }
    // Handle cases where response might be empty or blob
    const contentType = response.headers.get("content-type");
    if (contentType && contentType.indexOf("application/json") !== -1) {
      return await response.json();
    }
    return response;
  } catch (error) {
    console.error('API request failed:', error);
    throw error;
  }
}

export const fetchRuns = () => request('/runs');
export const fetchRun = (id) => request(`/runs/${id}`);
export const fetchResults = (runId) => request(`/runs/${runId}/results`);
export const compareRuns = (id1, id2) => request(`/compare/${id1}/${id2}`);
export const fetchHistory = () => request('/history');
export const fetchJudgeAgreement = (runId) => request(`/judge-agreement/${runId}`);
export const liveTest = (data) => request('/live-test', { method: 'POST', body: JSON.stringify(data) });
export const startRun = (data) => request('/runs/start', { method: 'POST', body: JSON.stringify(data) });
export const fetchRunStatus = (runId) => request(`/runs/${runId}/status`);
export const fetchMethodology = () => request('/methodology');
export const fetchCategories = () => request('/categories');
export const downloadReport = (runId, format) => {
  window.open(`${BASE_URL}/runs/${runId}/report?format=${format}`, '_blank');
};
