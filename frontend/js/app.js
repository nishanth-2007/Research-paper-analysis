// ScholarCheck AI - Academic Readiness Dashboard App

import { ApiClient } from './api.js';

// Application State
let currentManuscript = null;
let currentAnalysis = null;
let currentReport = null;
let activeCatTab = 'compliance';
let activeActionTier = 'all';
let activeActionStatus = 'all';
let activeAuditFilter = 'all';

// DOM Element References
const statusDot = document.getElementById('status-dot');
const statusText = document.getElementById('status-text');
const journalSelect = document.getElementById('journal-select');

// Upload & Metadata
const dropzone = document.getElementById('dropzone');
const fileInput = document.getElementById('file-input');
const docInfoBar = document.getElementById('doc-info-bar');
const docTitle = document.getElementById('doc-title');
const docPages = document.getElementById('doc-pages');
const docWords = document.getElementById('doc-words');
const docHash = document.getElementById('doc-hash');
const docScannedAlert = document.getElementById('doc-scanned-alert');
const btnAnalyze = document.getElementById('btn-analyze');

// Progress
const progressCard = document.getElementById('progress-card');
const progressFill = document.getElementById('progress-fill');
const progressPercent = document.getElementById('progress-percent');
const currentStepText = document.getElementById('current-step-text');

// Document Validation Notice
const docValidationBanner = document.getElementById('doc-validation-banner');
const valBannerTitle = document.getElementById('val-banner-title');
const valBannerDesc = document.getElementById('val-banner-desc');
const btnDismissValAlert = document.getElementById('btn-dismiss-val-alert');

// Dashboard Containers
const resultsDashboard = document.getElementById('results-dashboard');

// Header
const headerVenueTag = document.getElementById('header-venue-tag');
const headerManuscriptTitle = document.getElementById('header-manuscript-title');
const headerAnalysisDate = document.getElementById('header-analysis-date');
const headerVersionId = document.getElementById('header-version-id');
const headerStatusBadge = document.getElementById('header-status-badge');
const btnExportPdf = document.getElementById('btn-export-pdf');
const btnExportDocx = document.getElementById('btn-export-docx');
const btnExportJson = document.getElementById('btn-export-json');
const btnRerunAnalysis = document.getElementById('btn-rerun-analysis');

// Overview Score & Coverage
const circleScoreVal = document.getElementById('circle-score-val');
const tierBadge = document.getElementById('tier-badge');
const provisionalScorePill = document.getElementById('provisional-score-pill');
const coveragePercentLabel = document.getElementById('coverage-percent-label');
const coverageFill = document.getElementById('coverage-fill');
const coverageSummaryText = document.getElementById('coverage-summary-text');
const scoreSynthesisText = document.getElementById('score-synthesis-text');

// 3 Metric Cards
const countBlockers = document.getElementById('count-blockers');
const countImprovements = document.getElementById('count-improvements');
const countChecks = document.getElementById('count-checks');

// Category Tabs
const catTabContent = document.getElementById('cat-tab-content');

// Prioritized Action Plan
const actionPlanContainer = document.getElementById('action-plan-container');
const pillAllCount = document.getElementById('pill-all-count');
const pillBlockerCount = document.getElementById('pill-blocker-count');
const pillImproveCount = document.getElementById('pill-improve-count');
const pillCheckCount = document.getElementById('pill-check-count');
const selectIssueStatusFilter = document.getElementById('select-issue-status-filter');

// Audit Trail Findings List
const findingsList = document.getElementById('findings-list');

// Revision Guidance Modal
const revisionModal = document.getElementById('revision-modal');
const modalTitle = document.getElementById('modal-title');
const modalProblem = document.getElementById('modal-problem');
const modalAction = document.getElementById('modal-action');
const modalStrategy = document.getElementById('modal-strategy');
const btnCloseModal = document.getElementById('btn-close-modal');
const btnModalDone = document.getElementById('btn-modal-done');
const btnModalCopy = document.getElementById('btn-modal-copy');

// --- Initialization ---
async function init() {
  bindEvents();
  await checkSystemHealth();
  await loadJournals();
}

