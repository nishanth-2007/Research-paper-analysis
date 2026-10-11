import React, { useState, useEffect, useRef } from 'react';
import { Navbar } from './components/Navbar';
import { UploadCard } from './components/UploadCard';
import { ProgressTracker } from './components/ProgressTracker';
import { ValidationAlertBanner } from './components/ValidationAlertBanner';
import { ReadinessScoreHero } from './components/ReadinessScoreHero';
import { ThreeEngineScores } from './components/ThreeEngineScores';
import { ManuscriptSectionScores } from './components/ManuscriptSectionScores';
import { MetricCounterCards } from './components/MetricCounterCards';
import { EvaluationTabs } from './components/EvaluationTabs';
import { ActionPlanSection } from './components/ActionPlanSection';
import { RevisionGuidanceModal } from './components/RevisionGuidanceModal';
import { AuthModal, AuthMode, UserSession } from './components/AuthModal';
import { LandingHero } from './components/LandingHero';
import { ManuscriptStudio } from './components/ManuscriptStudio';
import { UserUploadHistory } from './components/UserUploadHistory';
import { supabase, isSupabaseConfigured } from './services/supabase';
import { UserService } from './services/userService';
import { ApiService } from './services/api';
import {
  Journal,
  ManuscriptUploadResponse,
  AnalysisStatusResponse,
  CompleteAnalysisReport,
  ConsolidatedIssue,
  IssueTier,
  UserAuditHistoryItem,
} from './types';
import { AlertCircle } from 'lucide-react';

