import React, { useState } from 'react';
import {
  History,
  FileText,
  Building,
  Calendar,
  Sparkles,
  Eye,
  Trash2,
  ChevronDown,
  ChevronUp,
  ShieldCheck,
  AlertCircle,
  FileDown,
  Search,
  RotateCcw,
} from 'lucide-react';
import { UserAuditHistoryItem } from '../types';

interface UserUploadHistoryProps {
  history: UserAuditHistoryItem[];
  currentAnalysisId?: string;
  onLoadHistoryItem: (item: UserAuditHistoryItem) => void;
  onOpenStudioForItem: (item: UserAuditHistoryItem) => void;
  onDeleteItem: (id: string) => void;
  onClearAll: () => void;
}

export const UserUploadHistory: React.FC<UserUploadHistoryProps> = ({
  history,
  currentAnalysisId,
  onLoadHistoryItem,
  onOpenStudioForItem,
  onDeleteItem,
  onClearAll,
}) => {
  const [isCollapsed, setIsCollapsed] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');

  if (history.length === 0) {
    return null;
  }

  const filteredHistory = history.filter((item) => {
    const q = searchQuery.toLowerCase();
    return (
      item.title.toLowerCase().includes(q) ||
      item.filename.toLowerCase().includes(q) ||
      (item.journal_name || item.journal_id || '').toLowerCase().includes(q)
    );
  });

  return (
    <div className="glass-panel-elevated rounded-2xl p-5 sm:p-6 border border-slate-800 space-y-4">
      {/* Header Row */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-slate-800/80 pb-4">
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 rounded-lg bg-indigo-500/20 border border-indigo-500/30 flex items-center justify-center text-indigo-400">
            <History className="w-4 h-4" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h2 className="text-base sm:text-lg font-bold font-heading text-white">
                Audit History &amp; Recent Uploads
              </h2>
              <span className="text-[11px] font-mono px-2 py-0.5 rounded-full bg-slate-800 text-indigo-300 border border-slate-700">
                {history.length} {history.length === 1 ? 'file' : 'files'}
              </span>
            </div>
            <p className="text-xs text-slate-400">
              Access your previously audited manuscripts, inspection reports, and remediated files
            </p>
          </div>
        </div>

        {/* Toolbar: Search, Clear, Collapse */}
        <div className="flex items-center gap-2">
          {history.length > 2 && (
            <div className="relative">
              <Search className="w-3.5 h-3.5 text-slate-400 absolute left-2.5 top-2.5" />
              <input
                type="text"
                placeholder="Search history..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="pl-8 pr-3 py-1.5 text-xs rounded-lg bg-slate-900 border border-slate-800 text-slate-200 placeholder-slate-500 focus:outline-none focus:border-indigo-500 w-36 sm:w-44 transition-all"
              />
            </div>
          )}

          <button
            onClick={onClearAll}
            className="p-1.5 rounded-lg text-slate-400 hover:text-rose-400 hover:bg-slate-800/60 border border-transparent hover:border-slate-700 text-xs transition-colors cursor-pointer"
            title="Clear all audit history"
          >
            <RotateCcw className="w-3.5 h-3.5" />
          </button>

          <button
            onClick={() => setIsCollapsed(!isCollapsed)}
            className="p-1.5 rounded-lg text-slate-400 hover:text-slate-200 hover:bg-slate-800/60 border border-transparent hover:border-slate-700 transition-colors cursor-pointer"
            title={isCollapsed ? 'Expand history' : 'Collapse history'}
          >
            {isCollapsed ? <ChevronDown className="w-4 h-4" /> : <ChevronUp className="w-4 h-4" />}
          </button>
        </div>
      </div>

      {/* History Items List */}
      {!isCollapsed && (
        <div className="space-y-3 pt-1">
          {filteredHistory.length === 0 ? (
            <p className="text-xs text-slate-500 text-center py-4 font-mono">
              No previous manuscripts match "{searchQuery}"
            </p>
          ) : (
            filteredHistory.map((item) => {
              const isActive = currentAnalysisId === item.id;
              const formattedDate = new Date(item.uploaded_at).toLocaleDateString(undefined, {
                month: 'short',
                day: 'numeric',
                hour: '2-digit',
                minute: '2-digit',
              });

              // Color classes based on readiness score
              const score = item.readiness_score;
              let scoreColor = 'text-rose-400 border-rose-500/30 bg-rose-500/10';
              if (score !== undefined && score !== null) {
                if (score >= 80) {
                  scoreColor = 'text-emerald-400 border-emerald-500/30 bg-emerald-500/10';
                } else if (score >= 65) {
                  scoreColor = 'text-amber-400 border-amber-500/30 bg-amber-500/10';
                }
              }

              return (
                <div
                  key={item.id}
                  className={`rounded-xl p-4 border transition-all duration-200 flex flex-col md:flex-row md:items-center justify-between gap-4 ${
                    isActive
                      ? 'bg-slate-900/90 border-indigo-500/50 shadow-md shadow-indigo-950/40'
                      : 'bg-slate-900/50 hover:bg-slate-900/80 border-slate-800 hover:border-slate-700'
                  }`}
                >
                  {/* Left Column: Title & Metadata */}
                  <div className="space-y-1.5 min-w-0">
                    <div className="flex flex-wrap items-center gap-2">
                      <h3
                        onClick={() => onLoadHistoryItem(item)}
                        className="text-sm font-bold font-heading text-white hover:text-indigo-300 transition-colors cursor-pointer truncate max-w-md sm:max-w-xl"
                        title={item.title}
                      >
                        {item.title}
                      </h3>
                      {isActive && (
                        <span className="text-[10px] font-mono px-2 py-0.5 rounded-full bg-indigo-500/20 text-indigo-300 border border-indigo-500/30">
                          Active View
                        </span>
                      )}
                    </div>

                    <div className="flex flex-wrap items-center gap-x-3 gap-y-1 text-xs text-slate-400 font-mono">
                      <span className="flex items-center gap-1 text-slate-300">
                        <FileText className="w-3 h-3 text-slate-500" />
                        {item.filename}
                      </span>
                      <span className="flex items-center gap-1 text-indigo-300">
                        <Building className="w-3 h-3 text-indigo-400" />
                        {item.journal_name || item.journal_id}
                      </span>
                      <span className="flex items-center gap-1 text-slate-500">
                        <Calendar className="w-3 h-3" />
                        {formattedDate}
                      </span>
                    </div>
                  </div>

                  {/* Middle / Right: Metrics & Actions */}
                  <div className="flex flex-wrap items-center justify-between md:justify-end gap-3 flex-shrink-0">
                    {/* Metrics Pills */}
                    <div className="flex items-center gap-2">
                      {score !== undefined && score !== null ? (
                        <div className={`px-2.5 py-1 rounded-lg border text-xs font-mono font-bold ${scoreColor}`}>
                          <span>{score.toFixed(1)}</span>
                          <span className="text-[10px] font-normal opacity-80 ml-1">Score</span>
                        </div>
                      ) : (
                        <div className="px-2.5 py-1 rounded-lg border border-amber-500/30 bg-amber-500/10 text-amber-300 text-xs font-mono font-medium">
                          Uploaded
                        </div>
                      )}

                      {item.similarity_score !== undefined && (
                        <div className="px-2.5 py-1 rounded-lg border border-cyan-500/30 bg-cyan-500/10 text-cyan-300 text-xs font-mono">
                          <span>{item.similarity_score.toFixed(1)}%</span>
                          <span className="text-[10px] opacity-75 ml-1">Sim</span>
                        </div>
                      )}

                      {item.blockers_count !== undefined ? (
                        item.blockers_count > 0 ? (
                          <span className="inline-flex items-center gap-1 text-[11px] font-mono px-2 py-0.5 rounded bg-rose-500/10 text-rose-300 border border-rose-500/25">
                            <AlertCircle className="w-3 h-3 text-rose-400" />
                            {item.blockers_count} Blocker{item.blockers_count > 1 ? 's' : ''}
                          </span>
                        ) : (
                          <span className="inline-flex items-center gap-1 text-[11px] font-mono px-2 py-0.5 rounded bg-emerald-500/10 text-emerald-300 border border-emerald-500/25">
                            <ShieldCheck className="w-3 h-3" />
                            0 Blockers
                          </span>
                        )
                      ) : null}
                    </div>

                    {/* Action Buttons */}
                    <div className="flex items-center gap-1.5">
                      {item.report ? (
                        <>
                          <button
                            onClick={() => onLoadHistoryItem(item)}
                            className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 transition-colors cursor-pointer"
                            title="View audit results for this manuscript"
                          >
                            <Eye className="w-3.5 h-3.5 text-indigo-400" />
                            <span>Audit Report</span>
                          </button>

                          <button
                            onClick={() => onOpenStudioForItem(item)}
                            className="inline-flex items-center gap-1 px-3 py-1.5 rounded-lg text-xs font-semibold text-white bg-gradient-to-r from-indigo-600 to-purple-600 hover:from-indigo-500 hover:to-purple-500 shadow-sm border border-indigo-400/30 transition-all cursor-pointer"
                            title="Open Remediated Manuscript Studio with Word and PDF download"
                          >
                            <Sparkles className="w-3 h-3 text-amber-300" />
                            <span>Studio</span>
                          </button>
                        </>
                      ) : (
                        <button
                          onClick={() => onLoadHistoryItem(item)}
                          className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold bg-indigo-600 hover:bg-indigo-500 text-white transition-colors cursor-pointer shadow-sm"
                          title="Load this manuscript to view or run verification"
                        >
                          <Eye className="w-3.5 h-3.5" />
                          <span>Load Manuscript</span>
                        </button>
                      )}

                      <button
                        onClick={() => onDeleteItem(item.id)}
                        className="p-1.5 rounded-lg text-slate-500 hover:text-rose-400 hover:bg-slate-800 transition-colors cursor-pointer"
                        title="Remove from history"
                      >
                        <Trash2 className="w-3.5 h-3.5" />
                      </button>
                    </div>
                  </div>
                </div>
              );
            })
          )}
        </div>
      )}
    </div>
  );
};
