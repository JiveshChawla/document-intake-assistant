import React, { useState } from 'react';
import { Copy, Check, Code, ShieldCheck, Edit3 } from 'lucide-react';
import { PersonalWishesState } from '../../types';

interface StateViewerProps {
  state: PersonalWishesState;
  onOpenEditModal: () => void;
}

export const StateViewer: React.FC<StateViewerProps> = ({ state, onOpenEditModal }) => {
  const [copied, setCopied] = useState(false);
  const jsonString = JSON.stringify(state, null, 2);

  const handleCopy = () => {
    navigator.clipboard.writeText(jsonString);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="flex flex-col h-full bg-slate-950 text-slate-100 overflow-hidden font-sans">
      {/* Top Banner explaining state separation */}
      <div className="px-6 py-3 bg-slate-900/90 border-b border-slate-800/90 flex items-center justify-between shadow-xs">
        <div className="flex items-center gap-2">
          <ShieldCheck className="h-4 w-4 text-emerald-400" />
          <span className="text-xs font-bold text-slate-200 tracking-tight">
            Structured State (Single Source of Truth)
          </span>
        </div>

        <div className="flex items-center gap-2">
          <button
            onClick={onOpenEditModal}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-slate-800 hover:bg-slate-700 text-xs font-semibold text-slate-200 border border-slate-700 transition-colors shadow-2xs"
            title="Open modal to directly edit full JSON"
          >
            <Edit3 className="h-3.5 w-3.5 text-brand-400" />
            <span>Raw JSON Editor</span>
          </button>

          <button
            onClick={handleCopy}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-slate-800 hover:bg-slate-700 text-xs font-semibold text-slate-200 border border-slate-700 transition-colors shadow-2xs"
          >
            {copied ? (
              <>
                <Check className="h-3.5 w-3.5 text-emerald-400" />
                <span className="text-emerald-400 font-bold">Copied</span>
              </>
            ) : (
              <>
                <Copy className="h-3.5 w-3.5 text-slate-400" />
                <span>Copy JSON</span>
              </>
            )}
          </button>
        </div>
      </div>

      <div className="p-3 bg-slate-900/50 border-b border-slate-800/80 text-[11px] text-slate-400 flex items-center gap-2 px-6">
        <Code className="h-3.5 w-3.5 text-brand-400 flex-shrink-0" />
        <span>
          Strictly decoupled from conversation transcript. State transitions validated by Pydantic models on every mutation.
        </span>
      </div>

      {/* JSON Viewer with vibrant syntax styling */}
      <div className="flex-1 overflow-auto p-6 font-mono text-xs leading-relaxed selection:bg-brand-800 selection:text-white">
        <pre className="text-emerald-400 font-mono">
          {jsonString}
        </pre>
      </div>
    </div>
  );
};
