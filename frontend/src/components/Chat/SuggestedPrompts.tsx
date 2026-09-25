import React, { useState } from 'react';
import { Sparkles, ChevronDown, ChevronUp } from 'lucide-react';

interface SuggestedPromptsProps {
  onSelectPrompt: (prompt: string) => void;
  isLoading: boolean;
}

const SAMPLE_PROMPTS = [
  {
    label: 'Multi-Field Intake',
    prompt: "I am Jane Doe living at 10 Downing St, London. I want worldwide coverage and I don't have children.",
    badge: '4 fields',
  },
  {
    label: 'Executor Details',
    prompt: 'I want to appoint my sister Sarah Jenkins as my executor.',
    badge: 'Name & relation',
  },
  {
    label: 'Specific Gift',
    prompt: 'I want to give my vintage gold pocket watch to my nephew Lucas.',
    badge: 'Bequest',
  },
  {
    label: 'Additional Wishes',
    prompt: 'I wish to be cremated and have my ashes scattered in the Lake District.',
    badge: 'Directives',
  },
];

export const SuggestedPrompts: React.FC<SuggestedPromptsProps> = ({
  onSelectPrompt,
  isLoading,
}) => {
  const [isExpanded, setIsExpanded] = useState(false);

  return (
    <div className="mb-2">
      <div className="flex items-center justify-between mb-1.5 px-0.5">
        <button
          type="button"
          onClick={() => setIsExpanded(!isExpanded)}
          className="flex items-center gap-1.5 text-[11px] font-semibold text-slate-500 dark:text-slate-400 hover:text-slate-800 dark:hover:text-slate-200 transition-colors"
        >
          <Sparkles className="h-3 w-3 text-amber-500" />
          <span>Quick Test Prompts</span>
          {isExpanded ? (
            <ChevronUp className="h-3 w-3 text-slate-400 dark:text-slate-500" />
          ) : (
            <ChevronDown className="h-3 w-3 text-slate-400 dark:text-slate-500" />
          )}
        </button>
      </div>

      {isExpanded && (
        <div className="flex flex-wrap gap-1.5 pt-1 pb-2">
          {SAMPLE_PROMPTS.map((sample, idx) => (
            <button
              key={idx}
              type="button"
              disabled={isLoading}
              onClick={() => onSelectPrompt(sample.prompt)}
              className="group text-left text-xs bg-slate-50 dark:bg-slate-800/80 hover:bg-white dark:hover:bg-slate-800 hover:border-brand-400 dark:hover:border-brand-500 border border-slate-200/80 dark:border-slate-700 text-slate-700 dark:text-slate-300 rounded-xl px-2.5 py-1.5 transition-all shadow-2xs hover:shadow-xs disabled:opacity-40"
              title={sample.prompt}
            >
              <div className="flex items-center gap-1.5">
                <span className="font-semibold text-slate-800 dark:text-slate-200 group-hover:text-brand-600 dark:group-hover:text-brand-400">
                  {sample.label}
                </span>
                <span className="text-[10px] text-slate-400 dark:text-slate-500 group-hover:text-brand-500 font-mono">
                  ({sample.badge})
                </span>
              </div>
            </button>
          ))}
        </div>
      )}
    </div>
  );
};
