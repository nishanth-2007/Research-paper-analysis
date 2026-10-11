import React, { useState, useEffect } from 'react';
import {
  AlertCircle,
  AlertTriangle,
  ShieldCheck,
  Copy,
  Check,
  Sparkles,
  Filter,
  CheckCircle2,
} from 'lucide-react';
import { ConsolidatedIssue, IssueTier, ResolutionStatus } from '../types';

interface ActionPlanSectionProps {
  issues: ConsolidatedIssue[];
  analysisId: string;
  activeTier: IssueTier | 'all';
  onSelectTier: (tier: IssueTier | 'all') => void;
  onOpenGuidanceModal: (issue: ConsolidatedIssue) => void;
}

export const ActionPlanSection: React.FC<ActionPlanSectionProps> = ({
  issues,
  analysisId,
  activeTier,
  onSelectTier,
  onOpenGuidanceModal,
}) => {
  const [activeStatusFilter, setActiveStatusFilter] = useState<'all' | 'open' | 'resolved'>('all');
  const [copiedId, setCopiedId] = useState<string | null>(null);
  const [issueStatuses, setIssueStatuses] = useState<Record<string, ResolutionStatus>>({});

  // Load stored statuses on mount or analysisId change
  useEffect(() => {
    try {
      const stored = localStorage.getItem(`scholarcheck_statuses_${analysisId}`);
      if (stored) {
        setIssueStatuses(JSON.parse(stored));
      } else {
        setIssueStatuses({});
      }
    } catch (e) {
      console.warn('Failed to load stored issue statuses:', e);
    }
  }, [analysisId]);

  // Update status handler
  const handleStatusChange = (issueId: string, newStatus: ResolutionStatus) => {
    const updated = { ...issueStatuses, [issueId]: newStatus };
    setIssueStatuses(updated);
    try {
      localStorage.setItem(`scholarcheck_statuses_${analysisId}`, JSON.stringify(updated));
    } catch (e) {
      console.warn('Failed to save issue status:', e);
    }
  };

  // Copy action text
  const handleCopyAction = (issueId: string, actionText: string) => {
    navigator.clipboard.writeText(actionText);
    setCopiedId(issueId);
    setTimeout(() => setCopiedId(null), 2000);
  };

  // Filter issues
  const filteredIssues = issues.filter((issue) => {
    // Filter by Tier
    if (activeTier !== 'all' && issue.tier !== activeTier) {
      return false;
    }

    // Filter by Status
    const st = issueStatuses[issue.issue_id] || 'open';
    if (activeStatusFilter === 'open') {
      return st === 'open' || st === 'in_progress';
    }
    if (activeStatusFilter === 'resolved') {
      return st === 'resolved' || st === 'dismissed';
    }

    return true;
  });

  const blockersCount = issues.filter((i) => i.tier === 'submission_blocker').length;
  const improvementsCount = issues.filter((i) => i.tier === 'improvement_recommended').length;
  const checksCount = issues.filter((i) => i.tier === 'check_or_limitation').length;

  return (
    <div className="space-y-6">
      {/* Header and Filter Controls */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-slate-800 pb-4">
        <div>
          <h3 className="text-xl font-bold font-heading text-white tracking-tight flex items-center gap-2">
            Prioritized Action Plan
          </h3>
          <p className="text-xs text-slate-400 mt-1">
            Taxonomically consolidated manuscript corrections with step-by-step resolution tracking.
          </p>
        </div>

        <div className="flex flex-wrap items-center gap-2 sm:gap-3">
          {/* Tier Pills */}
          <div className="flex items-center space-x-1 p-1 rounded-xl bg-slate-900 border border-slate-800 text-xs">
            <button
              onClick={() => onSelectTier('all')}
              className={`px-2.5 py-1 rounded-lg font-medium transition-colors cursor-pointer ${
                activeTier === 'all'
                  ? 'bg-slate-700 text-white'
                  : 'text-slate-400 hover:text-slate-200'
              }`}
            >
              All ({issues.length})
            </button>
            <button
              onClick={() => onSelectTier('submission_blocker')}
              className={`px-2.5 py-1 rounded-lg font-medium transition-colors cursor-pointer ${
                activeTier === 'submission_blocker'
                  ? 'bg-rose-500/30 text-rose-300 font-semibold'
                  : 'text-slate-400 hover:text-slate-200'
              }`}
            >
              Blockers ({blockersCount})
            </button>
            <button
              onClick={() => onSelectTier('improvement_recommended')}
              className={`px-2.5 py-1 rounded-lg font-medium transition-colors cursor-pointer ${
                activeTier === 'improvement_recommended'
                  ? 'bg-amber-500/30 text-amber-300 font-semibold'
                  : 'text-slate-400 hover:text-slate-200'
              }`}
            >
              Improvements ({improvementsCount})
            </button>
            <button
              onClick={() => onSelectTier('check_or_limitation')}
              className={`px-2.5 py-1 rounded-lg font-medium transition-colors cursor-pointer ${
                activeTier === 'check_or_limitation'
                  ? 'bg-indigo-500/30 text-indigo-300 font-semibold'
                  : 'text-slate-400 hover:text-slate-200'
              }`}
            >
              Checks ({checksCount})
            </button>
          </div>

          {/* Status Filter Dropdown */}
          <div className="flex items-center space-x-1.5">
            <select
              value={activeStatusFilter}
              onChange={(e) => setActiveStatusFilter(e.target.value as any)}
              className="bg-slate-900 border border-slate-800 text-slate-300 text-xs rounded-xl px-3 py-1.5 focus:outline-none focus:ring-1 focus:ring-indigo-500 cursor-pointer"
            >
              <option value="all">Status: All Issues</option>
              <option value="open">Status: Active (Open & In Progress)</option>
              <option value="resolved">Status: Resolved & Dismissed</option>
            </select>
          </div>
        </div>
      </div>

      {/* Issues List */}
      {filteredIssues.length === 0 ? (
        <div className="glass-panel rounded-2xl p-8 text-center text-slate-400 text-sm">
          No action items match the selected tier and status filters.
        </div>
      ) : (
        <div className="space-y-4">
          {filteredIssues.map((issue) => {
            const currentStatus = issueStatuses[issue.issue_id] || 'open';

            // Tier styling
            let tierBorderClass = 'border-slate-800';
            let tierPillClass = 'bg-indigo-500/10 text-indigo-300 border-indigo-500/20';
            let tierLabel = 'CHECK OR LIMITATION';

            if (issue.tier === 'submission_blocker') {
              tierBorderClass = 'border-rose-500/30 hover:border-rose-500/50';
              tierPillClass = 'bg-rose-500/10 text-rose-300 border-rose-500/20';
              tierLabel = 'SUBMISSION BLOCKER';
            } else if (issue.tier === 'improvement_recommended') {
              tierBorderClass = 'border-amber-500/30 hover:border-amber-500/50';
              tierPillClass = 'bg-amber-500/10 text-amber-300 border-amber-500/20';
              tierLabel = 'RECOMMENDED IMPROVEMENT';
            }

            // Severity badge
            let severityBadge = 'bg-slate-800 text-slate-400 border-slate-700';
            if (issue.severity === 'critical') severityBadge = 'bg-rose-500/20 text-rose-300 border-rose-500/30';
            if (issue.severity === 'major') severityBadge = 'bg-amber-500/20 text-amber-300 border-amber-500/30';
            if (issue.severity === 'minor') severityBadge = 'bg-blue-500/20 text-blue-300 border-blue-500/30';

            const isResolved = currentStatus === 'resolved' || currentStatus === 'dismissed';

            return (
              <div
                key={issue.issue_id}
                className={`glass-panel rounded-2xl p-5 sm:p-6 border transition-all duration-200 ${tierBorderClass} ${
                  isResolved ? 'opacity-70 bg-slate-950/40' : ''
                }`}
              >
                {/* Top Row: Meta pills & Status dropdown */}
                <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 mb-3">
                  <div className="flex flex-wrap items-center gap-2">
                    <span className={`text-[10px] font-mono px-2.5 py-0.5 rounded-full border ${tierPillClass} font-bold`}>
                      {tierLabel}
                    </span>
                    <span className={`text-[10px] font-mono px-2 py-0.5 rounded border uppercase ${severityBadge}`}>
                      {issue.severity}
                    </span>
                    <span className="text-xs text-slate-400 capitalize">
                      {issue.category === 'journal_peer_review_rigor' || issue.category === 'academic_quality'
                        ? 'Journal Review Rigor'
                        : issue.category.replace(/_/g, ' ')}
                    </span>
                  </div>

                  {/* Interactive Status Dropdown */}
                  <div>
                    <select
                      value={currentStatus}
                      onChange={(e) => handleStatusChange(issue.issue_id, e.target.value as ResolutionStatus)}
                      className={`text-xs rounded-lg px-2.5 py-1 border font-medium cursor-pointer transition-colors focus:outline-none ${
                        currentStatus === 'resolved'
                          ? 'bg-emerald-950/40 text-emerald-300 border-emerald-500/40'
                          : currentStatus === 'in_progress'
                          ? 'bg-amber-950/40 text-amber-300 border-amber-500/40'
                          : currentStatus === 'dismissed'
                          ? 'bg-slate-900 text-slate-500 border-slate-800'
                          : 'bg-slate-900 text-slate-300 border-slate-700'
                      }`}
                    >
                      <option value="open">Status: Open</option>
                      <option value="in_progress">Status: In Progress</option>
                      <option value="resolved">Status: Resolved (User-Reviewed)</option>
                      <option value="dismissed">Status: Dismissed</option>
                    </select>
                  </div>
                </div>

                {/* Issue Title */}
                <h4 className="text-base sm:text-lg font-bold font-heading text-white tracking-tight mb-2">
                  {issue.title}
                </h4>

                {/* Why It Matters */}
                <div className="p-3 rounded-xl bg-slate-900/60 border border-slate-800 text-xs sm:text-sm text-slate-300 mb-4 leading-relaxed">
                  <b className="text-indigo-300">Why It Matters:</b> {issue.why_it_matters}
                </div>

                {/* Observation Grid: Actual vs Expected */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-3 mb-4 text-xs">
                  <div className="p-3 rounded-lg bg-slate-900/80 border border-slate-800/80">
                    <span className="text-[10px] text-slate-400 font-mono uppercase tracking-wider block mb-1">
                      Actual Observation
                    </span>
                    <p className="text-slate-200 leading-relaxed">{issue.actual_observation}</p>
                  </div>

                  <div className="p-3 rounded-lg bg-slate-900/80 border border-slate-800/80">
                    <span className="text-[10px] text-slate-400 font-mono uppercase tracking-wider block mb-1">
                      Expected Requirement
                    </span>
                    <p className="text-slate-200 leading-relaxed">
                      {issue.expected_requirement || 'Target journal guideline compliance'}
                    </p>
                  </div>
                </div>

                {/* Measured Values Pill (if available) */}
                {issue.measured_values && (
                  <div className="mb-4 inline-flex flex-wrap items-center gap-x-3 gap-y-1 px-3 py-1.5 rounded-lg bg-cyan-950/20 border border-cyan-500/30 text-xs text-cyan-300 font-mono">
                    <span>📊 {issue.measured_values.metric_name || 'Measured Metric'}:</span>
                    <span>Detected: <b className="text-white font-sans">{issue.measured_values.detected_value}</b></span>
                    <span>Allowed: <b className="text-white font-sans">{issue.measured_values.allowed_value}</b></span>
                    <span>Diff: <b className="text-amber-400 font-sans">+{issue.measured_values.difference}</b></span>
                  </div>
                )}

                {/* Concrete Recommended Action Box */}
                <div className="p-3.5 rounded-xl bg-indigo-950/20 border border-indigo-500/30 mb-4">
                  <div className="text-[11px] font-bold font-mono text-indigo-400 uppercase tracking-wider mb-1">
                    Concrete Recommended Action
                  </div>
                  <p className="text-xs sm:text-sm text-indigo-100 font-medium leading-relaxed">
                    {issue.recommended_action}
                  </p>
                </div>

                {/* Action Buttons: Copy & AI Guidance */}
                <div className="flex flex-wrap items-center gap-2 mb-4">
                  <button
                    onClick={() => handleCopyAction(issue.issue_id, issue.recommended_action)}
                    className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 transition-colors cursor-pointer"
                  >
                    {copiedId === issue.issue_id ? (
                      <>
                        <Check className="w-3.5 h-3.5 text-emerald-400" />
                        <span className="text-emerald-400 font-semibold">Copied!</span>
                      </>
                    ) : (
                      <>
                        <Copy className="w-3.5 h-3.5 text-slate-400" />
                        <span>Copy Action Item</span>
                      </>
                    )}
                  </button>

                  <button
                    onClick={() => onOpenGuidanceModal(issue)}
                    className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium bg-indigo-600/20 hover:bg-indigo-600/30 text-indigo-300 border border-indigo-500/30 transition-colors cursor-pointer"
                  >
                    <Sparkles className="w-3.5 h-3.5 text-indigo-400" />
                    <span>AI Revision Guidance</span>
                  </button>
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
};
