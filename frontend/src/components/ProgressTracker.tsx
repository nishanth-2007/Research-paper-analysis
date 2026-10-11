import React from 'react';
import { Cpu, Loader2 } from 'lucide-react';
import { AnalysisStatusResponse } from '../types';

interface ProgressTrackerProps {
  status: AnalysisStatusResponse;
}

export const ProgressTracker: React.FC<ProgressTrackerProps> = ({ status }) => {
  const percent = status.progress_percent || 5;

  return (
    <div className="glass-panel-elevated rounded-2xl p-6 relative overflow-hidden border border-indigo-500/30">
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center space-x-2.5">
          <div className="w-8 h-8 rounded-lg bg-indigo-500/20 border border-indigo-500/30 flex items-center justify-center">
            <Cpu className="w-4 h-4 text-indigo-400 animate-pulse" />
          </div>
          <div>
            <h4 className="text-sm font-semibold text-white font-heading">
              Verification Engine Orchestration in Progress
            </h4>
            <p className="text-xs text-slate-400">
              {status.current_step || 'Initializing evaluation pipeline...'}
            </p>
          </div>
        </div>

        <div className="flex items-center space-x-2 font-mono text-sm font-semibold text-indigo-400">
          <Loader2 className="w-4 h-4 animate-spin text-indigo-400" />
          <span>{percent}%</span>
        </div>
      </div>

      {/* Progress Bar */}
      <div className="w-full bg-slate-900/80 rounded-full h-2.5 overflow-hidden border border-slate-800">
        <div
          className="bg-gradient-to-r from-indigo-500 via-cyan-400 to-emerald-400 h-2.5 rounded-full transition-all duration-300 ease-out shadow-sm shadow-indigo-500/50"
          style={{ width: `${Math.min(100, Math.max(5, percent))}%` }}
        />
      </div>

      <div className="mt-3 flex items-center justify-between text-[11px] text-slate-500 font-mono">
        <span>Deterministic Verification &bull; Publisher RAG &bull; Journal Review Rigor LLM</span>
        <span>Parallel Engine Execution</span>
      </div>
    </div>
  );
};
