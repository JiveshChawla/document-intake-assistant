import React, { useState } from 'react';
import { FileText, Database } from 'lucide-react';
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
}

export const PreviewContainer: React.FC<PreviewContainerProps> = ({
  state,
  documentMarkdown,
  documentHtml,
  completionPercentage,
  onOpenEditModal,
}) => {
  const [activeTab, setActiveTab] = useState<'document' | 'state'>('document');

  return (
    <div className="flex flex-col h-full bg-white">
      {/* Real-time Field Checklist & Progress Tracker */}
      <ProgressTracker state={state} completionPercentage={completionPercentage} />

      {/* Tab Navigation */}
      <div className="flex items-center justify-between border-b border-slate-200 px-5 bg-white">
        <div className="flex items-center gap-4">
          <button
            onClick={() => setActiveTab('document')}
            className={`flex items-center gap-2 py-3 text-xs font-semibold border-b-2 transition-all ${
              activeTab === 'document'
                ? 'border-brand-600 text-brand-600'
                : 'border-transparent text-slate-500 hover:text-slate-900'
            }`}
          >
            <FileText className="h-4 w-4" />
            <span>Draft Legal Document</span>
          </button>

          <button
            onClick={() => setActiveTab('state')}
            className={`flex items-center gap-2 py-3 text-xs font-semibold border-b-2 transition-all ${
              activeTab === 'state'
                ? 'border-brand-600 text-brand-600'
                : 'border-transparent text-slate-500 hover:text-slate-900'
            }`}
          >
            <Database className="h-4 w-4" />
            <span>Structured State JSON</span>
          </button>
        </div>
      </div>

      {/* Tab Body */}
      <div className="flex-1 overflow-hidden">
        {activeTab === 'document' ? (
          <DocumentPreview html={documentHtml} markdown={documentMarkdown} />
        ) : (
          <StateViewer state={state} onOpenEditModal={onOpenEditModal} />
        )}
      </div>
    </div>
  );
};
