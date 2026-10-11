import React from 'react';
import {
  Sparkles,
  ArrowRight,
  ShieldCheck,
  Cpu,
  Database,
  CheckCircle2,
  AlertTriangle,
  FileText,
  Search,
  BookOpen,
  Award,
  Layers,
  Zap,
  LogIn,
  UserPlus,
  Compass,
} from 'lucide-react';
import { AuthMode } from './AuthModal';

interface LandingHeroProps {
  onOpenAuth: (mode: AuthMode) => void;
}

export const LandingHero: React.FC<LandingHeroProps> = ({ onOpenAuth }) => {
  return (
    <div className="space-y-16 py-4 animate-fadeIn">
      {/* 1. Hero Section */}
      <section className="relative overflow-hidden rounded-3xl glass-panel-elevated border border-slate-800/80 p-8 sm:p-12 lg:p-16 text-center">
        {/* Ambient glow backgrounds */}
        <div className="absolute -top-32 -left-32 w-96 h-96 bg-indigo-600/20 rounded-full blur-3xl pointer-events-none" />
        <div className="absolute -bottom-32 -right-32 w-96 h-96 bg-cyan-600/15 rounded-full blur-3xl pointer-events-none" />
        <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[500px] h-[300px] bg-purple-600/10 rounded-full blur-3xl pointer-events-none" />

        <div className="relative z-10 max-w-4xl mx-auto space-y-6">
          {/* Badge */}
          <div className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-indigo-950/60 border border-indigo-500/30 text-indigo-300 text-xs font-semibold tracking-wide shadow-inner">
            <Sparkles className="w-3.5 h-3.5 text-cyan-400" />
            <span>Autonomous Pre-Flight Journal Readiness Audit</span>
          </div>

          {/* Main Title */}
          <h1 className="text-3xl sm:text-5xl lg:text-6xl font-extrabold font-heading text-white tracking-tight leading-tight">
            Audit Your Manuscript for{' '}
            <span className="bg-gradient-to-r from-indigo-400 via-cyan-300 to-indigo-300 bg-clip-text text-transparent">
              Zero Desk Rejections
            </span>
          </h1>

          {/* Subtitle */}
          <p className="text-base sm:text-lg text-slate-300 max-w-2xl mx-auto leading-relaxed">
            Eliminate submission blockers before editor review. Our autonomous{' '}
            <strong className="text-white font-semibold">Tri-Engine verification pipeline</strong>{' '}
            audits deterministic formatting, target publisher guidelines via RAG, and peer-review rigor in seconds.
          </p>

          {/* Action CTAs */}
          <div className="flex flex-col sm:flex-row items-center justify-center gap-3 pt-2">
            <button
              onClick={() => onOpenAuth('signup')}
              className="w-full sm:w-auto inline-flex items-center justify-center gap-2 px-6 py-3.5 rounded-xl font-heading font-semibold text-sm text-white bg-gradient-to-r from-indigo-600 via-indigo-500 to-cyan-500 hover:from-indigo-500 hover:to-cyan-400 shadow-lg shadow-indigo-600/30 hover:shadow-indigo-500/40 active:scale-[0.98] transition-all cursor-pointer"
            >
              <UserPlus className="w-4 h-4" />
              <span>Create Free Account to Audit</span>
              <ArrowRight className="w-4 h-4" />
            </button>

            <button
              onClick={() => onOpenAuth('login')}
              className="w-full sm:w-auto inline-flex items-center justify-center gap-2 px-6 py-3.5 rounded-xl font-heading font-semibold text-sm text-slate-200 hover:text-white bg-slate-900/80 hover:bg-slate-800/90 border border-slate-700/80 hover:border-slate-600 transition-all cursor-pointer shadow-sm"
            >
              <LogIn className="w-4 h-4 text-indigo-400" />
              <span>Sign In with Existing Account</span>
            </button>
          </div>

          {/* Micro Trust Indicators */}
          <div className="pt-6 border-t border-slate-800/60 grid grid-cols-2 sm:grid-cols-4 gap-4 text-center">
            <div className="p-2">
              <p className="text-xl sm:text-2xl font-bold font-mono text-cyan-400">10s</p>
              <p className="text-xs text-slate-400 mt-0.5">Automated Pre-Flight Check</p>
            </div>
            <div className="p-2">
              <p className="text-xl sm:text-2xl font-bold font-mono text-indigo-400">3 Engines</p>
              <p className="text-xs text-slate-400 mt-0.5">Deterministic &bull; RAG &bull; LLM</p>
            </div>
            <div className="p-2">
              <p className="text-xl sm:text-2xl font-bold font-mono text-emerald-400">7+ Venues</p>
              <p className="text-xs text-slate-400 mt-0.5">IEEE, Nature, ACM & more</p>
            </div>
            <div className="p-2">
              <p className="text-xl sm:text-2xl font-bold font-mono text-amber-400">0 - 100</p>
              <p className="text-xs text-slate-400 mt-0.5">Readiness Score & Action Plan</p>
            </div>
          </div>
        </div>
      </section>

      {/* 2. How the Platform Works: 4-Step Interactive Workflow */}
      <section className="space-y-8">
        <div className="text-center space-y-2">
          <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-slate-900 border border-slate-800 text-xs text-indigo-300 font-medium">
            <Layers className="w-3.5 h-3.5 text-indigo-400" />
            <span>Under The Hood</span>
          </div>
          <h2 className="text-2xl sm:text-3xl font-bold font-heading text-white tracking-tight">
            How The Verification Workflow Operates
          </h2>
          <p className="text-xs sm:text-sm text-slate-400 max-w-xl mx-auto">
            From raw manuscript PDF/DOCX to a prioritized pre-submission action plan in four automated phases.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-5">
          {/* Step 1 */}
          <div className="glass-panel p-6 rounded-2xl border border-slate-800/80 space-y-4 hover:border-indigo-500/40 transition-colors relative">
            <div className="w-10 h-10 rounded-xl bg-indigo-600/10 border border-indigo-500/20 text-indigo-400 font-mono font-bold flex items-center justify-center text-sm">
              01
            </div>
            <h3 className="text-base font-semibold text-white font-heading">
              1. Document Ingestion
            </h3>
            <p className="text-xs text-slate-400 leading-relaxed">
              Upload your manuscript in PDF or DOCX format. The parser automatically structures sections, abstracts, formulas, tables, citations, and figure numbering.
            </p>
            <div className="pt-2 text-[11px] text-slate-500 font-mono flex items-center gap-1.5">
              <FileText className="w-3.5 h-3.5 text-indigo-400" />
              <span>Full text & reference extraction</span>
            </div>
          </div>

          {/* Step 2 */}
          <div className="glass-panel p-6 rounded-2xl border border-slate-800/80 space-y-4 hover:border-cyan-500/40 transition-colors relative">
            <div className="w-10 h-10 rounded-xl bg-cyan-600/10 border border-cyan-500/20 text-cyan-400 font-mono font-bold flex items-center justify-center text-sm">
              02
            </div>
            <h3 className="text-base font-semibold text-white font-heading">
              2. Tri-Engine Audit
            </h3>
            <p className="text-xs text-slate-400 leading-relaxed">
              Three synchronized verification engines inspect the paper: Deterministic rule verification, Publisher Knowledge Base RAG, and Peer-Review Rigor Evaluation.
            </p>
            <div className="pt-2 text-[11px] text-slate-500 font-mono flex items-center gap-1.5">
              <Cpu className="w-3.5 h-3.5 text-cyan-400" />
              <span>Parallel multi-layer evaluation</span>
            </div>
          </div>

          {/* Step 3 */}
          <div className="glass-panel p-6 rounded-2xl border border-slate-800/80 space-y-4 hover:border-emerald-500/40 transition-colors relative">
            <div className="w-10 h-10 rounded-xl bg-emerald-600/10 border border-emerald-500/20 text-emerald-400 font-mono font-bold flex items-center justify-center text-sm">
              03
            </div>
            <h3 className="text-base font-semibold text-white font-heading">
              3. Readiness Scoring
            </h3>
            <p className="text-xs text-slate-400 leading-relaxed">
              Generates a weighted 0-100 Submission Readiness Gauge categorized into Ready (85+), Minor Revisions (70-84), or Major Revisions Required (&lt;70).
            </p>
            <div className="pt-2 text-[11px] text-slate-500 font-mono flex items-center gap-1.5">
              <Award className="w-3.5 h-3.5 text-emerald-400" />
              <span>Section-by-section breakdown</span>
            </div>
          </div>

          {/* Step 4 */}
          <div className="glass-panel p-6 rounded-2xl border border-slate-800/80 space-y-4 hover:border-amber-500/40 transition-colors relative">
            <div className="w-10 h-10 rounded-xl bg-amber-600/10 border border-amber-500/20 text-amber-400 font-mono font-bold flex items-center justify-center text-sm">
              04
            </div>
            <h3 className="text-base font-semibold text-white font-heading">
              4. Actionable Fix Plan
            </h3>
            <p className="text-xs text-slate-400 leading-relaxed">
              Every flagged issue is categorized into Submission Blockers, Recommended Improvements, or Informational Checks, complete with interactive AI revision instructions.
            </p>
            <div className="pt-2 text-[11px] text-slate-500 font-mono flex items-center gap-1.5">
              <Zap className="w-3.5 h-3.5 text-amber-400" />
              <span>Step-by-step resolution advice</span>
            </div>
          </div>
        </div>
      </section>

      {/* 3. The Tri-Engine Architecture Deep Dive */}
      <section className="rounded-3xl bg-slate-900/60 border border-slate-800/80 p-8 sm:p-10 space-y-8">
        <div className="flex flex-col md:flex-row md:items-end justify-between gap-4 border-b border-slate-800 pb-5">
          <div>
            <div className="inline-flex items-center gap-1.5 text-xs font-semibold text-cyan-400 uppercase tracking-wider">
              <Cpu className="w-3.5 h-3.5" />
              Autonomous Verification Core
            </div>
            <h2 className="text-2xl sm:text-3xl font-bold font-heading text-white mt-1">
              The Three Specialized Verification Engines
            </h2>
            <p className="text-xs sm:text-sm text-slate-400 mt-1">
              Combining exact deterministic rules, contextual publisher retrieval, and advanced peer-review intelligence.
            </p>
          </div>
          <button
            onClick={() => onOpenAuth('signup')}
            className="inline-flex items-center gap-1.5 px-4 py-2 rounded-xl text-xs font-semibold bg-indigo-600 hover:bg-indigo-500 text-white cursor-pointer transition-colors shadow-sm self-start md:self-auto"
          >
            <span>Audit Your Paper</span>
            <ArrowRight className="w-3.5 h-3.5" />
          </button>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {/* Engine 1 */}
          <div className="bg-slate-950/70 border border-slate-800 rounded-2xl p-6 space-y-4 flex flex-col justify-between hover:border-indigo-500/50 transition-all">
            <div className="space-y-3">
              <div className="w-12 h-12 rounded-xl bg-indigo-600/10 border border-indigo-500/20 flex items-center justify-center text-indigo-400">
                <ShieldCheck className="w-6 h-6" />
              </div>
              <h3 className="text-lg font-bold font-heading text-white">
                Engine 1: Deterministic Engine
              </h3>
              <p className="text-xs text-slate-300 leading-relaxed">
                Algorithmic validation of mechanical manuscript constraints with zero hallucination.
              </p>
              <ul className="text-xs text-slate-400 space-y-2 pt-2 border-t border-slate-800/60">
                <li className="flex items-start gap-2">
                  <CheckCircle2 className="w-3.5 h-3.5 text-indigo-400 flex-shrink-0 mt-0.5" />
                  <span>Citation format &amp; reference style integrity (IEEE, APA, Harvard)</span>
                </li>
                <li className="flex items-start gap-2">
                  <CheckCircle2 className="w-3.5 h-3.5 text-indigo-400 flex-shrink-0 mt-0.5" />
                  <span>Abstract word limits and manuscript length constraints</span>
                </li>
                <li className="flex items-start gap-2">
                  <CheckCircle2 className="w-3.5 h-3.5 text-indigo-400 flex-shrink-0 mt-0.5" />
                  <span>Figure and table sequential numbering and in-text callouts</span>
                </li>
              </ul>
            </div>
            <div className="mt-4 pt-3 border-t border-slate-800/60 text-[11px] font-mono text-indigo-400">
              Deterministic &bull; Exact Rule Matching
            </div>
          </div>

          {/* Engine 2 */}
          <div className="bg-slate-950/70 border border-slate-800 rounded-2xl p-6 space-y-4 flex flex-col justify-between hover:border-cyan-500/50 transition-all">
            <div className="space-y-3">
              <div className="w-12 h-12 rounded-xl bg-cyan-600/10 border border-cyan-500/20 flex items-center justify-center text-cyan-400">
                <Database className="w-6 h-6" />
              </div>
              <h3 className="text-lg font-bold font-heading text-white">
                Engine 2: Publisher Guidelines RAG
              </h3>
              <p className="text-xs text-slate-300 leading-relaxed">
                Semantic retrieval against live author guidelines across top academic venues.
              </p>
              <ul className="text-xs text-slate-400 space-y-2 pt-2 border-t border-slate-800/60">
                <li className="flex items-start gap-2">
                  <CheckCircle2 className="w-3.5 h-3.5 text-cyan-400 flex-shrink-0 mt-0.5" />
                  <span>Publisher-specific author instruction verification</span>
                </li>
                <li className="flex items-start gap-2">
                  <CheckCircle2 className="w-3.5 h-3.5 text-cyan-400 flex-shrink-0 mt-0.5" />
                  <span>Data sharing, ethical approvals &amp; conflict disclosure audits</span>
                </li>
                <li className="flex items-start gap-2">
                  <CheckCircle2 className="w-3.5 h-3.5 text-cyan-400 flex-shrink-0 mt-0.5" />
                  <span>Double-blind anonymization compliance checks</span>
                </li>
              </ul>
            </div>
            <div className="mt-4 pt-3 border-t border-slate-800/60 text-[11px] font-mono text-cyan-400">
              Retrieval Augmented Generation &bull; Venue Guidelines
            </div>
          </div>

          {/* Engine 3 */}
          <div className="bg-slate-950/70 border border-slate-800 rounded-2xl p-6 space-y-4 flex flex-col justify-between hover:border-purple-500/50 transition-all">
            <div className="space-y-3">
              <div className="w-12 h-12 rounded-xl bg-purple-600/10 border border-purple-500/20 flex items-center justify-center text-purple-400">
                <Sparkles className="w-6 h-6" />
              </div>
              <h3 className="text-lg font-bold font-heading text-white">
                Engine 3: Peer-Review Rigor Engine
              </h3>
              <p className="text-xs text-slate-300 leading-relaxed">
                Simulates senior peer-reviewer scrutiny to evaluate scientific depth and integrity.
              </p>
              <ul className="text-xs text-slate-400 space-y-2 pt-2 border-t border-slate-800/60">
                <li className="flex items-start gap-2">
                  <CheckCircle2 className="w-3.5 h-3.5 text-purple-400 flex-shrink-0 mt-0.5" />
                  <span>Methodology soundness and statistical reporting clarity</span>
                </li>
                <li className="flex items-start gap-2">
                  <CheckCircle2 className="w-3.5 h-3.5 text-purple-400 flex-shrink-0 mt-0.5" />
                  <span>Alignment between empirical results and claimed conclusions</span>
                </li>
                <li className="flex items-start gap-2">
                  <CheckCircle2 className="w-3.5 h-3.5 text-purple-400 flex-shrink-0 mt-0.5" />
                  <span>Limitations transparency &amp; reproducibility indicators</span>
                </li>
              </ul>
            </div>
            <div className="mt-4 pt-3 border-t border-slate-800/60 text-[11px] font-mono text-purple-400">
              LLM Cognitive Review &bull; Scientific Rigor
            </div>
          </div>
        </div>
      </section>

      {/* 4. Supported Journals & Venue Profiles */}
      <section className="space-y-6">
        <div className="text-center space-y-2">
          <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-slate-900 border border-slate-800 text-xs text-cyan-300 font-medium">
            <BookOpen className="w-3.5 h-3.5 text-cyan-400" />
            <span>Target Publisher Profiles</span>
          </div>
          <h2 className="text-2xl sm:text-3xl font-bold font-heading text-white tracking-tight">
            Built-In Author Guidelines For Major Journals
          </h2>
          <p className="text-xs sm:text-sm text-slate-400 max-w-xl mx-auto">
            Select your target publication venue once logged in to apply tailored guidelines and strict publisher requirements.
          </p>
        </div>

        <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-4">
          {[
            {
              id: 'ieee-access',
              name: 'IEEE Access',
              publisher: 'IEEE',
              desc: 'Bracketed numeric citations, two-column templates, structured abstracts',
            },
            {
              id: 'nature-srep',
              name: 'Scientific Reports',
              publisher: 'Nature Portfolio',
              desc: 'Strict data availability statements, Nature reference format, author disclosures',
            },
            {
              id: 'acm-csur',
              name: 'Computing Surveys',
              publisher: 'ACM',
              desc: 'ACM CCS taxonomy classification, comprehensive bibliography, syntax standards',
            },
            {
              id: 'plos-one',
              name: 'PLOS ONE',
              publisher: 'PLOS',
              desc: 'Public repository data availability, ethical protocols, reproducible methodology',
            },
            {
              id: 'elsevier-compelec',
              name: 'Computers & Security',
              publisher: 'Elsevier',
              desc: 'Research highlights, CRediT authorship declarations, structured sections',
            },
            {
              id: 'oup-bioinformatics',
              name: 'Bioinformatics',
              publisher: 'Oxford Univ Press',
              desc: 'Open software code availability, documentation URLs, OUP referencing',
            },
            {
              id: 'aps-prb',
              name: 'Physical Review B',
              publisher: 'American Physical Society',
              desc: 'PhysSH physics classification, standard equation labeling, APS conventions',
            },
            {
              id: 'general-guidelines',
              name: 'General Journal Guidelines',
              publisher: 'Universal Standard',
              desc: 'IMRAD structure, ethical clearances, rigor standards across peer-reviewed science',
            },
          ].map((venue) => (
            <div
              key={venue.id}
              className="glass-panel p-4 rounded-xl border border-slate-800/80 hover:border-slate-700 transition-all flex flex-col justify-between space-y-2.5"
            >
              <div>
                <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-slate-800 text-slate-300">
                  {venue.publisher}
                </span>
                <h4 className="text-sm font-semibold text-white font-heading mt-2">
                  {venue.name}
                </h4>
                <p className="text-xs text-slate-400 mt-1 line-clamp-2">
                  {venue.desc}
                </p>
              </div>
              <span className="text-[11px] text-indigo-400 font-medium flex items-center gap-1">
                <span>Profile Available</span>
                <CheckCircle2 className="w-3 h-3" />
              </span>
            </div>
          ))}
        </div>
      </section>

      {/* 5. Bottom Call to Action Banner */}
      <section className="relative overflow-hidden rounded-3xl bg-gradient-to-r from-indigo-950/80 via-slate-900 to-cyan-950/70 border border-indigo-500/30 p-8 sm:p-12 text-center space-y-6 shadow-2xl">
        <div className="max-w-2xl mx-auto space-y-4 relative z-10">
          <div className="w-12 h-12 rounded-2xl bg-indigo-600/20 border border-indigo-500/30 text-indigo-300 flex items-center justify-center mx-auto">
            <Compass className="w-6 h-6 text-cyan-400" />
          </div>
          <h2 className="text-2xl sm:text-4xl font-extrabold font-heading text-white tracking-tight">
            Ready to Verify Your Manuscript?
          </h2>
          <p className="text-xs sm:text-sm text-slate-300 leading-relaxed">
            Create an account or sign in to upload your document, select your target journal, and receive a comprehensive readiness breakdown before submitting.
          </p>

          <div className="flex flex-col sm:flex-row items-center justify-center gap-3 pt-2">
            <button
              onClick={() => onOpenAuth('signup')}
              className="w-full sm:w-auto inline-flex items-center justify-center gap-2 px-6 py-3 rounded-xl font-heading font-semibold text-sm text-white bg-gradient-to-r from-indigo-600 to-cyan-600 hover:from-indigo-500 hover:to-cyan-500 shadow-lg shadow-indigo-600/30 cursor-pointer transition-all"
            >
              <UserPlus className="w-4 h-4" />
              <span>Sign Up for Free</span>
            </button>
            <button
              onClick={() => onOpenAuth('login')}
              className="w-full sm:w-auto inline-flex items-center justify-center gap-2 px-6 py-3 rounded-xl font-heading font-semibold text-sm text-slate-200 hover:text-white bg-slate-900 hover:bg-slate-800 border border-slate-700 cursor-pointer transition-all"
            >
              <LogIn className="w-4 h-4 text-indigo-400" />
              <span>Sign In</span>
            </button>
          </div>
        </div>
      </section>
    </div>
  );
};
