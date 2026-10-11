import React, { useState } from 'react';
import {
  ShieldCheck,
  CheckCircle2,
  XCircle,
  AlertTriangle,
  HelpCircle,
  ExternalLink,
} from 'lucide-react';
import { Finding } from '../types';

interface AuditTrailProps {
  findings: Finding[];
}

export const AuditTrail: React.FC<AuditTrailProps> = ({ findings }) => {
  const [filter, setFilter] = useState<'all' | 'critical' | 'warning' | 'unverified' | 'pass'>('all');

  const filtered = findings.filter((f) => {
    if (filter === 'critical') return f.status === 'fail' && f.severity === 'critical';
    if (filter === 'warning') return f.status === 'warning';
    if (filter === 'unverified') return f.status === 'unable_to_verify';
    if (filter === 'pass') return f.status === 'pass';
    return true;
  });

  return (
    <div className="glass-panel-elevated rounded-2xl p-6 sm:p-8 border border-slate-800 space-y-6">
      {/* Header & Filter Row */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-slate-800 pb-4">
        <div>
          <h3 className="text-xl font-bold font-heading text-white tracking-tight flex items-center gap-2">
            <ShieldCheck className="w-5 h-5 text-indigo-400" />
            Verification Check Audit Trail
          </h3>
          <p className="text-xs text-slate-400 mt-0.5">
            Complete rule-by-rule audit trace evaluated by deterministic checks, RAG guidelines, and academic heuristics.
          </p>
        </div>

        {/* Filter Pills */}
        <div className="flex flex-wrap items-center gap-1.5 p-1 rounded-xl bg-slate-900 border border-slate-800 text-xs self-start sm:self-auto">
          <button
            onClick={() => setFilter('all')}
            className={`px-2.5 py-1 rounded-lg font-medium transition-colors cursor-pointer ${
              filter === 'all' ? 'bg-slate-700 text-white' : 'text-slate-400 hover:text-slate-200'
            }`}
          >
            All ({findings.length})
          </button>
          <button
            onClick={() => setFilter('critical')}
            className={`px-2.5 py-1 rounded-lg font-medium transition-colors cursor-pointer ${
              filter === 'critical' ? 'bg-rose-500/30 text-rose-300 font-semibold' : 'text-slate-400 hover:text-slate-200'
            }`}
          >
            Critical
          </button>
          <button
            onClick={() => setFilter('warning')}
            className={`px-2.5 py-1 rounded-lg font-medium transition-colors cursor-pointer ${
              filter === 'warning' ? 'bg-amber-500/30 text-amber-300 font-semibold' : 'text-slate-400 hover:text-slate-200'
            }`}
          >
            Warnings
          </button>
          <button
            onClick={() => setFilter('unverified')}
            className={`px-2.5 py-1 rounded-lg font-medium transition-colors cursor-pointer ${
              filter === 'unverified' ? 'bg-violet-500/30 text-violet-300 font-semibold' : 'text-slate-400 hover:text-slate-200'
            }`}
          >
            Unverified
          </button>
          <button
            onClick={() => setFilter('pass')}
            className={`px-2.5 py-1 rounded-lg font-medium transition-colors cursor-pointer ${
              filter === 'pass' ? 'bg-emerald-500/30 text-emerald-300 font-semibold' : 'text-slate-400 hover:text-slate-200'
            }`}
          >
            Passed
          </button>
        </div>
      </div>

      {/* Findings List */}
      {filtered.length === 0 ? (
        <div className="text-center py-8 text-xs text-slate-400">
          No findings matching this filter.
        </div>
      ) : (
        <div className="space-y-3">
          {filtered.map((f, idx) => {
            let statusBadge = 'bg-emerald-500/10 text-emerald-300 border-emerald-500/30';
            let cardBorder = 'border-slate-800/80';

            if (f.status === 'fail') {
              statusBadge = 'bg-rose-500/10 text-rose-300 border-rose-500/30';
              cardBorder = 'border-rose-500/20';
            } else if (f.status === 'warning') {
              statusBadge = 'bg-amber-500/10 text-amber-300 border-amber-500/30';
              cardBorder = 'border-amber-500/20';
            } else if (f.status === 'unable_to_verify') {
              statusBadge = 'bg-violet-500/10 text-violet-300 border-violet-500/30';
              cardBorder = 'border-violet-500/20';
            }

            return (
              <div
                key={f.finding_id || idx}
                className={`p-4 rounded-xl bg-slate-900/60 border ${cardBorder} transition-all space-y-2.5`}
              >
                {/* Header */}
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-2">
                    <span className={`text-[10px] font-mono px-2 py-0.5 rounded border uppercase font-bold ${statusBadge}`}>
                      {f.status.replace(/_/g, ' ')}
                    </span>
                    <span className="text-xs text-slate-400 capitalize">
                      {f.category ? f.category.replace(/_/g, ' ') : ''}
                    </span>
                  </div>
                </div>

                {/* Title */}
                <h5 className="text-sm font-semibold text-slate-100 font-heading">
                  {f.title}
                </h5>

                {/* Grid */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-2 text-xs">
                  <div className="p-2.5 rounded-lg bg-slate-950/60 border border-slate-800">
                    <span className="text-[10px] text-slate-500 font-mono uppercase block mb-0.5">
                      Expected Requirement
                    </span>
                    <p className="text-slate-300">{f.expected_requirement}</p>
                  </div>

                  <div className="p-2.5 rounded-lg bg-slate-950/60 border border-slate-800">
                    <span className="text-[10px] text-slate-500 font-mono uppercase block mb-0.5">
                      Actual Observation
                    </span>
                    <p className="text-slate-300">{f.actual_observation}</p>
                  </div>
                </div>

                {/* Evidence Excerpt */}
                {f.evidence && (
                  <div className="p-2.5 rounded-lg bg-slate-950/40 border border-slate-800/80 text-xs">
                    <span className="text-[10px] text-slate-500 font-mono uppercase block mb-0.5">
                      Evidence Excerpt
                    </span>
                    <p className="font-mono text-slate-300 text-[11px] italic">
                      "{f.evidence}"
                    </p>
                  </div>
                )}

                {/* Publisher Policy link */}
                {f.guideline_source && f.guideline_source.source_url && (
                  <div className="text-[11px] text-cyan-400 flex items-center gap-1 pt-1">
                    <ExternalLink className="w-3 h-3 flex-shrink-0" />
                    <a
                      href={f.guideline_source.source_url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="hover:underline"
                    >
                      {f.guideline_source.publisher || 'Publisher'} Policy (
                      {f.guideline_source.section_title || 'Guidelines'})
                    </a>
                  </div>
                )}
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
};
