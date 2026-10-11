import React, { useState } from 'react';
import {
  FileCheck2,
  Sparkles,
  ShieldCheck,
  CheckCircle2,
  XCircle,
  AlertTriangle,
  HelpCircle,
  Award,
  Lightbulb,
} from 'lucide-react';
import { CompleteAnalysisReport } from '../types';

interface EvaluationTabsProps {
  report: CompleteAnalysisReport;
}

export const EvaluationTabs: React.FC<EvaluationTabsProps> = ({ report }) => {
  const [activeTab, setActiveTab] = useState<'compliance' | 'quality' | 'verification'>('compliance');

  const catScores = report.readiness_score.category_scores || {};
  const coverage = report.verification_coverage;
  const assessments = report.academic_assessments || [];

  return (
    <div className="glass-panel-elevated rounded-2xl p-6 sm:p-8 border border-slate-800 space-y-6">
      {/* Tab Navigation Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-slate-800/80 pb-4">
        <div>
          <h3 className="text-lg font-bold font-heading text-white tracking-tight">
            Detailed Evaluation Dimensions
          </h3>
          <p className="text-xs text-slate-400 mt-0.5">
            Examine breakdown across structural compliance, academic rigor heuristics, and verification coverage.
          </p>
        </div>

        <div className="flex items-center space-x-1.5 p-1 rounded-xl bg-slate-900 border border-slate-800 self-start sm:self-auto">
          <button
            onClick={() => setActiveTab('compliance')}
            className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-all cursor-pointer flex items-center gap-1.5 ${
              activeTab === 'compliance'
                ? 'bg-indigo-600 text-white shadow-sm'
                : 'text-slate-400 hover:text-slate-200'
            }`}
          >
            <FileCheck2 className="w-3.5 h-3.5" />
            <span>Journal Compliance</span>
          </button>

          <button
            onClick={() => setActiveTab('quality')}
            className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-all cursor-pointer flex items-center gap-1.5 ${
              activeTab === 'quality'
                ? 'bg-indigo-600 text-white shadow-sm'
                : 'text-slate-400 hover:text-slate-200'
            }`}
          >
            <Sparkles className="w-3.5 h-3.5" />
            <span>Journal Peer-Review Rigor</span>
          </button>

          <button
            onClick={() => setActiveTab('verification')}
            className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-all cursor-pointer flex items-center gap-1.5 ${
              activeTab === 'verification'
                ? 'bg-indigo-600 text-white shadow-sm'
                : 'text-slate-400 hover:text-slate-200'
            }`}
          >
            <ShieldCheck className="w-3.5 h-3.5" />
            <span>Verification Status</span>
          </button>
        </div>
      </div>

      {/* Tab 1: Journal Compliance */}
      {activeTab === 'compliance' && (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-5">
          {/* Structure & Sections */}
          {(() => {
            const item = catScores['manuscript_completeness'] || {
              score: 100,
              weight: 0.2,
              passed_count: 0,
              failed_count: 0,
              warning_count: 0,
            };
            return (
              <div className="glass-panel rounded-xl p-5 border border-slate-800 flex flex-col justify-between">
                <div>
                  <div className="flex items-center justify-between mb-2">
                    <h4 className="text-sm font-bold text-white font-heading">
                      Structure & Required Sections
                    </h4>
                    <span className="text-[11px] font-mono text-slate-400">Weight: 20%</span>
                  </div>
                  <p className="text-xs text-slate-400 mb-4">
                    Verifies explicit presence of Abstract, Introduction, Methods, Results, and Conclusion.
                  </p>
                </div>
                <div>
                  <div className="flex items-baseline justify-between mb-1.5">
                    <span className="text-xs text-slate-400 font-mono">Category Score</span>
                    <span
                      className={`text-xl font-bold font-heading ${
                        item.score >= 80 ? 'text-emerald-400' : 'text-rose-400'
                      }`}
                    >
                      {item.score.toFixed(1)} / 100
                    </span>
                  </div>
                  <div className="w-full bg-slate-900 rounded-full h-1.5 overflow-hidden mb-3">
                    <div
                      className={`h-1.5 rounded-full ${item.score >= 80 ? 'bg-emerald-500' : 'bg-rose-500'}`}
                      style={{ width: `${item.score}%` }}
                    />
                  </div>
                  <div className="text-[11px] font-mono text-slate-400 pt-2 border-t border-slate-800/80 flex justify-between">
                    <span>{item.passed_count} passed</span>
                    <span className="text-rose-400">{item.failed_count} failed</span>
                    <span className="text-amber-400">{item.warning_count} warnings</span>
                  </div>
                </div>
              </div>
            );
          })()}

          {/* Citation & References */}
          {(() => {
            const item = catScores['citation_reference'] || {
              score: 100,
              weight: 0.25,
              passed_count: 0,
              failed_count: 0,
              warning_count: 0,
            };
            return (
              <div className="glass-panel rounded-xl p-5 border border-slate-800 flex flex-col justify-between">
                <div>
                  <div className="flex items-center justify-between mb-2">
                    <h4 className="text-sm font-bold text-white font-heading">
                      Citation & Reference Matching
                    </h4>
                    <span className="text-[11px] font-mono text-slate-400">Weight: 25%</span>
                  </div>
                  <p className="text-xs text-slate-400 mb-4">
                    Deterministic cross-referencing between in-text citation tags and bibliography entries.
                  </p>
                </div>
                <div>
                  <div className="flex items-baseline justify-between mb-1.5">
                    <span className="text-xs text-slate-400 font-mono">Category Score</span>
                    <span
                      className={`text-xl font-bold font-heading ${
                        item.score >= 80 ? 'text-emerald-400' : 'text-rose-400'
                      }`}
                    >
                      {item.score.toFixed(1)} / 100
                    </span>
                  </div>
                  <div className="w-full bg-slate-900 rounded-full h-1.5 overflow-hidden mb-3">
                    <div
                      className={`h-1.5 rounded-full ${item.score >= 80 ? 'bg-emerald-500' : 'bg-rose-500'}`}
                      style={{ width: `${item.score}%` }}
                    />
                  </div>
                  <div className="text-[11px] font-mono text-slate-400 pt-2 border-t border-slate-800/80 flex justify-between">
                    <span>{item.passed_count} passed</span>
                    <span className="text-rose-400">{item.failed_count} failed</span>
                    <span className="text-amber-400">{item.warning_count} warnings</span>
                  </div>
                </div>
              </div>
            );
          })()}

          {/* Formatting & Declarations */}
          {(() => {
            const item = catScores['compliance_formatting'] || {
              score: 100,
              weight: 0.2,
              passed_count: 0,
              failed_count: 0,
              warning_count: 0,
            };
            return (
              <div className="glass-panel rounded-xl p-5 border border-slate-800 flex flex-col justify-between">
                <div>
                  <div className="flex items-center justify-between mb-2">
                    <h4 className="text-sm font-bold text-white font-heading">
                      Journal Guidelines & Declarations
                    </h4>
                    <span className="text-[11px] font-mono text-slate-400">Weight: 20%</span>
                  </div>
                  <p className="text-xs text-slate-400 mb-4">
                    Word count limits, mandatory Data Availability statements, figure numbering, and captions.
                  </p>
                </div>
                <div>
                  <div className="flex items-baseline justify-between mb-1.5">
                    <span className="text-xs text-slate-400 font-mono">Category Score</span>
                    <span
                      className={`text-xl font-bold font-heading ${
                        item.score >= 80 ? 'text-emerald-400' : 'text-rose-400'
                      }`}
                    >
                      {item.score.toFixed(1)} / 100
                    </span>
                  </div>
                  <div className="w-full bg-slate-900 rounded-full h-1.5 overflow-hidden mb-3">
                    <div
                      className={`h-1.5 rounded-full ${item.score >= 80 ? 'bg-emerald-500' : 'bg-rose-500'}`}
                      style={{ width: `${item.score}%` }}
                    />
                  </div>
                  <div className="text-[11px] font-mono text-slate-400 pt-2 border-t border-slate-800/80 flex justify-between">
                    <span>{item.passed_count} passed</span>
                    <span className="text-rose-400">{item.failed_count} failed</span>
                    <span className="text-amber-400">{item.warning_count} warnings</span>
                  </div>
                </div>
              </div>
            );
          })()}
        </div>
      )}

      {/* Tab 2: Academic Quality & Rigor */}
      {activeTab === 'quality' && (
        <div className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {/* Methodology Rigor */}
            {(() => {
              const item = catScores['academic_methodology'] || { score: 100, weight: 0.2 };
              return (
                <div className="bg-slate-900/60 p-4 rounded-xl border border-slate-800">
                  <div className="flex items-center justify-between mb-1">
                    <h5 className="text-sm font-semibold text-white">Methodology & Rigor Score</h5>
                    <span className="text-base font-bold text-indigo-400 font-heading">
                      {item.score.toFixed(1)} / 100
                    </span>
                  </div>
                  <p className="text-xs text-slate-400">
                    Evaluation of experimental controls, statistical rigor, and dataset disclosures.
                  </p>
                </div>
              );
            })()}

            {/* Scope Alignment */}
            {(() => {
              const item = catScores['scope_alignment'] || { score: 100, weight: 0.15 };
              return (
                <div className="bg-slate-900/60 p-4 rounded-xl border border-slate-800">
                  <div className="flex items-center justify-between mb-1">
                    <h5 className="text-sm font-semibold text-white">Scope & Venue Alignment</h5>
                    <span className="text-base font-bold text-cyan-400 font-heading">
                      {item.score.toFixed(1)} / 100
                    </span>
                  </div>
                  <p className="text-xs text-slate-400">
                    Fit against targeted publisher themes, contribution depth, and novelty positioning.
                  </p>
                </div>
              );
            })()}
          </div>

          {/* Peer Review Assessment Dimensions */}
          <div className="space-y-3 pt-2">
            <h4 className="text-sm font-bold text-slate-300 font-heading flex items-center gap-2">
              <Award className="w-4 h-4 text-indigo-400" />
              Peer-Review Evaluation Dimensions
            </h4>

            {assessments.length > 0 ? (
              <div className="space-y-3">
                {assessments.map((a, idx) => {
                  let badgeClass = 'bg-emerald-500/10 text-emerald-300 border-emerald-500/30';
                  if (a.assessment === 'critical_gap') {
                    badgeClass = 'bg-rose-500/10 text-rose-300 border-rose-500/30';
                  } else if (a.assessment === 'needs_improvement') {
                    badgeClass = 'bg-amber-500/10 text-amber-300 border-amber-500/30';
                  } else if (a.assessment === 'adequate') {
                    badgeClass = 'bg-blue-500/10 text-blue-300 border-blue-500/30';
                  }

                  return (
                    <div
                      key={idx}
                      className="p-4 rounded-xl bg-slate-900/70 border border-slate-800 hover:border-slate-700/80 transition-all space-y-2"
                    >
                      <div className="flex items-center justify-between">
                        <span className="text-sm font-bold text-white font-heading">
                          {a.criterion_label || a.criterion.replace(/_/g, ' ').toUpperCase()}
                        </span>
                        <span className={`text-[10px] font-mono px-2.5 py-0.5 rounded-full border ${badgeClass} uppercase font-semibold`}>
                          {a.assessment.replace(/_/g, ' ')}
                        </span>
                      </div>

                      <p className="text-xs sm:text-sm text-slate-300 leading-relaxed">
                        {a.explanation}
                      </p>

                      <div className="pt-2 border-t border-slate-800/80 flex items-start gap-1.5 text-xs text-indigo-300">
                        <Lightbulb className="w-3.5 h-3.5 flex-shrink-0 text-indigo-400 mt-0.5" />
                        <span><b>Recommended Action:</b> {a.recommended_action}</span>
                      </div>
                    </div>
                  );
                })}
              </div>
            ) : (
              <p className="text-xs text-slate-400 italic">
                Standard peer-review heuristics applied across methodology and claim-evidence consistency.
              </p>
            )}
          </div>
        </div>
      )}

      {/* Tab 3: Verification Status */}
      {activeTab === 'verification' && (
        <div className="space-y-6">
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
            <div className="p-4 rounded-xl bg-emerald-950/20 border border-emerald-500/30 flex flex-col justify-between">
              <div className="flex items-center justify-between mb-2">
                <span className="text-xs text-emerald-400 font-medium">Passed Checks</span>
                <CheckCircle2 className="w-4 h-4 text-emerald-400" />
              </div>
              <span className="text-2xl font-black text-emerald-300 font-heading">
                {coverage?.passed_count || 0}
              </span>
              <p className="text-[11px] text-slate-400 mt-1">Verified rules satisfied</p>
            </div>

            <div className="p-4 rounded-xl bg-rose-950/20 border border-rose-500/30 flex flex-col justify-between">
              <div className="flex items-center justify-between mb-2">
                <span className="text-xs text-rose-400 font-medium">Failed Requirements</span>
                <XCircle className="w-4 h-4 text-rose-400" />
              </div>
              <span className="text-2xl font-black text-rose-300 font-heading">
                {coverage?.failed_count || 0}
              </span>
              <p className="text-[11px] text-slate-400 mt-1">Mandatory rules violated</p>
            </div>

            <div className="p-4 rounded-xl bg-amber-950/20 border border-amber-500/30 flex flex-col justify-between">
              <div className="flex items-center justify-between mb-2">
                <span className="text-xs text-amber-400 font-medium">Advisory Warnings</span>
                <AlertTriangle className="w-4 h-4 text-amber-400" />
              </div>
              <span className="text-2xl font-black text-amber-300 font-heading">
                {coverage?.warning_count || 0}
              </span>
              <p className="text-[11px] text-slate-400 mt-1">Recommended adjustments</p>
            </div>

            <div className="p-4 rounded-xl bg-violet-950/20 border border-violet-500/30 flex flex-col justify-between">
              <div className="flex items-center justify-between mb-2">
                <span className="text-xs text-violet-400 font-medium">Unable to Verify</span>
                <HelpCircle className="w-4 h-4 text-violet-400" />
              </div>
              <span className="text-2xl font-black text-violet-300 font-heading">
                {coverage?.unverified_count || 0}
              </span>
              <p className="text-[11px] text-slate-400 mt-1">Extraction boundaries</p>
            </div>
          </div>

          {coverage && (
            <div className="p-4 rounded-xl bg-slate-900/80 border border-slate-800 text-xs text-slate-300 space-y-1">
              <p>
                <b>Platform Verification Audit:</b> Evaluated <b>{coverage.total_checks}</b> automated rules across all three verification engines.
              </p>
              <p className="text-slate-400">
                Checks unable to verify are not assumed to have passed; they receive a conservative provisional rating to protect authors against unexpected desk rejections.
              </p>
            </div>
          )}
        </div>
      )}
    </div>
  );
};
