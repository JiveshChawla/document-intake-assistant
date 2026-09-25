import React, { useState } from 'react';
import { Copy, Printer, Check, FileCode, FileText } from 'lucide-react';

interface DocumentPreviewProps {
  html: string;
  markdown: string;
}

export const DocumentPreview: React.FC<DocumentPreviewProps> = ({ html, markdown }) => {
  const [viewMode, setViewMode] = useState<'formatted' | 'markdown'>('formatted');
  const [copied, setCopied] = useState(false);

  const handleCopy = () => {
    navigator.clipboard.writeText(markdown);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const handlePrint = () => {
    window.print();
  };

  return (
    <div className="flex flex-col h-full bg-slate-100">
      {/* Action Toolbar */}
      <div className="px-5 py-2.5 bg-white border-b border-slate-200 flex items-center justify-between no-print">
        {/* Toggle Mode */}
        <div className="flex items-center gap-1 bg-slate-100 p-1 rounded-lg border border-slate-200 text-xs">
          <button
            onClick={() => setViewMode('formatted')}
            className={`flex items-center gap-1.5 px-2.5 py-1 rounded-md font-medium transition-all ${
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
            className={`flex items-center gap-1.5 px-2.5 py-1 rounded-md font-medium transition-all ${
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
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-md border border-slate-300 bg-white text-slate-700 hover:bg-slate-50 transition-colors"
            title="Copy Markdown text"
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
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-md bg-slate-900 text-white hover:bg-slate-800 transition-colors"
            title="Print or save as PDF"
          >
            <Printer className="h-3.5 w-3.5" />
            <span>Print / PDF</span>
          </button>
        </div>
      </div>

      {/* Content Area */}
      <div className="flex-1 overflow-y-auto p-6 flex justify-center">
        <div className="w-full max-w-3xl">
          {viewMode === 'formatted' ? (
            <div
              className="legal-document-container"
              dangerouslySetInnerHTML={{ __html: html }}
            />
          ) : (
            <div className="bg-slate-900 text-slate-100 p-6 rounded-lg font-mono text-xs whitespace-pre-wrap leading-relaxed shadow-sm border border-slate-800 overflow-x-auto">
              {markdown}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
