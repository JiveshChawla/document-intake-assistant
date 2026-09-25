import React from 'react';
import { Sparkles, RotateCcw, Cpu, Code2, Scale } from 'lucide-react';

interface HeaderProps {
  activeProvider: string;
  completionPercentage: number;
  onReset: () => void;
  onOpenStateEditor: () => void;
  isLoading: boolean;
}

export const Header: React.FC<HeaderProps> = ({
  activeProvider,
  completionPercentage,
  onReset,
  onOpenStateEditor,
  isLoading,
}) => {
  const isComplete = completionPercentage === 100;

  return (
    <header className="bg-white/95 backdrop-blur-md border-b border-slate-200/80 px-6 py-3 sticky top-0 z-30 shadow-xs">
      <div className="max-w-7xl mx-auto flex items-center justify-between gap-4">
        {/* Brand & Title */}
        <div className="flex items-center gap-3">
          <div className="h-9 w-9 rounded-xl bg-gradient-to-tr from-slate-900 to-brand-700 flex items-center justify-center text-white shadow-sm ring-1 ring-slate-900/10">
            <Scale className="h-4.5 w-4.5" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h1 className="font-semibold text-slate-900 text-base tracking-tight leading-tight">
                Document Intake Assistant
              </h1>
              <span className="hidden sm:inline-flex items-center px-2 py-0.5 rounded-full text-[10px] font-semibold uppercase tracking-wider bg-slate-100 text-slate-600 border border-slate-200/70">
                Personal Wishes
              </span>
            </div>
            <p className="text-xs text-slate-500 hidden md:block">
              Conversational Intake & Live Legal Draft Generator
            </p>
          </div>
        </div>

        {/* Center/Right Status & Controls */}
        <div className="flex items-center gap-2.5">
          {/* Active Provider Pill */}
          <div className="hidden lg:flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-medium bg-slate-50 border border-slate-200/80 text-slate-600">
            <Cpu className="h-3.5 w-3.5 text-brand-600" />
            <span className="text-slate-400">LLM:</span>
            <span className="font-semibold text-slate-800 capitalize">
              {activeProvider === 'mock' ? 'Mock Provider' : activeProvider}
            </span>
          </div>

          {/* Intake Completeness Pill */}
          <div
            className={`flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-semibold transition-all duration-300 ${
              isComplete
                ? 'bg-emerald-50 text-emerald-800 border border-emerald-300 shadow-glow-emerald'
                : 'bg-amber-50 text-amber-800 border border-amber-200'
            }`}
          >
            {isComplete ? (
              <>
                <Sparkles className="h-3.5 w-3.5 text-emerald-600 animate-spin-slow" />
                <span className="tracking-tight">Draft Ready (100%)</span>
              </>
            ) : (
              <>
                <div className="w-2 h-2 rounded-full bg-amber-500 animate-pulse" />
                <span className="tracking-tight">{completionPercentage}% Completed</span>
              </>
            )}
          </div>

          {/* Direct State Override / Inspector Button */}
          <button
            onClick={onOpenStateEditor}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium text-slate-700 bg-white hover:bg-slate-50 border border-slate-200 shadow-xs transition-colors"
            title="Inspect or manually edit structured JSON state"
          >
            <Code2 className="h-3.5 w-3.5 text-slate-500" />
            <span className="hidden sm:inline">Inspect JSON</span>
          </button>

          {/* Reset Session Button */}
          <button
            onClick={onReset}
            disabled={isLoading}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium text-slate-600 hover:text-red-700 hover:bg-red-50 hover:border-red-200 border border-slate-200 bg-white transition-colors disabled:opacity-50"
            title="Reset interview conversation and state"
          >
            <RotateCcw className="h-3.5 w-3.5" />
            <span className="hidden sm:inline">Reset</span>
          </button>
        </div>
      </div>
    </header>
  );
};
