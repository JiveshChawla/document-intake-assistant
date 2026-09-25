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
    <div className="flex flex-col h-full bg-slate-900 text-slate-100">
      {/* Top Banner explaining state separation */}
      <div className="px-5 py-3 bg-slate-950 border-b border-slate-800 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <ShieldCheck className="h-4 w-4 text-emerald-400" />
          <span className="text-xs font-semibold text-slate-200">
            Structured State (Single Source of Truth)
          </span>
        </div>

        <div className="flex items-center gap-2">
          <button
            onClick={onOpenEditModal}
            className="flex items-center gap-1.5 px-2.5 py-1 rounded bg-slate-800 hover:bg-slate-700 text-xs font-medium text-slate-300 border border-slate-700 transition-colors"
          >
            <Edit3 className="h-3 w-3" />
            <span>Edit JSON</span>
          </button>

          <button
            onClick={handleCopy}
            className="flex items-center gap-1.5 px-2.5 py-1 rounded bg-slate-800 hover:bg-slate-700 text-xs font-medium text-slate-300 border border-slate-700 transition-colors"
          >
            {copied ? (
              <>
                <Check className="h-3 w-3 text-emerald-400" />
                <span className="text-emerald-400 font-semibold">Copied!</span>
              </>
            ) : (
              <>
                <Copy className="h-3 w-3 text-slate-400" />
                <span>Copy JSON</span>
              </>
            )}
          </button>
        </div>
      </div>

      <div className="p-3 bg-slate-850 border-b border-slate-800 text-[11px] text-slate-400 flex items-center gap-2 px-5">
        <Code className="h-3.5 w-3.5 text-brand-400 flex-shrink-0" />
        <span>
          Maintained strictly independent of chat transcript. Validated by backend Pydantic schema before mutation.
        </span>
      </div>

      {/* JSON Viewer */}
      <div className="flex-1 overflow-auto p-5 font-mono text-xs leading-relaxed">
        <pre className="text-emerald-300 font-mono">
          {jsonString}
        </pre>
      </div>
    </div>
  );
};