function bindEvents() {
  // Drag and drop
  dropzone.addEventListener('dragover', (e) => {
    e.preventDefault();
    dropzone.classList.add('dragover');
  });

  dropzone.addEventListener('dragleave', () => {
    dropzone.classList.remove('dragover');
  });

  dropzone.addEventListener('drop', (e) => {
    e.preventDefault();
    dropzone.classList.remove('dragover');
    if (e.dataTransfer.files.length > 0) {
      handleFileSelected(e.dataTransfer.files[0]);
    }
  });

  dropzone.addEventListener('click', () => fileInput.click());
  fileInput.addEventListener('change', (e) => {
    if (e.target.files.length > 0) {
      handleFileSelected(e.target.files[0]);
    }
  });

  btnAnalyze.addEventListener('click', handleRunAnalysis);
  btnRerunAnalysis.addEventListener('click', handleRunAnalysis);

  // Category tab buttons
  document.querySelectorAll('.cat-tab-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      document.querySelectorAll('.cat-tab-btn').forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      activeCatTab = btn.getAttribute('data-cat-tab');
      renderCategoryTabContent();
    });
  });

  // Action plan tier pills
  document.querySelectorAll('.action-pill').forEach(btn => {
    btn.addEventListener('click', () => {
      document.querySelectorAll('.action-pill').forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      activeActionTier = btn.getAttribute('data-action-tier');
      renderActionPlan();
    });
  });

  // Metric cards clickable to filter action plan
  document.querySelectorAll('.metric-card').forEach(card => {
    card.addEventListener('click', () => {
      const tier = card.getAttribute('data-filter-tier');
      const targetPill = document.querySelector(`.action-pill[data-action-tier="${tier}"]`);
      if (targetPill) targetPill.click();
      document.querySelector('.action-plan-section').scrollIntoView({ behavior: 'smooth' });
    });
  });

  // Issue status filter
  selectIssueStatusFilter.addEventListener('change', (e) => {
    activeActionStatus = e.target.value;
    renderActionPlan();
  });

  // Audit filter buttons
  document.querySelectorAll('.filter-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      activeAuditFilter = btn.getAttribute('data-filter');
      renderAuditFindings();
    });
  });

  // Dismiss validation banner
  btnDismissValAlert.addEventListener('click', () => {
    docValidationBanner.style.display = 'none';
  });

  // Export JSON
  btnExportJson.addEventListener('click', handleExportJson);

  // Modal close handlers
  btnCloseModal.addEventListener('click', () => revisionModal.close());
  btnModalDone.addEventListener('click', () => revisionModal.close());
  btnModalCopy.addEventListener('click', () => {
    const textToCopy = `Strategy for: ${modalTitle.textContent}\nAction: ${modalAction.textContent}\nStrategy:\n${modalStrategy.textContent}`;
    navigator.clipboard.writeText(textToCopy);
    btnModalCopy.textContent = 'Copied to Clipboard!';
    setTimeout(() => { btnModalCopy.textContent = 'Copy Strategy'; }, 2000);
  });
}

// --- Health Check ---
async function checkSystemHealth() {
  const health = await ApiClient.checkHealth();
  if (health.status === 'operational') {
    statusDot.className = 'status-dot online';
    statusText.textContent = `Online (v${health.version})`;
  } else {
    statusDot.className = 'status-dot offline';
    statusText.textContent = 'System Offline';
  }
}

// --- Load Journals ---
async function loadJournals() {
  try {
    const data = await ApiClient.fetchJournals();
    journalSelect.innerHTML = '<option value="">-- General Academic Standard (No Specific Venue) --</option>';
    if (data.journals) {
      data.journals.forEach(j => {
        const opt = document.createElement('option');
        opt.value = j.journal_id;
        opt.textContent = `${j.name} (${j.publisher})`;
        if (j.journal_id === 'ieee-access') opt.selected = true;
        journalSelect.appendChild(opt);
      });
    }
  } catch (err) {
    console.error('Failed to load journals:', err);
    journalSelect.innerHTML = '<option value="">General Academic Guidelines</option>';
  }
}

