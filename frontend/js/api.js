// API Client for ScholarCheck Backend

const API_BASE = '/api/v1';

export const ApiClient = {
  async checkHealth() {
    try {
      const res = await fetch(`${API_BASE}/health`);
      if (!res.ok) throw new Error(`Health check failed: ${res.status}`);
      return await res.json();
    } catch (err) {
      console.error('API health check error:', err);
      return { status: 'offline', error: err.message };
    }
  },

  async fetchJournals() {
    const res = await fetch(`${API_BASE}/journals`);
    if (!res.ok) throw new Error('Failed to load journals');
    return await res.json();
  },

  async fetchJournalGuidelines(journalId) {
    const res = await fetch(`${API_BASE}/journals/${journalId}/guidelines`);
    if (!res.ok) throw new Error('Failed to load journal guidelines');
    return await res.json();
  },

  async uploadManuscript(file, title = '') {
    const formData = new FormData();
    formData.append('file', file);
    if (title) formData.append('title', title);

    const res = await fetch(`${API_BASE}/manuscripts/upload`, {
      method: 'POST',
      body: formData,
    });

    if (!res.ok) {
      const errData = await res.json().catch(() => ({ detail: res.statusText }));
      throw new Error(errData.detail || 'Upload failed');
    }

    return await res.json();
  },

  async triggerAnalysis(manuscriptId, journalId = null) {
    const res = await fetch(`${API_BASE}/manuscripts/${manuscriptId}/analyze`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ journal_id: journalId, include_academic_evaluation: true }),
    });

    if (!res.ok) {
      const errData = await res.json().catch(() => ({ detail: res.statusText }));
      throw new Error(errData.detail || 'Analysis trigger failed');
    }

    return await res.json();
  },

  async pollAnalysisStatus(analysisId) {
    const res = await fetch(`${API_BASE}/analysis/${analysisId}`);
    if (!res.ok) throw new Error('Status poll failed');
    return await res.json();
  },

  async fetchAnalysisResults(analysisId) {
    const res = await fetch(`${API_BASE}/analysis/${analysisId}/results`);
    if (!res.ok) throw new Error('Results fetch failed');
    return await res.json();
  },

  async fetchAnalysisReport(analysisId) {
    const res = await fetch(`${API_BASE}/analysis/${analysisId}/report`);
    if (!res.ok) throw new Error('Report fetch failed');
    return await res.json();
  },

  getExportUrl(analysisId, format = 'pdf') {
    return `${API_BASE}/analysis/${analysisId}/export?format=${format}`;
  },
};
