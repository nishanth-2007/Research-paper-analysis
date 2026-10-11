import React from 'react';
import { BookOpen, User, LogIn, LogOut, UserPlus } from 'lucide-react';
import { Journal } from '../types';
import { UserSession, AuthMode } from './AuthModal';

interface NavbarProps {
  journals: Journal[];
  selectedJournalId: string;
  onSelectJournal: (id: string) => void;
  systemStatus?: { status: string; version?: string };
  user?: UserSession | null;
  onOpenAuth?: (mode?: AuthMode) => void;
  onSignOut?: () => void;
  onGoHome?: () => void;
}

export const Navbar: React.FC<NavbarProps> = ({
  journals,
  selectedJournalId,
  onSelectJournal,
  user,
  onOpenAuth,
  onSignOut,
  onGoHome,
}) => {
  return (
    <header className="sticky top-0 z-40 w-full glass-panel border-b border-slate-800/80 bg-slate-950/80 backdrop-blur-md">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between gap-3">
        {/* Brand / Title (Clicking returns to home) */}
        <button
          onClick={onGoHome}
          className="flex items-center space-x-2.5 text-left group cursor-pointer focus:outline-none"
          title="Journal Readiness Home"
        >
          <div className="w-9 h-9 rounded-xl bg-gradient-to-tr from-indigo-600 via-indigo-500 to-cyan-400 flex items-center justify-center shadow-lg shadow-indigo-500/20 flex-shrink-0 group-hover:scale-105 transition-transform">
            <BookOpen className="w-5 h-5 text-white" />
          </div>
          <h1 className="text-base sm:text-lg font-bold font-heading tracking-tight text-white whitespace-nowrap group-hover:text-indigo-200 transition-colors">
            Journal Readiness
          </h1>
        </button>

        {/* Right Section: Auth Actions */}
        <div className="flex items-center space-x-2 sm:space-x-3">
          {/* User Auth Action: Profile/Logout when logged in, BOTH Sign In and Sign Up when not logged in */}
          {user ? (
            <div className="flex items-center space-x-1.5 bg-slate-900 border border-slate-800 rounded-lg p-1 pl-2.5 text-xs text-slate-200">
              <User className="w-3.5 h-3.5 text-indigo-400" />
              <span className="font-medium max-w-[90px] sm:max-w-[120px] truncate">
                {user.username}
              </span>
              <button
                onClick={onSignOut}
                className="p-1 hover:bg-slate-800 rounded text-slate-400 hover:text-rose-400 transition-colors cursor-pointer"
                title="Sign out"
              >
                <LogOut className="w-3.5 h-3.5" />
              </button>
            </div>
          ) : (
            <div className="flex items-center space-x-2">
              <button
                onClick={() => onOpenAuth?.('login')}
                className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold text-slate-200 hover:text-white bg-slate-900 hover:bg-slate-800 border border-slate-700/80 hover:border-slate-600 transition-colors cursor-pointer shadow-sm whitespace-nowrap"
              >
                <LogIn className="w-3.5 h-3.5 text-indigo-400" />
                <span>Sign In</span>
              </button>
              <button
                onClick={() => onOpenAuth?.('signup')}
                className="inline-flex items-center gap-1.5 px-3.5 py-1.5 rounded-lg text-xs font-semibold text-white bg-gradient-to-r from-indigo-600 to-cyan-600 hover:from-indigo-500 hover:to-cyan-500 shadow-md shadow-indigo-600/20 hover:shadow-indigo-600/30 active:scale-[0.98] transition-all cursor-pointer whitespace-nowrap"
              >
                <UserPlus className="w-3.5 h-3.5" />
                <span>Sign Up</span>
              </button>
            </div>
          )}
        </div>
      </div>
    </header>
  );
};
