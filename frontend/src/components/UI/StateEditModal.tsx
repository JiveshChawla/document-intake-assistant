import React, { useState, useEffect } from 'react';
import { X, Check, AlertCircle, Code2 } from 'lucide-react';
import { PersonalWishesState } from '../../types';

interface StateEditModalProps {
  isOpen: boolean;
  onClose: () => void;
  currentState: PersonalWishesState;
  onSaveState: (newState: PersonalWishesState) => Promise<void>;
}

export const StateEditModal: React.FC<StateEditModalProps> = ({
  isOpen,
  onClose,
  currentState,
  onSaveState,
}) => {
  const [jsonText, setJsonText] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [isSaving, setIsSaving] = useState(false);

  useEffect(() => {
    if (isOpen) {
      setJsonText(JSON.stringify(currentState, null, 2));
      setError(null);
    }
  }, [isOpen, currentState]);

  if (!isOpen) return null;

  const handleSave = async () => {
    try {
      const parsed = JSON.parse(jsonText);
      setIsSaving(true);
      setError(null);
      await onSaveState(parsed);
      setIsSaving(false);
      onClose();
    } catch (err: any) {
      setError(err.message || 'Invalid JSON syntax');
      setIsSaving(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/50 backdrop-blur-xs p-4 animate-in fade-in duration-200">
      <div className="bg-white rounded-2xl shadow-2xl max-w-2xl w-full flex flex-col max-h-[85vh] border border-slate-200 overflow-hidden">
        {/* Modal Header */}
        <div className="px-6 py-4 border-b border-slate-200/80 flex items-center justify-between bg-slate-50/80">
          <div className="flex items-center gap-2.5">
            <div className="p-2 rounded-xl bg-slate-900 text-white">
              <Code2 className="h-4 w-4" />
            </div>
            <div>
              <h3 className="font-semibold text-slate-900 text-sm">
                Raw Structured State Editor
              </h3>
              <p className="text-xs text-slate-500">
                Directly edit JSON state. All updates validate against backend Pydantic models.
              </p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-1.5 rounded-lg text-slate-400 hover:text-slate-700 hover:bg-slate-200/70 transition-colors"
          >
            <X className="h-4 w-4" />
          </button>
        </div>

        {/* Modal Body */}
        <div className="p-6 flex-1 overflow-y-auto">
          {error && (
            <div className="mb-4 p-3 rounded-xl bg-red-50 border border-red-200 text-red-700 text-xs flex items-center gap-2">
              <AlertCircle className="h-4 w-4 flex-shrink-0" />
              <span>{error}</span>
            </div>
          )}

          <textarea
            value={jsonText}
            onChange={(e) => setJsonText(e.target.value)}
            rows={16}
            className="w-full font-mono text-xs p-4 bg-slate-950 text-emerald-300 rounded-xl border border-slate-800 focus:outline-none focus:ring-2 focus:ring-brand-500/30 leading-relaxed shadow-inner"
            spellCheck={false}
          />
        </div>

        {/* Modal Footer */}
        <div className="px-6 py-3.5 bg-slate-50 border-t border-slate-200/80 flex items-center justify-end gap-2.5">
          <button
            onClick={onClose}
            className="px-4 py-2 text-xs font-medium text-slate-600 hover:text-slate-900 hover:bg-slate-100 rounded-lg transition-colors"
          >
            Cancel
          </button>
          <button
            onClick={handleSave}
            disabled={isSaving}
            className="flex items-center gap-1.5 px-4 py-2 text-xs font-medium text-white bg-slate-900 hover:bg-brand-600 rounded-lg shadow-xs transition-colors disabled:opacity-50"
          >
            <Check className="h-3.5 w-3.5" />
            <span>{isSaving ? 'Validating...' : 'Apply & Sync State'}</span>
          </button>
        </div>
      </div>
    </div>
  );
};
