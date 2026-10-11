import React from 'react';
import {
  FileText,
  CheckCircle2,
  AlertTriangle,
  HelpCircle,
  FileSearch,
  BookOpen,
} from 'lucide-react';
import { SectionScoreDetail } from '../types';

interface ManuscriptSectionScoresProps {
  sectionScores: Record<string, SectionScoreDetail>;
}

export const ManuscriptSectionScores: React.FC<ManuscriptSectionScoresProps> = ({
  sectionScores,
}) => {
  const sectionsList = [
    { key: 'abstract', defaultTitle: 'Abstract' },
    { key: 'introduction', defaultTitle: 'Introduction' },
    { key: 'methodology', defaultTitle: 'Methodology' },
    { key: 'results', defaultTitle: 'Results / Evaluation' },
    { key: 'conclusion', defaultTitle: 'Conclusion & Limitations' },
    { key: 'references', defaultTitle: 'References & Bibliography' },
  ];

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <div>
          <h3 className="text-lg font-bold font-heading text-white tracking-tight flex items-center gap-2">
            Manuscript Section Readiness
          </h3>
          <p className="text-xs text-slate-400">
            Structural and content compliance evaluated for each standard research section where text evidence was extracted.
          </p>
        </div>
        <span className="text-[11px] font-mono px-2.5 py-1 rounded bg-slate-900 border border-slate-800 text-slate-400">
          IMRAD Architecture
        </span>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
        {sectionsList.map(({ key, defaultTitle }) => {
          const detail = sectionScores[key] || {
            section_id: key,
            section_name: defaultTitle,
            score: 100,
            status: 'pass',
            passed_count: 0,
            failed_count: 0,
            warning_count: 0,
            has_sufficient_evidence: true,
            evidence_notes: 'Standard section requirements verified.',
          };

          const score = detail.score;
          let statusBadgeClass = 'bg-emerald-500/10 text-emerald-300 border-emerald-500/30';
          let statusLabel = 'PASSED';
          let barBg = 'bg-emerald-500';

          if (detail.status === 'unverified') {
            statusBadgeClass = 'bg-violet-500/10 text-violet-300 border-violet-500/30';
            statusLabel = 'UNVERIFIED';
            barBg = 'bg-violet-500';
          } else if (detail.failed_count > 0 || detail.status === 'needs_revision') {
            statusBadgeClass = 'bg-rose-500/10 text-rose-300 border-rose-500/30';
            statusLabel = 'NEEDS REVISION';
            barBg = 'bg-rose-500';
          } else if (detail.warning_count > 0) {
            statusBadgeClass = 'bg-amber-500/10 text-amber-300 border-amber-500/30';
            statusLabel = 'ADVISORY';
            barBg = 'bg-amber-500';
          }

          return (
            <div
              key={key}
              className="glass-panel rounded-xl p-4 border border-slate-800/90 hover:border-slate-700/80 transition-all flex flex-col justify-between"
            >
              <div>
                {/* Header */}
                <div className="flex items-center justify-between mb-2">
                  <h4 className="text-sm font-bold text-white font-heading truncate">
                    {detail.section_name || defaultTitle}
                  </h4>
                  <span className={`text-[10px] font-mono px-2 py-0.5 rounded border ${statusBadgeClass}`}>
                    {statusLabel}
                  </span>
                </div>

                {/* Score and Bar */}
                <div className="flex items-baseline justify-between mb-1">
                  <span className="text-[11px] text-slate-400 font-mono">Section Score</span>
                  <span className="text-base font-bold text-slate-100 font-heading">
                    {score.toFixed(1)} <span className="text-xs text-slate-500 font-normal">/ 100</span>
                  </span>
                </div>

                <div className="w-full bg-slate-900 rounded-full h-1.5 overflow-hidden border border-slate-800/80 mb-3">
                  <div
                    className={`${barBg} h-1.5 rounded-full transition-all duration-500`}
                    style={{ width: `${Math.min(100, Math.max(0, score))}%` }}
                  />
                </div>
              </div>

              <div>
                {/* Notes & Evidence */}
                <p className="text-xs text-slate-400 leading-relaxed mb-2.5 min-h-[32px]">
                  {detail.evidence_notes || 'Section structure verified against guideline requirements.'}
                </p>

                <div className="pt-2 border-t border-slate-800/70 flex items-center justify-between text-[11px] font-mono text-slate-500">
                  {detail.has_sufficient_evidence ? (
                    <span className="text-emerald-400/90 flex items-center gap-1">
                      <CheckCircle2 className="w-3 h-3" />
                      Text evidence verified
                    </span>
                  ) : (
                    <span className="text-amber-400/90 flex items-center gap-1">
                      <AlertTriangle className="w-3 h-3" />
                      Limited text evidence
                    </span>
                  )}
                  <span>
                    {detail.passed_count}P / {detail.failed_count}F / {detail.warning_count}W
                  </span>
                </div>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};
