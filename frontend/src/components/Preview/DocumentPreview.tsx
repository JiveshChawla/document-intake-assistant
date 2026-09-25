import React, { useState } from 'react';
import { Copy, Printer, Check, FileCode, FileText, Sparkles, CheckCircle2 } from 'lucide-react';

interface DocumentPreviewProps {
  html: string;
  markdown: string;
  completionPercentage: number;
}

export const DocumentPreview: React.FC<DocumentPreviewProps> = ({
  html,
  markdown,
  completionPercentage,
}) => {
  const [viewMode, setViewMode] = useState<'formatted' | 'markdown'>('formatted');
  const [copied, setCopied] = useState(false);

  const isComplete = completionPercentage === 100;

  const handleCopy = () => {
    navigator.clipboard.writeText(markdown);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const handlePrint = () => {
    window.print();
  };

  return (
    <div className="flex flex-col h-full bg-slate-100/70 dark:bg-slate-950 overflow-hidden transition-colors duration-200">
      {/* Action Toolbar */}
      <div className="px-6 py-2.5 bg-white dark:bg-slate-900 border-b border-slate-200/80 dark:border-slate-800 flex flex-wrap items-center justify-between gap-3 no-print shadow-xs z-10 transition-colors">
        {/* Toggle Mode */}
        <div className="flex items-center gap-1 bg-slate-100 dark:bg-slate-800 p-1 rounded-xl border border-slate-200/80 dark:border-slate-700/80 text-xs">
          <button
            onClick={() => setViewMode('formatted')}
            className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg font-semibold transition-all ${
              viewMode === 'formatted'
                ? 'bg-white dark:bg-slate-900 text-slate-900 dark:text-white shadow-xs'
                : 'text-slate-500 dark:text-slate-400 hover:text-slate-900 dark:hover:text-slate-100'
            }`}
          >
            <FileText className="h-3.5 w-3.5 text-brand-600 dark:text-brand-400" />
            <span>Legal Paper View</span>
          </button>
          <button
            onClick={() => setViewMode('markdown')}
            className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg font-semibold transition-all ${
              viewMode === 'markdown'
                ? 'bg-white dark:bg-slate-900 text-slate-900 dark:text-white shadow-xs'
                : 'text-slate-500 dark:text-slate-400 hover:text-slate-900 dark:hover:text-slate-100'
            }`}
          >
            <FileCode className="h-3.5 w-3.5 text-brand-600 dark:text-brand-400" />
            <span>Markdown Source</span>
          </button>
        </div>

        {/* Export / Copy Tools */}
        <div className="flex items-center gap-2 text-xs">
          <button
            onClick={handleCopy}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-xl border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 text-slate-700 dark:text-slate-300 hover:bg-slate-50 dark:hover:bg-slate-700/80 shadow-2xs transition-colors"
            title="Copy draft markdown to clipboard"
          >
            {copied ? (
              <>
                <Check className="h-3.5 w-3.5 text-emerald-600 dark:text-emerald-400" />
                <span className="text-emerald-700 dark:text-emerald-400 font-bold">Copied!</span>
              </>
            ) : (
              <>
                <Copy className="h-3.5 w-3.5 text-slate-500 dark:text-slate-400" />
                <span>Copy Draft</span>
              </>
            )}
          </button>

          <button
            onClick={handlePrint}
            className="flex items-center gap-1.5 px-3.5 py-1.5 rounded-xl bg-slate-900 dark:bg-brand-600 text-white hover:bg-brand-600 dark:hover:bg-brand-500 shadow-xs font-semibold transition-colors"
            title="Print or export as PDF"
          >
            <Printer className="h-3.5 w-3.5" />
            <span>Print / PDF</span>
          </button>
        </div>
      </div>

      {/* Celebratory Banner when 100% Completed */}
      {isComplete && (
        <div className="no-print bg-gradient-to-r from-emerald-600 via-teal-500 to-emerald-600 text-white px-6 py-2.5 text-xs font-medium flex items-center justify-between shadow-sm">
          <div className="flex items-center gap-2">
            <Sparkles className="h-4 w-4 animate-spin-slow text-emerald-100 flex-shrink-0" />
            <span>
              <strong>Draft Ready:</strong> All required interview questions are answered. Document is ready for review and signing.
            </span>
          </div>
          <div className="hidden sm:flex items-center gap-1 bg-white/20 backdrop-blur-xs px-2.5 py-0.5 rounded-full text-[11px] font-bold">
            <CheckCircle2 className="h-3 w-3" />
            <span>100% Validated</span>
          </div>
        </div>
      )}

      {/* Document Viewport Area */}
      <div className="flex-1 overflow-y-auto p-6 md:p-8 flex justify-center">
        <div className="w-full max-w-3xl">
          {viewMode === 'formatted' ? (
            <div
              className="legal-document"
              dangerouslySetInnerHTML={{ __html: html }}
            />
          ) : (
            <div className="bg-slate-950 text-slate-200 p-6 rounded-2xl font-mono text-xs whitespace-pre-wrap leading-relaxed shadow-paper-dark border border-slate-800 overflow-x-auto selection:bg-brand-800">
              {markdown}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
