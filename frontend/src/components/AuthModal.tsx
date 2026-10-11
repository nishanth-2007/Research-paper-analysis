import React, { useState, useEffect } from 'react';
import {
  X,
  Mail,
  User,
  Lock,
  Eye,
  EyeOff,
  CheckCircle2,
  AlertCircle,
  LogIn,
  UserPlus,
  BookOpen,
} from 'lucide-react';
import { supabase, isSupabaseConfigured } from '../services/supabase';
import { UserService } from '../services/userService';

export type AuthMode = 'login' | 'signup';

export interface UserSession {
  username: string;
  email: string;
}

interface AuthModalProps {
  isOpen: boolean;
  initialMode?: AuthMode;
  onClose: () => void;
  onAuthSuccess: (user: UserSession) => void;
}

export const AuthModal: React.FC<AuthModalProps> = ({
  isOpen,
  initialMode = 'login',
  onClose,
  onAuthSuccess,
}) => {
  const [mode, setMode] = useState<AuthMode>(initialMode);

  // Login form state
  const [loginEmailOrUser, setLoginEmailOrUser] = useState('');
  const [loginPassword, setLoginPassword] = useState('');
  const [showLoginPassword, setShowLoginPassword] = useState(false);
  const [rememberMe, setRememberMe] = useState(true);

  // Sign up form state
  const [signupUsername, setSignupUsername] = useState('');
  const [signupEmail, setSignupEmail] = useState('');
  const [signupPassword, setSignupPassword] = useState('');
  const [signupConfirmPassword, setSignupConfirmPassword] = useState('');
  const [showSignupPassword, setShowSignupPassword] = useState(false);
  const [showSignupConfirmPassword, setShowSignupConfirmPassword] = useState(false);

  // UI feedback state
  const [error, setError] = useState<string | null>(null);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [isGoogleLoading, setIsGoogleLoading] = useState(false);

  useEffect(() => {
    setMode(initialMode);
    setError(null);
    setSuccessMessage(null);
  }, [initialMode, isOpen]);

  if (!isOpen) return null;

  const handleGoogleSignIn = async () => {
    setError(null);
    setIsGoogleLoading(true);

    if (isSupabaseConfigured && supabase) {
      try {
        const { error: oauthError } = await supabase.auth.signInWithOAuth({
          provider: 'google',
          options: {
            redirectTo: window.location.origin,
          },
        });

        if (oauthError) {
          if (
            oauthError.message?.toLowerCase().includes('not enabled') ||
            oauthError.message?.toLowerCase().includes('unsupported provider')
          ) {
            setError(
              'Google provider is not enabled in your Supabase dashboard yet. Enable it under Authentication -> Providers -> Google.'
            );
          } else {
            setError(oauthError.message);
          }
          setIsGoogleLoading(false);
          return;
        }
      } catch (err: any) {
        setError(err.message || 'Google sign-in failed.');
        setIsGoogleLoading(false);
      }
      return;
    }

    // Fallback demonstration mode
    setTimeout(() => {
      setIsGoogleLoading(false);
      const session: UserSession = {
        username: 'GoogleResearcher',
        email: 'researcher@gmail.com',
      };
      setSuccessMessage('Successfully signed in with Google! Welcome.');
      setTimeout(() => {
        onAuthSuccess(session);
        onClose();
      }, 700);
    }, 600);
  };

  const handleLoginSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);

    const rawIdentifier = loginEmailOrUser.trim();
    if (!rawIdentifier) {
      setError('Please enter your email or username.');
      return;
    }
    if (!loginPassword) {
      setError('Please enter your password.');
      return;
    }

    setIsLoading(true);

    // 1. Resolve Identifier: If user typed a username (without @), find associated email
    const emailToSubmit = await UserService.resolveEmailFromIdentifier(rawIdentifier);
    if (!emailToSubmit) {
      setIsLoading(false);
      setError(
        `No account found with username "${rawIdentifier}". Please check your spelling or sign in with your email address.`
      );
      return;
    }

    if (isSupabaseConfigured && supabase) {
      try {
        const { data, error: sbError } = await supabase.auth.signInWithPassword({
          email: emailToSubmit,
          password: loginPassword,
        });

        if (sbError) {
          setError(sbError.message);
          setIsLoading(false);
          return;
        }

        if (data?.user) {
          const userMeta = data.user.user_metadata || {};
          const resolvedUsername =
            userMeta.username ||
            (!rawIdentifier.includes('@') ? rawIdentifier : data.user.email?.split('@')[0]) ||
            'Researcher';

          const session: UserSession = {
            username: resolvedUsername,
            email: data.user.email || emailToSubmit,
          };

          // Cache / register mapping for future fast logins
          await UserService.registerUserMapping(
            resolvedUsername,
            session.email,
            data.user.id
          );

          setSuccessMessage('Successfully signed in with Supabase!');
          setTimeout(() => {
            onAuthSuccess(session);
            onClose();
          }, 600);
        }
      } catch (err: any) {
        setError(err.message || 'An unexpected error occurred during sign in.');
      } finally {
        setIsLoading(false);
      }
      return;
    }

    // Fallback demonstration mode if Supabase credentials are pending in .env
    setTimeout(async () => {
      setIsLoading(false);
      const isEmail = rawIdentifier.includes('@');
      const resolvedUsername = isEmail ? rawIdentifier.split('@')[0] : rawIdentifier;
      const session: UserSession = {
        username: resolvedUsername,
        email: emailToSubmit,
      };

      await UserService.registerUserMapping(resolvedUsername, emailToSubmit);
      setSuccessMessage('Successfully signed in! Welcome back.');
      setTimeout(() => {
        onAuthSuccess(session);
        onClose();
      }, 700);
    }, 600);
  };

  const handleSignupSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);

    const cleanUsername = signupUsername.trim();
    const cleanEmail = signupEmail.trim();

    if (!cleanUsername) {
      setError('Please choose a username.');
      return;
    }
    if (!cleanEmail || !cleanEmail.includes('@')) {
      setError('Please enter a valid email address.');
      return;
    }
    if (signupPassword.length < 6) {
      setError('Password must be at least 6 characters long.');
      return;
    }
    if (signupPassword !== signupConfirmPassword) {
      setError('Passwords do not match. Please verify your confirmation password.');
      return;
    }

    setIsLoading(true);

    // 1. Strict Username Uniqueness Check: Prevent another user from creating an account with an already taken username
    const availability = await UserService.checkUsernameAvailable(cleanUsername);
    if (!availability.available) {
      setIsLoading(false);
      setError(
        availability.reason ||
          `The username "${cleanUsername}" is already taken. Please choose another username.`
      );
      return;
    }

    if (isSupabaseConfigured && supabase) {
      try {
        const { data, error: sbError } = await supabase.auth.signUp({
          email: cleanEmail,
          password: signupPassword,
          options: {
            data: {
              username: cleanUsername,
            },
          },
        });

        if (sbError) {
          setError(sbError.message);
          setIsLoading(false);
          return;
        }

        if (data?.user) {
          const session: UserSession = {
            username: cleanUsername,
            email: data.user.email || cleanEmail,
          };

          // Register new username <-> email mapping to enforce uniqueness and allow username login
          await UserService.registerUserMapping(cleanUsername, cleanEmail, data.user.id);

          if (data.session) {
            setSuccessMessage('Account created and signed in with Supabase!');
          } else {
            setSuccessMessage('Account created! If email confirmation is enabled, check your inbox.');
          }

          setTimeout(() => {
            onAuthSuccess(session);
            onClose();
          }, 800);
        }
      } catch (err: any) {
        setError(err.message || 'An error occurred during account registration.');
      } finally {
        setIsLoading(false);
      }
      return;
    }

    // Fallback demonstration mode if Supabase credentials are pending in .env
    setTimeout(async () => {
      setIsLoading(false);
      const session: UserSession = {
        username: cleanUsername,
        email: cleanEmail,
      };

      await UserService.registerUserMapping(cleanUsername, cleanEmail);
      setSuccessMessage('Account created successfully! Welcome to Journal Readiness.');
      setTimeout(() => {
        onAuthSuccess(session);
        onClose();
      }, 700);
    }, 600);
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/80 backdrop-blur-md animate-fadeIn overflow-y-auto">
      <div className="glass-panel-elevated w-full max-w-md rounded-2xl sm:rounded-3xl border border-slate-700/80 bg-slate-950/95 overflow-hidden shadow-2xl relative my-auto p-6 sm:p-8">
        {/* Subtle background glow */}
        <div className="absolute -top-24 -right-24 w-60 h-60 bg-indigo-600/15 rounded-full blur-3xl pointer-events-none" />
        <div className="absolute -bottom-24 -left-24 w-60 h-60 bg-cyan-600/10 rounded-full blur-3xl pointer-events-none" />

        {/* Close Button top-right */}
        <button
          onClick={onClose}
          className="absolute top-4 right-4 z-20 text-slate-400 hover:text-white p-2 rounded-xl bg-slate-900/60 hover:bg-slate-800 border border-slate-800 transition-colors cursor-pointer"
          aria-label="Close modal"
        >
          <X className="w-5 h-5" />
        </button>

        {/* Brand & Mode Header */}
        <div className="space-y-4 mb-6 relative z-10">
          <div className="flex items-center space-x-3 pr-8">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-indigo-600 via-indigo-500 to-cyan-400 flex items-center justify-center shadow-lg shadow-indigo-500/20 flex-shrink-0">
              <BookOpen className="w-5 h-5 text-white" />
            </div>
            <div>
              <h3 className="text-lg sm:text-xl font-bold font-heading text-white">
                {mode === 'login' ? 'Researcher Sign In' : 'Create Researcher Account'}
              </h3>
              <p className="text-xs text-slate-400 mt-0.5">
                {mode === 'login'
                  ? 'Access your saved manuscript audits & reports.'
                  : 'Start auditing papers against publisher standards.'}
              </p>
            </div>
          </div>

          {/* Tab Switcher */}
          <div className="flex rounded-xl bg-slate-900/90 p-1 border border-slate-800">
            <button
              type="button"
              onClick={() => {
                setMode('login');
                setError(null);
              }}
              className={`flex-1 py-2 text-xs font-semibold rounded-lg transition-all duration-200 flex items-center justify-center gap-1.5 cursor-pointer ${
                mode === 'login'
                  ? 'bg-indigo-600 text-white shadow-md'
                  : 'text-slate-400 hover:text-slate-200'
              }`}
            >
              <LogIn className="w-3.5 h-3.5" />
              Sign In
            </button>
            <button
              type="button"
              onClick={() => {
                setMode('signup');
                setError(null);
              }}
              className={`flex-1 py-2 text-xs font-semibold rounded-lg transition-all duration-200 flex items-center justify-center gap-1.5 cursor-pointer ${
                mode === 'signup'
                  ? 'bg-indigo-600 text-white shadow-md'
                  : 'text-slate-400 hover:text-slate-200'
              }`}
            >
              <UserPlus className="w-3.5 h-3.5" />
              Sign Up
            </button>
          </div>

          {/* Google One-Click OAuth Button */}
          <button
            type="button"
            onClick={handleGoogleSignIn}
            disabled={isGoogleLoading || isLoading}
            className="w-full py-2.5 px-4 rounded-xl text-xs sm:text-sm font-semibold bg-slate-900/90 hover:bg-slate-800 text-slate-200 hover:text-white border border-slate-700/80 hover:border-slate-600 transition-all cursor-pointer shadow-sm flex items-center justify-center gap-2.5 relative group active:scale-[0.99] disabled:opacity-50"
          >
            {isGoogleLoading ? (
              <span className="text-xs text-indigo-300">Connecting to Google...</span>
            ) : (
              <>
                <svg className="w-4 h-4 flex-shrink-0" viewBox="0 0 24 24">
                  <path
                    fill="#4285F4"
                    d="M23.745 12.27c0-.7-.06-1.4-.19-2.07H12v4.51h6.6c-.29 1.52-1.14 2.82-2.4 3.68v3.05h3.88c2.27-2.09 3.66-5.17 3.66-9.17z"
                  />
                  <path
                    fill="#34A853"
                    d="M12 24c3.24 0 5.95-1.08 7.93-2.91l-3.88-3.05c-1.08.72-2.45 1.16-4.05 1.16-3.12 0-5.77-2.1-6.72-4.93H1.25v3.15C3.26 21.36 7.33 24 12 24z"
                  />
                  <path
                    fill="#FBBC05"
                    d="M5.28 14.27c-.25-.72-.38-1.49-.38-2.27s.13-1.55.38-2.27V6.58H1.25C.45 8.18 0 9.98 0 12s.45 3.82 1.25 5.42l4.03-3.15z"
                  />
                  <path
                    fill="#EA4335"
                    d="M12 4.75c1.77 0 3.35.61 4.6 1.8l3.42-3.42C17.95 1.19 15.24 0 12 0 7.33 0 3.26 2.64 1.25 6.58l4.03 3.15c.95-2.83 3.6-4.98 6.72-4.98z"
                  />
                </svg>
                <span>Continue with Google</span>
              </>
            )}
          </button>

          {/* Divider */}
          <div className="relative flex items-center justify-center my-3">
            <div className="border-t border-slate-800 w-full" />
            <span className="bg-slate-950 px-3 text-[11px] font-mono text-slate-500 uppercase tracking-wider whitespace-nowrap">
              or continue with {mode === 'login' ? 'credentials' : 'email'}
            </span>
            <div className="border-t border-slate-800 w-full" />
          </div>
        </div>

        {/* Error / Success Banners */}
        {error && (
          <div className="mb-4 p-3 rounded-xl bg-rose-950/40 border border-rose-500/40 text-xs text-rose-300 flex items-center gap-2 animate-shake relative z-10">
            <AlertCircle className="w-4 h-4 flex-shrink-0 text-rose-400" />
            <span>{error}</span>
          </div>
        )}

        {successMessage && (
          <div className="mb-4 p-3 rounded-xl bg-emerald-950/40 border border-emerald-500/40 text-xs text-emerald-300 flex items-center gap-2 relative z-10">
            <CheckCircle2 className="w-4 h-4 flex-shrink-0 text-emerald-400" />
            <span>{successMessage}</span>
          </div>
        )}

        {/* LOGIN FORM */}
        {mode === 'login' ? (
          <form onSubmit={handleLoginSubmit} className="space-y-4 relative z-10">
            {/* Email or Username Slot */}
            <div className="space-y-1.5">
              <label
                htmlFor="login-identifier"
                className="text-xs font-medium text-slate-300 block"
              >
                Email or Username
              </label>
              <div className="relative">
                <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none text-slate-500">
                  <User className="w-4 h-4" />
                </div>
                <input
                  id="login-identifier"
                  type="text"
                  value={loginEmailOrUser}
                  onChange={(e) => setLoginEmailOrUser(e.target.value)}
                  placeholder="name@university.edu or username"
                  className="w-full pl-9 pr-3 py-2 bg-slate-900/80 border border-slate-700/80 rounded-xl text-xs sm:text-sm text-slate-100 placeholder-slate-500 focus:outline-none focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 transition-colors"
                  required
                />
              </div>
            </div>

            {/* Password Slot */}
            <div className="space-y-1.5">
              <div className="flex items-center justify-between">
                <label
                  htmlFor="login-password"
                  className="text-xs font-medium text-slate-300 block"
                >
                  Password
                </label>
                <a
                  href="#forgot-password"
                  onClick={(e) => {
                    e.preventDefault();
                    setError('Password reset instructions will be sent to your registered email.');
                  }}
                  className="text-[11px] text-indigo-400 hover:text-indigo-300 transition-colors"
                >
                  Forgot password?
                </a>
              </div>
              <div className="relative">
                <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none text-slate-500">
                  <Lock className="w-4 h-4" />
                </div>
                <input
                  id="login-password"
                  type={showLoginPassword ? 'text' : 'password'}
                  value={loginPassword}
                  onChange={(e) => setLoginPassword(e.target.value)}
                  placeholder="Enter your password"
                  className="w-full pl-9 pr-10 py-2 bg-slate-900/80 border border-slate-700/80 rounded-xl text-xs sm:text-sm text-slate-100 placeholder-slate-500 focus:outline-none focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 transition-colors"
                  required
                />
                <button
                  type="button"
                  onClick={() => setShowLoginPassword(!showLoginPassword)}
                  className="absolute inset-y-0 right-0 pr-3 flex items-center text-slate-400 hover:text-slate-200 cursor-pointer"
                >
                  {showLoginPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                </button>
              </div>
            </div>

            {/* Remember Me */}
            <div className="flex items-center justify-between pt-1">
              <label className="flex items-center space-x-2 cursor-pointer text-xs text-slate-400">
                <input
                  type="checkbox"
                  checked={rememberMe}
                  onChange={(e) => setRememberMe(e.target.checked)}
                  className="w-3.5 h-3.5 rounded border-slate-700 bg-slate-900 text-indigo-600 focus:ring-indigo-500"
                />
                <span>Remember this workstation</span>
              </label>
            </div>

            {/* Submit Button */}
            <button
              type="submit"
              disabled={isLoading}
              className="w-full py-2.5 px-4 rounded-xl text-xs sm:text-sm font-semibold bg-indigo-600 hover:bg-indigo-500 disabled:opacity-50 text-white transition-colors cursor-pointer shadow-lg shadow-indigo-600/20 flex items-center justify-center gap-2 mt-2"
            >
              {isLoading ? (
                <span>Signing In...</span>
              ) : (
                <>
                  <LogIn className="w-4 h-4" />
                  <span>Sign In</span>
                </>
              )}
            </button>

            {/* Toggle Prompt */}
            <div className="text-center pt-2">
              <span className="text-xs text-slate-400">Don't have an account yet? </span>
              <button
                type="button"
                onClick={() => {
                  setMode('signup');
                  setError(null);
                }}
                className="text-xs font-semibold text-indigo-400 hover:text-indigo-300 cursor-pointer"
              >
                Create Account
              </button>
            </div>
          </form>
        ) : (
          /* SIGN UP FORM */
          <form onSubmit={handleSignupSubmit} className="space-y-3 relative z-10">
            {/* Username Slot */}
            <div className="space-y-1">
              <label
                htmlFor="signup-username"
                className="text-xs font-medium text-slate-300 block"
              >
                Username
              </label>
              <div className="relative">
                <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none text-slate-500">
                  <User className="w-4 h-4" />
                </div>
                <input
                  id="signup-username"
                  type="text"
                  value={signupUsername}
                  onChange={(e) => setSignupUsername(e.target.value)}
                  placeholder="e.g. dr_smith or alex_k"
                  className="w-full pl-9 pr-3 py-2 bg-slate-900/80 border border-slate-700/80 rounded-xl text-xs sm:text-sm text-slate-100 placeholder-slate-500 focus:outline-none focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 transition-colors"
                  required
                />
              </div>
            </div>

            {/* Email Slot */}
            <div className="space-y-1">
              <label htmlFor="signup-email" className="text-xs font-medium text-slate-300 block">
                Email Address
              </label>
              <div className="relative">
                <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none text-slate-500">
                  <Mail className="w-4 h-4" />
                </div>
                <input
                  id="signup-email"
                  type="email"
                  value={signupEmail}
                  onChange={(e) => setSignupEmail(e.target.value)}
                  placeholder="researcher@institution.edu"
                  className="w-full pl-9 pr-3 py-2 bg-slate-900/80 border border-slate-700/80 rounded-xl text-xs sm:text-sm text-slate-100 placeholder-slate-500 focus:outline-none focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 transition-colors"
                  required
                />
              </div>
            </div>

            {/* Password Slot */}
            <div className="space-y-1">
              <label
                htmlFor="signup-password"
                className="text-xs font-medium text-slate-300 block"
              >
                Password
              </label>
              <div className="relative">
                <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none text-slate-500">
                  <Lock className="w-4 h-4" />
                </div>
                <input
                  id="signup-password"
                  type={showSignupPassword ? 'text' : 'password'}
                  value={signupPassword}
                  onChange={(e) => setSignupPassword(e.target.value)}
                  placeholder="At least 6 characters"
                  className="w-full pl-9 pr-10 py-2 bg-slate-900/80 border border-slate-700/80 rounded-xl text-xs sm:text-sm text-slate-100 placeholder-slate-500 focus:outline-none focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 transition-colors"
                  required
                  minLength={6}
                />
                <button
                  type="button"
                  onClick={() => setShowSignupPassword(!showSignupPassword)}
                  className="absolute inset-y-0 right-0 pr-3 flex items-center text-slate-400 hover:text-slate-200 cursor-pointer"
                >
                  {showSignupPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                </button>
              </div>
            </div>

            {/* Confirm Password Slot */}
            <div className="space-y-1">
              <label
                htmlFor="signup-confirm-password"
                className="text-xs font-medium text-slate-300 block"
              >
                Confirm Password
              </label>
              <div className="relative">
                <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none text-slate-500">
                  <Lock className="w-4 h-4" />
                </div>
                <input
                  id="signup-confirm-password"
                  type={showSignupConfirmPassword ? 'text' : 'password'}
                  value={signupConfirmPassword}
                  onChange={(e) => setSignupConfirmPassword(e.target.value)}
                  placeholder="Re-enter password"
                  className={`w-full pl-9 pr-10 py-2 bg-slate-900/80 border rounded-xl text-xs sm:text-sm text-slate-100 placeholder-slate-500 focus:outline-none focus:ring-1 transition-colors ${
                    signupConfirmPassword && signupPassword !== signupConfirmPassword
                      ? 'border-rose-500/80 focus:border-rose-500 focus:ring-rose-500'
                      : 'border-slate-700/80 focus:border-indigo-500 focus:ring-indigo-500'
                  }`}
                  required
                />
                <button
                  type="button"
                  onClick={() => setShowSignupConfirmPassword(!showSignupConfirmPassword)}
                  className="absolute inset-y-0 right-0 pr-3 flex items-center text-slate-400 hover:text-slate-200 cursor-pointer"
                >
                  {showSignupConfirmPassword ? (
                    <EyeOff className="w-4 h-4" />
                  ) : (
                    <Eye className="w-4 h-4" />
                  )}
                </button>
              </div>
              {signupConfirmPassword && signupPassword !== signupConfirmPassword && (
                <span className="text-[11px] text-rose-400 block pt-0.5">
                  Passwords do not match
                </span>
              )}
            </div>

            {/* Submit Button */}
            <button
              type="submit"
              disabled={isLoading}
              className="w-full py-2.5 px-4 rounded-xl text-xs sm:text-sm font-semibold bg-indigo-600 hover:bg-indigo-500 disabled:opacity-50 text-white transition-colors cursor-pointer shadow-lg shadow-indigo-600/20 flex items-center justify-center gap-2 mt-2"
            >
              {isLoading ? (
                <span>Creating Account...</span>
              ) : (
                <>
                  <UserPlus className="w-4 h-4" />
                  <span>Create Account</span>
                </>
              )}
            </button>

            {/* Toggle Prompt */}
            <div className="text-center pt-2">
              <span className="text-xs text-slate-400">Already registered? </span>
              <button
                type="button"
                onClick={() => {
                  setMode('login');
                  setError(null);
                }}
                className="text-xs font-semibold text-indigo-400 hover:text-indigo-300 cursor-pointer"
              >
                Sign In
              </button>
            </div>
          </form>
        )}
      </div>
    </div>
  );
};