// --- Manuscript Upload Handling ---
async function handleFileSelected(file) {
  try {
    btnAnalyze.disabled = true;
    btnAnalyze.textContent = 'Ingesting & Validating Document...';

    const resp = await ApiClient.uploadManuscript(file);
    currentManuscript = resp;

    docTitle.textContent = resp.title || file.name;
    docPages.textContent = `${resp.page_count} page(s)`;
    docWords.textContent = `${resp.word_count.toLocaleString()} words`;
    docHash.textContent = resp.file_hash ? `${resp.file_hash.substring(0, 16)}...` : '—';

    // Scanned document notice
    if (resp.is_scanned) {
      docScannedAlert.style.display = 'block';
      docScannedAlert.innerHTML = `⚠️ <b>Scanned Document Notice:</b> Raster scanned document detected. Some coordinate checks will be provisional until OCR completes.`;
    } else {
      docScannedAlert.style.display = 'none';
    }

    docInfoBar.style.display = 'block';
    btnAnalyze.disabled = false;
    btnAnalyze.textContent = 'Run Multi-Engine Verification & Scoring';

    // Hide previous results dashboard while new upload is pending
    resultsDashboard.style.display = 'none';
    docValidationBanner.style.display = 'none';

  } catch (err) {
    alert(`Ingestion error: ${err.message}`);
    btnAnalyze.disabled = false;
    btnAnalyze.textContent = 'Upload Failed - Retry';
  }
}

// --- Analysis Orchestration ---
async function handleRunAnalysis() {
  if (!currentManuscript) return;

  btnAnalyze.disabled = true;
  progressCard.style.display = 'block';
  progressFill.style.width = '5%';
  progressPercent.textContent = '5%';
  currentStepText.textContent = 'Initializing analysis job...';

  try {
    const targetJournal = journalSelect.value || null;
    const jobResp = await ApiClient.triggerAnalysis(currentManuscript.manuscript_id, targetJournal);
    currentAnalysis = jobResp;

    pollJob(jobResp.analysis_id);
  } catch (err) {
    alert(`Failed to start analysis: ${err.message}`);
    btnAnalyze.disabled = false;
    progressCard.style.display = 'none';
  }
}

async function pollJob(analysisId) {
  const interval = setInterval(async () => {
    try {
      const statusData = await ApiClient.pollAnalysisStatus(analysisId);

      const percent = statusData.progress_percent || 10;
      progressFill.style.width = `${percent}%`;
      progressPercent.textContent = `${percent}%`;
      currentStepText.textContent = statusData.current_step || 'Processing...';

      if (statusData.status === 'completed') {
        clearInterval(interval);
        setTimeout(async () => {
          progressCard.style.display = 'none';
          btnAnalyze.disabled = false;
          await loadAndRenderReport(analysisId);
        }, 400);
      } else if (statusData.status === 'failed') {
        clearInterval(interval);
        currentStepText.textContent = `Analysis failed: ${statusData.error_message || 'Unknown error'}`;
        btnAnalyze.disabled = false;
      }
    } catch (err) {
      console.error('Polling error:', err);
    }
  }, 750);
}

