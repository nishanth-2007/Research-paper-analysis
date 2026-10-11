import React, { useState } from 'react';
import { X, Sparkles, Copy, Check, Lightbulb } from 'lucide-react';
import { ConsolidatedIssue } from '../types';

interface RevisionGuidanceModalProps {
  issue: ConsolidatedIssue | null;
  onClose: () => void;
}

export const RevisionGuidanceModal: React.FC<RevisionGuidanceModalProps> = ({
  issue,
  onClose,
}) => {
  const [copied, setCopied] = useState(false);

  if (!issue) return null;

  const strategyText =
    issue.suggested_revision_guidance ||
    'Drafting Tip: State clear empirical evidence, define parameter variables, and align section headers with target journal guidelines.';

  const handleCopyStrategy = () => {
    const textToCopy = `Strategy for: ${issue.title}\nProblem: ${issue.problem_statement}\nRecommended Action: ${issue.recommended_action}\n\nRevision Guidance:\n${strategyText}`;
    navigator.clipboard.writeText(textToCopy);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/80 backdrop-blur-sm animate-fadeIn">
      <div className="glass-panel-elevated w-full max-w-2xl rounded-2xl border border-slate-700/80 p-6 sm:p-8 space-y-5 relative shadow-2xl">
        {/* Header */}
        <div className="flex items-start justify-between gap-4 border-b border-slate-800 pb-4">
          <div className="flex items-center space-x-2.5">
            <div className="w-9 h-9 rounded-xl bg-indigo-600/20 border border-indigo-500/30 flex items-center justify-center">
              <Sparkles className="w-5 h-5 text-indigo-400" />
            </div>
            <div>
              <h3 className="text-base sm:text-lg font-bold font-heading text-white">
                AI Journal Revision Guidance
              </h3>
              <p className="text-xs text-slate-400">
                Actionable writing guidance and rewriting strategies tailored to target journal guidelines.
              </p>
            </div>
          </div>

          <button
            onClick={onClose}
            className="text-slate-400 hover:text-white p-1.5 rounded-lg hover:bg-slate-800 transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Content */}
        <div className="space-y-4 text-xs sm:text-sm">
          <div>
            <span className="text-[11px] font-mono uppercase text-slate-400 tracking-wider block mb-1">
              Issue Context
            </span>
            <h4 className="text-sm sm:text-base font-semibold text-slate-100 font-heading">
              {issue.title}
            </h4>
          </div>

          <div className="p-3.5 rounded-xl bg-slate-900/80 border border-slate-800">
            <span className="text-[11px] font-mono text-slate-400 uppercase tracking-wider block mb-1">
              Core Problem
            </span>
            <p className="text-slate-200 leading-relaxed">
              {issue.problem_statement || issue.actual_observation}
            </p>
          </div>

          <div className="p-3.5 rounded-xl bg-indigo-950/20 border border-indigo-500/30">
            <span className="text-[11px] font-mono text-indigo-400 uppercase tracking-wider block mb-1">
              Recommended Action Item
            </span>
            <p className="text-indigo-100 leading-relaxed font-medium">
              {issue.recommended_action}
            </p>
          </div>

          <div className="p-4 rounded-xl bg-slate-900 border border-slate-700/80">
            <div className="flex items-center gap-1.5 text-xs font-bold text-amber-400 mb-1.5">
              <Lightbulb className="w-4 h-4 text-amber-400" />
              <span>Recommended Drafting Strategy</span>
            </div>
            <p className="text-slate-300 leading-relaxed font-sans text-xs sm:text-sm">
              {strategyText}
            </p>
          </div>
        </div>

        {/* Footer Actions */}
        <div className="flex items-center justify-end gap-3 pt-4 border-t border-slate-800">
          <button
            onClick={handleCopyStrategy}
            className="inline-flex items-center gap-1.5 px-4 py-2 rounded-xl text-xs font-semibold bg-indigo-600 hover:bg-indigo-500 text-white transition-colors shadow-sm cursor-pointer"
          >
            {copied ? (
              <>
                <Check className="w-4 h-4 text-white" />
                <span>Copied to Clipboard!</span>
              </>
            ) : (
              <>
                <Copy className="w-4 h-4 text-indigo-200" />
                <span>Copy Strategy & Prompt</span>
              </>
            )}
          </button>

          <button
            onClick={onClose}
            className="px-4 py-2 rounded-xl text-xs font-semibold bg-slate-800 hover:bg-slate-700 text-slate-300 transition-colors cursor-pointer"
          >
            Close
          </button>
        </div>
      </div>
    </div>
  );
};
