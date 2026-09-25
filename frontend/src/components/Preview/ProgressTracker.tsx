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
    // sync drafts with current state
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
    <div className="h-full flex flex-col bg-slate-50/50 overflow-y-auto">
      {/* Top Banner / Progress Summary */}
      <div className="bg-white border-b border-slate-200/80 p-6 sticky top-0 z-10 shadow-xs">
        <div className="flex items-center justify-between mb-2.5">
          <div>
            <h3 className="text-sm font-semibold text-slate-900 tracking-tight">
              Intake Completeness & Field Overrides
            </h3>
            <p className="text-xs text-slate-500 mt-0.5">
              Review captured legal state or directly override any item. All changes synchronize immediately.
            </p>
          </div>
          <div className="text-right">
            <span className="text-xl font-bold font-mono tracking-tight text-slate-900">
              {completionPercentage}%
            </span>
          </div>
        </div>

        {/* Progress Bar */}
        <div className="w-full bg-slate-100 rounded-full h-2.5 overflow-hidden">
          <div
            className={`h-full transition-all duration-500 rounded-full ${
              isComplete
                ? 'bg-emerald-500 shadow-glow-emerald'
                : completionPercentage >= 50
                ? 'bg-brand-600'
                : 'bg-amber-500'
            }`}
            style={{ width: `${completionPercentage}%` }}
          />
        </div>

        {/* Success Alert Banner if 100% */}
        {isComplete && (
          <div className="mt-4 p-3 rounded-xl bg-emerald-50 border border-emerald-200 text-emerald-800 text-xs flex items-center justify-between shadow-2xs">
            <div className="flex items-center gap-2">
              <Sparkles className="h-4 w-4 text-emerald-600 flex-shrink-0" />
              <span className="font-semibold">All 5 Core Legal Requirements Completed!</span>
            </div>
            <span className="text-emerald-700 font-medium text-[11px]">Ready to execute</span>
          </div>
        )}
      </div>

      {/* Save Error Alert */}
      {saveError && (
        <div className="m-6 mb-0 p-3 bg-red-50 border border-red-200 rounded-xl text-red-700 text-xs flex items-center gap-2">
          <AlertCircle className="h-4 w-4 flex-shrink-0" />
          <span>{saveError}</span>
        </div>
      )}

      {/* Field Cards Grid */}
      <div className="p-6 space-y-4 max-w-4xl mx-auto w-full">
        {/* 1. Full Name */}
        <div className="bg-white rounded-2xl border border-slate-200/90 shadow-xs p-5 transition-all">
          <div className="flex items-start justify-between gap-4">
            <div className="flex items-start gap-3">
              <div className="p-2 rounded-xl bg-slate-100 text-slate-700 mt-0.5">
                <UserCheck className="h-4 w-4" />
              </div>
              <div>
                <div className="flex items-center gap-2">
                  <h4 className="font-semibold text-slate-900 text-sm">Principal Full Name</h4>
                  {state.full_name ? (
                    <span className="inline-flex items-center gap-1 text-[11px] font-medium text-emerald-700 bg-emerald-50 border border-emerald-200/70 px-2 py-0.5 rounded-full">
                      <CheckCircle2 className="h-3 w-3" /> Captured
                    </span>
                  ) : (
                    <span className="inline-flex items-center gap-1 text-[11px] font-medium text-amber-700 bg-amber-50 border border-amber-200/70 px-2 py-0.5 rounded-full">
                      <Clock className="h-3 w-3" /> Required
                    </span>
                  )}
                </div>
                <div className="group relative inline-block mt-0.5">
                  <p className="text-xs text-slate-500 flex items-center gap-1">
                    <span>The testator whose wishes and bequests are declared.</span>
                    <HelpCircle className="h-3 w-3 text-slate-400 cursor-help" />
                  </p>
                </div>
                {editingField !== 'full_name' && (
                  <p className="mt-2 text-sm font-medium text-slate-800">
                    {state.full_name || <span className="text-slate-400 italic">Not specified yet</span>}
                  </p>
                )}
              </div>
            </div>

            {editingField !== 'full_name' && (
              <button
                onClick={() => startEditing('full_name')}
                className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium text-slate-600 hover:text-slate-900 hover:bg-slate-100 border border-slate-200 transition-colors"
              >
                <Edit2 className="h-3 w-3" />
                <span>Edit</span>
              </button>
            )}
          </div>

          {/* Inline Edit Form */}
          {editingField === 'full_name' && (
            <div className="mt-4 pt-4 border-t border-slate-100">
              <label className="block text-xs font-semibold text-slate-700 mb-1.5">
                Update Full Legal Name
              </label>
              <input
                type="text"
                value={draftFullName}
                onChange={(e) => setDraftFullName(e.target.value)}
                placeholder="e.g. Jane Margaret Doe"
                className="w-full px-3 py-2 text-sm border border-slate-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-brand-500/20 focus:border-brand-500 mb-3"
              />
              <div className="flex justify-end gap-2">
                <button
                  onClick={cancelEditing}
                  disabled={isSaving}
                  className="px-3 py-1.5 text-xs font-medium text-slate-600 hover:bg-slate-100 rounded-lg"
                >
                  Cancel
                </button>
                <button
                  onClick={() => handleSaveField('full_name')}
                  disabled={isSaving}
                  className="flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium text-white bg-slate-900 hover:bg-brand-600 rounded-lg shadow-xs transition-colors"
                >
                  <Check className="h-3.5 w-3.5" />
                  <span>{isSaving ? 'Saving...' : 'Save'}</span>
                </button>
              </div>
            </div>
          )}
        </div>

        {/* 2. Home Address */}
        <div className="bg-white rounded-2xl border border-slate-200/90 shadow-xs p-5 transition-all">
          <div className="flex items-start justify-between gap-4">
            <div className="flex items-start gap-3">
              <div className="p-2 rounded-xl bg-slate-100 text-slate-700 mt-0.5">
                <Home className="h-4 w-4" />
              </div>
              <div>
                <div className="flex items-center gap-2">
                  <h4 className="font-semibold text-slate-900 text-sm">Home Address</h4>
                  {state.home_address ? (
                    <span className="inline-flex items-center gap-1 text-[11px] font-medium text-emerald-700 bg-emerald-50 border border-emerald-200/70 px-2 py-0.5 rounded-full">
                      <CheckCircle2 className="h-3 w-3" /> Captured
                    </span>
                  ) : (
                    <span className="inline-flex items-center gap-1 text-[11px] font-medium text-amber-700 bg-amber-50 border border-amber-200/70 px-2 py-0.5 rounded-full">
                      <Clock className="h-3 w-3" /> Required
                    </span>
                  )}
                </div>
                <p className="text-xs text-slate-500 mt-0.5 flex items-center gap-1">
                  <span>Primary residential address establishing jurisdiction.</span>
                  <HelpCircle className="h-3 w-3 text-slate-400 cursor-help" />
                </p>
                {editingField !== 'home_address' && (
                  <p className="mt-2 text-sm font-medium text-slate-800">
                    {state.home_address || <span className="text-slate-400 italic">Not specified yet</span>}
                  </p>
                )}
              </div>
            </div>

            {editingField !== 'home_address' && (
              <button
                onClick={() => startEditing('home_address')}
                className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium text-slate-600 hover:text-slate-900 hover:bg-slate-100 border border-slate-200 transition-colors"
              >
                <Edit2 className="h-3 w-3" />
                <span>Edit</span>
              </button>
            )}
          </div>

          {/* Inline Edit Form */}
          {editingField === 'home_address' && (
            <div className="mt-4 pt-4 border-t border-slate-100">
              <label className="block text-xs font-semibold text-slate-700 mb-1.5">
                Update Residential Address
              </label>
              <textarea
                rows={2}
                value={draftAddress}
                onChange={(e) => setDraftAddress(e.target.value)}
                placeholder="e.g. 10 Downing Street, London SW1A 2AA, United Kingdom"
                className="w-full px-3 py-2 text-sm border border-slate-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-brand-500/20 focus:border-brand-500 mb-3"
              />
              <div className="flex justify-end gap-2">
                <button
                  onClick={cancelEditing}
                  disabled={isSaving}
                  className="px-3 py-1.5 text-xs font-medium text-slate-600 hover:bg-slate-100 rounded-lg"
                >
                  Cancel
                </button>
                <button
                  onClick={() => handleSaveField('home_address')}
                  disabled={isSaving}
                  className="flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium text-white bg-slate-900 hover:bg-brand-600 rounded-lg shadow-xs transition-colors"
                >
                  <Check className="h-3.5 w-3.5" />
                  <span>{isSaving ? 'Saving...' : 'Save'}</span>
                </button>
              </div>
            </div>
          )}
        </div>

        {/* 3. Worldwide Asset Scope */}
        <div className="bg-white rounded-2xl border border-slate-200/90 shadow-xs p-5 transition-all">
          <div className="flex items-start justify-between gap-4">
            <div className="flex items-start gap-3">
              <div className="p-2 rounded-xl bg-slate-100 text-slate-700 mt-0.5">
                <Globe className="h-4 w-4" />
              </div>
              <div>
                <div className="flex items-center gap-2">
                  <h4 className="font-semibold text-slate-900 text-sm">Asset Jurisdiction Scope</h4>
                  {state.covers_worldwide_assets !== null ? (
                    <span className="inline-flex items-center gap-1 text-[11px] font-medium text-emerald-700 bg-emerald-50 border border-emerald-200/70 px-2 py-0.5 rounded-full">
                      <CheckCircle2 className="h-3 w-3" /> Captured
                    </span>
                  ) : (
                    <span className="inline-flex items-center gap-1 text-[11px] font-medium text-amber-700 bg-amber-50 border border-amber-200/70 px-2 py-0.5 rounded-full">
                      <Clock className="h-3 w-3" /> Required
                    </span>
                  )}
                </div>
                <p className="text-xs text-slate-500 mt-0.5 flex items-center gap-1">
                  <span>Defines whether directives cover worldwide property or domestic assets only.</span>
                  <HelpCircle className="h-3 w-3 text-slate-400 cursor-help" />
                </p>
                {editingField !== 'worldwide' && (
                  <div className="mt-2">
                    {state.covers_worldwide_assets === true && (
                      <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-semibold bg-blue-50 text-blue-800 border border-blue-200">
                        <Globe className="h-3 w-3" /> Worldwide Assets Covered
                      </span>
                    )}
                    {state.covers_worldwide_assets === false && (
                      <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-semibold bg-slate-100 text-slate-700 border border-slate-200">
                        Domestic Jurisdiction Only
                      </span>
                    )}
                    {state.covers_worldwide_assets === null && (
                      <span className="text-slate-400 italic text-sm">Unconfirmed</span>
                    )}
                  </div>
                )}
              </div>
            </div>

            {editingField !== 'worldwide' && (
              <button
                onClick={() => startEditing('worldwide')}
                className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium text-slate-600 hover:text-slate-900 hover:bg-slate-100 border border-slate-200 transition-colors"
              >
                <Edit2 className="h-3 w-3" />
                <span>Edit</span>
              </button>
            )}
          </div>

          {/* Inline Edit Form */}
          {editingField === 'worldwide' && (
            <div className="mt-4 pt-4 border-t border-slate-100">
              <label className="block text-xs font-semibold text-slate-700 mb-2">
                Select Scope of Assets
              </label>
              <div className="grid grid-cols-2 gap-3 mb-3">
                <button
                  type="button"
                  onClick={() => setDraftWorldwide(true)}
                  className={`p-3 rounded-xl border text-left text-xs font-medium transition-all ${
                    draftWorldwide === true
                      ? 'border-brand-600 bg-brand-50 text-brand-900 ring-2 ring-brand-500/20'
                      : 'border-slate-200 bg-white text-slate-700 hover:bg-slate-50'
                  }`}
                >
                  <div className="font-semibold mb-0.5">🌍 Worldwide Coverage</div>
                  <div className="text-[11px] text-slate-500">Includes all foreign and global assets</div>
                </button>
                <button
                  type="button"
                  onClick={() => setDraftWorldwide(false)}
                  className={`p-3 rounded-xl border text-left text-xs font-medium transition-all ${
                    draftWorldwide === false
                      ? 'border-brand-600 bg-brand-50 text-brand-900 ring-2 ring-brand-500/20'
                      : 'border-slate-200 bg-white text-slate-700 hover:bg-slate-50'
                  }`}
                >
                  <div className="font-semibold mb-0.5">🏠 Domestic Only</div>
                  <div className="text-[11px] text-slate-500">Excludes international assets</div>
                </button>
              </div>
              <div className="flex justify-end gap-2">
                <button
                  onClick={cancelEditing}
                  disabled={isSaving}
                  className="px-3 py-1.5 text-xs font-medium text-slate-600 hover:bg-slate-100 rounded-lg"
                >
                  Cancel
                </button>
                <button
                  onClick={() => handleSaveField('worldwide')}
                  disabled={isSaving}
                  className="flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium text-white bg-slate-900 hover:bg-brand-600 rounded-lg shadow-xs transition-colors"
                >
                  <Check className="h-3.5 w-3.5" />
                  <span>{isSaving ? 'Saving...' : 'Save'}</span>
                </button>
              </div>
            </div>
          )}
        </div>

        {/* 4. Children Status */}
        <div className="bg-white rounded-2xl border border-slate-200/90 shadow-xs p-5 transition-all">
          <div className="flex items-start justify-between gap-4">
            <div className="flex items-start gap-3">
              <div className="p-2 rounded-xl bg-slate-100 text-slate-700 mt-0.5">
                <Users className="h-4 w-4" />
              </div>
              <div>
                <div className="flex items-center gap-2">
                  <h4 className="font-semibold text-slate-900 text-sm">Children Details</h4>
                  {state.has_children === false || (state.has_children === true && state.children && state.children.length > 0) ? (
                    <span className="inline-flex items-center gap-1 text-[11px] font-medium text-emerald-700 bg-emerald-50 border border-emerald-200/70 px-2 py-0.5 rounded-full">
                      <CheckCircle2 className="h-3 w-3" /> Captured
                    </span>
                  ) : state.has_children === true ? (
                    <span className="inline-flex items-center gap-1 text-[11px] font-medium text-amber-700 bg-amber-50 border border-amber-200/70 px-2 py-0.5 rounded-full">
                      <AlertCircle className="h-3 w-3" /> Names Pending
                    </span>
                  ) : (
                    <span className="inline-flex items-center gap-1 text-[11px] font-medium text-amber-700 bg-amber-50 border border-amber-200/70 px-2 py-0.5 rounded-full">
                      <Clock className="h-3 w-3" /> Required
                    </span>
                  )}
                </div>
                <p className="text-xs text-slate-500 mt-0.5 flex items-center gap-1">
                  <span>Crucial for estate clarity, statutory claims, and guardianship.</span>
                  <HelpCircle className="h-3 w-3 text-slate-400 cursor-help" />
                </p>
                {editingField !== 'children' && (
                  <div className="mt-2 text-sm font-medium text-slate-800">
                    {state.has_children === false ? (
                      <span className="text-slate-600">No children</span>
                    ) : state.has_children === true ? (
                      state.children && state.children.length > 0 ? (
                        <div className="flex flex-wrap gap-1.5 mt-1">
                          {state.children.map((child, idx) => (
                            <span
                              key={idx}
                              className="px-2.5 py-0.5 rounded-md bg-slate-100 text-slate-700 border border-slate-200 text-xs"
                            >
                              {child}
                            </span>
                          ))}
                        </div>
                      ) : (
                        <span className="text-amber-600 italic">Has children (names pending)</span>
                      )
                    ) : (
                      <span className="text-slate-400 italic">Unconfirmed</span>
                    )}
                  </div>
                )}
              </div>
            </div>

            {editingField !== 'children' && (
              <button
                onClick={() => startEditing('children')}
                className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium text-slate-600 hover:text-slate-900 hover:bg-slate-100 border border-slate-200 transition-colors"
              >
                <Edit2 className="h-3 w-3" />
                <span>Edit</span>
              </button>
            )}
          </div>

          {/* Inline Edit Form */}
          {editingField === 'children' && (
            <div className="mt-4 pt-4 border-t border-slate-100">
              <label className="block text-xs font-semibold text-slate-700 mb-2">
                Do you have children?
              </label>
              <div className="flex gap-3 mb-4">
                <button
                  type="button"
                  onClick={() => setDraftHasChildren(true)}
                  className={`px-4 py-2 rounded-xl border text-xs font-semibold transition-all ${
                    draftHasChildren === true
                      ? 'border-brand-600 bg-brand-50 text-brand-900'
                      : 'border-slate-200 bg-white text-slate-700'
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
                  className={`px-4 py-2 rounded-xl border text-xs font-semibold transition-all ${
                    draftHasChildren === false
                      ? 'border-brand-600 bg-brand-50 text-brand-900'
                      : 'border-slate-200 bg-white text-slate-700'
                  }`}
                >
                  No children
                </button>
              </div>

              {draftHasChildren === true && (
                <div className="mb-4">
                  <label className="block text-xs font-semibold text-slate-700 mb-1.5">
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
                      className="flex-1 px-3 py-1.5 text-sm border border-slate-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-brand-500/20 focus:border-brand-500"
                    />
                    <button
                      type="button"
                      onClick={addChild}
                      className="px-3 py-1.5 bg-slate-100 hover:bg-slate-200 text-slate-800 rounded-xl text-xs font-semibold flex items-center gap-1"
                    >
                      <Plus className="h-3.5 w-3.5" />
                      <span>Add</span>
                    </button>
                  </div>

                  <div className="flex flex-wrap gap-1.5 mt-2">
                    {draftChildren.map((child, idx) => (
                      <span
                        key={idx}
                        className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-lg bg-slate-100 text-slate-800 text-xs border border-slate-200"
                      >
                        <span>{child}</span>
                        <button
                          type="button"
                          onClick={() => removeChild(idx)}
                          className="text-slate-400 hover:text-red-600"
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
                  className="px-3 py-1.5 text-xs font-medium text-slate-600 hover:bg-slate-100 rounded-lg"
                >
                  Cancel
                </button>
                <button
                  onClick={() => handleSaveField('children')}
                  disabled={isSaving}
                  className="flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium text-white bg-slate-900 hover:bg-brand-600 rounded-lg shadow-xs transition-colors"
                >
                  <Check className="h-3.5 w-3.5" />
                  <span>{isSaving ? 'Saving...' : 'Save'}</span>
                </button>
              </div>
            </div>
          )}
        </div>

        {/* 5. Executor & Fiduciary */}
        <div className="bg-white rounded-2xl border border-slate-200/90 shadow-xs p-5 transition-all">
          <div className="flex items-start justify-between gap-4">
            <div className="flex items-start gap-3">
              <div className="p-2 rounded-xl bg-slate-100 text-slate-700 mt-0.5">
                <Shield className="h-4 w-4" />
              </div>
              <div>
                <div className="flex items-center gap-2">
                  <h4 className="font-semibold text-slate-900 text-sm">Appointed Executor</h4>
                  {state.executor?.name && state.executor?.relationship ? (
                    <span className="inline-flex items-center gap-1 text-[11px] font-medium text-emerald-700 bg-emerald-50 border border-emerald-200/70 px-2 py-0.5 rounded-full">
                      <CheckCircle2 className="h-3 w-3" /> Captured
                    </span>
                  ) : state.executor?.name || state.executor?.relationship ? (
                    <span className="inline-flex items-center gap-1 text-[11px] font-medium text-amber-700 bg-amber-50 border border-amber-200/70 px-2 py-0.5 rounded-full">
                      <AlertCircle className="h-3 w-3" /> Partial
                    </span>
                  ) : (
                    <span className="inline-flex items-center gap-1 text-[11px] font-medium text-amber-700 bg-amber-50 border border-amber-200/70 px-2 py-0.5 rounded-full">
                      <Clock className="h-3 w-3" /> Required
                    </span>
                  )}
                </div>
                <p className="text-xs text-slate-500 mt-0.5 flex items-center gap-1">
                  <span>The legal fiduciary entrusted to distribute assets and carry out wishes.</span>
                  <HelpCircle className="h-3 w-3 text-slate-400 cursor-help" />
                </p>
                {editingField !== 'executor' && (
                  <div className="mt-2 text-sm font-medium text-slate-800">
                    {state.executor?.name ? (
                      <div>
                        <span>{state.executor.name}</span>
                        {state.executor.relationship && (
                          <span className="text-slate-500 font-normal ml-1">
                            ({state.executor.relationship})
                          </span>
                        )}
                      </div>
                    ) : (
                      <span className="text-slate-400 italic">Not appointed yet</span>
                    )}
                  </div>
                )}
              </div>
            </div>

            {editingField !== 'executor' && (
              <button
                onClick={() => startEditing('executor')}
                className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium text-slate-600 hover:text-slate-900 hover:bg-slate-100 border border-slate-200 transition-colors"
              >
                <Edit2 className="h-3 w-3" />
                <span>Edit</span>
              </button>
            )}
          </div>

          {/* Inline Edit Form */}
          {editingField === 'executor' && (
            <div className="mt-4 pt-4 border-t border-slate-100">
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 mb-3">
                <div>
                  <label className="block text-xs font-semibold text-slate-700 mb-1.5">
                    Executor Full Name
                  </label>
                  <input
                    type="text"
                    value={draftExecName}
                    onChange={(e) => setDraftExecName(e.target.value)}
                    placeholder="e.g. Sarah Jenkins"
                    className="w-full px-3 py-2 text-sm border border-slate-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-brand-500/20 focus:border-brand-500"
                  />
                </div>
                <div>
                  <label className="block text-xs font-semibold text-slate-700 mb-1.5">
                    Relationship to Principal
                  </label>
                  <input
                    type="text"
                    value={draftExecRel}
                    onChange={(e) => setDraftExecRel(e.target.value)}
                    placeholder="e.g. Sister, Trusted Friend, Solicitor"
                    className="w-full px-3 py-2 text-sm border border-slate-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-brand-500/20 focus:border-brand-500"
                  />
                </div>
              </div>
              <div className="flex justify-end gap-2">
                <button
                  onClick={cancelEditing}
                  disabled={isSaving}
                  className="px-3 py-1.5 text-xs font-medium text-slate-600 hover:bg-slate-100 rounded-lg"
                >
                  Cancel
                </button>
                <button
                  onClick={() => handleSaveField('executor')}
                  disabled={isSaving}
                  className="flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium text-white bg-slate-900 hover:bg-brand-600 rounded-lg shadow-xs transition-colors"
                >
                  <Check className="h-3.5 w-3.5" />
                  <span>{isSaving ? 'Saving...' : 'Save'}</span>
                </button>
              </div>
            </div>
          )}
        </div>

        {/* 6. Specific Gifts & Bequests (Optional) */}
        <div className="bg-white rounded-2xl border border-slate-200/90 shadow-xs p-5 transition-all">
          <div className="flex items-start justify-between gap-4">
            <div className="flex items-start gap-3">
              <div className="p-2 rounded-xl bg-slate-100 text-slate-700 mt-0.5">
                <Gift className="h-4 w-4" />
              </div>
              <div>
                <div className="flex items-center gap-2">
                  <h4 className="font-semibold text-slate-900 text-sm">Specific Gifts & Bequests</h4>
                  <span className="inline-flex items-center text-[11px] font-medium text-slate-500 bg-slate-100 px-2 py-0.5 rounded-full">
                    Optional
                  </span>
                </div>
                <p className="text-xs text-slate-500 mt-0.5 flex items-center gap-1">
                  <span>Particular family heirlooms, jewelry, or cash designated for specific recipients.</span>
                  <HelpCircle className="h-3 w-3 text-slate-400 cursor-help" />
                </p>
                {editingField !== 'gifts' && (
                  <div className="mt-2">
                    {state.specific_gifts && state.specific_gifts.length > 0 ? (
                      <div className="space-y-1.5">
                        {state.specific_gifts.map((g, idx) => (
                          <div
                            key={idx}
                            className="text-xs bg-slate-50 px-3 py-1.5 rounded-lg border border-slate-200/70 flex items-center justify-between"
                          >
                            <span className="font-medium text-slate-800">{g.item}</span>
                            <span className="text-slate-500">to {g.recipient}</span>
                          </div>
                        ))}
                      </div>
                    ) : (
                      <span className="text-slate-400 italic text-sm">No specific gifts listed</span>
                    )}
                  </div>
                )}
              </div>
            </div>

            {editingField !== 'gifts' && (
              <button
                onClick={() => startEditing('gifts')}
                className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium text-slate-600 hover:text-slate-900 hover:bg-slate-100 border border-slate-200 transition-colors"
              >
                <Edit2 className="h-3 w-3" />
                <span>Manage</span>
              </button>
            )}
          </div>

          {/* Inline Edit Form */}
          {editingField === 'gifts' && (
            <div className="mt-4 pt-4 border-t border-slate-100">
              <label className="block text-xs font-semibold text-slate-700 mb-2">
                Add a Specific Gift
              </label>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 mb-2">
                <input
                  type="text"
                  value={newGiftItem}
                  onChange={(e) => setNewGiftItem(e.target.value)}
                  placeholder="Item (e.g. Gold pocket watch)"
                  className="px-3 py-1.5 text-sm border border-slate-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-brand-500/20"
                />
                <input
                  type="text"
                  value={newGiftRecipient}
                  onChange={(e) => setNewGiftRecipient(e.target.value)}
                  placeholder="Recipient (e.g. Lucas Doe)"
                  className="px-3 py-1.5 text-sm border border-slate-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-brand-500/20"
                />
              </div>
              <button
                type="button"
                onClick={addGift}
                className="mb-4 px-3 py-1.5 bg-slate-100 hover:bg-slate-200 text-slate-800 rounded-xl text-xs font-semibold flex items-center gap-1"
              >
                <Plus className="h-3.5 w-3.5" />
                <span>Add Item to List</span>
              </button>

              {draftGifts.length > 0 && (
                <div className="space-y-1.5 mb-4">
                  {draftGifts.map((g, idx) => (
                    <div
                      key={idx}
                      className="p-2.5 rounded-xl bg-slate-50 border border-slate-200 flex items-center justify-between text-xs"
                    >
                      <div>
                        <span className="font-semibold text-slate-800">{g.item}</span>
                        <span className="text-slate-500 ml-2">to {g.recipient}</span>
                      </div>
                      <button
                        type="button"
                        onClick={() => removeGift(idx)}
                        className="text-slate-400 hover:text-red-600 p-1"
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
                  className="px-3 py-1.5 text-xs font-medium text-slate-600 hover:bg-slate-100 rounded-lg"
                >
                  Cancel
                </button>
                <button
                  onClick={() => handleSaveField('gifts')}
                  disabled={isSaving}
                  className="flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium text-white bg-slate-900 hover:bg-brand-600 rounded-lg shadow-xs transition-colors"
                >
                  <Check className="h-3.5 w-3.5" />
                  <span>{isSaving ? 'Saving...' : 'Save'}</span>
                </button>
              </div>
            </div>
          )}
        </div>

        {/* 7. Additional Wishes & Directives (Optional) */}
        <div className="bg-white rounded-2xl border border-slate-200/90 shadow-xs p-5 transition-all">
          <div className="flex items-start justify-between gap-4">
            <div className="flex items-start gap-3">
              <div className="p-2 rounded-xl bg-slate-100 text-slate-700 mt-0.5">
                <HeartHandshake className="h-4 w-4" />
              </div>
              <div>
                <div className="flex items-center gap-2">
                  <h4 className="font-semibold text-slate-900 text-sm">Additional Wishes & Directives</h4>
                  <span className="inline-flex items-center text-[11px] font-medium text-slate-500 bg-slate-100 px-2 py-0.5 rounded-full">
                    Optional
                  </span>
                </div>
                <p className="text-xs text-slate-500 mt-0.5 flex items-center gap-1">
                  <span>Funeral instructions, memorial preferences, religious rites, or personal notes.</span>
                  <HelpCircle className="h-3 w-3 text-slate-400 cursor-help" />
                </p>
                {editingField !== 'wishes' && (
                  <div className="mt-2">
                    {state.additional_wishes && state.additional_wishes.length > 0 ? (
                      <ul className="list-disc pl-4 text-xs text-slate-700 space-y-1">
                        {state.additional_wishes.map((w, idx) => (
                          <li key={idx}>{w}</li>
                        ))}
                      </ul>
                    ) : (
                      <span className="text-slate-400 italic text-sm">No additional directives entered</span>
                    )}
                  </div>
                )}
              </div>
            </div>

            {editingField !== 'wishes' && (
              <button
                onClick={() => startEditing('wishes')}
                className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium text-slate-600 hover:text-slate-900 hover:bg-slate-100 border border-slate-200 transition-colors"
              >
                <Edit2 className="h-3 w-3" />
                <span>Manage</span>
              </button>
            )}
          </div>

          {/* Inline Edit Form */}
          {editingField === 'wishes' && (
            <div className="mt-4 pt-4 border-t border-slate-100">
              <label className="block text-xs font-semibold text-slate-700 mb-1.5">
                Add a Directive or Wish
              </label>
              <div className="flex gap-2 mb-3">
                <input
                  type="text"
                  value={newWishText}
                  onChange={(e) => setNewWishText(e.target.value)}
                  placeholder="e.g. I wish to be cremated and scattered in the Lake District"
                  className="flex-1 px-3 py-1.5 text-sm border border-slate-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-brand-500/20"
                />
                <button
                  type="button"
                  onClick={addWish}
                  className="px-3 py-1.5 bg-slate-100 hover:bg-slate-200 text-slate-800 rounded-xl text-xs font-semibold flex items-center gap-1"
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
                      className="p-2.5 rounded-xl bg-slate-50 border border-slate-200 flex items-center justify-between text-xs"
                    >
                      <span className="text-slate-800">{w}</span>
                      <button
                        type="button"
                        onClick={() => removeWish(idx)}
                        className="text-slate-400 hover:text-red-600 p-1"
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
                  className="px-3 py-1.5 text-xs font-medium text-slate-600 hover:bg-slate-100 rounded-lg"
                >
                  Cancel
                </button>
                <button
                  onClick={() => handleSaveField('wishes')}
                  disabled={isSaving}
                  className="flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium text-white bg-slate-900 hover:bg-brand-600 rounded-lg shadow-xs transition-colors"
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
