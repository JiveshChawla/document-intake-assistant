import React from 'react';
import { Sparkles } from 'lucide-react';

interface SuggestedPromptsProps {
  onSelectPrompt: (prompt: string) => void;
  isLoading: boolean;
}

const SAMPLE_PROMPTS = [
  {
    label: '🚀 Multi-Field Intake',
    prompt: "I am Jane Doe living at 10 Downing St, London. I want worldwide coverage and I don't have children.",
    description: 'Provide 4 fields in a single sentence',
  },
  {
    label: '❓ Ambiguous Executor',
    prompt: 'I want to appoint my brother as executor.',
    description: 'Missing name; triggers smart follow-up',
  },
  {
    label: '✏️ Correction Test',
    prompt: 'Actually, change my executor to my sister Sarah Jenkins.',
    description: 'Updates executor without resetting state',
  },
  {
    label: '🎁 Specific Gift',
    prompt: 'I want to give my vintage gold pocket watch to my nephew Lucas.',
    description: 'Adds itemized bequest',
  },
  {
    label: '🕊️ Additional Wishes',
    prompt: 'I wish to be cremated and have my ashes scattered in the Lake District.',
    description: 'Adds personal funeral directives',
  },
];

export const SuggestedPrompts: React.FC<SuggestedPromptsProps> = ({
  onSelectPrompt,
  isLoading,
}) => {
  return (
    <div className="py-2.5">
      <div className="flex items-center gap-1.5 text-xs font-semibold text-slate-500 mb-2 px-1">
        <Sparkles className="h-3.5 w-3.5 text-amber-500" />
        <span>Quick Test Scenarios:</span>
      </div>
      <div className="flex flex-wrap gap-1.5">
        {SAMPLE_PROMPTS.map((sample, idx) => (
          <button
            key={idx}
            type="button"
            disabled={isLoading}
            onClick={() => onSelectPrompt(sample.prompt)}
            className="text-left text-xs bg-slate-100 hover:bg-brand-50 hover:text-brand-700 hover:border-brand-200 border border-slate-200 text-slate-700 rounded-lg px-2.5 py-1.5 transition-all disabled:opacity-50"
            title={sample.description}
          >
            <span className="font-medium">{sample.label}</span>
          </button>
        ))}
      </div>
    </div>
  );
};
