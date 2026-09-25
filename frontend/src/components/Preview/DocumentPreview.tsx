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
    <div className="flex flex-col h-full bg-slate-100/70 overflow-hidden">
      {/* Action Toolbar */}
      <div className="px-6 py-2.5 bg-white border-b border-slate-200/80 flex flex-wrap items-center justify-between gap-3 no-print shadow-xs z-10">
        {/* Toggle Mode */}
        <div className="flex items-center gap-1 bg-slate-100 p-1 rounded-xl border border-slate-200/80 text-xs">
          <button
            onClick={() => setViewMode('formatted')}
            className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg font-medium transition-all ${
              viewMode === 'formatted'
                ? 'bg-white text-slate-900 shadow-xs'
                : 'text-slate-500 hover:text-slate-900'
            }`}
          >
            <FileText className="h-3.5 w-3.5" />
            <span>Legal Paper View</span>
          </button>
          <button
            onClick={() => setViewMode('markdown')}
            className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg font-medium transition-all ${
              viewMode === 'markdown'
                ? 'bg-white text-slate-900 shadow-xs'
                : 'text-slate-500 hover:text-slate-900'
            }`}
          >
            <FileCode className="h-3.5 w-3.5" />
            <span>Markdown Source</span>
          </button>
        </div>

        {/* Export / Copy Tools */}
        <div className="flex items-center gap-2 text-xs">
          <button
            onClick={handleCopy}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg border border-slate-200 bg-white text-slate-700 hover:bg-slate-50 shadow-2xs transition-colors"
            title="Copy draft markdown to clipboard"
          >
            {copied ? (
              <>
                <Check className="h-3.5 w-3.5 text-emerald-600" />
                <span className="text-emerald-700 font-semibold">Copied!</span>
              </>
            ) : (
              <>
                <Copy className="h-3.5 w-3.5 text-slate-500" />
                <span>Copy Draft</span>
              </>
            )}
          </button>

          <button
            onClick={handlePrint}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-slate-900 text-white hover:bg-brand-600 shadow-xs transition-colors"
            title="Print or export as PDF"
          >
            <Printer className="h-3.5 w-3.5" />
            <span>Print / PDF</span>
          </button>
        </div>
      </div>

      {/* Celebratory Banner when 100% Completed */}
      {isComplete && (
        <div className="no-print bg-gradient-to-r from-emerald-500 via-teal-500 to-emerald-600 text-white px-6 py-2.5 text-xs font-medium flex items-center justify-between shadow-sm">
          <div className="flex items-center gap-2">
            <Sparkles className="h-4 w-4 animate-spin-slow text-emerald-100 flex-shrink-0" />
            <span>
              <strong>Draft Ready:</strong> All required interview questions are answered. Document is ready for review and signing.
            </span>
          </div>
          <div className="hidden sm:flex items-center gap-1 bg-white/20 backdrop-blur-xs px-2.5 py-0.5 rounded-full text-[11px] font-semibold">
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
            <div className="bg-slate-950 text-slate-200 p-6 rounded-2xl font-mono text-xs whitespace-pre-wrap leading-relaxed shadow-paper border border-slate-800 overflow-x-auto">
              {markdown}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