// --- Report Loading & Rendering ---
async function loadAndRenderReport(analysisId) {
  try {
    const report = await ApiClient.fetchAnalysisReport(analysisId);
    currentReport = report;

    // 1. Document Validation Warning Banner
    if (report.document_validation && report.document_validation.is_plausible_manuscript === false) {
      docValidationBanner.style.display = 'flex';
      valBannerTitle.textContent = `Document Validation Notice (${report.document_validation.document_type.replace(/_/g, ' ').toUpperCase()})`;
      valBannerDesc.textContent = report.document_validation.warning_message || 'The uploaded file appears to be a résumé or non-academic file rather than a scholarly manuscript.';
    } else {
      docValidationBanner.style.display = 'none';
    }

    // 2. Report Header
    headerManuscriptTitle.textContent = report.manuscript_title || 'Untitled Manuscript';
    headerVenueTag.textContent = report.target_journal_name ? `${report.target_journal_name} Target` : 'General Academic Standard';
    const reportDate = new Date(report.generated_at);
    headerAnalysisDate.textContent = reportDate.toLocaleDateString(undefined, { year: 'numeric', month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' });
    headerVersionId.textContent = report.guideline_version_tag ? `Guidelines ${report.guideline_version_tag}` : 'Standard';

    btnExportPdf.href = ApiClient.getExportUrl(analysisId, 'pdf');
    btnExportDocx.href = ApiClient.getExportUrl(analysisId, 'docx');

    // 3. Readiness Overview & Score
    const scoreVal = report.readiness_score.overall_score;
    circleScoreVal.textContent = scoreVal.toFixed(1);
    circleScoreVal.style.color = scoreVal >= 80 ? '#34d399' : (scoreVal >= 65 ? '#fbbf24' : '#fb7185');

    tierBadge.textContent = report.readiness_score.readiness_tier;
    tierBadge.className = 'tier-badge ' + (scoreVal >= 80 ? 'high' : (scoreVal >= 65 ? 'medium' : 'low'));

    if (report.readiness_score.is_provisional || (report.document_validation && !report.document_validation.is_plausible_manuscript)) {
      provisionalScorePill.style.display = 'inline-block';
      provisionalScorePill.textContent = `⚠️ Provisional Score: ${report.readiness_score.provisional_reason || 'Document structure unverified'}`;
    } else {
      provisionalScorePill.style.display = 'none';
    }

    // Verification Coverage
    const cov = report.verification_coverage;
    if (cov) {
      coveragePercentLabel.textContent = `${cov.coverage_percent}%`;
      coverageFill.style.width = `${cov.coverage_percent}%`;
      coverageSummaryText.textContent = `${cov.total_checks - cov.unverified_count} of ${cov.total_checks} rules verified • ${cov.passed_count} passed`;
    } else {
      coveragePercentLabel.textContent = '100%';
      coverageFill.style.width = '100%';
      coverageSummaryText.textContent = 'All rules verified';
    }

    scoreSynthesisText.textContent = report.executive_summary.synthesis;

    // Metric Counts
    const blockers = (report.consolidated_issues || []).filter(c => c.tier === 'submission_blocker');
    const improvements = (report.consolidated_issues || []).filter(c => c.tier === 'improvement_recommended');
    const checks = (report.consolidated_issues || []).filter(c => c.tier === 'check_or_limitation');

    countBlockers.textContent = blockers.length;
    countImprovements.textContent = improvements.length;
    countChecks.textContent = checks.length;

    pillAllCount.textContent = (report.consolidated_issues || []).length;
    pillBlockerCount.textContent = blockers.length;
    pillImproveCount.textContent = improvements.length;
    pillCheckCount.textContent = checks.length;

    // 4. Render Evaluation Categories Tab View
    renderCategoryTabContent();

    // 5. Render Prioritized Action Plan
    renderActionPlan();

    // 6. Render Technical Audit Trail
    renderAuditFindings();

    // Reveal Dashboard
    resultsDashboard.style.display = 'block';

  } catch (err) {
    console.error('Error rendering report:', err);
    alert(`Failed to load analysis report: ${err.message}`);
  }
}

// --- Render Three Evaluation Categories Tab Content ---
function renderCategoryTabContent() {
  if (!currentReport) return;
  catTabContent.innerHTML = '';

  const catScores = currentReport.readiness_score.category_scores || {};

  if (activeCatTab === 'compliance') {
    // 1. Journal Compliance Tab
    const compScore = catScores['compliance_formatting'] || { score: 100, weight: 0.2, passed_count: 0, failed_count: 0 };
    const citScore = catScores['citation_reference'] || { score: 100, weight: 0.25, passed_count: 0, failed_count: 0 };
    const secScore = catScores['manuscript_completeness'] || { score: 100, weight: 0.2, passed_count: 0, failed_count: 0 };

    catTabContent.innerHTML = `
      <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 16px;">
        <div class="category-card">
          <div class="cat-header">Structure & Required Sections</div>
          <div class="cat-score-row">
            <div class="cat-score-val" style="color: ${secScore.score >= 80 ? '#34d399' : '#fb7185'}">${secScore.score.toFixed(1)}</div>
            <div class="cat-score-weight">Weight: 20%</div>
          </div>
          <div class="cat-bar"><div class="cat-bar-fill" style="width: ${secScore.score}%; background: ${secScore.score >= 80 ? '#10b981' : '#f43f5e'};"></div></div>
          <div class="cat-stats">${secScore.failed_count} failed • ${secScore.warning_count || 0} warnings • ${secScore.passed_count} passed</div>
          <div style="font-size: 0.78rem; color: var(--text-dim); margin-top: 8px;">Checks Abstract, Introduction, Methods, Results, and Conclusion presence.</div>
        </div>

        <div class="category-card">
          <div class="cat-header">Citation & Reference Consistency</div>
          <div class="cat-score-row">
            <div class="cat-score-val" style="color: ${citScore.score >= 80 ? '#34d399' : '#fb7185'}">${citScore.score.toFixed(1)}</div>
            <div class="cat-score-weight">Weight: 25%</div>
          </div>
          <div class="cat-bar"><div class="cat-bar-fill" style="width: ${citScore.score}%; background: ${citScore.score >= 80 ? '#10b981' : '#f43f5e'};"></div></div>
          <div class="cat-stats">${citScore.failed_count} failed • ${citScore.warning_count || 0} warnings • ${citScore.passed_count} passed</div>
          <div style="font-size: 0.78rem; color: var(--text-dim); margin-top: 8px;">Verifies every in-text citation tag corresponds to an entry in the bibliography.</div>
        </div>

        <div class="category-card">
          <div class="cat-header">Journal Guidelines & Declarations</div>
          <div class="cat-score-row">
            <div class="cat-score-val" style="color: ${compScore.score >= 80 ? '#34d399' : '#fb7185'}">${compScore.score.toFixed(1)}</div>
            <div class="cat-score-weight">Weight: 20%</div>
          </div>
          <div class="cat-bar"><div class="cat-bar-fill" style="width: ${compScore.score}%; background: ${compScore.score >= 80 ? '#10b981' : '#f43f5e'};"></div></div>
          <div class="cat-stats">${compScore.failed_count} failed • ${compScore.warning_count || 0} warnings • ${compScore.passed_count} passed</div>
          <div style="font-size: 0.78rem; color: var(--text-dim); margin-top: 8px;">Word count limits, Data Availability statements, figure numbering, and margins.</div>
        </div>
      </div>
    `;

  } else if (activeCatTab === 'quality') {
    // 2. Academic Quality Tab
    const methScore = catScores['academic_methodology'] || { score: 100, weight: 0.2, passed_count: 0, failed_count: 0 };
    const scopeScore = catScores['scope_alignment'] || { score: 100, weight: 0.15, passed_count: 0, failed_count: 0 };

    let assessmentsHtml = '';
    if (currentReport.academic_assessments && currentReport.academic_assessments.length > 0) {
      assessmentsHtml = currentReport.academic_assessments.map(a => `
        <div style="background: rgba(0,0,0,0.2); padding: 12px; border-radius: 6px; margin-top: 8px; border-left: 2px solid #818cf8;">
          <div style="display: flex; justify-content: space-between; font-weight: 700; font-size: 0.88rem;">
            <span>${a.criterion_label || a.criterion.replace(/_/g, ' ').toUpperCase()}</span>
            <span class="badge ${a.assessment === 'strong' ? 'pass' : (a.assessment === 'adequate' ? 'info' : 'warning')}">${a.assessment.toUpperCase()}</span>
          </div>
          <div style="font-size: 0.82rem; color: var(--text-muted); margin-top: 4px;">${escapeHtml(a.explanation)}</div>
          <div style="font-size: 0.78rem; color: #a5b4fc; margin-top: 6px;">💡 <b>Action:</b> ${escapeHtml(a.recommended_action)}</div>
        </div>
      `).join('');
    } else {
      assessmentsHtml = '<div style="font-size: 0.85rem; color: var(--text-muted); margin-top: 10px;">Academic peer review heuristics evaluated research questions, contributions, and baseline completeness.</div>';
    }

    catTabContent.innerHTML = `
      <div style="display: grid; grid-template-columns: 340px 1fr; gap: 20px;">
        <div class="category-card">
          <div class="cat-header">Methodology & Rigor Score</div>
          <div class="cat-score-row">
            <div class="cat-score-val" style="color: ${methScore.score >= 80 ? '#34d399' : '#fb7185'}">${methScore.score.toFixed(1)}</div>
            <div class="cat-score-weight">Weight: 20%</div>
          </div>
          <div class="cat-bar"><div class="cat-bar-fill" style="width: ${methScore.score}%; background: ${methScore.score >= 80 ? '#10b981' : '#f43f5e'};"></div></div>
          <div class="cat-stats">${methScore.failed_count} failed • ${methScore.warning_count || 0} warnings • ${methScore.passed_count} passed</div>
          <div style="font-size: 0.78rem; color: var(--text-dim); margin-top: 8px;">Scope Alignment: ${scopeScore.score.toFixed(1)} / 100 (Weight: 15%)</div>
        </div>
        <div>
          <div style="font-weight: 700; font-size: 0.95rem; margin-bottom: 8px;">Peer-Review Evaluation Dimensions</div>
          ${assessmentsHtml}
        </div>
      </div>
    `;

  } else {
    // 3. Verification Status Tab
    const cov = currentReport.verification_coverage || {};
    catTabContent.innerHTML = `
      <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 16px;">
        <div class="category-card" style="border-left: 3px solid #10b981;">
          <div class="cat-header">Passed Checks</div>
          <div class="cat-score-val" style="color: #34d399;">${cov.passed_count || 0}</div>
          <div style="font-size: 0.8rem; color: var(--text-muted); margin-top: 4px;">Verified manuscript rules successfully satisfied.</div>
        </div>
        <div class="category-card" style="border-left: 3px solid #f43f5e;">
          <div class="cat-header">Failed Requirements</div>
          <div class="cat-score-val" style="color: #fb7185;">${cov.failed_count || 0}</div>
          <div style="font-size: 0.8rem; color: var(--text-muted); margin-top: 4px;">Confirmed mandatory requirements violated.</div>
        </div>
        <div class="category-card" style="border-left: 3px solid #f59e0b;">
          <div class="cat-header">Advisory Warnings</div>
          <div class="cat-score-val" style="color: #fbbf24;">${cov.warning_count || 0}</div>
          <div style="font-size: 0.8rem; color: var(--text-muted); margin-top: 4px;">Recommended adjustments for optimal readability.</div>
        </div>
        <div class="category-card" style="border-left: 3px solid #8b5cf6;">
          <div class="cat-header">Unable to Verify</div>
          <div class="cat-score-val" style="color: #c084fc;">${cov.unverified_count || 0}</div>
          <div style="font-size: 0.8rem; color: var(--text-muted); margin-top: 4px;">Extraction limitations or non-academic format constraints.</div>
        </div>
      </div>
    `;
  }
}

// --- Render Prioritized Action Plan ---
function renderActionPlan() {
  actionPlanContainer.innerHTML = '';

  if (!currentReport || !currentReport.consolidated_issues || currentReport.consolidated_issues.length === 0) {
    actionPlanContainer.innerHTML = '<div style="color: var(--text-muted); font-size: 0.95rem; padding: 20px 0;">No active action items identified. The manuscript satisfies guideline standards.</div>';
    return;
  }

  // Load saved issue statuses from localStorage
  const savedStatuses = getStoredIssueStatuses(currentReport.analysis_id);

  let filtered = currentReport.consolidated_issues;

  // Filter by Tier
  if (activeActionTier !== 'all') {
    filtered = filtered.filter(item => item.tier === activeActionTier);
  }

  // Filter by Status
  if (activeActionStatus === 'open') {
    filtered = filtered.filter(item => {
      const st = savedStatuses[item.issue_id] || 'open';
      return st === 'open' || st === 'in_progress';
    });
  } else if (activeActionStatus === 'resolved') {
    filtered = filtered.filter(item => {
      const st = savedStatuses[item.issue_id] || 'open';
      return st === 'resolved';
    });
  }

  if (filtered.length === 0) {
    actionPlanContainer.innerHTML = '<div style="color: var(--text-muted); font-size: 0.9rem; padding: 24px 0; text-align: center;">No issues matching the selected filters.</div>';
    return;
  }

  filtered.forEach(issue => {
    const currentStatus = savedStatuses[issue.issue_id] || 'open';
    const card = document.createElement('div');
    card.className = `issue-card tier-${issue.tier} status-${currentStatus}`;

    // Measured values pill
    let measuredHtml = '';
    if (issue.measured_values) {
      const mv = issue.measured_values;
      measuredHtml = `
        <div class="measured-pill">
          <span>📊 ${escapeHtml(mv.metric_name || 'Measured')}</span>
          <span>Detected: <b>${mv.detected_value}</b></span>
          <span>Allowed: <b>${mv.allowed_value}</b></span>
          <span>Diff: <b>+${mv.difference}</b></span>
        </div>
      `;
    }

    // Evidence Items for Drawer (Clean user-facing evidence without internal engine labels or rule IDs)
    const evidenceListHtml = issue.evidence_items.map(ev => {
      let locHtml = '';
      if (ev.source_location && (ev.source_location.section_name || ev.source_location.page_number)) {
        locHtml = `
          <div style="font-size: 0.8rem; color: var(--text-dim); margin-bottom: 6px;">
            ${ev.source_location.section_name ? `Location: Section <b>${escapeHtml(ev.source_location.section_name)}</b> ` : ''}
            ${ev.source_location.page_number ? `(Page ${ev.source_location.page_number})` : ''}
          </div>
        `;
      }

      let excerptHtml = ev.excerpt ? `<div class="evidence-excerpt-box">"${escapeHtml(ev.excerpt)}"</div>` : '';

      let sourceHtml = (ev.guideline_source && ev.guideline_source.source_url) ? `
        <div style="font-size: 0.78rem; color: var(--accent-cyan); margin-top: 6px;">
          🔗 Official Publisher Guideline: <a href="${ev.guideline_source.source_url}" target="_blank" rel="noopener">${escapeHtml(ev.guideline_source.publisher || 'Publisher')} Policy (${escapeHtml(ev.guideline_source.section_title || 'Guidelines')})</a>
        </div>
      ` : '';

      if (!locHtml && !excerptHtml && !sourceHtml) {
        return '';
      }

      return `
        <div style="background: rgba(0,0,0,0.25); padding: 10px; border-radius: 6px; margin-bottom: 8px;">
          ${locHtml}
          ${excerptHtml}
          ${sourceHtml}
        </div>
      `;
    }).filter(Boolean).join('');

    let evidenceDrawerHtml = '';
    if (evidenceListHtml) {
      evidenceDrawerHtml = `
        <details class="issue-evidence-details">
          <summary>🔍 View Supporting Evidence & Publisher Guideline Citations</summary>
          <div class="evidence-drawer-body">
            ${evidenceListHtml}
          </div>
        </details>
      `;
    }

    card.innerHTML = `
      <div class="issue-top-row">
        <div class="issue-meta-left">
          <span class="tier-pill ${issue.tier}">${issue.tier.replace(/_/g, ' ')}</span>
          <span class="badge ${issue.severity}">${issue.severity.toUpperCase()}</span>
          <span style="font-size: 0.8rem; color: var(--text-dim);">${issue.category.replace(/_/g, ' ')}</span>
        </div>
        <div>
          <select class="issue-status-dropdown" data-issue-id="${issue.issue_id}">
            <option value="open" ${currentStatus === 'open' ? 'selected' : ''}>Status: Open</option>
            <option value="in_progress" ${currentStatus === 'in_progress' ? 'selected' : ''}>Status: In Progress</option>
            <option value="resolved" ${currentStatus === 'resolved' ? 'selected' : ''}>Status: Resolved (User-Reviewed)</option>
            <option value="dismissed" ${currentStatus === 'dismissed' ? 'selected' : ''}>Status: Dismissed</option>
          </select>
        </div>
      </div>

      <div class="issue-title">${escapeHtml(issue.title)}</div>

      <div class="issue-why-matters">
        <b>Why It Matters:</b> ${escapeHtml(issue.why_it_matters)}
      </div>

      <div class="issue-obs-grid">
        <div class="issue-field">
          <div class="lbl">Actual Observation</div>
          <div class="txt">${escapeHtml(issue.actual_observation)}</div>
        </div>
        <div class="issue-field">
          <div class="lbl">Expected Requirement</div>
          <div class="txt">${escapeHtml(issue.expected_requirement || 'Standard academic compliance')}</div>
        </div>
      </div>

      ${measuredHtml}

      <div class="issue-action-box">
        <div class="action-lbl">Concrete Recommended Action</div>
        <div class="action-txt">${escapeHtml(issue.recommended_action)}</div>
      </div>

      <div class="issue-btn-row">
        <div class="issue-btn-actions">
          <button class="btn-issue-tool btn-copy-action" data-text="${escapeHtml(issue.recommended_action)}">
            📋 Copy Action
          </button>
          <button class="btn-issue-tool btn-ai-guidance" data-issue-title="${escapeHtml(issue.title)}" data-issue-problem="${escapeHtml(issue.problem_statement)}" data-issue-action="${escapeHtml(issue.recommended_action)}" data-issue-strategy="${escapeHtml(issue.suggested_revision_guidance || '')}">
            💡 AI Revision Guidance
          </button>
        </div>
      </div>

      ${evidenceDrawerHtml}
    `;

    // Status dropdown change event
    const statusSelect = card.querySelector('.issue-status-dropdown');
    statusSelect.addEventListener('change', (e) => {
      saveIssueStatus(currentReport.analysis_id, issue.issue_id, e.target.value);
      renderActionPlan();
    });

    // Copy action button
    const btnCopy = card.querySelector('.btn-copy-action');
    btnCopy.addEventListener('click', () => {
      navigator.clipboard.writeText(issue.recommended_action);
      btnCopy.textContent = 'Copied!';
      setTimeout(() => { btnCopy.textContent = '📋 Copy Action'; }, 1500);
    });

    // AI revision guidance button
    const btnGuidance = card.querySelector('.btn-ai-guidance');
    btnGuidance.addEventListener('click', () => {
      modalTitle.textContent = issue.title;
      modalProblem.textContent = issue.problem_statement;
      modalAction.textContent = issue.recommended_action;
      modalStrategy.textContent = issue.suggested_revision_guidance || 'Drafting Tip: State clear empirical evidence, define parameter variables, and align section headers with target journal guidelines.';
      revisionModal.showModal();
    });

    actionPlanContainer.appendChild(card);
  });
}

// --- Render Detailed Verification Findings (Technical Audit Trail) ---
function renderAuditFindings() {
  findingsList.innerHTML = '';
  if (!currentReport || !currentReport.all_findings) return;

  let filtered = currentReport.all_findings;
  if (activeAuditFilter === 'critical') {
    filtered = currentReport.all_findings.filter(f => f.severity === 'critical' && f.status === 'fail');
  } else if (activeAuditFilter === 'warning') {
    filtered = currentReport.all_findings.filter(f => f.status === 'warning');
  } else if (activeAuditFilter === 'unverified') {
    filtered = currentReport.all_findings.filter(f => f.status === 'unable_to_verify');
  } else if (activeAuditFilter === 'pass') {
    filtered = currentReport.all_findings.filter(f => f.status === 'pass');
  }

  if (filtered.length === 0) {
    findingsList.innerHTML = '<div style="color: var(--text-muted); font-size: 0.88rem; padding: 14px 0;">No findings matching this filter.</div>';
    return;
  }

  filtered.forEach(f => {
    const card = document.createElement('div');
    const statusClass = f.status === 'fail' ? f.severity : (f.status === 'warning' ? 'warning' : (f.status === 'unable_to_verify' ? 'unverified' : 'pass'));
    card.className = `finding-card ${statusClass}`;

    let evidenceHtml = f.evidence ? `
      <div class="finding-field" style="grid-column: span 2;">
        <div class="field-label">Evidence Excerpt</div>
        <div style="font-family: var(--font-mono); font-size: 0.82rem; color: var(--text-muted);">${escapeHtml(f.evidence)}</div>
      </div>
    ` : '';

    let provenanceHtml = (f.guideline_source && f.guideline_source.source_url) ? `
      <div class="finding-provenance">
        🔗 Publisher Policy: <a href="${f.guideline_source.source_url}" target="_blank" rel="noopener">${f.guideline_source.publisher || 'Guideline'} (${f.guideline_source.section_title || 'Rules'})</a>
      </div>
    ` : '';

    card.innerHTML = `
      <div class="finding-header">
        <div class="finding-meta">
          <span class="badge ${f.status === 'fail' ? f.severity : f.status}">${f.status.toUpperCase()}</span>
          <span style="font-size: 0.8rem; color: var(--text-dim); text-transform: capitalize;">${f.category ? f.category.replace(/_/g, ' ') : ''}</span>
        </div>
      </div>
      <div class="finding-title">${escapeHtml(f.title)}</div>
      <div class="finding-grid">
        <div class="finding-field">
          <div class="field-label">Expected Requirement</div>
          <div>${escapeHtml(f.expected_requirement)}</div>
        </div>
        <div class="finding-field">
          <div class="field-label">Actual Observation</div>
          <div>${escapeHtml(f.actual_observation)}</div>
        </div>
        ${evidenceHtml}
      </div>
      ${provenanceHtml}
    `;
    findingsList.appendChild(card);
  });
}

// --- Local Storage Issue Status Helpers ---
function getStoredIssueStatuses(analysisId) {
  try {
    const raw = localStorage.getItem(`scholarcheck_statuses_${analysisId}`);
    return raw ? JSON.parse(raw) : {};
  } catch (e) {
    return {};
  }
}

function saveIssueStatus(analysisId, issueId, status) {
  try {
    const statuses = getStoredIssueStatuses(analysisId);
    statuses[issueId] = status;
    localStorage.setItem(`scholarcheck_statuses_${analysisId}`, JSON.stringify(statuses));
  } catch (e) {
    console.error('Failed to save issue status:', e);
  }
}

// --- Export JSON Handler ---
function handleExportJson() {
  if (!currentReport) return;
  const jsonStr = JSON.stringify(currentReport, null, 2);
  const blob = new Blob([jsonStr], { type: 'application/json' });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = `readiness_report_${currentReport.analysis_id}.json`;
  a.click();
  URL.revokeObjectURL(url);
}

function escapeHtml(str) {
  if (!str) return '';
  return String(str)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#039;');
}

document.addEventListener('DOMContentLoaded', init);
