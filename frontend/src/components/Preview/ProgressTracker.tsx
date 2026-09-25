import React from 'react';
import { Check, Clock, AlertCircle } from 'lucide-react';
import { PersonalWishesState } from '../../types';

interface ProgressTrackerProps {
  state: PersonalWishesState;
  completionPercentage: number;
}

export const ProgressTracker: React.FC<ProgressTrackerProps> = ({
  state,
  completionPercentage,
}) => {
  const fields = [
    {
      label: 'Full Name',
      value: state.full_name,
      status: state.full_name ? 'complete' : 'pending',
      summary: state.full_name || 'Not provided',
    },
    {
      label: 'Home Address',
      value: state.home_address,
      status: state.home_address ? 'complete' : 'pending',
      summary: state.home_address || 'Not provided',
    },
    {
      label: 'Asset Scope',
      value: state.covers_worldwide_assets,
      status: state.covers_worldwide_assets !== null ? 'complete' : 'pending',
      summary:
        state.covers_worldwide_assets === true
          ? 'Worldwide'
          : state.covers_worldwide_assets === false
          ? 'Domestic only'
          : 'Unconfirmed',
    },
    {
      label: 'Children Status',
      value: state.has_children,
      status:
        state.has_children === false ||
        (state.has_children === true && state.children && state.children.length > 0)
          ? 'complete'
          : state.has_children === true
          ? 'partial'
          : 'pending',
      summary:
        state.has_children === false
          ? 'None'
          : state.children && state.children.length > 0
          ? `${state.children.length} listed (${state.children.join(', ')})`
          : state.has_children === true
          ? 'Has children (names pending)'
          : 'Unconfirmed',
    },
    {
      label: 'Executor',
      value: state.executor,
      status:
        state.executor?.name && state.executor?.relationship
          ? 'complete'
          : state.executor?.name || state.executor?.relationship
          ? 'partial'
          : 'pending',
      summary:
        state.executor?.name && state.executor?.relationship
          ? `${state.executor.name} (${state.executor.relationship})`
          : state.executor?.name
          ? `${state.executor.name} (relationship pending)`
          : state.executor?.relationship
          ? `${state.executor.relationship} (name pending)`
          : 'Not appointed',
    },
    {
      label: 'Specific Gifts',
      value: state.specific_gifts,
      status: state.specific_gifts && state.specific_gifts.length > 0 ? 'complete' : 'optional',
      summary:
        state.specific_gifts && state.specific_gifts.length > 0
          ? `${state.specific_gifts.length} gift(s) designated`
          : 'Optional / None yet',
    },
    {
      label: 'Additional Wishes',
      value: state.additional_wishes,
      status:
        state.additional_wishes && state.additional_wishes.length > 0 ? 'complete' : 'optional',
      summary:
        state.additional_wishes && state.additional_wishes.length > 0
          ? `${state.additional_wishes.length} directive(s)`
          : 'Optional / None yet',
    },
  ];

  return (
    <div className="bg-white border-b border-slate-200 p-4">
      {/* Percentage Bar */}
      <div className="flex items-center justify-between text-xs mb-2">
        <span className="font-semibold text-slate-700">Document Intake Completeness</span>
        <span className="font-mono font-bold text-brand-600">{completionPercentage}%</span>
      </div>
      <div className="w-full bg-slate-100 rounded-full h-2 mb-3 overflow-hidden">
        <div
          className={`h-full transition-all duration-500 rounded-full ${
            completionPercentage === 100
              ? 'bg-emerald-500'
              : completionPercentage > 50
              ? 'bg-brand-600'
              : 'bg-amber-500'
          }`}
          style={{ width: `${completionPercentage}%` }}
        />
      </div>

      {/* Field Pills Grid */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-2">
        {fields.map((f, i) => (
          <div
            key={i}
            className={`p-2 rounded-lg border text-xs flex flex-col justify-between ${
              f.status === 'complete'
                ? 'bg-emerald-50/60 border-emerald-200 text-emerald-950'
                : f.status === 'partial'
                ? 'bg-amber-50 border-amber-200 text-amber-950'
                : f.status === 'optional'
                ? 'bg-slate-50 border-slate-200 text-slate-600'
                : 'bg-white border-slate-200 text-slate-500'
            }`}
          >
            <div className="flex items-center justify-between font-semibold mb-1">
              <span className="truncate">{f.label}</span>
              {f.status === 'complete' ? (
                <Check className="h-3 w-3 text-emerald-600 flex-shrink-0" />
              ) : f.status === 'partial' ? (
                <AlertCircle className="h-3 w-3 text-amber-600 flex-shrink-0" />
              ) : (
                <Clock className="h-3 w-3 text-slate-400 flex-shrink-0" />
              )}
            </div>
            <span className="text-[11px] truncate text-slate-600" title={f.summary}>
              {f.summary}
            </span>
          </div>
        ))}
      </div>
    </div>
  );
};
