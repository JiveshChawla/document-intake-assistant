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
  const [activeTab, setActiveTab] = useState<'document' | 'state' | 'completeness'>('document');

  const isComplete = completionPercentage === 100;

  return (
    <div className="flex flex-col h-full bg-white overflow-hidden">
      {/* Tab Navigation Bar */}
      <div className="flex items-center justify-between border-b border-slate-200/80 px-6 bg-white/95 backdrop-blur-xs z-20">
        <div className="flex items-center gap-1 sm:gap-2">
          {/* Tab 1: Live Document Draft */}
          <button
            onClick={() => setActiveTab('document')}
            className={`flex items-center gap-2 py-3 px-3 text-xs font-semibold border-b-2 transition-all ${
              activeTab === 'document'
                ? 'border-brand-600 text-brand-700'
                : 'border-transparent text-slate-500 hover:text-slate-900'
            }`}
          >
            <FileText className="h-4 w-4" />
            <span>Live Document Draft</span>
            {isComplete && (
              <span className="hidden sm:inline-flex items-center gap-0.5 px-1.5 py-0.2 rounded-full text-[10px] bg-emerald-100 text-emerald-800 font-bold">
                <Sparkles className="h-2.5 w-2.5 text-emerald-600" /> Ready
              </span>
            )}
          </button>

          {/* Tab 2: Structured JSON State */}
          <button
            onClick={() => setActiveTab('state')}
            className={`flex items-center gap-2 py-3 px-3 text-xs font-semibold border-b-2 transition-all ${
              activeTab === 'state'
                ? 'border-brand-600 text-brand-700'
                : 'border-transparent text-slate-500 hover:text-slate-900'
            }`}
          >
            <Database className="h-4 w-4" />
            <span>Structured JSON State</span>
          </button>

          {/* Tab 3: Intake Completeness & Edit */}
          <button
            onClick={() => setActiveTab('completeness')}
            className={`flex items-center gap-2 py-3 px-3 text-xs font-semibold border-b-2 transition-all ${
              activeTab === 'completeness'
                ? 'border-brand-600 text-brand-700'
                : 'border-transparent text-slate-500 hover:text-slate-900'
            }`}
          >
            <CheckSquare className="h-4 w-4" />
            <span>Intake Completeness & Edit</span>
            <span
              className={`px-1.5 py-0.5 rounded-full text-[10px] font-bold ${
                isComplete
                  ? 'bg-emerald-100 text-emerald-800'
                  : 'bg-slate-100 text-slate-600'
              }`}
            >
              {completionPercentage}%
            </span>
          </button>
        </div>
      </div>

      {/* Tab Body */}
      <div className="flex-1 overflow-hidden">
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

        {activeTab === 'completeness' && (
          <ProgressTracker
            state={state}
            completionPercentage={completionPercentage}
            onSaveState={onSaveStateDirectly}
          />
        )}
      </div>
    </div>
  );
};
