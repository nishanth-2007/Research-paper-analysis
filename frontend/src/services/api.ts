import {
  ManuscriptUploadResponse,
  AnalysisStatusResponse,
  CompleteAnalysisReport,
  Journal,
} from '../types';

const API_BASE = '/api/v1';

export const ApiService = {
  async checkHealth(): Promise<{ status: string; version?: string; error?: string }> {
    try {
      const res = await fetch(`${API_BASE}/health`);
      if (!res.ok) throw new Error(`Health check returned status ${res.status}`);
      return await res.json();
    } catch (err: any) {
      console.warn('Backend health check error:', err);
      return { status: 'offline', error: err?.message || 'Server unreachable' };
    }
  },

  async fetchJournals(): Promise<Journal[]> {
    try {
      const res = await fetch(`${API_BASE}/journals`);
      if (!res.ok) throw new Error('Failed to load journals');
      const data = await res.json();
      const list = Array.isArray(data) ? data : (data.journals || []);
      return list.map((j: any) => ({
        journal_id: j.id || j.journal_id,
        name: j.name,
        publisher: j.publisher,
        description: Array.isArray(j.scope) ? j.scope.join(', ') : (j.description || ''),
      }));
    } catch (err) {
      console.error('Failed to load journals:', err);
      return [];
    }
  },

  async uploadManuscript(file: File, title: string = ''): Promise<ManuscriptUploadResponse> {
    const formData = new FormData();
    formData.append('file', file);
    if (title) formData.append('title', title);

    const res = await fetch(`${API_BASE}/manuscripts/upload`, {
      method: 'POST',
      body: formData,
    });

    if (!res.ok) {
      const errData = await res.json().catch(() => ({ detail: res.statusText }));
      throw new Error(errData.detail || 'Failed to upload manuscript');
    }

    return await res.json();
  },

  async triggerAnalysis(
    manuscriptId: string,
    journalId: string | null = null
  ): Promise<{ analysis_id: string; manuscript_id: string; status: string }> {
    const res = await fetch(`${API_BASE}/manuscripts/${manuscriptId}/analyze`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        journal_id: journalId || null,
        include_academic_evaluation: true,
      }),
    });

    if (!res.ok) {
      const errData = await res.json().catch(() => ({ detail: res.statusText }));
      throw new Error(errData.detail || 'Analysis initialization failed');
    }

    return await res.json();
  },

  async pollAnalysisStatus(analysisId: string): Promise<AnalysisStatusResponse> {
    const res = await fetch(`${API_BASE}/analysis/${analysisId}`);
    if (!res.ok) {
      throw new Error(`Failed to check analysis status: ${res.statusText}`);
    }
    return await res.json();
  },

  async fetchAnalysisReport(analysisId: string): Promise<CompleteAnalysisReport> {
    const res = await fetch(`${API_BASE}/analysis/${analysisId}/report`);
    if (!res.ok) {
      const errData = await res.json().catch(() => ({ detail: res.statusText }));
      throw new Error(errData.detail || 'Failed to retrieve analysis report');
    }
    return await res.json();
  },

  getExportUrl(analysisId: string, format: 'pdf' | 'docx' = 'pdf'): string {
    return `${API_BASE}/analysis/${analysisId}/export?format=${format}`;
  },
};
