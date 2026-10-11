export type CheckStatus = 'pass' | 'fail' | 'warning' | 'unable_to_verify';
export type SeverityLevel = 'info' | 'minor' | 'major' | 'critical';
export type IssueTier = 'submission_blocker' | 'improvement_recommended' | 'check_or_limitation';
export type ResolutionStatus = 'open' | 'in_progress' | 'resolved' | 'dismissed';

export interface SourceLocation {
  section_name?: string | null;
  page_number?: number | null;
  paragraph_number?: number | null;
  bounding_box?: number[] | null;
}

export interface GuidelineSource {
  publisher?: string | null;
  journal_name?: string | null;
  section_title?: string | null;
  rule_snippet?: string | null;
  source_url?: string | null;
}

export interface MeasuredValues {
  metric_name: string;
  detected_value: string | number;
  allowed_value: string | number;
  difference: string | number;
}

export interface EvidenceItem {
  excerpt?: string | null;
  source_location?: SourceLocation | null;
  guideline_source?: GuidelineSource | null;
}

export interface Finding {
  finding_id: string;
  rule_id: string;
  engine: string;
  category: string;
  status: CheckStatus;
  severity: SeverityLevel;
  title: string;
  expected_requirement: string;
  actual_observation: string;
  evidence?: string | null;
  source_location?: SourceLocation | null;
  guideline_source?: GuidelineSource | null;
  suggested_correction?: string | null;
  is_provisional?: boolean;
}

export interface ConsolidatedIssue {
  issue_id: string;
  title: string;
  tier: IssueTier;
  category: string;
  severity: SeverityLevel;
  problem_statement: string;
  why_it_matters: string;
  actual_observation: string;
  expected_requirement?: string | null;
  measured_values?: MeasuredValues | null;
  recommended_action: string;
  suggested_revision_guidance?: string | null;
  rule_count: number;
  evidence_items: EvidenceItem[];
}

export interface EngineScoreDetail {
  engine_id: string; // 'deterministic' | 'rag_knowledge' | 'llm_academic'
  engine_name: string;
  score: number;
  passed_count: number;
  failed_count: number;
  warning_count: number;
  unverified_count: number;
  is_provisional: boolean;
  weight: number;
}

export interface SectionScoreDetail {
  section_id: string; // 'abstract' | 'introduction' | 'methodology' | 'results' | 'conclusion' | 'references'
  section_name: string;
  score: number;
  status: 'pass' | 'needs_revision' | 'incomplete' | 'unverified';
  passed_count: number;
  failed_count: number;
  warning_count: number;
  has_sufficient_evidence: boolean;
  evidence_notes?: string | null;
}

export interface CategoryScoreDetail {
  category_id: string;
  category_label: string;
  score: number;
  weight: number;
  weighted_score: number;
  passed_count: number;
  failed_count: number;
  warning_count: number;
  unverified_count: number;
  is_provisional: boolean;
  deductions: Array<{
    rule_id: string;
    severity: string;
    points_deducted: number;
    reason: string;
  }>;
}

export interface VerificationCoverage {
  total_checks: number;
  passed_count: number;
  failed_count: number;
  warning_count: number;
  unverified_count: number;
  coverage_percent: number;
  provisional_penalty_applied: boolean;
}

export interface DocumentValidation {
  is_plausible_manuscript: boolean;
  document_type: string;
  confidence: number;
  warning_message?: string | null;
  detected_signals?: string[];
  missing_academic_markers?: string[];
}

export interface AcademicAssessment {
  criterion: string;
  criterion_label?: string;
  assessment: 'strong' | 'adequate' | 'needs_improvement' | 'critical_gap';
  score?: number;
  explanation: string;
  recommended_action: string;
}

export interface ReadinessScoreResponse {
  overall_score: number;
  readiness_tier: string;
  is_provisional: boolean;
  provisional_reason?: string | null;
  category_scores: Record<string, CategoryScoreDetail>;
  engine_scores: Record<string, EngineScoreDetail>;
  section_scores: Record<string, SectionScoreDetail>;
  critical_issues_count: number;
  warnings_count: number;
  unverified_count: number;
  disclaimer?: string;
}

export interface ExecutiveSummary {
  manuscript_title: string;
  target_journal?: string | null;
  overall_score: number;
  readiness_tier: string;
  key_strengths: string[];
  critical_deficits: string[];
  synthesis: string;
}

export interface CompleteAnalysisReport {
  analysis_id: string;
  manuscript_id: string;
  version_id: string;
  manuscript_title: string;
  target_journal_id?: string | null;
  target_journal_name?: string | null;
  guideline_version_tag?: string | null;
  generated_at: string;
  document_validation?: DocumentValidation | null;
  verification_coverage?: VerificationCoverage | null;
  consolidated_issues: ConsolidatedIssue[];
  executive_summary: ExecutiveSummary;
  readiness_score: ReadinessScoreResponse;
  all_findings: Finding[];
  academic_assessments?: AcademicAssessment[];
  limitations?: Array<{
    engine: string;
    scope: string;
    reason: string;
    guidance: string;
  }>;
}

export interface Journal {
  journal_id: string;
  name: string;
  publisher: string;
  description?: string;
}

export interface ManuscriptUploadResponse {
  manuscript_id: string;
  title: string;
  page_count: number;
  word_count: number;
  file_hash?: string;
  is_scanned: boolean;
  filename?: string;
}

export interface AnalysisStatusResponse {
  analysis_id: string;
  status: 'pending' | 'running' | 'completed' | 'failed';
  progress_percent: number;
  current_step: string;
  error_message?: string | null;
}

export interface UserAuditHistoryItem {
  id: string;
  manuscript_id: string;
  filename: string;
  title: string;
  journal_id: string;
  journal_name?: string;
  uploaded_at: string;
  readiness_score?: number;
  readiness_tier?: string;
  similarity_score?: number;
  blockers_count?: number;
  improvements_count?: number;
  report?: CompleteAnalysisReport;
  manuscript_info?: ManuscriptUploadResponse;
}
