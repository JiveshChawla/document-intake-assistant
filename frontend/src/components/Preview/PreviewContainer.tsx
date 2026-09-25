import React, { useState } from 'react';
import { FileText, Database, CheckSquare, Sparkles } from 'lucide-react';
import { PersonalWishesState } from '../../types';
import { ProgressTracker } from './ProgressTracker';
import { DocumentPreview } from './DocumentPreview';
import { StateViewer } from './StateViewer';

interface PreviewContainerProps {
  state: PersonalWishesState;
  documentMarkdown: string;
  documentHtml: string;
  completionPercentage: number;
  onOpenEditModal: () => void;
  onSaveStateDirectly: (newState: PersonalWishesState) => Promise<void>;
}

export const PreviewContainer: React.FC<PreviewContainerProps> = ({
  state,
  documentMarkdown,
  documentHtml,
  completionPercentage,
  onOpenEditModal,
  onSaveStateDirectly,
}) => {
  // Requirement: Tab 1 "Intake Completeness & Edit" is first!
  const [activeTab, setActiveTab] = useState<'completeness' | 'document' | 'state'>('completeness');

  const isComplete = completionPercentage === 100;

  return (
    <div className="flex flex-col h-full bg-white dark:bg-slate-900 overflow-hidden transition-colors duration-200">
      {/* Tab Navigation Bar - Reordered per requirement:
          1. Intake Completeness & Edit (Questions/progress cards first)
          2. Live Document Draft (Legal view second)
          3. Structured JSON State (Raw JSON third)
      */}
      <div className="flex items-center justify-between border-b border-slate-200/80 dark:border-slate-800 px-6 bg-white/95 dark:bg-slate-900/95 backdrop-blur-xs z-20 transition-colors">
        <div className="flex items-center gap-1 sm:gap-2">
          {/* Tab 1: Intake Completeness & Edit (FIRST) */}
          <button
            onClick={() => setActiveTab('completeness')}
            className={`flex items-center gap-2 py-3 px-3 text-xs font-semibold border-b-2 transition-all ${
              activeTab === 'completeness'
                ? 'border-brand-600 dark:border-brand-400 text-brand-700 dark:text-brand-300 font-bold'
                : 'border-transparent text-slate-500 dark:text-slate-400 hover:text-slate-900 dark:hover:text-slate-100'
            }`}
          >
            <CheckSquare className="h-4 w-4 text-brand-600 dark:text-brand-400" />
            <span>Intake Completeness & Edit</span>
            <span
              className={`px-1.5 py-0.5 rounded-full text-[10px] font-bold ${
                isComplete
                  ? 'bg-emerald-100 dark:bg-emerald-950 text-emerald-800 dark:text-emerald-300 border border-emerald-300 dark:border-emerald-700'
                  : 'bg-brand-50 dark:bg-brand-950/60 text-brand-700 dark:text-brand-300 border border-brand-200 dark:border-brand-800'
              }`}
            >
              {completionPercentage}%
            </span>
          </button>

          {/* Tab 2: Live Document Draft (SECOND) */}
          <button
            onClick={() => setActiveTab('document')}
            className={`flex items-center gap-2 py-3 px-3 text-xs font-semibold border-b-2 transition-all ${
              activeTab === 'document'
                ? 'border-brand-600 dark:border-brand-400 text-brand-700 dark:text-brand-300 font-bold'
                : 'border-transparent text-slate-500 dark:text-slate-400 hover:text-slate-900 dark:hover:text-slate-100'
            }`}
          >
            <FileText className="h-4 w-4" />
            <span>Live Document Draft</span>
            {isComplete && (
              <span className="hidden sm:inline-flex items-center gap-0.5 px-1.5 py-0.2 rounded-full text-[10px] bg-emerald-100 dark:bg-emerald-950 text-emerald-800 dark:text-emerald-300 font-bold border border-emerald-300 dark:border-emerald-800">
                <Sparkles className="h-2.5 w-2.5 text-emerald-600 dark:text-emerald-400" /> Ready
              </span>
            )}
          </button>

          {/* Tab 3: Structured JSON State (THIRD) */}
          <button
            onClick={() => setActiveTab('state')}
            className={`flex items-center gap-2 py-3 px-3 text-xs font-semibold border-b-2 transition-all ${
              activeTab === 'state'
                ? 'border-brand-600 dark:border-brand-400 text-brand-700 dark:text-brand-300 font-bold'
                : 'border-transparent text-slate-500 dark:text-slate-400 hover:text-slate-900 dark:hover:text-slate-100'
            }`}
          >
            <Database className="h-4 w-4" />
            <span>Structured JSON State</span>
          </button>
        </div>
      </div>

      {/* Tab Body */}
      <div className="flex-1 overflow-hidden">
        {activeTab === 'completeness' && (
          <ProgressTracker
            state={state}
            completionPercentage={completionPercentage}
            onSaveState={onSaveStateDirectly}
          />
        )}

        {activeTab === 'document' && (
          <DocumentPreview
            html={documentHtml}
            markdown={documentMarkdown}
            completionPercentage={completionPercentage}
          />
        )}

        {activeTab === 'state' && (
          <StateViewer
            state={state}
            onOpenEditModal={onOpenEditModal}
          />
        )}
      </div>
    </div>
  );
};
