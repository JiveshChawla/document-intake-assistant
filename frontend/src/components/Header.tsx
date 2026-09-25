import React from 'react';
import { FileText, RotateCcw, Cpu, CheckCircle2, AlertTriangle, Code2 } from 'lucide-react';

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
    <header className="bg-white border-b border-slate-200 px-6 py-3.5 sticky top-0 z-30 shadow-sm">
      <div className="max-w-7xl mx-auto flex items-center justify-between">
        {/* Brand & Title */}
        <div className="flex items-center gap-3">
          <div className="h-10 w-10 rounded-lg bg-gradient-to-tr from-brand-600 to-indigo-500 flex items-center justify-center text-white shadow-md">
            <FileText className="h-5 w-5" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h1 className="font-semibold text-slate-900 text-lg leading-tight">
                Document Intake Assistant
              </h1>
              <span className="text-[11px] font-bold tracking-wider uppercase px-2 py-0.5 rounded-full bg-slate-100 text-slate-600 border border-slate-200">
                Fictional Legal Tech
              </span>
            </div>
            <p className="text-xs text-slate-500">
              Conversational Personal Wishes Intake & Structured State Engine
            </p>
          </div>
        </div>

        {/* Center/Right Status & Controls */}
        <div className="flex items-center gap-3">
          {/* Active Provider Pill */}
          <div className="hidden sm:flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-medium bg-slate-100 border border-slate-200 text-slate-700">
            <Cpu className="h-3.5 w-3.5 text-brand-600" />
            <span>Provider:</span>
            <span className="font-semibold capitalize text-slate-900">
              {activeProvider === 'mock' ? 'Mock (Deterministic)' : activeProvider}
            </span>
          </div>

          {/* Intake Status Pill */}
          <div
            className={`hidden md:flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-semibold border ${
              isComplete
                ? 'bg-emerald-50 text-emerald-700 border-emerald-200'
                : 'bg-amber-50 text-amber-700 border-amber-200'
            }`}
          >
            {isComplete ? (
              <CheckCircle2 className="h-3.5 w-3.5 text-emerald-600" />
            ) : (
              <AlertTriangle className="h-3.5 w-3.5 text-amber-600" />
            )}
            <span>{isComplete ? 'Draft Ready (100%)' : `${completionPercentage}% Completed`}</span>
          </div>

          {/* Direct State Override Button */}
          <button
            onClick={onOpenStateEditor}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-md text-xs font-medium text-slate-700 bg-slate-100 hover:bg-slate-200 border border-slate-300 transition-colors"
            title="Inspect or manually edit structured state"
          >
            <Code2 className="h-3.5 w-3.5 text-slate-600" />
            <span className="hidden sm:inline">Inspect State</span>
          </button>

          {/* Reset Session Button */}
          <button
            onClick={onReset}
            disabled={isLoading}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-md text-xs font-medium text-red-600 bg-red-50 hover:bg-red-100 border border-red-200 transition-colors disabled:opacity-50"
            title="Reset interview conversation & state"
          >
            <RotateCcw className="h-3.5 w-3.5" />
            <span>Reset</span>
          </button>
        </div>
      </div>
    </header>
  );
};
