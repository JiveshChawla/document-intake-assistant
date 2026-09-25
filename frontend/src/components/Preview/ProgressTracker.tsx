import React, { useState } from 'react';
import {
  CheckCircle2,
  Clock,
  AlertCircle,
  HelpCircle,
  Edit2,
  Check,
  X,
  Plus,
  Trash2,
  Sparkles,
  Shield,
  UserCheck,
  Globe,
  Home,
  Users,
  Gift,
  HeartHandshake
} from 'lucide-react';
import { PersonalWishesState, GiftItem } from '../../types';

interface ProgressTrackerProps {
  state: PersonalWishesState;
  completionPercentage: number;
  onSaveState: (newState: PersonalWishesState) => Promise<void>;
}

export const ProgressTracker: React.FC<ProgressTrackerProps> = ({
  state,
  completionPercentage,
  onSaveState,
}) => {
  const [editingField, setEditingField] = useState<string | null>(null);
  const [isSaving, setIsSaving] = useState(false);
  const [saveError, setSaveError] = useState<string | null>(null);

  // Form draft states
  const [draftFullName, setDraftFullName] = useState(state.full_name || '');
  const [draftAddress, setDraftAddress] = useState(state.home_address || '');
  const [draftWorldwide, setDraftWorldwide] = useState<boolean | null>(state.covers_worldwide_assets);
  const [draftHasChildren, setDraftHasChildren] = useState<boolean | null>(state.has_children);
  const [draftChildren, setDraftChildren] = useState<string[]>(state.children || []);
  const [newChildName, setNewChildName] = useState('');
  const [draftExecName, setDraftExecName] = useState(state.executor?.name || '');
  const [draftExecRel, setDraftExecRel] = useState(state.executor?.relationship || '');
  const [draftGifts, setDraftGifts] = useState<GiftItem[]>(state.specific_gifts || []);
  const [newGiftItem, setNewGiftItem] = useState('');
  const [newGiftRecipient, setNewGiftRecipient] = useState('');
  const [draftWishes, setDraftWishes] = useState<string[]>(state.additional_wishes || []);
  const [newWishText, setNewWishText] = useState('');

  const isComplete = completionPercentage === 100;

  const startEditing = (fieldKey: string) => {
    setSaveError(null);
    setEditingField(fieldKey);
    if (fieldKey === 'full_name') setDraftFullName(state.full_name || '');
    if (fieldKey === 'home_address') setDraftAddress(state.home_address || '');
    if (fieldKey === 'worldwide') setDraftWorldwide(state.covers_worldwide_assets);
    if (fieldKey === 'children') {
      setDraftHasChildren(state.has_children);
      setDraftChildren(state.children ? [...state.children] : []);
      setNewChildName('');
    }
    if (fieldKey === 'executor') {
      setDraftExecName(state.executor?.name || '');
      setDraftExecRel(state.executor?.relationship || '');
    }
    if (fieldKey === 'gifts') {
      setDraftGifts(state.specific_gifts ? [...state.specific_gifts] : []);
      setNewGiftItem('');
      setNewGiftRecipient('');
    }
    if (fieldKey === 'wishes') {
      setDraftWishes(state.additional_wishes ? [...state.additional_wishes] : []);
      setNewWishText('');
    }
  };

  const cancelEditing = () => {
    setEditingField(null);
    setSaveError(null);
  };

  const handleSaveField = async (fieldKey: string) => {
    setIsSaving(true);
    setSaveError(null);
    try {
      const nextState: PersonalWishesState = { ...state };

      if (fieldKey === 'full_name') {
        nextState.full_name = draftFullName.trim() || null;
      } else if (fieldKey === 'home_address') {
        nextState.home_address = draftAddress.trim() || null;
      } else if (fieldKey === 'worldwide') {
        nextState.covers_worldwide_assets = draftWorldwide;
      } else if (fieldKey === 'children') {
        nextState.has_children = draftHasChildren;
        nextState.children = draftHasChildren ? draftChildren : [];
      } else if (fieldKey === 'executor') {
        if (!draftExecName.trim() && !draftExecRel.trim()) {
          nextState.executor = null;
        } else {
          nextState.executor = {
            name: draftExecName.trim() || null,
            relationship: draftExecRel.trim() || null,
          };
        }
      } else if (fieldKey === 'gifts') {
        nextState.specific_gifts = draftGifts;
      } else if (fieldKey === 'wishes') {
        nextState.additional_wishes = draftWishes;
      }

      await onSaveState(nextState);
      setEditingField(null);
    } catch (err: any) {
      setSaveError(err.message || 'Failed to save field');
    } finally {
      setIsSaving(false);
    }
  };

  const addChild = () => {
    if (newChildName.trim()) {
      setDraftChildren([...draftChildren, newChildName.trim()]);
      setNewChildName('');
    }
  };

  const removeChild = (index: number) => {
    setDraftChildren(draftChildren.filter((_, i) => i !== index));
  };

  const addGift = () => {
    if (newGiftItem.trim() && newGiftRecipient.trim()) {
      setDraftGifts([...draftGifts, { item: newGiftItem.trim(), recipient: newGiftRecipient.trim() }]);
      setNewGiftItem('');
      setNewGiftRecipient('');
    }
  };

  const removeGift = (index: number) => {
    setDraftGifts(draftGifts.filter((_, i) => i !== index));
  };

  const addWish = () => {
    if (newWishText.trim()) {
      setDraftWishes([...draftWishes, newWishText.trim()]);
      setNewWishText('');
    }
  };

  const removeWish = (index: number) => {
    setDraftWishes(draftWishes.filter((_, i) => i !== index));
  };

  return (
    <div className="h-full flex flex-col bg-slate-50/80 dark:bg-slate-950 overflow-y-auto transition-colors duration-200">
      {/* Top Banner / Progress Summary */}
      <div className="bg-gradient-to-b from-white to-slate-50/90 dark:from-slate-900 dark:to-slate-900/90 backdrop-blur-md border-b border-slate-200/80 dark:border-slate-800 p-6 sticky top-0 z-10 shadow-xs">
        <div className="flex items-center justify-between mb-3">
          <div>
            <h3 className="text-base font-bold text-slate-900 dark:text-white tracking-tight flex items-center gap-2">
              <span>Intake Completeness & Field Overrides</span>
              <span className="text-[11px] font-bold text-brand-700 dark:text-brand-300 bg-brand-50 dark:bg-brand-950/80 px-2.5 py-0.5 rounded-full border border-brand-200/80 dark:border-brand-800 shadow-2xs">
                5 Core Requirements
              </span>
            </h3>
            <p className="text-xs text-slate-500 dark:text-slate-400 mt-1">
              Review captured answers or click Edit to override any field directly. Live updates sync instantly.
            </p>
          </div>
          <div className="text-right">
            <span className="text-3xl font-black font-mono tracking-tight bg-gradient-to-r from-brand-600 via-indigo-600 to-violet-600 dark:from-brand-400 dark:via-indigo-400 dark:to-violet-400 bg-clip-text text-transparent drop-shadow-xs">
              {completionPercentage}%
            </span>
          </div>
        </div>

        {/* Vibrant Multi-Color Progress Bar */}
        <div className="w-full bg-slate-200/70 dark:bg-slate-800 rounded-full h-3 overflow-hidden shadow-inner p-0.5">
          <div
            className={`h-full transition-all duration-500 rounded-full ${
              isComplete
                ? 'bg-gradient-to-r from-emerald-500 via-teal-400 to-emerald-400 shadow-glow-emerald'
                : completionPercentage >= 50
                ? 'bg-gradient-to-r from-brand-600 via-indigo-600 to-violet-500 shadow-glow-brand'
                : 'bg-gradient-to-r from-amber-500 via-orange-500 to-amber-400'
            }`}
            style={{ width: `${completionPercentage}%` }}
          />
        </div>

        {/* Success Alert Banner if 100% */}
        {isComplete && (
          <div className="mt-4 p-3.5 rounded-2xl bg-gradient-to-r from-emerald-500/10 via-teal-500/10 to-emerald-500/10 border border-emerald-500/30 text-emerald-900 dark:text-emerald-200 text-xs flex items-center justify-between shadow-xs">
            <div className="flex items-center gap-2.5">
              <Sparkles className="h-4.5 w-4.5 text-emerald-600 dark:text-emerald-400 flex-shrink-0 animate-spin-slow" />
              <span className="font-bold text-sm">All 5 Core Legal Requirements Completed!</span>
            </div>
            <span className="text-emerald-800 dark:text-emerald-300 font-bold text-xs bg-emerald-100 dark:bg-emerald-950/80 px-3 py-1 rounded-full border border-emerald-300 dark:border-emerald-700 shadow-2xs">
              Ready to execute
            </span>
          </div>
        )}
      </div>

      {/* Save Error Alert */}
      {saveError && (
        <div className="m-6 mb-0 p-3.5 bg-red-50 dark:bg-red-950/60 border border-red-200 dark:border-red-800 rounded-2xl text-red-700 dark:text-red-300 text-xs flex items-center gap-2 shadow-xs">
          <AlertCircle className="h-4 w-4 flex-shrink-0" />
          <span className="font-medium">{saveError}</span>
        </div>
      )}

      {/* Field Cards Grid with Rich Color Accents & Left Border Highlights */}
      <div className="p-6 space-y-4 max-w-4xl mx-auto w-full">
        {/* 1. Full Name (Indigo Accent) */}
        <div className="bg-gradient-to-r from-indigo-50/60 via-white to-white dark:from-indigo-950/30 dark:via-slate-900 dark:to-slate-900 rounded-2xl border border-slate-200/90 dark:border-slate-800 border-l-4 border-l-indigo-500 dark:border-l-indigo-400 shadow-xs hover:shadow-md hover:border-indigo-400/50 dark:hover:border-indigo-500/50 transition-all duration-200 p-5">
          <div className="flex items-start justify-between gap-4">
            <div className="flex items-start gap-3.5">
              <div className="p-2.5 rounded-xl bg-indigo-100 dark:bg-indigo-950/80 text-indigo-700 dark:text-indigo-300 ring-1 ring-indigo-500/30 shadow-2xs mt-0.5">
                <UserCheck className="h-4 w-4" />
              </div>
              <div>
                <div className="flex items-center gap-2">
                  <h4 className="font-bold text-slate-900 dark:text-slate-100 text-sm">Principal Full Name</h4>
                  {state.full_name ? (
                    <span className="inline-flex items-center gap-1 text-[11px] font-bold text-emerald-800 dark:text-emerald-300 bg-emerald-500/10 dark:bg-emerald-950/80 border border-emerald-500/30 px-2.5 py-0.5 rounded-full shadow-2xs">
                      <CheckCircle2 className="h-3 w-3 text-emerald-600 dark:text-emerald-400" /> Captured
                    </span>
                  ) : (
                    <span className="inline-flex items-center gap-1 text-[11px] font-bold text-amber-800 dark:text-amber-300 bg-amber-500/10 dark:bg-amber-950/80 border border-amber-500/30 px-2.5 py-0.5 rounded-full shadow-2xs">
                      <Clock className="h-3 w-3 text-amber-600 dark:text-amber-400" /> Required
                    </span>
                  )}
                </div>
                <p className="text-xs text-slate-500 dark:text-slate-400 mt-0.5 flex items-center gap-1">
                  <span>The testator whose wishes and bequests are declared.</span>
                  <HelpCircle className="h-3 w-3 text-slate-400 dark:text-slate-500 cursor-help" />
                </p>
                {editingField !== 'full_name' && (
                  <p className="mt-2.5 text-sm font-bold text-slate-900 dark:text-slate-100 tracking-tight">
                    {state.full_name || <span className="text-slate-400 dark:text-slate-500 italic font-normal">Not specified yet</span>}
                  </p>
                )}
              </div>
            </div>

            {editingField !== 'full_name' && (
              <button
                onClick={() => startEditing('full_name')}
                className="flex items-center gap-1.5 px-3 py-1.5 rounded-xl text-xs font-bold text-indigo-700 dark:text-indigo-300 hover:text-indigo-900 dark:hover:text-white bg-indigo-50 dark:bg-indigo-950/70 hover:bg-indigo-100 dark:hover:bg-indigo-900 border border-indigo-200/80 dark:border-indigo-800 shadow-2xs hover:shadow-xs transition-all"
              >
                <Edit2 className="h-3 w-3" />
                <span>Edit</span>
              </button>
            )}
          </div>

          {/* Inline Edit Form */}
          {editingField === 'full_name' && (
            <div className="mt-4 pt-4 border-t border-slate-100 dark:border-slate-800">
              <label className="block text-xs font-bold text-slate-700 dark:text-slate-300 mb-1.5">
                Update Full Legal Name
              </label>
              <input
                type="text"
                value={draftFullName}
                onChange={(e) => setDraftFullName(e.target.value)}
                placeholder="e.g. Jane Margaret Doe"
                className="w-full px-3.5 py-2 text-sm bg-white dark:bg-slate-950 border border-slate-300 dark:border-slate-700 text-slate-900 dark:text-slate-100 rounded-xl focus:outline-none focus:ring-2 focus:ring-indigo-500/30 focus:border-indigo-500 mb-3 shadow-inner"
              />
              <div className="flex justify-end gap-2">
                <button
                  onClick={cancelEditing}
                  disabled={isSaving}
                  className="px-3.5 py-1.5 text-xs font-semibold text-slate-600 dark:text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-800 rounded-xl"
                >
                  Cancel
                </button>
                <button
                  onClick={() => handleSaveField('full_name')}
                  disabled={isSaving}
                  className="flex items-center gap-1.5 px-4 py-1.5 text-xs font-bold text-white bg-indigo-600 hover:bg-indigo-700 dark:bg-indigo-600 dark:hover:bg-indigo-500 rounded-xl shadow-xs transition-all"
                >
                  <Check className="h-3.5 w-3.5" />
                  <span>{isSaving ? 'Saving...' : 'Save'}</span>
                </button>
              </div>
            </div>
          )}
        </div>

        {/* 2. Home Address (Sky Accent) */}
        <div className="bg-gradient-to-r from-sky-50/60 via-white to-white dark:from-sky-950/30 dark:via-slate-900 dark:to-slate-900 rounded-2xl border border-slate-200/90 dark:border-slate-800 border-l-4 border-l-sky-500 dark:border-l-sky-400 shadow-xs hover:shadow-md hover:border-sky-400/50 dark:hover:border-sky-500/50 transition-all duration-200 p-5">
          <div className="flex items-start justify-between gap-4">
            <div className="flex items-start gap-3.5">
              <div className="p-2.5 rounded-xl bg-sky-100 dark:bg-sky-950/80 text-sky-700 dark:text-sky-300 ring-1 ring-sky-500/30 shadow-2xs mt-0.5">
                <Home className="h-4 w-4" />
              </div>
              <div>
                <div className="flex items-center gap-2">
                  <h4 className="font-bold text-slate-900 dark:text-slate-100 text-sm">Home Address</h4>
                  {state.home_address ? (
                    <span className="inline-flex items-center gap-1 text-[11px] font-bold text-emerald-800 dark:text-emerald-300 bg-emerald-500/10 dark:bg-emerald-950/80 border border-emerald-500/30 px-2.5 py-0.5 rounded-full shadow-2xs">
                      <CheckCircle2 className="h-3 w-3 text-emerald-600 dark:text-emerald-400" /> Captured
                    </span>
                  ) : (
                    <span className="inline-flex items-center gap-1 text-[11px] font-bold text-amber-800 dark:text-amber-300 bg-amber-500/10 dark:bg-amber-950/80 border border-amber-500/30 px-2.5 py-0.5 rounded-full shadow-2xs">
                      <Clock className="h-3 w-3 text-amber-600 dark:text-amber-400" /> Required
                    </span>
                  )}
                </div>
                <p className="text-xs text-slate-500 dark:text-slate-400 mt-0.5 flex items-center gap-1">
                  <span>Primary residential address establishing jurisdiction.</span>
                  <HelpCircle className="h-3 w-3 text-slate-400 dark:text-slate-500 cursor-help" />
                </p>
                {editingField !== 'home_address' && (
                  <p className="mt-2.5 text-sm font-bold text-slate-900 dark:text-slate-100 tracking-tight">
                    {state.home_address || <span className="text-slate-400 dark:text-slate-500 italic font-normal">Not specified yet</span>}
                  </p>
                )}
              </div>
            </div>

            {editingField !== 'home_address' && (
              <button
                onClick={() => startEditing('home_address')}
                className="flex items-center gap-1.5 px-3 py-1.5 rounded-xl text-xs font-bold text-sky-700 dark:text-sky-300 hover:text-sky-900 dark:hover:text-white bg-sky-50 dark:bg-sky-950/70 hover:bg-sky-100 dark:hover:bg-sky-900 border border-sky-200/80 dark:border-sky-800 shadow-2xs hover:shadow-xs transition-all"
              >
                <Edit2 className="h-3 w-3" />
                <span>Edit</span>
              </button>
            )}
          </div>

          {/* Inline Edit Form */}
          {editingField === 'home_address' && (
            <div className="mt-4 pt-4 border-t border-slate-100 dark:border-slate-800">
              <label className="block text-xs font-bold text-slate-700 dark:text-slate-300 mb-1.5">
                Update Residential Address
              </label>
              <textarea
                rows={2}
                value={draftAddress}
                onChange={(e) => setDraftAddress(e.target.value)}
                placeholder="e.g. 10 Downing Street, London SW1A 2AA, United Kingdom"
                className="w-full px-3.5 py-2 text-sm bg-white dark:bg-slate-950 border border-slate-300 dark:border-slate-700 text-slate-900 dark:text-slate-100 rounded-xl focus:outline-none focus:ring-2 focus:ring-sky-500/30 focus:border-sky-500 mb-3 shadow-inner"
              />
              <div className="flex justify-end gap-2">
                <button
                  onClick={cancelEditing}
                  disabled={isSaving}
                  className="px-3.5 py-1.5 text-xs font-semibold text-slate-600 dark:text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-800 rounded-xl"
                >
                  Cancel
                </button>
                <button
                  onClick={() => handleSaveField('home_address')}
                  disabled={isSaving}
                  className="flex items-center gap-1.5 px-4 py-1.5 text-xs font-bold text-white bg-sky-600 hover:bg-sky-700 dark:bg-sky-600 dark:hover:bg-sky-500 rounded-xl shadow-xs transition-all"
                >
                  <Check className="h-3.5 w-3.5" />
                  <span>{isSaving ? 'Saving...' : 'Save'}</span>
                </button>
              </div>
            </div>
          )}
        </div>

        {/* 3. Worldwide Asset Scope (Violet Accent) */}
        <div className="bg-gradient-to-r from-violet-50/60 via-white to-white dark:from-violet-950/30 dark:via-slate-900 dark:to-slate-900 rounded-2xl border border-slate-200/90 dark:border-slate-800 border-l-4 border-l-violet-500 dark:border-l-violet-400 shadow-xs hover:shadow-md hover:border-violet-400/50 dark:hover:border-violet-500/50 transition-all duration-200 p-5">
          <div className="flex items-start justify-between gap-4">
            <div className="flex items-start gap-3.5">
              <div className="p-2.5 rounded-xl bg-violet-100 dark:bg-violet-950/80 text-violet-700 dark:text-violet-300 ring-1 ring-violet-500/30 shadow-2xs mt-0.5">
                <Globe className="h-4 w-4" />
              </div>
              <div>
                <div className="flex items-center gap-2">
                  <h4 className="font-bold text-slate-900 dark:text-slate-100 text-sm">Asset Jurisdiction Scope</h4>
                  {state.covers_worldwide_assets !== null ? (
                    <span className="inline-flex items-center gap-1 text-[11px] font-bold text-emerald-800 dark:text-emerald-300 bg-emerald-500/10 dark:bg-emerald-950/80 border border-emerald-500/30 px-2.5 py-0.5 rounded-full shadow-2xs">
                      <CheckCircle2 className="h-3 w-3 text-emerald-600 dark:text-emerald-400" /> Captured
                    </span>
                  ) : (
                    <span className="inline-flex items-center gap-1 text-[11px] font-bold text-amber-800 dark:text-amber-300 bg-amber-500/10 dark:bg-amber-950/80 border border-amber-500/30 px-2.5 py-0.5 rounded-full shadow-2xs">
                      <Clock className="h-3 w-3 text-amber-600 dark:text-amber-400" /> Required
                    </span>
                  )}
                </div>
                <p className="text-xs text-slate-500 dark:text-slate-400 mt-0.5 flex items-center gap-1">
                  <span>Defines whether directives cover worldwide property or domestic assets only.</span>
                  <HelpCircle className="h-3 w-3 text-slate-400 dark:text-slate-500 cursor-help" />
                </p>
                {editingField !== 'worldwide' && (
                  <div className="mt-2.5">
                    {state.covers_worldwide_assets === true && (
                      <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-bold bg-violet-100 dark:bg-violet-950/80 text-violet-800 dark:text-violet-300 border border-violet-300 dark:border-violet-700 shadow-2xs">
                        <Globe className="h-3.5 w-3.5" /> Worldwide Assets Covered
                      </span>
                    )}
                    {state.covers_worldwide_assets === false && (
                      <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-bold bg-slate-100 dark:bg-slate-800 text-slate-700 dark:text-slate-300 border border-slate-300 dark:border-slate-700">
                        Domestic Jurisdiction Only
                      </span>
                    )}
                    {state.covers_worldwide_assets === null && (
                      <span className="text-slate-400 dark:text-slate-500 italic text-sm">Unconfirmed</span>
                    )}
                  </div>
                )}
              </div>
            </div>

            {editingField !== 'worldwide' && (
              <button
                onClick={() => startEditing('worldwide')}
                className="flex items-center gap-1.5 px-3 py-1.5 rounded-xl text-xs font-bold text-violet-700 dark:text-violet-300 hover:text-violet-900 dark:hover:text-white bg-violet-50 dark:bg-violet-950/70 hover:bg-violet-100 dark:hover:bg-violet-900 border border-violet-200/80 dark:border-violet-800 shadow-2xs hover:shadow-xs transition-all"
              >
                <Edit2 className="h-3 w-3" />
                <span>Edit</span>
              </button>
            )}
          </div>

          {/* Inline Edit Form */}
          {editingField === 'worldwide' && (
            <div className="mt-4 pt-4 border-t border-slate-100 dark:border-slate-800">
              <label className="block text-xs font-bold text-slate-700 dark:text-slate-300 mb-2">
                Select Scope of Assets
              </label>
              <div className="grid grid-cols-2 gap-3 mb-3">
                <button
                  type="button"
                  onClick={() => setDraftWorldwide(true)}
                  className={`p-3.5 rounded-xl border text-left text-xs font-medium transition-all ${
                    draftWorldwide === true
                      ? 'border-violet-600 dark:border-violet-500 bg-violet-50 dark:bg-violet-950/80 text-violet-950 dark:text-violet-200 ring-2 ring-violet-500/20 shadow-xs'
                      : 'border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-950 text-slate-700 dark:text-slate-300 hover:bg-slate-50 dark:hover:bg-slate-800'
                  }`}
                >
                  <div className="font-bold mb-0.5 text-slate-900 dark:text-slate-100">🌍 Worldwide Coverage</div>
                  <div className="text-[11px] text-slate-500 dark:text-slate-400">Includes all foreign and global assets</div>
                </button>
                <button
                  type="button"
                  onClick={() => setDraftWorldwide(false)}
                  className={`p-3.5 rounded-xl border text-left text-xs font-medium transition-all ${
                    draftWorldwide === false
                      ? 'border-violet-600 dark:border-violet-500 bg-violet-50 dark:bg-violet-950/80 text-violet-950 dark:text-violet-200 ring-2 ring-violet-500/20 shadow-xs'
                      : 'border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-950 text-slate-700 dark:text-slate-300 hover:bg-slate-50 dark:hover:bg-slate-800'
                  }`}
                >
                  <div className="font-bold mb-0.5 text-slate-900 dark:text-slate-100">🏠 Domestic Only</div>
                  <div className="text-[11px] text-slate-500 dark:text-slate-400">Excludes international assets</div>
                </button>
              </div>
              <div className="flex justify-end gap-2">
                <button
                  onClick={cancelEditing}
                  disabled={isSaving}
                  className="px-3.5 py-1.5 text-xs font-semibold text-slate-600 dark:text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-800 rounded-xl"
                >
                  Cancel
                </button>
                <button
                  onClick={() => handleSaveField('worldwide')}
                  disabled={isSaving}
                  className="flex items-center gap-1.5 px-4 py-1.5 text-xs font-bold text-white bg-violet-600 hover:bg-violet-700 dark:bg-violet-600 dark:hover:bg-violet-500 rounded-xl shadow-xs transition-all"
                >
                  <Check className="h-3.5 w-3.5" />
                  <span>{isSaving ? 'Saving...' : 'Save'}</span>
                </button>
              </div>
            </div>
          )}
        </div>

        {/* 4. Children Status (Emerald Accent) */}
        <div className="bg-gradient-to-r from-emerald-50/60 via-white to-white dark:from-emerald-950/30 dark:via-slate-900 dark:to-slate-900 rounded-2xl border border-slate-200/90 dark:border-slate-800 border-l-4 border-l-emerald-500 dark:border-l-emerald-400 shadow-xs hover:shadow-md hover:border-emerald-400/50 dark:hover:border-emerald-500/50 transition-all duration-200 p-5">
          <div className="flex items-start justify-between gap-4">
            <div className="flex items-start gap-3.5">
              <div className="p-2.5 rounded-xl bg-emerald-100 dark:bg-emerald-950/80 text-emerald-700 dark:text-emerald-300 ring-1 ring-emerald-500/30 shadow-2xs mt-0.5">
                <Users className="h-4 w-4" />
              </div>
              <div>
                <div className="flex items-center gap-2">
                  <h4 className="font-bold text-slate-900 dark:text-slate-100 text-sm">Children Details</h4>
                  {state.has_children === false || (state.has_children === true && state.children && state.children.length > 0) ? (
                    <span className="inline-flex items-center gap-1 text-[11px] font-bold text-emerald-800 dark:text-emerald-300 bg-emerald-500/10 dark:bg-emerald-950/80 border border-emerald-500/30 px-2.5 py-0.5 rounded-full shadow-2xs">
                      <CheckCircle2 className="h-3 w-3 text-emerald-600 dark:text-emerald-400" /> Captured
                    </span>
                  ) : state.has_children === true ? (
                    <span className="inline-flex items-center gap-1 text-[11px] font-bold text-amber-800 dark:text-amber-300 bg-amber-500/10 dark:bg-amber-950/80 border border-amber-500/30 px-2.5 py-0.5 rounded-full shadow-2xs">
                      <AlertCircle className="h-3 w-3 text-amber-600 dark:text-amber-400" /> Names Pending
                    </span>
                  ) : (
                    <span className="inline-flex items-center gap-1 text-[11px] font-bold text-amber-800 dark:text-amber-300 bg-amber-500/10 dark:bg-amber-950/80 border border-amber-500/30 px-2.5 py-0.5 rounded-full shadow-2xs">
                      <Clock className="h-3 w-3 text-amber-600 dark:text-amber-400" /> Required
                    </span>
                  )}
                </div>
                <p className="text-xs text-slate-500 dark:text-slate-400 mt-0.5 flex items-center gap-1">
                  <span>Crucial for estate clarity, statutory claims, and guardianship.</span>
                  <HelpCircle className="h-3 w-3 text-slate-400 dark:text-slate-500 cursor-help" />
                </p>
                {editingField !== 'children' && (
                  <div className="mt-2.5 text-sm font-bold text-slate-900 dark:text-slate-100 tracking-tight">
                    {state.has_children === false ? (
                      <span className="text-slate-600 dark:text-slate-400 font-semibold">No children</span>
                    ) : state.has_children === true ? (
                      state.children && state.children.length > 0 ? (
                        <div className="flex flex-wrap gap-1.5 mt-1">
                          {state.children.map((child, idx) => (
                            <span
                              key={idx}
                              className="px-2.5 py-0.5 rounded-lg bg-emerald-100 dark:bg-emerald-950/80 text-emerald-900 dark:text-emerald-200 border border-emerald-300 dark:border-emerald-700 text-xs font-bold shadow-2xs"
                            >
                              {child}
                            </span>
                          ))}
                        </div>
                      ) : (
                        <span className="text-amber-600 dark:text-amber-400 italic font-semibold">Has children (names pending)</span>
                      )
                    ) : (
                      <span className="text-slate-400 dark:text-slate-500 italic font-normal">Unconfirmed</span>
                    )}
                  </div>
                )}
              </div>
            </div>

            {editingField !== 'children' && (
              <button
                onClick={() => startEditing('children')}
                className="flex items-center gap-1.5 px-3 py-1.5 rounded-xl text-xs font-bold text-emerald-700 dark:text-emerald-300 hover:text-emerald-900 dark:hover:text-white bg-emerald-50 dark:bg-emerald-950/70 hover:bg-emerald-100 dark:hover:bg-emerald-900 border border-emerald-200/80 dark:border-emerald-800 shadow-2xs hover:shadow-xs transition-all"
              >
                <Edit2 className="h-3 w-3" />
                <span>Edit</span>
              </button>
            )}
          </div>

          {/* Inline Edit Form */}
          {editingField === 'children' && (
            <div className="mt-4 pt-4 border-t border-slate-100 dark:border-slate-800">
              <label className="block text-xs font-bold text-slate-700 dark:text-slate-300 mb-2">
                Do you have children?
              </label>
              <div className="flex gap-3 mb-4">
                <button
                  type="button"
                  onClick={() => setDraftHasChildren(true)}
                  className={`px-4 py-2 rounded-xl border text-xs font-bold transition-all ${
                    draftHasChildren === true
                      ? 'border-emerald-600 dark:border-emerald-500 bg-emerald-50 dark:bg-emerald-950/80 text-emerald-950 dark:text-emerald-200 shadow-xs'
                      : 'border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-950 text-slate-700 dark:text-slate-300'
                  }`}
                >
                  Yes, I have children
                </button>
                <button
                  type="button"
                  onClick={() => {
                    setDraftHasChildren(false);
                    setDraftChildren([]);
                  }}
                  className={`px-4 py-2 rounded-xl border text-xs font-bold transition-all ${
                    draftHasChildren === false
                      ? 'border-emerald-600 dark:border-emerald-500 bg-emerald-50 dark:bg-emerald-950/80 text-emerald-950 dark:text-emerald-200 shadow-xs'
                      : 'border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-950 text-slate-700 dark:text-slate-300'
                  }`}
                >
                  No children
                </button>
              </div>

              {draftHasChildren === true && (
                <div className="mb-4">
                  <label className="block text-xs font-bold text-slate-700 dark:text-slate-300 mb-1.5">
                    Children Names
                  </label>
                  <div className="flex gap-2 mb-2">
                    <input
                      type="text"
                      value={newChildName}
                      onChange={(e) => setNewChildName(e.target.value)}
                      onKeyDown={(e) => {
                        if (e.key === 'Enter') {
                          e.preventDefault();
                          addChild();
                        }
                      }}
                      placeholder="Enter child full name..."
                      className="flex-1 px-3.5 py-1.5 text-sm bg-white dark:bg-slate-950 border border-slate-300 dark:border-slate-700 text-slate-900 dark:text-slate-100 rounded-xl focus:outline-none focus:ring-2 focus:ring-emerald-500/30 focus:border-emerald-500 shadow-inner"
                    />
                    <button
                      type="button"
                      onClick={addChild}
                      className="px-3.5 py-1.5 bg-emerald-100 dark:bg-emerald-900 hover:bg-emerald-200 dark:hover:bg-emerald-800 text-emerald-900 dark:text-emerald-200 rounded-xl text-xs font-bold flex items-center gap-1 shadow-2xs"
                    >
                      <Plus className="h-3.5 w-3.5" />
                      <span>Add</span>
                    </button>
                  </div>

                  <div className="flex flex-wrap gap-1.5 mt-2">
                    {draftChildren.map((child, idx) => (
                      <span
                        key={idx}
                        className="inline-flex items-center gap-1.5 px-3 py-1 rounded-xl bg-emerald-100 dark:bg-emerald-950/80 text-emerald-900 dark:text-emerald-200 border border-emerald-300 dark:border-emerald-700 text-xs font-bold shadow-2xs"
                      >
                        <span>{child}</span>
                        <button
                          type="button"
                          onClick={() => removeChild(idx)}
                          className="text-slate-400 hover:text-red-600 dark:hover:text-red-400"
                        >
                          <X className="h-3 w-3" />
                        </button>
                      </span>
                    ))}
                  </div>
                </div>
              )}

              <div className="flex justify-end gap-2">
                <button
                  onClick={cancelEditing}
                  disabled={isSaving}
                  className="px-3.5 py-1.5 text-xs font-semibold text-slate-600 dark:text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-800 rounded-xl"
                >
                  Cancel
                </button>
                <button
                  onClick={() => handleSaveField('children')}
                  disabled={isSaving}
                  className="flex items-center gap-1.5 px-4 py-1.5 text-xs font-bold text-white bg-emerald-600 hover:bg-emerald-700 dark:bg-emerald-600 dark:hover:bg-emerald-500 rounded-xl shadow-xs transition-all"
                >
                  <Check className="h-3.5 w-3.5" />
                  <span>{isSaving ? 'Saving...' : 'Save'}</span>
                </button>
              </div>
            </div>
          )}
        </div>

        {/* 5. Executor & Fiduciary (Amber Accent) */}
        <div className="bg-gradient-to-r from-amber-50/60 via-white to-white dark:from-amber-950/30 dark:via-slate-900 dark:to-slate-900 rounded-2xl border border-slate-200/90 dark:border-slate-800 border-l-4 border-l-amber-500 dark:border-l-amber-400 shadow-xs hover:shadow-md hover:border-amber-400/50 dark:hover:border-amber-500/50 transition-all duration-200 p-5">
          <div className="flex items-start justify-between gap-4">
            <div className="flex items-start gap-3.5">
              <div className="p-2.5 rounded-xl bg-amber-100 dark:bg-amber-950/80 text-amber-700 dark:text-amber-300 ring-1 ring-amber-500/30 shadow-2xs mt-0.5">
                <Shield className="h-4 w-4" />
              </div>
              <div>
                <div className="flex items-center gap-2">
                  <h4 className="font-bold text-slate-900 dark:text-slate-100 text-sm">Appointed Executor</h4>
                  {state.executor?.name && state.executor?.relationship ? (
                    <span className="inline-flex items-center gap-1 text-[11px] font-bold text-emerald-800 dark:text-emerald-300 bg-emerald-500/10 dark:bg-emerald-950/80 border border-emerald-500/30 px-2.5 py-0.5 rounded-full shadow-2xs">
                      <CheckCircle2 className="h-3 w-3 text-emerald-600 dark:text-emerald-400" /> Captured
                    </span>
                  ) : state.executor?.name || state.executor?.relationship ? (
                    <span className="inline-flex items-center gap-1 text-[11px] font-bold text-amber-800 dark:text-amber-300 bg-amber-500/10 dark:bg-amber-950/80 border border-amber-500/30 px-2.5 py-0.5 rounded-full shadow-2xs">
                      <AlertCircle className="h-3 w-3 text-amber-600 dark:text-amber-400" /> Partial
                    </span>
                  ) : (
                    <span className="inline-flex items-center gap-1 text-[11px] font-bold text-amber-800 dark:text-amber-300 bg-amber-500/10 dark:bg-amber-950/80 border border-amber-500/30 px-2.5 py-0.5 rounded-full shadow-2xs">
                      <Clock className="h-3 w-3 text-amber-600 dark:text-amber-400" /> Required
                    </span>
                  )}
                </div>
                <p className="text-xs text-slate-500 dark:text-slate-400 mt-0.5 flex items-center gap-1">
                  <span>The legal fiduciary entrusted to distribute assets and carry out wishes.</span>
                  <HelpCircle className="h-3 w-3 text-slate-400 dark:text-slate-500 cursor-help" />
                </p>
                {editingField !== 'executor' && (
                  <div className="mt-2.5 text-sm font-bold text-slate-900 dark:text-slate-100 tracking-tight">
                    {state.executor?.name ? (
                      <div>
                        <span>{state.executor.name}</span>
                        {state.executor.relationship && (
                          <span className="text-brand-600 dark:text-brand-400 font-semibold ml-2">
                            ({state.executor.relationship})
                          </span>
                        )}
                      </div>
                    ) : (
                      <span className="text-slate-400 dark:text-slate-500 italic font-normal">Not appointed yet</span>
                    )}
                  </div>
                )}
              </div>
            </div>

            {editingField !== 'executor' && (
              <button
                onClick={() => startEditing('executor')}
                className="flex items-center gap-1.5 px-3 py-1.5 rounded-xl text-xs font-bold text-amber-700 dark:text-amber-300 hover:text-amber-900 dark:hover:text-white bg-amber-50 dark:bg-amber-950/70 hover:bg-amber-100 dark:hover:bg-amber-900 border border-amber-200/80 dark:border-amber-800 shadow-2xs hover:shadow-xs transition-all"
              >
                <Edit2 className="h-3 w-3" />
                <span>Edit</span>
              </button>
            )}
          </div>

          {/* Inline Edit Form */}
          {editingField === 'executor' && (
            <div className="mt-4 pt-4 border-t border-slate-100 dark:border-slate-800">
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 mb-3">
                <div>
                  <label className="block text-xs font-bold text-slate-700 dark:text-slate-300 mb-1.5">
                    Executor Full Name
                  </label>
                  <input
                    type="text"
                    value={draftExecName}
                    onChange={(e) => setDraftExecName(e.target.value)}
                    placeholder="e.g. Sarah Jenkins"
                    className="w-full px-3.5 py-2 text-sm bg-white dark:bg-slate-950 border border-slate-300 dark:border-slate-700 text-slate-900 dark:text-slate-100 rounded-xl focus:outline-none focus:ring-2 focus:ring-amber-500/30 focus:border-amber-500 shadow-inner"
                  />
                </div>
                <div>
                  <label className="block text-xs font-bold text-slate-700 dark:text-slate-300 mb-1.5">
                    Relationship to Principal
                  </label>
                  <input
                    type="text"
                    value={draftExecRel}
                    onChange={(e) => setDraftExecRel(e.target.value)}
                    placeholder="e.g. Sister, Trusted Friend, Solicitor"
                    className="w-full px-3.5 py-2 text-sm bg-white dark:bg-slate-950 border border-slate-300 dark:border-slate-700 text-slate-900 dark:text-slate-100 rounded-xl focus:outline-none focus:ring-2 focus:ring-amber-500/30 focus:border-amber-500 shadow-inner"
                  />
                </div>
              </div>
              <div className="flex justify-end gap-2">
                <button
                  onClick={cancelEditing}
                  disabled={isSaving}
                  className="px-3.5 py-1.5 text-xs font-semibold text-slate-600 dark:text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-800 rounded-xl"
                >
                  Cancel
                </button>
                <button
                  onClick={() => handleSaveField('executor')}
                  disabled={isSaving}
                  className="flex items-center gap-1.5 px-4 py-1.5 text-xs font-bold text-white bg-amber-600 hover:bg-amber-700 dark:bg-amber-600 dark:hover:bg-amber-500 rounded-xl shadow-xs transition-all"
                >
                  <Check className="h-3.5 w-3.5" />
                  <span>{isSaving ? 'Saving...' : 'Save'}</span>
                </button>
              </div>
            </div>
          )}
        </div>

        {/* 6. Specific Gifts & Bequests (Pink Accent) */}
        <div className="bg-gradient-to-r from-pink-50/60 via-white to-white dark:from-pink-950/30 dark:via-slate-900 dark:to-slate-900 rounded-2xl border border-slate-200/90 dark:border-slate-800 border-l-4 border-l-pink-500 dark:border-l-pink-400 shadow-xs hover:shadow-md hover:border-pink-400/50 dark:hover:border-pink-500/50 transition-all duration-200 p-5">
          <div className="flex items-start justify-between gap-4">
            <div className="flex items-start gap-3.5">
              <div className="p-2.5 rounded-xl bg-pink-100 dark:bg-pink-950/80 text-pink-700 dark:text-pink-300 ring-1 ring-pink-500/30 shadow-2xs mt-0.5">
                <Gift className="h-4 w-4" />
              </div>
              <div>
                <div className="flex items-center gap-2">
                  <h4 className="font-bold text-slate-900 dark:text-slate-100 text-sm">Specific Gifts & Bequests</h4>
                  <span className="inline-flex items-center text-[11px] font-bold text-pink-700 dark:text-pink-300 bg-pink-100 dark:bg-pink-950/80 border border-pink-200 dark:border-pink-800 px-2.5 py-0.5 rounded-full shadow-2xs">
                    Optional
                  </span>
                </div>
                <p className="text-xs text-slate-500 dark:text-slate-400 mt-0.5 flex items-center gap-1">
                  <span>Particular family heirlooms, jewelry, or cash designated for specific recipients.</span>
                  <HelpCircle className="h-3 w-3 text-slate-400 dark:text-slate-500 cursor-help" />
                </p>
                {editingField !== 'gifts' && (
                  <div className="mt-2.5">
                    {state.specific_gifts && state.specific_gifts.length > 0 ? (
                      <div className="space-y-1.5">
                        {state.specific_gifts.map((g, idx) => (
                          <div
                            key={idx}
                            className="text-xs bg-pink-50/80 dark:bg-slate-800/80 px-3.5 py-2 rounded-xl border border-pink-200/80 dark:border-slate-700 flex items-center justify-between shadow-2xs"
                          >
                            <span className="font-bold text-slate-900 dark:text-slate-100">{g.item}</span>
                            <span className="text-pink-700 dark:text-pink-400 font-semibold">to {g.recipient}</span>
                          </div>
                        ))}
                      </div>
                    ) : (
                      <span className="text-slate-400 dark:text-slate-500 italic text-sm">No specific gifts listed</span>
                    )}
                  </div>
                )}
              </div>
            </div>

            {editingField !== 'gifts' && (
              <button
                onClick={() => startEditing('gifts')}
                className="flex items-center gap-1.5 px-3 py-1.5 rounded-xl text-xs font-bold text-pink-700 dark:text-pink-300 hover:text-pink-900 dark:hover:text-white bg-pink-50 dark:bg-pink-950/70 hover:bg-pink-100 dark:hover:bg-pink-900 border border-pink-200/80 dark:border-pink-800 shadow-2xs hover:shadow-xs transition-all"
              >
                <Edit2 className="h-3 w-3" />
                <span>Manage</span>
              </button>
            )}
          </div>

          {/* Inline Edit Form */}
          {editingField === 'gifts' && (
            <div className="mt-4 pt-4 border-t border-slate-100 dark:border-slate-800">
              <label className="block text-xs font-bold text-slate-700 dark:text-slate-300 mb-2">
                Add a Specific Gift
              </label>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-2.5 mb-2.5">
                <input
                  type="text"
                  value={newGiftItem}
                  onChange={(e) => setNewGiftItem(e.target.value)}
                  placeholder="Item (e.g. Gold pocket watch)"
                  className="px-3.5 py-1.5 text-sm bg-white dark:bg-slate-950 border border-slate-300 dark:border-slate-700 text-slate-900 dark:text-slate-100 rounded-xl focus:outline-none focus:ring-2 focus:ring-pink-500/30 shadow-inner"
                />
                <input
                  type="text"
                  value={newGiftRecipient}
                  onChange={(e) => setNewGiftRecipient(e.target.value)}
                  placeholder="Recipient (e.g. Lucas Doe)"
                  className="px-3.5 py-1.5 text-sm bg-white dark:bg-slate-950 border border-slate-300 dark:border-slate-700 text-slate-900 dark:text-slate-100 rounded-xl focus:outline-none focus:ring-2 focus:ring-pink-500/30 shadow-inner"
                />
              </div>
              <button
                type="button"
                onClick={addGift}
                className="mb-4 px-3.5 py-1.5 bg-pink-100 dark:bg-pink-900 hover:bg-pink-200 dark:hover:bg-pink-800 text-pink-900 dark:text-pink-200 rounded-xl text-xs font-bold flex items-center gap-1 shadow-2xs"
              >
                <Plus className="h-3.5 w-3.5" />
                <span>Add Item to List</span>
              </button>

              {draftGifts.length > 0 && (
                <div className="space-y-1.5 mb-4">
                  {draftGifts.map((g, idx) => (
                    <div
                      key={idx}
                      className="p-2.5 rounded-xl bg-pink-50 dark:bg-slate-800/80 border border-pink-200 dark:border-slate-700 flex items-center justify-between text-xs"
                    >
                      <div>
                        <span className="font-bold text-slate-900 dark:text-slate-100">{g.item}</span>
                        <span className="text-pink-700 dark:text-pink-400 font-semibold ml-2">to {g.recipient}</span>
                      </div>
                      <button
                        type="button"
                        onClick={() => removeGift(idx)}
                        className="text-slate-400 hover:text-red-600 dark:hover:text-red-400 p-1"
                      >
                        <Trash2 className="h-3.5 w-3.5" />
                      </button>
                    </div>
                  ))}
                </div>
              )}

              <div className="flex justify-end gap-2">
                <button
                  onClick={cancelEditing}
                  disabled={isSaving}
                  className="px-3.5 py-1.5 text-xs font-semibold text-slate-600 dark:text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-800 rounded-xl"
                >
                  Cancel
                </button>
                <button
                  onClick={() => handleSaveField('gifts')}
                  disabled={isSaving}
                  className="flex items-center gap-1.5 px-4 py-1.5 text-xs font-bold text-white bg-pink-600 hover:bg-pink-700 dark:bg-pink-600 dark:hover:bg-pink-500 rounded-xl shadow-xs transition-all"
                >
                  <Check className="h-3.5 w-3.5" />
                  <span>{isSaving ? 'Saving...' : 'Save'}</span>
                </button>
              </div>
            </div>
          )}
        </div>

        {/* 7. Additional Wishes & Directives (Teal Accent) */}
        <div className="bg-gradient-to-r from-teal-50/60 via-white to-white dark:from-teal-950/30 dark:via-slate-900 dark:to-slate-900 rounded-2xl border border-slate-200/90 dark:border-slate-800 border-l-4 border-l-teal-500 dark:border-l-teal-400 shadow-xs hover:shadow-md hover:border-teal-400/50 dark:hover:border-teal-500/50 transition-all duration-200 p-5">
          <div className="flex items-start justify-between gap-4">
            <div className="flex items-start gap-3.5">
              <div className="p-2.5 rounded-xl bg-teal-100 dark:bg-teal-950/80 text-teal-700 dark:text-teal-300 ring-1 ring-teal-500/30 shadow-2xs mt-0.5">
                <HeartHandshake className="h-4 w-4" />
              </div>
              <div>
                <div className="flex items-center gap-2">
                  <h4 className="font-bold text-slate-900 dark:text-slate-100 text-sm">Additional Wishes & Directives</h4>
                  <span className="inline-flex items-center text-[11px] font-bold text-teal-700 dark:text-teal-300 bg-teal-100 dark:bg-teal-950/80 border border-teal-200 dark:border-teal-800 px-2.5 py-0.5 rounded-full shadow-2xs">
                    Optional
                  </span>
                </div>
                <p className="text-xs text-slate-500 dark:text-slate-400 mt-0.5 flex items-center gap-1">
                  <span>Funeral instructions, memorial preferences, religious rites, or personal notes.</span>
                  <HelpCircle className="h-3 w-3 text-slate-400 dark:text-slate-500 cursor-help" />
                </p>
                {editingField !== 'wishes' && (
                  <div className="mt-2.5">
                    {state.additional_wishes && state.additional_wishes.length > 0 ? (
                      <ul className="list-disc pl-4 text-xs font-semibold text-slate-800 dark:text-slate-200 space-y-1">
                        {state.additional_wishes.map((w, idx) => (
                          <li key={idx}>{w}</li>
                        ))}
                      </ul>
                    ) : (
                      <span className="text-slate-400 dark:text-slate-500 italic text-sm">No additional directives entered</span>
                    )}
                  </div>
                )}
              </div>
            </div>

            {editingField !== 'wishes' && (
              <button
                onClick={() => startEditing('wishes')}
                className="flex items-center gap-1.5 px-3 py-1.5 rounded-xl text-xs font-bold text-teal-700 dark:text-teal-300 hover:text-teal-900 dark:hover:text-white bg-teal-50 dark:bg-teal-950/70 hover:bg-teal-100 dark:hover:bg-teal-900 border border-teal-200/80 dark:border-teal-800 shadow-2xs hover:shadow-xs transition-all"
              >
                <Edit2 className="h-3 w-3" />
                <span>Manage</span>
              </button>
            )}
          </div>

          {/* Inline Edit Form */}
          {editingField === 'wishes' && (
            <div className="mt-4 pt-4 border-t border-slate-100 dark:border-slate-800">
              <label className="block text-xs font-bold text-slate-700 dark:text-slate-300 mb-1.5">
                Add a Directive or Wish
              </label>
              <div className="flex gap-2 mb-3">
                <input
                  type="text"
                  value={newWishText}
                  onChange={(e) => setNewWishText(e.target.value)}
                  placeholder="e.g. I wish to be cremated and scattered in the Lake District"
                  className="flex-1 px-3.5 py-1.5 text-sm bg-white dark:bg-slate-950 border border-slate-300 dark:border-slate-700 text-slate-900 dark:text-slate-100 rounded-xl focus:outline-none focus:ring-2 focus:ring-teal-500/30 shadow-inner"
                />
                <button
                  type="button"
                  onClick={addWish}
                  className="px-3.5 py-1.5 bg-teal-100 dark:bg-teal-900 hover:bg-teal-200 dark:hover:bg-teal-800 text-teal-900 dark:text-teal-200 rounded-xl text-xs font-bold flex items-center gap-1 shadow-2xs"
                >
                  <Plus className="h-3.5 w-3.5" />
                  <span>Add</span>
                </button>
              </div>

              {draftWishes.length > 0 && (
                <div className="space-y-1.5 mb-4">
                  {draftWishes.map((w, idx) => (
                    <div
                      key={idx}
                      className="p-2.5 rounded-xl bg-teal-50 dark:bg-slate-800/80 border border-teal-200 dark:border-slate-700 flex items-center justify-between text-xs"
                    >
                      <span className="font-semibold text-slate-800 dark:text-slate-200">{w}</span>
                      <button
                        type="button"
                        onClick={() => removeWish(idx)}
                        className="text-slate-400 hover:text-red-600 dark:hover:text-red-400 p-1"
                      >
                        <Trash2 className="h-3.5 w-3.5" />
                      </button>
                    </div>
                  ))}
                </div>
              )}

              <div className="flex justify-end gap-2">
                <button
                  onClick={cancelEditing}
                  disabled={isSaving}
                  className="px-3.5 py-1.5 text-xs font-semibold text-slate-600 dark:text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-800 rounded-xl"
                >
                  Cancel
                </button>
                <button
                  onClick={() => handleSaveField('wishes')}
                  disabled={isSaving}
                  className="flex items-center gap-1.5 px-4 py-1.5 text-xs font-bold text-white bg-teal-600 hover:bg-teal-700 dark:bg-teal-600 dark:hover:bg-teal-500 rounded-xl shadow-xs transition-all"
                >
                  <Check className="h-3.5 w-3.5" />
                  <span>{isSaving ? 'Saving...' : 'Save'}</span>
                </button>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
