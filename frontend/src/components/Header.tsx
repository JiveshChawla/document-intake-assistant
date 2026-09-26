import React from 'react';
import { Sparkles, RotateCcw, Cpu, Code2, Scale, Sun, Moon, ArrowLeft } from 'lucide-react';
import { useTheme } from '../context/ThemeContext';

interface HeaderProps {
  activeProvider: string;
  completionPercentage: number;
  onReset: () => void;
  onOpenStateEditor: () => void;
  isLoading: boolean;
  onNavigateHome?: () => void;
}

export const Header: React.FC<HeaderProps> = ({
  activeProvider,
  completionPercentage,
  onReset,
  onOpenStateEditor,
  isLoading,
  onNavigateHome,
}) => {
  const { theme, toggleTheme } = useTheme();
  const isComplete = completionPercentage === 100;

  return (
    <header className="bg-white/90 dark:bg-slate-900/90 backdrop-blur-md border-b border-slate-200/80 dark:border-slate-800 px-6 py-3 sticky top-0 z-30 shadow-xs transition-colors duration-200">
      <div className="max-w-7xl mx-auto flex items-center justify-between gap-4">
        {/* Brand & Title */}
        <div className="flex items-center gap-3">
          {onNavigateHome && (
            <button
              onClick={onNavigateHome}
              className="flex items-center gap-1.5 px-2.5 py-1.5 rounded-xl text-xs font-semibold text-slate-600 dark:text-slate-300 hover:text-brand-600 dark:hover:text-brand-300 hover:bg-slate-100 dark:hover:bg-slate-850 border border-slate-200/80 dark:border-slate-700 transition-all cursor-pointer shadow-2xs hover:shadow-xs"
              title="Return to Overview / Landing Page"
            >
              <ArrowLeft className="h-3.5 w-3.5 text-brand-600 dark:text-brand-400" />
              <span className="hidden sm:inline">Overview</span>
            </button>
          )}

          <div
            onClick={onNavigateHome}
            className={`flex items-center gap-3 ${onNavigateHome ? 'cursor-pointer group' : ''}`}
            title={onNavigateHome ? 'Go to Overview' : undefined}
          >
            <div className="h-9 w-9 rounded-xl bg-gradient-to-tr from-brand-600 via-indigo-600 to-violet-500 flex items-center justify-center text-white shadow-glow-brand ring-1 ring-white/20 group-hover:scale-105 transition-transform">
              <Scale className="h-4.5 w-4.5" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h1 className="font-bold text-slate-900 dark:text-white text-base tracking-tight leading-tight group-hover:text-brand-600 dark:group-hover:text-brand-400 transition-colors">
                  Document Intake Assistant
                </h1>
                <span className="hidden sm:inline-flex items-center px-2 py-0.5 rounded-full text-[10px] font-bold uppercase tracking-wider bg-brand-50 dark:bg-brand-950/60 text-brand-700 dark:text-brand-300 border border-brand-200/70 dark:border-brand-800">
                  Personal Wishes
                </span>
              </div>
              <p className="text-xs text-slate-500 dark:text-slate-400 hidden md:block">
                Conversational Intake & Live Legal Draft Generator
              </p>
            </div>
          </div>
        </div>

        {/* Center/Right Status & Controls
            Exact requested order:
            [ LLM Badge ] [ Progress Badge ] [ Inspect JSON ] [ Reset ] [ Light/Dark Mode Toggle ]
        */}
        <div className="flex items-center gap-2.5">
          {/* 1. LLM Badge */}
          <div className="hidden lg:flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-medium bg-slate-100/90 dark:bg-slate-800/90 border border-slate-200 dark:border-slate-700 text-slate-600 dark:text-slate-300 shadow-2xs">
            <Cpu className="h-3.5 w-3.5 text-brand-600 dark:text-brand-400" />
            <span className="text-slate-400 dark:text-slate-500 font-medium">LLM:</span>
            <span className="font-semibold text-slate-800 dark:text-slate-200 capitalize">
              {activeProvider === 'mock' ? 'Mock Provider' : activeProvider}
            </span>
          </div>

          {/* 2. Progress Badge */}
          <div
            className={`flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-bold transition-all duration-300 shadow-2xs ${
              isComplete
                ? 'bg-emerald-50 dark:bg-emerald-950/70 text-emerald-800 dark:text-emerald-300 border border-emerald-300 dark:border-emerald-600 shadow-glow-emerald'
                : 'bg-amber-50 dark:bg-amber-950/70 text-amber-800 dark:text-amber-300 border border-amber-300 dark:border-amber-700'
            }`}
          >
            {isComplete ? (
              <>
                <Sparkles className="h-3.5 w-3.5 text-emerald-600 dark:text-emerald-400 animate-spin-slow" />
                <span className="tracking-tight">Draft Ready (100%)</span>
              </>
            ) : (
              <>
                <div className="w-2 h-2 rounded-full bg-amber-500 animate-pulse" />
                <span className="tracking-tight">{completionPercentage}% Completed</span>
              </>
            )}
          </div>

          {/* 3. Inspect JSON Button */}
          <button
            onClick={onOpenStateEditor}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-xl text-xs font-semibold text-slate-700 dark:text-slate-200 bg-white dark:bg-slate-800 hover:bg-brand-50 dark:hover:bg-brand-950/50 hover:text-brand-700 dark:hover:text-brand-300 hover:border-brand-300 dark:hover:border-brand-700 border border-slate-200 dark:border-slate-700 shadow-xs hover:shadow-sm transition-all duration-150"
            title="Inspect or manually edit structured JSON state"
          >
            <Code2 className="h-3.5 w-3.5 text-brand-600 dark:text-brand-400" />
            <span className="hidden sm:inline">Inspect JSON</span>
          </button>

          {/* 4. Reset Button */}
          <button
            onClick={onReset}
            disabled={isLoading}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-xl text-xs font-semibold text-slate-600 dark:text-slate-400 hover:text-red-700 dark:hover:text-red-400 hover:bg-red-50 dark:hover:bg-red-950/40 hover:border-red-200 dark:hover:border-red-900 border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 transition-all duration-150 disabled:opacity-50 shadow-xs"
            title="Reset interview conversation and state"
          >
            <RotateCcw className="h-3.5 w-3.5 text-slate-400 group-hover:text-red-600" />
            <span className="hidden sm:inline">Reset</span>
          </button>

          {/* 5. Light/Dark Mode Toggle (at the very end after Reset) */}
          <button
            onClick={toggleTheme}
            className="flex items-center justify-center p-2 rounded-xl text-slate-600 dark:text-slate-300 bg-slate-100 dark:bg-slate-800 hover:bg-brand-50 dark:hover:bg-slate-700 hover:text-brand-600 dark:hover:text-amber-400 border border-slate-200 dark:border-slate-700 transition-all duration-200 shadow-xs hover:shadow-sm hover:scale-105 active:scale-95"
            title={`Switch to ${theme === 'light' ? 'Dark' : 'Light'} Mode`}
            aria-label="Toggle theme"
          >
            {theme === 'light' ? (
              <Moon className="h-4 w-4 text-brand-600" />
            ) : (
              <Sun className="h-4 w-4 text-amber-400 animate-spin-slow" />
            )}
          </button>
        </div>
      </div>
    </header>
  );
};
