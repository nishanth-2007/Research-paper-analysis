import React from 'react';
import { Layers, BookCheck, Sparkles, AlertCircle, CheckCircle2 } from 'lucide-react';
import { EngineScoreDetail } from '../types';

interface ThreeEngineScoresProps {
  engineScores: Record<string, EngineScoreDetail>;
}

export const ThreeEngineScores: React.FC<ThreeEngineScoresProps> = ({ engineScores }) => {
  const deterministic = engineScores['deterministic'] || {
    engine_id: 'deterministic',
    engine_name: 'Deterministic Verification Engine',
    score: 100,
    passed_count: 0,
    failed_count: 0,
    warning_count: 0,
    unverified_count: 0,
    is_provisional: false,
    weight: 0.33,
  };

  const rag = engineScores['rag_knowledge'] || {
    engine_id: 'rag_knowledge',
    engine_name: 'Journal Guidelines RAG Engine',
    score: 100,
    passed_count: 0,
    failed_count: 0,
    warning_count: 0,
    unverified_count: 0,
    is_provisional: false,
    weight: 0.33,
  };

  const llm = engineScores['llm_academic'] || {
    engine_id: 'llm_academic',
    engine_name: 'LLM Research Evaluation Engine',
    score: 100,
    passed_count: 0,
    failed_count: 0,
    warning_count: 0,
    unverified_count: 0,
    is_provisional: false,
    weight: 0.33,
  };

  const engines = [
    {
      detail: deterministic,
      title: 'Deterministic Verification Engine',
      description:
        'Exact structural checks: missing sections, abstract word count, citation-to-reference matching, figure/table numbering, and formatting properties.',
      icon: Layers,
      accentColor: 'indigo',
    },
    {
      detail: rag,
      title: 'Journal Guidelines RAG Engine',
      description:
        'Isolated vector retrieval against versioned publisher guidelines: mandatory statements, ethics declarations, and venue-specific policies.',
      icon: BookCheck,
      accentColor: 'cyan',
    },
    {
      detail: llm,
      title: 'LLM Research Evaluation Engine',
      description:
        'Journal peer-review rigor assessment: research question clarity, methodology completeness, literature coverage, contribution, and limitation disclosure.',
      icon: Sparkles,
      accentColor: 'emerald',
    },
  ];

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <div>
          <h3 className="text-lg font-bold font-heading text-white tracking-tight flex items-center gap-2">
            Multi-Engine Verification Scores
          </h3>
          <p className="text-xs text-slate-400">
            Individual audit scores computed autonomously across our three specialized evaluation engines.
          </p>
        </div>
        <span className="text-[11px] font-mono px-2.5 py-1 rounded bg-slate-900 border border-slate-800 text-slate-400">
          Weight: 33.3% Each
        </span>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-5">
        {engines.map(({ detail, title, description, icon: Icon, accentColor }) => {
          const score = detail.score;
          let scoreTextClass = 'text-rose-400';
          let barBgClass = 'bg-rose-500';

          if (score >= 80) {
            scoreTextClass = 'text-emerald-400';
            barBgClass = 'bg-emerald-500';
          } else if (score >= 65) {
            scoreTextClass = 'text-amber-400';
            barBgClass = 'bg-amber-500';
          }

          return (
            <div
              key={detail.engine_id}
              className="glass-panel rounded-xl p-5 border border-slate-800 hover:border-slate-700/80 transition-all flex flex-col justify-between"
            >
              <div>
                {/* Header with Icon and Provisional Tag */}
                <div className="flex items-start justify-between gap-3 mb-3">
                  <div className="flex items-center space-x-2.5">
                    <div
                      className={`w-9 h-9 rounded-lg bg-${accentColor}-500/10 border border-${accentColor}-500/20 flex items-center justify-center flex-shrink-0`}
                    >
                      <Icon className="w-5 h-5 text-indigo-400" />
                    </div>
                    <div>
                      <h4 className="text-sm font-bold text-white font-heading leading-tight">
                        {title}
                      </h4>
                    </div>
                  </div>

                  {detail.is_provisional && (
                    <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-amber-500/10 text-amber-300 border border-amber-500/20">
                      Provisional
                    </span>
                  )}
                </div>

                <p className="text-xs text-slate-400 leading-relaxed mb-4 min-h-[48px]">
                  {description}
                </p>
              </div>

              <div>
                {/* Score and Bar */}
                <div className="flex items-baseline justify-between mb-1.5">
                  <span className="text-xs text-slate-400 font-medium">Engine Score</span>
                  <div className="flex items-baseline gap-1">
                    <span className={`text-2xl font-black font-heading ${scoreTextClass}`}>
                      {score.toFixed(1)}
                    </span>
                    <span className="text-xs text-slate-500">/ 100</span>
                  </div>
                </div>

                <div className="w-full bg-slate-900 rounded-full h-2 overflow-hidden border border-slate-800 mb-3">
                  <div
                    className={`${barBgClass} h-2 rounded-full transition-all duration-700`}
                    style={{ width: `${Math.min(100, Math.max(0, score))}%` }}
                  />
                </div>

                {/* Engine Check Stats */}
                <div className="flex items-center justify-between text-[11px] font-mono text-slate-400 pt-3 border-t border-slate-800/80">
                  <span className="text-emerald-400">{detail.passed_count} passed</span>
                  <span className="text-rose-400">{detail.failed_count} failed</span>
                  <span className="text-amber-400">{detail.warning_count} warnings</span>
                  <span className="text-slate-500">{detail.unverified_count} unverified</span>
                </div>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};
