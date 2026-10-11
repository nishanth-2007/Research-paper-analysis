import React, { useRef, useState } from 'react';
import {
  UploadCloud,
  FileText,
  CheckCircle2,
  AlertTriangle,
  Play,
  RefreshCw,
  Hash,
  FileCheck2,
  BookOpen,
} from 'lucide-react';
import { ManuscriptUploadResponse, Journal } from '../types';

interface UploadCardProps {
  onFileUpload: (file: File) => void;
  onRunAnalysis: () => void;
  isUploading: boolean;
  isAnalyzing: boolean;
  currentManuscript: ManuscriptUploadResponse | null;
  journals: Journal[];
  selectedJournalId: string;
  onSelectJournal: (id: string) => void;
}

export const UploadCard: React.FC<UploadCardProps> = ({
  onFileUpload,
  onRunAnalysis,
  isUploading,
  isAnalyzing,
  currentManuscript,
  journals,
  selectedJournalId,
  onSelectJournal,
}) => {
  const [isDragOver, setIsDragOver] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const selectedJournal = journals.find((j) => j.journal_id === selectedJournalId);

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(true);
  };

  const handleDragLeave = () => {
    setIsDragOver(false);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(false);
    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      onFileUpload(e.dataTransfer.files[0]);
    }
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      onFileUpload(e.target.files[0]);
    }
  };

  return (
    <section className="glass-panel-elevated rounded-2xl p-6 sm:p-8 relative overflow-hidden transition-all duration-300">
      {/* Decorative gradient blur in background */}
      <div className="absolute -top-24 -right-24 w-72 h-72 bg-indigo-600/10 rounded-full blur-3xl pointer-events-none" />
      <div className="absolute -bottom-24 -left-24 w-72 h-72 bg-cyan-600/10 rounded-full blur-3xl pointer-events-none" />

      <div className="relative z-10">
        <div className="mb-6 flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-slate-800/80 pb-5">
          <div>
            <h2 className="text-xl sm:text-2xl font-bold font-heading text-white tracking-tight flex items-center gap-2.5">
              <FileCheck2 className="w-6 h-6 text-indigo-400" />
              Manuscript Submission & Verification
            </h2>
            <p className="text-xs sm:text-sm text-slate-400 mt-1">
              Upload your research manuscript in PDF or DOCX format for automated multi-engine audit.
            </p>
          </div>

          {/* Target Journal Selection on Main Page */}
          <div className="flex flex-col sm:flex-row items-start sm:items-center gap-2 bg-slate-900/90 border border-slate-800 p-2 sm:px-3 sm:py-2 rounded-xl flex-shrink-0 shadow-inner">
            <label
              htmlFor="main-journal-select"
              className="text-xs font-semibold text-slate-300 flex items-center gap-1.5 whitespace-nowrap"
            >
              <BookOpen className="w-4 h-4 text-cyan-400" />
              <span>Target Journal:</span>
            </label>
            <select
              id="main-journal-select"
              value={selectedJournalId}
              onChange={(e) => onSelectJournal(e.target.value)}
              className="bg-slate-950 border border-slate-700/80 hover:border-slate-600 text-slate-100 text-xs sm:text-sm rounded-lg px-2.5 py-1.5 focus:outline-none focus:ring-2 focus:ring-indigo-500/50 cursor-pointer min-w-[200px] sm:min-w-[250px] max-w-[280px] truncate"
            >
              <option value="">General Journal Guidelines</option>
              {journals.map((j) => (
                <option key={j.journal_id} value={j.journal_id}>
                  {j.name} ({j.publisher})
                </option>
              ))}
            </select>
          </div>
        </div>

        {/* Drag and Drop Zone */}
        <div
          onDragOver={handleDragOver}
          onDragLeave={handleDragLeave}
          onDrop={handleDrop}
          onClick={() => fileInputRef.current?.click()}
          className={`relative border-2 border-dashed rounded-xl p-8 sm:p-10 text-center cursor-pointer transition-all duration-200 group ${
            isDragOver
              ? 'border-indigo-400 bg-indigo-950/30 scale-[0.99]'
              : 'border-slate-700/80 hover:border-indigo-500/60 bg-slate-900/40 hover:bg-slate-900/60'
          }`}
        >
          <input
            ref={fileInputRef}
            type="file"
            accept=".pdf,.docx"
            onChange={handleFileChange}
            className="hidden"
          />

          <div className="flex flex-col items-center justify-center space-y-3">
            <div className="w-14 h-14 rounded-2xl bg-indigo-600/10 border border-indigo-500/20 group-hover:border-indigo-500/40 group-hover:bg-indigo-600/20 flex items-center justify-center transition-all duration-300 group-hover:scale-105">
              {isUploading ? (
                <RefreshCw className="w-7 h-7 text-indigo-400 animate-spin" />
              ) : (
                <UploadCloud className="w-7 h-7 text-indigo-400" />
              )}
            </div>

            <div>
              <p className="text-sm sm:text-base font-semibold text-slate-200 group-hover:text-white transition-colors">
                {isUploading ? 'Ingesting & Validating Document...' : 'Drag & drop your manuscript here, or browse files'}
              </p>
              <p className="text-xs text-slate-400 mt-1">
                Supports research papers, review articles, short communications, and conference drafts
              </p>
            </div>
          </div>
        </div>

        {/* Manuscript Metadata Card (if uploaded) */}
        {currentManuscript && (
          <div className="mt-5 p-4 rounded-xl bg-slate-900/80 border border-slate-800 flex flex-col md:flex-row md:items-center justify-between gap-4">
            <div className="flex items-start space-x-3 min-w-0">
              <div className="w-10 h-10 rounded-lg bg-emerald-500/10 border border-emerald-500/20 flex-shrink-0 flex items-center justify-center mt-0.5">
                <FileText className="w-5 h-5 text-emerald-400" />
              </div>
              <div className="min-w-0">
                <h4 className="text-sm font-semibold text-slate-100 truncate">
                  {currentManuscript.title || 'Uploaded Manuscript'}
                </h4>
                <div className="flex flex-wrap items-center gap-x-4 gap-y-1 text-xs text-slate-400 mt-1 font-mono">
                  <span>Pages: <b className="text-slate-200 font-sans">{currentManuscript.page_count}</b></span>
                  <span>Words: <b className="text-slate-200 font-sans">{currentManuscript.word_count.toLocaleString()}</b></span>
                  <span className="flex items-center gap-1 text-cyan-300 font-sans font-medium">
                    <BookOpen className="w-3 h-3 text-cyan-400" />
                    Venue: {selectedJournal ? selectedJournal.name : 'General Guidelines'}
                  </span>
                  {currentManuscript.file_hash && (
                    <span className="flex items-center gap-1">
                      <Hash className="w-3 h-3 text-slate-500" />
                      SHA256: {currentManuscript.file_hash.substring(0, 12)}...
                    </span>
                  )}
                </div>
              </div>
            </div>

            {/* Scanned PDF warning notice */}
            {currentManuscript.is_scanned && (
              <div className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-amber-500/10 border border-amber-500/30 text-amber-300 text-xs">
                <AlertTriangle className="w-4 h-4 flex-shrink-0 text-amber-400" />
                <span>Scanned document detected. Coordinate checks may be provisional.</span>
              </div>
            )}

            {/* Run Button */}
            <div className="flex items-center gap-3">
              <button
                onClick={onRunAnalysis}
                disabled={isAnalyzing || isUploading}
                className="w-full md:w-auto px-5 py-2.5 rounded-xl font-medium text-sm text-white bg-gradient-to-r from-indigo-600 via-indigo-500 to-cyan-500 hover:from-indigo-500 hover:to-cyan-400 disabled:opacity-50 disabled:cursor-not-allowed shadow-lg shadow-indigo-500/20 hover:shadow-indigo-500/30 active:scale-[0.98] transition-all flex items-center justify-center gap-2 font-heading cursor-pointer"
              >
                {isAnalyzing ? (
                  <>
                    <RefreshCw className="w-4 h-4 animate-spin" />
                    <span>Analyzing Manuscript...</span>
                  </>
                ) : (
                  <>
                    <Play className="w-4 h-4 fill-white text-white" />
                    <span>Run Multi-Engine Verification</span>
                  </>
                )}
              </button>
            </div>
          </div>
        )}
      </div>
    </section>
  );
};