export const App: React.FC = () => {
  // Application State
  // Application State with Persistent Local Storage initialization
  const [journals, setJournals] = useState<Journal[]>([]);
  const [selectedJournalId, setSelectedJournalId] = useState<string>(() => {
    try {
      return localStorage.getItem('journal_readiness_selected_journal') || 'ieee-access';
    } catch {
      return 'ieee-access';
    }
  });
  const [systemStatus, setSystemStatus] = useState<{ status: string; version?: string }>({
    status: 'operational',
    version: '1.0.0',
  });

  const [currentManuscript, setCurrentManuscript] = useState<ManuscriptUploadResponse | null>(() => {
    try {
      const saved = localStorage.getItem('journal_readiness_manuscript');
      return saved ? JSON.parse(saved) : null;
    } catch {
      return null;
    }
  });
  const [isUploading, setIsUploading] = useState(false);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [analysisStatus, setAnalysisStatus] = useState<AnalysisStatusResponse | null>(null);
  const [report, setReport] = useState<CompleteAnalysisReport | null>(() => {
    try {
      const saved = localStorage.getItem('journal_readiness_report');
      return saved ? JSON.parse(saved) : null;
    } catch {
      return null;
    }
  });
  const [activeActionTier, setActiveActionTier] = useState<IssueTier | 'all'>('all');
  const [guidanceModalIssue, setGuidanceModalIssue] = useState<ConsolidatedIssue | null>(null);
  const [errorNotification, setErrorNotification] = useState<string | null>(null);
  const [currentView, setCurrentView] = useState<'dashboard' | 'manuscript_studio'>(() => {
    try {
      const hash = window.location.hash;
      if (hash === '#studio' || hash.startsWith('#studio')) {
        return 'manuscript_studio';
      }
    } catch {}
    return 'dashboard';
  });

  // Synchronize browser history (back/forward buttons) with application views
  useEffect(() => {
    const handleUrlChange = () => {
      const hash = window.location.hash;
      if (hash === '#studio' || hash.startsWith('#studio')) {
        setCurrentView('manuscript_studio');
        window.scrollTo({ top: 0, behavior: 'smooth' });
      } else {
        setCurrentView('dashboard');
        setTimeout(() => {
          if (resultsRef.current) {
            resultsRef.current.scrollIntoView({ behavior: 'smooth' });
          }
        }, 80);
      }
    };

    window.addEventListener('popstate', handleUrlChange);
    window.addEventListener('hashchange', handleUrlChange);

    // Clean up lingering OAuth token hash from URL bar
    if (window.location.hash.includes('access_token')) {
      setTimeout(() => {
        if (window.location.hash.includes('access_token')) {
          window.history.replaceState(null, '', window.location.pathname + window.location.search);
        }
      }, 300);
    }

    return () => {
      window.removeEventListener('popstate', handleUrlChange);
      window.removeEventListener('hashchange', handleUrlChange);
    };
  }, []);

  // Sync state changes to localStorage so page reloads never lose analysis results
  useEffect(() => {
    try {
      if (report) {
        localStorage.setItem('journal_readiness_report', JSON.stringify(report));
      } else {
        localStorage.removeItem('journal_readiness_report');
      }
    } catch (e) {
      console.warn('Could not persist report:', e);
    }
  }, [report]);

  useEffect(() => {
    try {
      if (currentManuscript) {
        localStorage.setItem('journal_readiness_manuscript', JSON.stringify(currentManuscript));
      } else {
        localStorage.removeItem('journal_readiness_manuscript');
      }
    } catch (e) {
      console.warn('Could not persist manuscript:', e);
    }
  }, [currentManuscript]);

  useEffect(() => {
    try {
      if (selectedJournalId) {
        localStorage.setItem('journal_readiness_selected_journal', selectedJournalId);
      }
    } catch (e) {
      console.warn('Could not persist selectedJournalId:', e);
    }
  }, [selectedJournalId]);

  // User Auth State
  const [currentUser, setCurrentUser] = useState<UserSession | null>(() => {
    try {
      const saved = localStorage.getItem('journal_readiness_user');
      return saved ? JSON.parse(saved) : null;
    } catch {
      return null;
    }
  });
  const [isAuthModalOpen, setIsAuthModalOpen] = useState(false);
  const [authMode, setAuthMode] = useState<AuthMode>('login');

  const handleOpenAuth = (mode: AuthMode = 'login') => {
    setAuthMode(mode);
    setIsAuthModalOpen(true);
  };

  const handleAuthSuccess = (user: UserSession) => {
    setCurrentUser(user);
    try {
      localStorage.setItem('journal_readiness_user', JSON.stringify(user));
    } catch (e) {
      console.warn('Could not persist session', e);
    }
  };

  // Helper to generate isolated localStorage storage keys per user
  const getUserHistoryStorageKey = (user: UserSession | null) => {
    if (!user) return 'journal_readiness_history_guest';
    const id = user.username || user.email || 'user';
    return `journal_readiness_history_${id.replace(/[^a-zA-Z0-9_-]/g, '_')}`;
  };

  // User Upload and Audit History (isolated strictly per user)
  const [userHistory, setUserHistory] = useState<UserAuditHistoryItem[]>(() => {
    try {
      const savedUser = localStorage.getItem('journal_readiness_user');
      const u: UserSession | null = savedUser ? JSON.parse(savedUser) : null;
      const key = getUserHistoryStorageKey(u);
      const saved = localStorage.getItem(key);
      return saved ? JSON.parse(saved) : [];
    } catch {
      return [];
    }
  });

  // Switch or reload user history whenever the authenticated user changes
  useEffect(() => {
    try {
      const key = getUserHistoryStorageKey(currentUser);
      const saved = localStorage.getItem(key);
      setUserHistory(saved ? JSON.parse(saved) : []);
    } catch (e) {
      console.warn('Could not load user history:', e);
      setUserHistory([]);
    }
  }, [currentUser?.username, currentUser?.email]);

  // Sync userHistory updates to the specific user's localStorage bucket
  useEffect(() => {
    if (!currentUser) return;
    try {
      const key = getUserHistoryStorageKey(currentUser);
      localStorage.setItem(key, JSON.stringify(userHistory));
    } catch (e) {
      console.warn('Could not persist user history:', e);
    }
  }, [userHistory, currentUser?.username, currentUser?.email]);

  // Backfill currently active report into userHistory if not already recorded
  useEffect(() => {
    if (report && currentManuscript && currentUser) {
      setUserHistory((prev) => {
        if (
          prev.some(
            (h) =>
              h.id === report.analysis_id ||
              (h.manuscript_id === currentManuscript.manuscript_id && h.report)
          )
        ) {
          return prev;
        }
        const journalObj = journals.find((j) => j.journal_id === selectedJournalId);
        const blockers = report.consolidated_issues.filter(
          (i) => i.tier === 'submission_blocker'
        ).length;
        const improvements = report.consolidated_issues.filter(
          (i) => i.tier === 'improvement_recommended'
        ).length;

        const currentItem: UserAuditHistoryItem = {
          id: report.analysis_id,
          manuscript_id: currentManuscript.manuscript_id,
          filename: currentManuscript.filename || `${currentManuscript.title || 'manuscript'}.pdf`,
          title:
            currentManuscript.title ||
            report.manuscript_title ||
            'Audited Manuscript',
          journal_id: selectedJournalId,
          journal_name: journalObj?.name || report.target_journal_name || selectedJournalId,
          uploaded_at: new Date().toISOString(),
          readiness_score: report.readiness_score.overall_score,
          readiness_tier: report.readiness_score.readiness_tier,
          blockers_count: blockers,
          improvements_count: improvements,
          report: report,
          manuscript_info: currentManuscript,
        };
        return [currentItem, ...prev];
      });
    }
  }, [report?.analysis_id, currentUser?.username, currentManuscript?.manuscript_id]);

  // Reset audit state (for "New Audit" action)
  const handleResetAudit = () => {
    setCurrentManuscript(null);
    setReport(null);
    setAnalysisStatus(null);
    setErrorNotification(null);
    setGuidanceModalIssue(null);
    setCurrentView('dashboard');
    if (window.location.hash.includes('studio')) {
      window.history.replaceState(null, '', window.location.pathname + window.location.search);
    }
    try {
      localStorage.removeItem('journal_readiness_report');
      localStorage.removeItem('journal_readiness_manuscript');
    } catch (e) {
      console.warn('Could not clear audit data:', e);
    }
  };

  const handleSignOut = async () => {
    if (isSupabaseConfigured && supabase) {
      try {
        await supabase.auth.signOut();
      } catch (e) {
        console.warn('Error signing out of Supabase', e);
      }
    }
    setCurrentUser(null);
    // Clear all manuscript and analysis output state on logout
    setCurrentManuscript(null);
    setReport(null);
    setAnalysisStatus(null);
    setIsAnalyzing(false);
    setIsUploading(false);
    setErrorNotification(null);
    setGuidanceModalIssue(null);
    setCurrentView('dashboard');
    if (window.location.hash.includes('studio')) {
      window.history.replaceState(null, '', window.location.pathname + window.location.search);
    }
    try {
      localStorage.removeItem('journal_readiness_user');
      localStorage.removeItem('journal_readiness_report');
      localStorage.removeItem('journal_readiness_manuscript');
    } catch (e) {
      console.warn('Could not clear session', e);
    }
  };

  const handleOpenManuscriptStudio = () => {
    setCurrentView('manuscript_studio');
    if (!window.location.hash.includes('studio')) {
      window.history.pushState({ view: 'manuscript_studio' }, '', '#studio');
    }
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  const handleBackToAudit = () => {
    setCurrentView('dashboard');
    if (window.location.hash.includes('studio')) {
      if (window.history.length > 1) {
        window.history.back();
      } else {
        window.history.replaceState({ view: 'dashboard' }, '', window.location.pathname + window.location.search);
      }
    } else {
      window.history.replaceState({ view: 'dashboard' }, '', window.location.pathname + window.location.search);
    }
    setTimeout(() => {
      if (resultsRef.current) {
        resultsRef.current.scrollIntoView({ behavior: 'smooth' });
      } else {
        window.scrollTo({ top: 0, behavior: 'smooth' });
      }
    }, 80);
  };

  const resultsRef = useRef<HTMLDivElement>(null);
  const actionPlanRef = useRef<HTMLDivElement>(null);

  // Initialize data on mount
  useEffect(() => {
    const init = async () => {
      try {
        const health = await ApiService.checkHealth();
        setSystemStatus(health);

        const fetchedJournals = await ApiService.fetchJournals();
        setJournals(fetchedJournals);
        if (fetchedJournals.length > 0) {
          const savedJournal = localStorage.getItem('journal_readiness_selected_journal');
          if (savedJournal && fetchedJournals.some((j) => j.journal_id === savedJournal)) {
            setSelectedJournalId(savedJournal);
          } else {
            const defaultJ = fetchedJournals.find((j) => j.journal_id === 'ieee-access');
            setSelectedJournalId(defaultJ ? defaultJ.journal_id : fetchedJournals[0].journal_id);
          }
        }
      } catch (err: any) {
        console.error('Initialization error:', err);
      }
    };
    init();

    // Check & subscribe to Supabase auth session if configured
    if (isSupabaseConfigured && supabase) {
      supabase.auth.getSession().then(({ data: { session } }) => {
        if (session?.user) {
          const meta = session.user.user_metadata || {};
          const googleName = meta.full_name || meta.name;
          const u: UserSession = {
            username: meta.username || googleName || session.user.email?.split('@')[0] || 'Researcher',
            email: session.user.email || '',
          };
          setCurrentUser(u);
          UserService.registerUserMapping(u.username, u.email, session.user.id);
        }
      });

      const { data: { subscription } } = supabase.auth.onAuthStateChange((_event, session) => {
        if (session?.user) {
          const meta = session.user.user_metadata || {};
          const googleName = meta.full_name || meta.name;
          const u: UserSession = {
            username: meta.username || googleName || session.user.email?.split('@')[0] || 'Researcher',
            email: session.user.email || '',
          };
          setCurrentUser(u);
          UserService.registerUserMapping(u.username, u.email, session.user.id);
        } else {
          setCurrentUser(null);
          setCurrentManuscript(null);
          setReport(null);
          setAnalysisStatus(null);
          setIsAnalyzing(false);
          setIsUploading(false);
          setErrorNotification(null);
          setGuidanceModalIssue(null);
          try {
            localStorage.removeItem('journal_readiness_user');
            localStorage.removeItem('journal_readiness_report');
            localStorage.removeItem('journal_readiness_manuscript');
          } catch (e) {
            console.warn('Could not clear session storage:', e);
          }
        }
      });

      return () => {
        subscription.unsubscribe();
      };
    }
  }, []);

  // Manuscript Upload Handler
  const handleFileUpload = async (file: File) => {
    try {
      setIsUploading(true);
      setErrorNotification(null);
      setReport(null);
      setCurrentView('dashboard');

      const resp = await ApiService.uploadManuscript(file);
      resp.filename = file.name;
      setCurrentManuscript(resp);

      // Record newly uploaded file immediately in the user's history
      const journalObj = journals.find((j) => j.journal_id === selectedJournalId);
      const newUploadItem: UserAuditHistoryItem = {
        id: `upload_${resp.manuscript_id}`,
        manuscript_id: resp.manuscript_id,
        filename: file.name,
        title: resp.title || file.name.replace(/\.[^/.]+$/, ''),
        journal_id: selectedJournalId,
        journal_name: journalObj?.name || selectedJournalId,
        uploaded_at: new Date().toISOString(),
        manuscript_info: resp,
      };

      setUserHistory((prev) => {
        const filtered = prev.filter(
          (item) => item.manuscript_id !== resp.manuscript_id && item.id !== newUploadItem.id
        );
        return [newUploadItem, ...filtered];
      });
    } catch (err: any) {
      setErrorNotification(`Upload failed: ${err.message || 'Could not process manuscript'}`);
    } finally {
      setIsUploading(false);
    }
  };

  // Run Analysis Orchestrator
  const handleRunAnalysis = async () => {
    if (!currentManuscript) return;

    try {
      setIsAnalyzing(true);
      setErrorNotification(null);
      setCurrentView('dashboard');
      setAnalysisStatus({
        analysis_id: '',
        status: 'pending',
        progress_percent: 5,
        current_step: 'Initializing multi-engine verification pipeline...',
      });

      const initData = await ApiService.triggerAnalysis(
        currentManuscript.manuscript_id,
        selectedJournalId || null
      );

      const analysisId = initData.analysis_id;

      // Poll job status
      const pollInterval = setInterval(async () => {
        try {
          const statusData = await ApiService.pollAnalysisStatus(analysisId);
          setAnalysisStatus(statusData);

          if (statusData.status === 'completed') {
            clearInterval(pollInterval);
            const reportData = await ApiService.fetchAnalysisReport(analysisId);
            setReport(reportData);
            setIsAnalyzing(false);

            // Record completed audit result in user's history
            const journalObj = journals.find((j) => j.journal_id === selectedJournalId);
            const blockers = reportData.consolidated_issues.filter(
              (i) => i.tier === 'submission_blocker'
            ).length;
            const improvements = reportData.consolidated_issues.filter(
              (i) => i.tier === 'improvement_recommended'
            ).length;

            const auditedItem: UserAuditHistoryItem = {
              id: reportData.analysis_id,
              manuscript_id: currentManuscript.manuscript_id,
              filename:
                currentManuscript.filename ||
                `${reportData.manuscript_title || 'manuscript'}.pdf`,
              title:
                currentManuscript.title ||
                reportData.manuscript_title ||
                'Untitled Manuscript',
              journal_id: selectedJournalId,
              journal_name: journalObj?.name || reportData.target_journal_name || selectedJournalId,
              uploaded_at: new Date().toISOString(),
              readiness_score: reportData.readiness_score.overall_score,
              readiness_tier: reportData.readiness_score.readiness_tier,
              blockers_count: blockers,
              improvements_count: improvements,
              report: reportData,
              manuscript_info: currentManuscript,
            };

            setUserHistory((prev) => {
              const filtered = prev.filter(
                (item) =>
                  item.manuscript_id !== currentManuscript.manuscript_id &&
                  item.id !== reportData.analysis_id &&
                  item.id !== `upload_${currentManuscript.manuscript_id}`
              );
              return [auditedItem, ...filtered];
            });

            // Scroll to results
            setTimeout(() => {
              resultsRef.current?.scrollIntoView({ behavior: 'smooth' });
            }, 300);
          } else if (statusData.status === 'failed') {
            clearInterval(pollInterval);
            setIsAnalyzing(false);
            setErrorNotification(`Analysis failed: ${statusData.error_message || 'Verification engine error'}`);
          }
        } catch (pollErr: any) {
          console.error('Polling error:', pollErr);
        }
      }, 700);
    } catch (err: any) {
      setIsAnalyzing(false);
      setErrorNotification(`Analysis initiation error: ${err.message || 'Server error'}`);
    }
  };

  // User History Actions
  const handleLoadHistoryItem = (item: UserAuditHistoryItem) => {
    if (item.report) {
      setReport(item.report);
    }
    if (item.manuscript_info) {
      setCurrentManuscript(item.manuscript_info);
    } else {
      setCurrentManuscript({
        manuscript_id: item.manuscript_id,
        title: item.title,
        page_count: 1,
        word_count: 0,
        is_scanned: false,
        filename: item.filename,
      });
    }
    if (item.journal_id) {
      setSelectedJournalId(item.journal_id);
    }
    setCurrentView('dashboard');
    if (window.location.hash.includes('studio')) {
      window.history.replaceState({ view: 'dashboard' }, '', window.location.pathname + window.location.search);
    }
    setTimeout(() => {
      if (item.report && resultsRef.current) {
        resultsRef.current.scrollIntoView({ behavior: 'smooth' });
      }
    }, 100);
  };

  const handleOpenStudioForItem = (item: UserAuditHistoryItem) => {
    handleLoadHistoryItem(item);
    if (item.report) {
      setCurrentView('manuscript_studio');
      if (!window.location.hash.includes('studio')) {
        window.history.pushState({ view: 'manuscript_studio' }, '', '#studio');
      }
      window.scrollTo({ top: 0, behavior: 'smooth' });
    }
  };

  const handleDeleteHistoryItem = (id: string) => {
    setUserHistory((prev) => prev.filter((item) => item.id !== id));
  };

  const handleClearAllHistory = () => {
    if (window.confirm('Are you sure you want to clear your uploaded manuscript history?')) {
      setUserHistory([]);
      try {
        const key = getUserHistoryStorageKey(currentUser);
        localStorage.removeItem(key);
      } catch (e) {
        console.warn('Could not clear user history:', e);
      }
    }
  };

  const handleUpdateSimilarityScore = (score: number) => {
    if (!report) return;
    setUserHistory((prev) =>
      prev.map((item) =>
        item.id === report.analysis_id
          ? { ...item, similarity_score: score }
          : item
      )
    );
  };

  // Filter metric click scroll to Action Plan
  const handleSelectTierFromCard = (tier: IssueTier | 'all') => {
    setActiveActionTier(tier);
    actionPlanRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const blockersCount = report
    ? report.consolidated_issues.filter((i) => i.tier === 'submission_blocker').length
    : 0;
  const improvementsCount = report
    ? report.consolidated_issues.filter((i) => i.tier === 'improvement_recommended').length
    : 0;
  const checksCount = report
    ? report.consolidated_issues.filter((i) => i.tier === 'check_or_limitation').length
    : 0;

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col font-sans">
      {/* Top Navigation */}
      <Navbar
        journals={journals}
        selectedJournalId={selectedJournalId}
        onSelectJournal={setSelectedJournalId}
        systemStatus={systemStatus}
        user={currentUser}
        onOpenAuth={handleOpenAuth}
        onSignOut={handleSignOut}
        onGoHome={handleBackToAudit}
      />

      {/* Main Container */}
      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
        {/* Error notification banner */}
        {errorNotification && (
          <div className="rounded-xl border border-rose-500/40 bg-rose-950/40 p-4 text-rose-200 text-xs sm:text-sm flex items-center justify-between gap-3 backdrop-blur-md">
            <div className="flex items-center space-x-2.5">
              <AlertCircle className="w-4 h-4 text-rose-400 flex-shrink-0" />
              <span>{errorNotification}</span>
            </div>
            <button
              onClick={() => setErrorNotification(null)}
              className="text-rose-400 hover:text-rose-200 text-xs font-semibold px-2 py-1 rounded bg-rose-900/40"
            >
              Dismiss
            </button>
          </div>
        )}

        {/* Unauthenticated Landing Experience vs Authenticated Workspace */}
        {!currentUser ? (
          <LandingHero onOpenAuth={handleOpenAuth} />
        ) : currentView === 'manuscript_studio' && report ? (
          /* Dedicated Remediated Manuscript Studio */
          <ManuscriptStudio
            report={report}
            targetJournalId={selectedJournalId}
            journals={journals}
            onBack={handleBackToAudit}
            onUpdateSimilarityScore={handleUpdateSimilarityScore}
          />
        ) : (
          <>
            {/* Upload & Ingestion Section with Target Journal Selector */}
            <UploadCard
              onFileUpload={handleFileUpload}
              onRunAnalysis={handleRunAnalysis}
              isUploading={isUploading}
              isAnalyzing={isAnalyzing}
              currentManuscript={currentManuscript}
              journals={journals}
              selectedJournalId={selectedJournalId}
              onSelectJournal={setSelectedJournalId}
            />

            {/* Audit History & Recent Uploads for Current User */}
            <UserUploadHistory
              history={userHistory}
              currentAnalysisId={report?.analysis_id}
              onLoadHistoryItem={handleLoadHistoryItem}
              onOpenStudioForItem={handleOpenStudioForItem}
              onDeleteItem={handleDeleteHistoryItem}
              onClearAll={handleClearAllHistory}
            />

            {/* Dynamic Progress Tracker */}
            {isAnalyzing && analysisStatus && (
              <ProgressTracker status={analysisStatus} />
            )}

            {/* Verification Results Dashboard */}
            {report && (
              <div ref={resultsRef} className="space-y-8 animate-fadeIn">
                {/* 1. Document Plausibility Warning (if CV or provisional) */}
                <ValidationAlertBanner
                  validation={report.document_validation}
                  isProvisional={report.readiness_score.is_provisional}
                  provisionalReason={report.readiness_score.provisional_reason}
                />

                {/* 2. Readiness Score Hero (Radial Gauge, Tier, Synthesis, Downloads, Generate Manuscript CTA) */}
                <ReadinessScoreHero
                  report={report}
                  onRerun={handleRunAnalysis}
                  onReset={handleResetAudit}
                  isAnalyzing={isAnalyzing}
                  onGenerateManuscript={handleOpenManuscriptStudio}
                />

                {/* 3. Three Specialized Verification Engine Scores (Deterministic, RAG, LLM) */}
                <ThreeEngineScores engineScores={report.readiness_score.engine_scores} />

                {/* 4. Manuscript Section Scores (Abstract, Intro, Methods, Results, Conclusion, References) */}
                <ManuscriptSectionScores sectionScores={report.readiness_score.section_scores} />

                {/* 5. Metric Counter Filter Cards (Blockers, Improvements, Checks) */}
                <MetricCounterCards
                  blockersCount={blockersCount}
                  improvementsCount={improvementsCount}
                  checksCount={checksCount}
                  activeTier={activeActionTier}
                  onSelectTier={handleSelectTierFromCard}
                />

                {/* 6. Evaluation Dimensions Tabbed Breakdown (Compliance, Rigor, Verification) */}
                <EvaluationTabs report={report} />

                {/* 7. Prioritized Action Plan with Status Tracking & AI Guidance */}
                <div ref={actionPlanRef}>
                  <ActionPlanSection
                    issues={report.consolidated_issues}
                    analysisId={report.analysis_id}
                    activeTier={activeActionTier}
                    onSelectTier={setActiveActionTier}
                    onOpenGuidanceModal={setGuidanceModalIssue}
                  />
                </div>
              </div>
            )}
          </>
        )}
      </main>

      {/* AI Revision Guidance Modal */}
      <RevisionGuidanceModal
        issue={guidanceModalIssue}
        onClose={() => setGuidanceModalIssue(null)}
      />

      {/* Researcher Auth Modal (Sign In / Sign Up) */}
      <AuthModal
        isOpen={isAuthModalOpen}
        initialMode={authMode}
        onClose={() => setIsAuthModalOpen(false)}
        onAuthSuccess={handleAuthSuccess}
      />

      {/* Footer */}
      <footer className="mt-16 border-t border-slate-900 bg-slate-950/80 py-8 text-center text-xs text-slate-500">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 space-y-2">
          <p className="font-heading text-slate-400 font-semibold">
            Research Paper Automation & Journal Readiness Platform
          </p>
          <p>
            Autonomous Tri-Engine Architecture &bull; Deterministic Verification &bull; Journal Knowledge RAG &bull; Journal Review Rigor Evaluation
          </p>
          <p className="text-[11px] text-slate-600 font-mono">
            Readiness scores indicate structural guideline compliance and do not guarantee editorial acceptance.
          </p>
        </div>
      </footer>
    </div>
  );
};
