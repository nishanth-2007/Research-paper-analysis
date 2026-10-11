import React from 'react';
import {
  Download,
  FileDown,
  RefreshCw,
  AlertCircle,
  CheckCircle2,
  FileCode,
  ShieldCheck,
  Calendar,
  Building,
  RotateCcw,
  Sparkles,
  ArrowRight,
  FileText,
} from 'lucide-react';
import { CompleteAnalysisReport } from '../types';
import { ApiService } from '../services/api';

interface ReadinessScoreHeroProps {
  report: CompleteAnalysisReport;
  onRerun: () => void;
  onReset?: () => void;
  isAnalyzing: boolean;
  onGenerateManuscript?: () => void;
}

export const ReadinessScoreHero: React.FC<ReadinessScoreHeroProps> = ({
  report,
  onRerun,
  onReset,
  isAnalyzing,
  onGenerateManuscript,
}) => {
  const { readiness_score, executive_summary, verification_coverage } = report;
  const score = readiness_score.overall_score;

  // Determine color scheme
  let scoreColorClass = 'text-rose-400';
  let scoreStrokeClass = '#fb7185';
  let tierBadgeClass = 'bg-rose-500/10 text-rose-300 border-rose-500/30';

  if (score >= 80) {
    scoreColorClass = 'text-emerald-400';
    scoreStrokeClass = '#34d399';
    tierBadgeClass = 'bg-emerald-500/10 text-emerald-300 border-emerald-500/30';
  } else if (score >= 65) {
    scoreColorClass = 'text-amber-400';
    scoreStrokeClass = '#fbbf24';
    tierBadgeClass = 'bg-amber-500/10 text-amber-300 border-amber-500/30';
  }

  // SVG circular gauge calculations
  const radius = 64;
  const circumference = 2 * Math.PI * radius;
  const strokeDashoffset = circumference - (score / 100) * circumference;

  // Export JSON
  const handleExportJson = () => {
    const jsonStr = JSON.stringify(report, null, 2);
    const blob = new Blob([jsonStr], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `readiness_report_${report.analysis_id}.json`;
    a.click();
    URL.revokeObjectURL(url);
  };

  const formattedDate = new Date(report.generated_at).toLocaleDateString(undefined, {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  });

  return (
    <div className="glass-panel-elevated rounded-2xl p-6 sm:p-8 relative overflow-hidden border border-slate-800">
      {/* Top Header Row with Manuscript details and export toolbar */}
      <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-4 border-b border-slate-800/80 pb-6 mb-6">
        <div>
          <div className="flex flex-wrap items-center gap-2 mb-1.5">
            <span className="inline-flex items-center gap-1 text-[11px] font-mono px-2.5 py-0.5 rounded-full bg-indigo-500/10 text-indigo-300 border border-indigo-500/20">
              <Building className="w-3 h-3" />
              {report.target_journal_name ? `${report.target_journal_name} Target` : 'General Journal Guidelines'}
            </span>
            {report.guideline_version_tag && (
              <span className="text-[11px] font-mono px-2 py-0.5 rounded-full bg-slate-800 text-slate-400 border border-slate-700">
                v{report.guideline_version_tag}
              </span>
            )}
            <span className="inline-flex items-center gap-1 text-[11px] text-slate-400 font-mono">
              <Calendar className="w-3 h-3 text-slate-500" />
              {formattedDate}
            </span>
          </div>

          <h2 className="text-xl sm:text-2xl font-bold font-heading text-white tracking-tight">
            {report.manuscript_title || 'Untitled Manuscript'}
          </h2>
        </div>

        {/* Action Toolbar */}
        <div className="flex flex-wrap items-center gap-2 sm:gap-2.5">
          <a
            href={ApiService.getExportUrl(report.analysis_id, 'pdf')}
            className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium bg-slate-800/90 hover:bg-slate-700 text-slate-200 border border-slate-700 hover:border-slate-600 transition-colors"
            title="Download PDF Publication Audit Report"
          >
            <Download className="w-3.5 h-3.5 text-rose-400" />
            <span>PDF Report</span>
          </a>

          <a
            href={ApiService.getExportUrl(report.analysis_id, 'docx')}
            className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium bg-slate-800/90 hover:bg-slate-700 text-slate-200 border border-slate-700 hover:border-slate-600 transition-colors"
            title="Download Word DOCX Publication Audit Report"
          >
            <FileDown className="w-3.5 h-3.5 text-blue-400" />
            <span>DOCX Report</span>
          </a>

          <button
            onClick={handleExportJson}
            className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium bg-slate-800/90 hover:bg-slate-700 text-slate-200 border border-slate-700 hover:border-slate-600 transition-colors cursor-pointer"
            title="Export raw JSON findings data"
          >
            <FileCode className="w-3.5 h-3.5 text-amber-400" />
            <span>Export JSON</span>
          </button>

          <button
            onClick={onRerun}
            disabled={isAnalyzing}
            className="inline-flex items-center gap-1.5 px-3.5 py-1.5 rounded-lg text-xs font-medium bg-indigo-600/20 hover:bg-indigo-600/30 text-indigo-300 border border-indigo-500/30 transition-colors cursor-pointer disabled:opacity-50"
            title="Re-run verification engines on this manuscript"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${isAnalyzing ? 'animate-spin' : ''}`} />
            <span>Re-Analyze</span>
          </button>

          {onReset && (
            <button
              onClick={onReset}
              className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium bg-slate-800/90 hover:bg-slate-700 text-slate-300 hover:text-white border border-slate-700 hover:border-slate-600 transition-colors cursor-pointer"
              title="Clear report and audit a new manuscript"
            >
              <RotateCcw className="w-3.5 h-3.5 text-slate-400" />
              <span>New Audit</span>
            </button>
          )}
        </div>
      </div>

      {/* Main Score Hero Layout: Radial Gauge + Synthesis */}
      <div className="grid grid-cols-1 md:grid-cols-12 gap-8 items-center">
        {/* Left: Circular Radial Score Indicator */}
        <div className="md:col-span-5 lg:col-span-4 flex flex-col items-center justify-center p-4">
          <div className="relative w-44 h-44 flex items-center justify-center">
            <svg className="w-full h-full transform -rotate-90" viewBox="0 0 160 160">
              {/* Background Track */}
              <circle
                cx="80"
                cy="80"
                r={radius}
                className="stroke-slate-800/80"
                strokeWidth="10"
                fill="transparent"
              />
              {/* Score Value Arc */}
              <circle
                cx="80"
                cy="80"
                r={radius}
                stroke={scoreStrokeClass}
                strokeWidth="10"
                strokeDasharray={circumference}
                strokeDashoffset={strokeDashoffset}
                strokeLinecap="round"
                fill="transparent"
                className="transition-all duration-1000 ease-out"
              />
            </svg>

            {/* Score Content in Center */}
            <div className="absolute inset-0 flex flex-col items-center justify-center text-center">
              <span className={`text-4xl font-extrabold font-heading tracking-tight ${scoreColorClass}`}>
                {score.toFixed(1)}
              </span>
              <span className="text-[10px] text-slate-400 uppercase tracking-wider font-mono mt-0.5">
                Readiness Score
              </span>
            </div>
          </div>

          {/* Tier Badge */}
          <div className="mt-3 flex flex-col items-center gap-1.5">
            <span className={`text-xs font-bold px-3 py-1 rounded-full border ${tierBadgeClass} uppercase tracking-wider`}>
              {readiness_score.readiness_tier}
            </span>

            {/* Provisional warning pill */}
            {(readiness_score.is_provisional || (report.document_validation && !report.document_validation.is_plausible_manuscript)) && (
              <span className="inline-flex items-center gap-1 text-[11px] px-2.5 py-0.5 rounded-full bg-amber-500/10 text-amber-300 border border-amber-500/30 font-medium">
                <AlertCircle className="w-3 h-3" />
                Provisional Score Flagged
              </span>
            )}
          </div>
        </div>

        {/* Right: Executive Synthesis and Verification Coverage */}
        <div className="md:col-span-7 lg:col-span-8 flex flex-col justify-center space-y-4">
          <div>
            <h3 className="text-sm font-semibold text-slate-300 font-heading uppercase tracking-wider mb-2 flex items-center gap-2">
              <ShieldCheck className="w-4 h-4 text-indigo-400" />
              Executive Verification Synthesis
            </h3>
            <p className="text-sm sm:text-base text-slate-200 leading-relaxed font-sans bg-slate-900/60 p-4 rounded-xl border border-slate-800/80">
              "{executive_summary.synthesis || 'Manuscript verified across deterministic structure, publisher guideline compliance, and journal peer-review rigor heuristics.'}"
            </p>
          </div>

          {/* Verification Coverage Progress Bar */}
          {verification_coverage && (
            <div className="bg-slate-900/50 p-3.5 rounded-xl border border-slate-800/80">
              <div className="flex items-center justify-between text-xs mb-2">
                <span className="text-slate-300 font-medium">Platform Verification Coverage:</span>
                <span className="font-mono text-cyan-400 font-semibold">
                  {verification_coverage.coverage_percent}%
                </span>
              </div>
              <div className="w-full bg-slate-800 rounded-full h-2 overflow-hidden">
                <div
                  className="bg-gradient-to-r from-indigo-500 to-cyan-400 h-2 rounded-full transition-all duration-700"
                  style={{ width: `${verification_coverage.coverage_percent}%` }}
                />
              </div>
              <div className="mt-2 flex items-center justify-between text-[11px] text-slate-400 font-mono">
                <span>
                  {verification_coverage.total_checks - verification_coverage.unverified_count} of {verification_coverage.total_checks} rules verified
                </span>
                <span className="text-emerald-400">
                  {verification_coverage.passed_count} verified passes
                </span>
              </div>
            </div>
          )}

          {/* Bottom-Right: Generate Updated Manuscript CTA */}
          {onGenerateManuscript && (
            <div className="pt-1 flex flex-col sm:flex-row sm:items-center justify-between gap-3 bg-gradient-to-r from-indigo-950/40 via-purple-950/30 to-slate-900/60 p-3.5 rounded-xl border border-indigo-500/25">
              <div className="flex items-center gap-2.5">
                <div className="w-8 h-8 rounded-lg bg-indigo-500/20 border border-indigo-500/30 flex items-center justify-center flex-shrink-0">
                  <Sparkles className="w-4 h-4 text-indigo-300" />
                </div>
                <div>
                  <p className="text-xs font-semibold text-white">
                    Automated Manuscript Remediation
                  </p>
                  <p className="text-[11px] text-slate-400">
                    Auto-align citations, missing sections &amp; target journal guidelines
                  </p>
                </div>
              </div>

              <button
                onClick={onGenerateManuscript}
                className="group inline-flex items-center justify-center gap-2 px-4 py-2.5 rounded-lg text-xs font-semibold text-white bg-gradient-to-r from-indigo-600 via-purple-600 to-pink-600 hover:from-indigo-500 hover:via-purple-500 hover:to-pink-500 shadow-md shadow-indigo-600/30 hover:shadow-indigo-600/50 border border-indigo-400/30 transition-all duration-200 transform hover:-translate-y-0.5 active:translate-y-0 cursor-pointer flex-shrink-0"
                title="Generate updated publication-ready manuscript with official citations"
              >
                <span>Generate Manuscript</span>
                <ArrowRight className="w-3.5 h-3.5 text-indigo-100 group-hover:translate-x-0.5 transition-transform" />
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
