import React from 'react';
import {
  Scale,
  Sparkles,
  Cpu,
  ShieldCheck,
  ArrowRight,
  Bot,
  FileText,
  Sliders,
  Database,
  CheckCircle2,
  Lock,
  Sun,
  Moon,
} from 'lucide-react';
import { useTheme } from '../context/ThemeContext';

interface LandingPageProps {
  onLaunch: () => void;
  activeProvider?: string;
  completionPercentage?: number;
}

export const LandingPage: React.FC<LandingPageProps> = ({
  onLaunch,
  activeProvider = 'mock',
  completionPercentage = 0,
}) => {
  const { theme, toggleTheme } = useTheme();

  return (
    <div className="min-h-screen bg-slate-50 dark:bg-slate-950 text-slate-900 dark:text-slate-100 font-sans transition-colors duration-200 overflow-x-hidden selection:bg-brand-500 selection:text-white">
      {/* -------------------------------------------------------------
          Top Navigation Bar
      ------------------------------------------------------------- */}
      <nav className="sticky top-0 z-40 bg-white/80 dark:bg-slate-900/80 backdrop-blur-md border-b border-slate-200/80 dark:border-slate-800 transition-colors">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
          {/* Logo & Brand */}
          <div className="flex items-center gap-3">
            <div className="h-10 w-10 rounded-xl bg-gradient-to-tr from-brand-600 via-indigo-600 to-violet-500 flex items-center justify-center text-white shadow-glow-brand ring-1 ring-white/20">
              <Scale className="h-5 w-5" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <span className="font-bold text-slate-900 dark:text-white text-base sm:text-lg tracking-tight">
                  Document Intake Assistant
                </span>
                <span className="inline-flex items-center px-2 py-0.5 rounded-full text-[10px] font-bold uppercase tracking-wider bg-brand-50 dark:bg-brand-950/60 text-brand-700 dark:text-brand-300 border border-brand-200/80 dark:border-brand-800">
                  Legal AI
                </span>
              </div>
            </div>
          </div>

          {/* Nav Links & Actions */}
          <div className="flex items-center gap-3">
            <a
              href="#features"
              className="hidden sm:inline-flex text-xs font-semibold text-slate-600 dark:text-slate-400 hover:text-brand-600 dark:hover:text-brand-400 transition-colors px-3 py-1.5"
            >
              Capabilities
            </a>
            <a
              href="#how-it-works"
              className="hidden sm:inline-flex text-xs font-semibold text-slate-600 dark:text-slate-400 hover:text-brand-600 dark:hover:text-brand-400 transition-colors px-3 py-1.5"
            >
              Workflow
            </a>

            {/* Provider Badge */}
            <div className="hidden lg:flex items-center gap-1.5 px-2.5 py-1 rounded-full text-[11px] font-medium bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-300 border border-slate-200 dark:border-slate-700">
              <Cpu className="h-3 w-3 text-brand-600 dark:text-brand-400" />
              <span>{activeProvider === 'mock' ? 'Mock Engine' : activeProvider}</span>
            </div>

            {/* Progress Badge if already in progress */}
            {completionPercentage > 0 && (
              <div className="hidden md:flex items-center gap-1.5 px-2.5 py-1 rounded-full text-[11px] font-semibold bg-emerald-50 dark:bg-emerald-950/70 text-emerald-700 dark:text-emerald-300 border border-emerald-300 dark:border-emerald-700">
                <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse" />
                <span>{completionPercentage}% In Progress</span>
              </div>
            )}

            {/* Theme Toggle */}
            <button
              onClick={toggleTheme}
              className="flex items-center justify-center p-2 rounded-xl text-slate-600 dark:text-slate-300 bg-slate-100 dark:bg-slate-800 hover:bg-slate-200 dark:hover:bg-slate-700 border border-slate-200 dark:border-slate-700 transition-all shadow-2xs hover:scale-105 active:scale-95"
              title={`Switch to ${theme === 'light' ? 'Dark' : 'Light'} Mode`}
              aria-label="Toggle theme"
            >
              {theme === 'light' ? (
                <Moon className="h-4 w-4 text-brand-600" />
              ) : (
                <Sun className="h-4 w-4 text-amber-400 animate-spin-slow" />
              )}
            </button>

            {/* Launch CTA */}
            <button
              onClick={onLaunch}
              className="flex items-center gap-2 px-4 py-2 rounded-xl text-xs sm:text-sm font-semibold text-white bg-gradient-to-r from-brand-600 via-indigo-600 to-violet-600 hover:from-brand-500 hover:to-violet-500 shadow-glow-brand hover:shadow-lg transition-all duration-200 hover:-translate-y-0.5 active:translate-y-0 cursor-pointer"
            >
              <span>{completionPercentage > 0 ? 'Resume Assistant' : 'Launch Assistant'}</span>
              <ArrowRight className="h-4 w-4" />
            </button>
          </div>
        </div>
      </nav>

      {/* -------------------------------------------------------------
          Hero Section
      ------------------------------------------------------------- */}
      <section className="relative pt-12 pb-20 sm:pt-20 sm:pb-28 overflow-hidden">
        {/* Ambient Glowing Orbs Background */}
        <div className="absolute top-1/4 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[600px] h-[600px] bg-gradient-to-tr from-brand-500/15 via-indigo-500/15 to-violet-500/10 blur-3xl rounded-full pointer-events-none -z-10" />
        <div className="absolute top-1/3 right-10 w-[350px] h-[350px] bg-emerald-500/10 blur-3xl rounded-full pointer-events-none -z-10" />

        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          {/* Top Badges */}
          <div className="flex flex-wrap items-center justify-center gap-2.5 mb-6">
            <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-semibold bg-indigo-50 dark:bg-indigo-950/60 text-indigo-700 dark:text-indigo-300 border border-indigo-200/80 dark:border-indigo-800 shadow-2xs">
              <Sparkles className="h-3.5 w-3.5 text-indigo-600 dark:text-indigo-400" />
              Enterprise Legal Tech
            </span>
            <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-semibold bg-emerald-50 dark:bg-emerald-950/60 text-emerald-700 dark:text-emerald-300 border border-emerald-200/80 dark:border-emerald-800 shadow-2xs">
              <Cpu className="h-3.5 w-3.5 text-emerald-600 dark:text-emerald-400" />
              Real-Time State Extraction
            </span>
            <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-semibold bg-amber-50 dark:bg-amber-950/60 text-amber-700 dark:text-amber-300 border border-amber-200/80 dark:border-amber-800 shadow-2xs">
              <ShieldCheck className="h-3.5 w-3.5 text-amber-600 dark:text-amber-400" />
              Deterministic Guardrails
            </span>
          </div>

          {/* Headline */}
          <h1 className="text-4xl sm:text-5xl lg:text-6xl font-extrabold tracking-tight text-slate-900 dark:text-white max-w-4xl mx-auto leading-[1.12] mb-6">
            AI-Powered Personal Wishes &{' '}
            <span className="bg-gradient-to-r from-brand-600 via-indigo-500 to-emerald-500 bg-clip-text text-transparent">
              Legal Document Intake
            </span>
          </h1>

          {/* Subtitle */}
          <p className="text-base sm:text-lg text-slate-600 dark:text-slate-400 max-w-2xl mx-auto mb-10 leading-relaxed font-normal">
            Conduct conversational legal interviews that dynamically transform free-form user answers into formal, verified Personal Wishes Documents with live drafting and instant state validation.
          </p>

          {/* CTA Buttons */}
          <div className="flex flex-col sm:flex-row items-center justify-center gap-3.5 mb-16">
            <button
              onClick={onLaunch}
              className="w-full sm:w-auto flex items-center justify-center gap-2.5 px-7 py-3.5 rounded-2xl text-sm sm:text-base font-bold text-white bg-gradient-to-r from-brand-600 via-indigo-600 to-violet-600 hover:from-brand-500 hover:to-violet-500 shadow-glow-brand hover:shadow-xl transition-all duration-200 hover:-translate-y-0.5 active:translate-y-0"
            >
              <span>Launch Intake Assistant</span>
              <ArrowRight className="h-4.5 w-4.5" />
            </button>
            <a
              href="#features"
              className="w-full sm:w-auto flex items-center justify-center gap-2 px-6 py-3.5 rounded-2xl text-sm sm:text-base font-semibold text-slate-700 dark:text-slate-300 bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 hover:bg-slate-50 dark:hover:bg-slate-850 hover:border-slate-300 dark:hover:border-slate-700 shadow-2xs hover:shadow-sm transition-all duration-200"
            >
              <FileText className="h-4.5 w-4.5 text-brand-600 dark:text-brand-400" />
              <span>Explore Capabilities</span>
            </a>
          </div>

          {/* Interactive UI Mockup Hero Card */}
          <div className="max-w-5xl mx-auto rounded-3xl p-2 sm:p-3 bg-gradient-to-b from-slate-200/80 via-slate-200/40 to-slate-200/80 dark:from-slate-800 dark:via-slate-800/40 dark:to-slate-800 shadow-2xl border border-slate-200 dark:border-slate-700/80">
            <div className="rounded-2xl bg-white dark:bg-slate-900 overflow-hidden border border-slate-200/60 dark:border-slate-800 grid grid-cols-1 md:grid-cols-12 shadow-inner">
              {/* Left Mockup: Chat Turn */}
              <div className="md:col-span-6 p-5 sm:p-6 border-b md:border-b-0 md:border-r border-slate-200/80 dark:border-slate-800 text-left flex flex-col justify-between bg-slate-50/50 dark:bg-slate-925/50">
                <div>
                  <div className="flex items-center justify-between pb-3 mb-4 border-b border-slate-200 dark:border-slate-800">
                    <div className="flex items-center gap-2">
                      <div className="w-2.5 h-2.5 rounded-full bg-emerald-500 animate-pulse" />
                      <span className="text-xs font-bold text-slate-700 dark:text-slate-300">
                        Live Interview Turn
                      </span>
                    </div>
                    <span className="text-[10px] font-semibold uppercase px-2 py-0.5 rounded-md bg-slate-200 dark:bg-slate-800 text-slate-600 dark:text-slate-400">
                      Turn 2
                    </span>
                  </div>

                  {/* Chat Bubbles */}
                  <div className="space-y-3">
                    <div className="flex gap-2.5 items-start">
                      <div className="h-6 w-6 rounded-md bg-brand-600 text-white flex items-center justify-center text-[10px] font-bold flex-shrink-0">
                        AI
                      </div>
                      <div className="bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-xl rounded-tl-xs p-3 text-xs text-slate-800 dark:text-slate-200 shadow-2xs">
                        Thank you, Eleanor Vance. What is your current residential home address?
                      </div>
                    </div>

                    <div className="flex gap-2.5 items-start justify-end">
                      <div className="bg-brand-600 text-white rounded-xl rounded-tr-xs p-3 text-xs shadow-2xs max-w-[85%] text-left">
                        14 Rue de la Paix, 75002 Paris, France. Worldwide assets please, and my brother James Smith is executor.
                      </div>
                      <div className="h-6 w-6 rounded-md bg-slate-300 dark:bg-slate-700 text-slate-700 dark:text-slate-300 flex items-center justify-center text-[10px] font-bold flex-shrink-0">
                        You
                      </div>
                    </div>

                    <div className="flex gap-2.5 items-start">
                      <div className="h-6 w-6 rounded-md bg-brand-600 text-white flex items-center justify-center text-[10px] font-bold flex-shrink-0">
                        AI
                      </div>
                      <div className="bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-xl rounded-tl-xs p-3 text-xs text-slate-800 dark:text-slate-200 shadow-2xs">
                        <span className="text-emerald-600 dark:text-emerald-400 font-semibold block mb-1">
                          ✓ Multi-Field Intake Captured:
                        </span>
                        Recorded address, worldwide jurisdiction, and executor James Smith (brother). Do you have any children?
                      </div>
                    </div>
                  </div>
                </div>

                <div className="mt-4 pt-3 border-t border-slate-200/80 dark:border-slate-800/80 flex items-center justify-between text-[11px] text-slate-500 dark:text-slate-400">
                  <span>Context: Context-aware mapping active</span>
                  <span className="font-semibold text-brand-600 dark:text-brand-400">Universal Address Parsing</span>
                </div>
              </div>

              {/* Right Mockup: Live Legal Draft Paper */}
              <div className="md:col-span-6 p-5 sm:p-6 text-left flex flex-col justify-between bg-white dark:bg-slate-900">
                <div>
                  <div className="flex items-center justify-between pb-3 mb-4 border-b border-slate-200 dark:border-slate-800">
                    <span className="text-xs font-bold text-slate-700 dark:text-slate-300 flex items-center gap-1.5">
                      <FileText className="h-3.5 w-3.5 text-brand-600 dark:text-brand-400" />
                      Live Document Draft Preview
                    </span>
                    <span className="text-[10px] font-bold px-2 py-0.5 rounded-full bg-emerald-50 dark:bg-emerald-950/60 text-emerald-700 dark:text-emerald-400 border border-emerald-300 dark:border-emerald-800">
                      83% Complete
                    </span>
                  </div>

                  {/* Document Parchment Card */}
                  <div className="p-4 rounded-xl bg-slate-50 dark:bg-slate-950 border border-slate-200 dark:border-slate-800 font-serif text-slate-800 dark:text-slate-200 text-xs space-y-2 shadow-2xs">
                    <div className="text-center font-bold text-sm tracking-wide text-slate-900 dark:text-white border-b pb-2 border-slate-200 dark:border-slate-800 font-sans">
                      PERSONAL WISHES DOCUMENT
                    </div>
                    <p className="leading-relaxed">
                      I, <strong className="font-sans font-semibold text-brand-600 dark:text-brand-400">Eleanor Vance</strong>, residing at <strong className="font-sans font-semibold">14 Rue de la Paix, 75002 Paris, France</strong>, declare this document to govern the administration of my estate.
                    </p>
                    <p className="leading-relaxed">
                      <strong>1. Worldwide Estate Scope:</strong> This document explicitly extends to all assets owned domestically and internationally.
                    </p>
                    <p className="leading-relaxed">
                      <strong>2. Appointment of Executor:</strong> I appoint my brother, <strong className="font-sans font-semibold text-indigo-600 dark:text-indigo-400">James Smith</strong>, as personal representative.
                    </p>
                  </div>
                </div>

                <div className="mt-4 pt-3 border-t border-slate-200/80 dark:border-slate-800/80 flex items-center justify-between text-[11px] text-slate-500 dark:text-slate-400">
                  <span className="flex items-center gap-1 text-emerald-600 dark:text-emerald-400 font-semibold">
                    <CheckCircle2 className="h-3.5 w-3.5" />
                    Structured State In Sync
                  </span>
                  <span className="font-mono text-[10px]">app.db persistent</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* -------------------------------------------------------------
          Value Proposition / Feature Grid (Exact requested capabilities)
      ------------------------------------------------------------- */}
      <section id="features" className="py-20 bg-white dark:bg-slate-900/60 border-y border-slate-200/80 dark:border-slate-800 transition-colors">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center max-w-3xl mx-auto mb-16">
            <span className="text-xs font-bold uppercase tracking-wider text-brand-600 dark:text-brand-400 mb-2 block">
              Core Architecture & Intelligence
            </span>
            <h2 className="text-3xl sm:text-4xl font-extrabold text-slate-900 dark:text-white tracking-tight mb-4">
              Engineered for Legal Precision and Conversational Freedom
            </h2>
            <p className="text-sm sm:text-base text-slate-600 dark:text-slate-400 leading-relaxed">
              Unlike rigid form wizards or unstructured chatbots, the Document Intake Assistant combines deterministic state management with fluid AI dialogue.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6 lg:gap-8">
            {/* Feature 1: Multi-Turn Conversational AI */}
            <div className="group rounded-2xl p-6 sm:p-7 bg-slate-50/80 dark:bg-slate-850/60 border border-slate-200/90 dark:border-slate-800 hover:border-brand-500/50 dark:hover:border-brand-500/50 transition-all duration-300 hover:shadow-xl hover:-translate-y-1">
              <div className="h-12 w-12 rounded-xl bg-indigo-100 dark:bg-indigo-950/80 text-indigo-600 dark:text-indigo-400 flex items-center justify-center mb-5 ring-1 ring-indigo-500/20 group-hover:scale-110 transition-transform">
                <Bot className="h-6 w-6" />
              </div>
              <div className="flex items-center gap-2 mb-2">
                <span className="text-[10px] font-bold uppercase tracking-wider px-2 py-0.5 rounded-full bg-indigo-50 dark:bg-indigo-950 text-indigo-700 dark:text-indigo-300 border border-indigo-200 dark:border-indigo-800">
                  Strict Guardrails
                </span>
              </div>
              <h3 className="text-lg sm:text-xl font-bold text-slate-900 dark:text-white mb-2 tracking-tight">
                Multi-Turn Conversational AI with Strict Validation
              </h3>
              <p className="text-xs sm:text-sm text-slate-600 dark:text-slate-400 leading-relaxed mb-4">
                Conducts intelligent interviews powered by Gemini 1.5 or the deterministic offline Mock provider. Detects and rejects nonsensical or keyboard-mash inputs, flags ambiguities, and asks smart follow-ups without trapped conversational loops.
              </p>
              <ul className="space-y-2 text-xs text-slate-600 dark:text-slate-400">
                <li className="flex items-center gap-2">
                  <CheckCircle2 className="h-3.5 w-3.5 text-emerald-500 flex-shrink-0" />
                  <span>Universal address & name acceptance from any country</span>
                </li>
                <li className="flex items-center gap-2">
                  <CheckCircle2 className="h-3.5 w-3.5 text-emerald-500 flex-shrink-0" />
                  <span>Two-tier executor mapping (never overwrites full name)</span>
                </li>
              </ul>
            </div>

            {/* Feature 2: Live Legal Paper & Markdown Preview */}
            <div className="group rounded-2xl p-6 sm:p-7 bg-slate-50/80 dark:bg-slate-850/60 border border-slate-200/90 dark:border-slate-800 hover:border-emerald-500/50 dark:hover:border-emerald-500/50 transition-all duration-300 hover:shadow-xl hover:-translate-y-1">
              <div className="h-12 w-12 rounded-xl bg-emerald-100 dark:bg-emerald-950/80 text-emerald-600 dark:text-emerald-400 flex items-center justify-center mb-5 ring-1 ring-emerald-500/20 group-hover:scale-110 transition-transform">
                <FileText className="h-6 w-6" />
              </div>
              <div className="flex items-center gap-2 mb-2">
                <span className="text-[10px] font-bold uppercase tracking-wider px-2 py-0.5 rounded-full bg-emerald-50 dark:bg-emerald-950 text-emerald-700 dark:text-emerald-300 border border-emerald-200 dark:border-emerald-800">
                  Real-Time Draft
                </span>
              </div>
              <h3 className="text-lg sm:text-xl font-bold text-slate-900 dark:text-white mb-2 tracking-tight">
                Live Legal Paper & Markdown Document Preview
              </h3>
              <p className="text-xs sm:text-sm text-slate-600 dark:text-slate-400 leading-relaxed mb-4">
                Watch your legal document synthesize continuously in real time. Switch smoothly between formal parchment serif presentation, clean raw Markdown source, and intake completeness progress tracking.
              </p>
              <ul className="space-y-2 text-xs text-slate-600 dark:text-slate-400">
                <li className="flex items-center gap-2">
                  <CheckCircle2 className="h-3.5 w-3.5 text-emerald-500 flex-shrink-0" />
                  <span>Formal legal clauses rendered with typographic elegance</span>
                </li>
                <li className="flex items-center gap-2">
                  <CheckCircle2 className="h-3.5 w-3.5 text-emerald-500 flex-shrink-0" />
                  <span>One-click clipboard copy for Markdown & clean print styling</span>
                </li>
              </ul>
            </div>

            {/* Feature 3: Instant Field Overrides & Flexible Mid-Interview Edits */}
            <div className="group rounded-2xl p-6 sm:p-7 bg-slate-50/80 dark:bg-slate-850/60 border border-slate-200/90 dark:border-slate-800 hover:border-amber-500/50 dark:hover:border-amber-500/50 transition-all duration-300 hover:shadow-xl hover:-translate-y-1">
              <div className="h-12 w-12 rounded-xl bg-amber-100 dark:bg-amber-950/80 text-amber-600 dark:text-amber-400 flex items-center justify-center mb-5 ring-1 ring-amber-500/20 group-hover:scale-110 transition-transform">
                <Sliders className="h-6 w-6" />
              </div>
              <div className="flex items-center gap-2 mb-2">
                <span className="text-[10px] font-bold uppercase tracking-wider px-2 py-0.5 rounded-full bg-amber-50 dark:bg-amber-950 text-amber-700 dark:text-amber-300 border border-amber-200 dark:border-amber-800">
                  Non-Linear Flow
                </span>
              </div>
              <h3 className="text-lg sm:text-xl font-bold text-slate-900 dark:text-white mb-2 tracking-tight">
                Instant Field Overrides & Flexible Mid-Interview Edits
              </h3>
              <p className="text-xs sm:text-sm text-slate-600 dark:text-slate-400 leading-relaxed mb-4">
                Users are never trapped in a rigid question sequence. Backtrack, correct an already-filled address, or say "I want to change my executor" at any moment. The conversation router pivots immediately and resumes intake seamlessly.
              </p>
              <ul className="space-y-2 text-xs text-slate-600 dark:text-slate-400">
                <li className="flex items-center gap-2">
                  <CheckCircle2 className="h-3.5 w-3.5 text-emerald-500 flex-shrink-0" />
                  <span>Proactive edit intent detection shifts focus automatically</span>
                </li>
                <li className="flex items-center gap-2">
                  <CheckCircle2 className="h-3.5 w-3.5 text-emerald-500 flex-shrink-0" />
                  <span>Out-of-order gift additions and wish removals handled cleanly</span>
                </li>
              </ul>
            </div>

            {/* Feature 4: Secure SQLite Persistence & Structured JSON State */}
            <div className="group rounded-2xl p-6 sm:p-7 bg-slate-50/80 dark:bg-slate-850/60 border border-slate-200/90 dark:border-slate-800 hover:border-cyan-500/50 dark:hover:border-cyan-500/50 transition-all duration-300 hover:shadow-xl hover:-translate-y-1">
              <div className="h-12 w-12 rounded-xl bg-cyan-100 dark:bg-cyan-950/80 text-cyan-600 dark:text-cyan-400 flex items-center justify-center mb-5 ring-1 ring-cyan-500/20 group-hover:scale-110 transition-transform">
                <Database className="h-6 w-6" />
              </div>
              <div className="flex items-center gap-2 mb-2">
                <span className="text-[10px] font-bold uppercase tracking-wider px-2 py-0.5 rounded-full bg-cyan-50 dark:bg-cyan-950 text-cyan-700 dark:text-cyan-300 border border-cyan-200 dark:border-cyan-800">
                  State Separation
                </span>
              </div>
              <h3 className="text-lg sm:text-xl font-bold text-slate-900 dark:text-white mb-2 tracking-tight">
                Secure SQLite Persistence & Structured JSON State
              </h3>
              <p className="text-xs sm:text-sm text-slate-600 dark:text-slate-400 leading-relaxed mb-4">
                Maintains a single source of truth structured JSON state explicitly separated from raw chat logs. Sessions and state deltas automatically persist to SQLite (`app.db`) with full direct manual JSON state editing capability.
              </p>
              <ul className="space-y-2 text-xs text-slate-600 dark:text-slate-400">
                <li className="flex items-center gap-2">
                  <CheckCircle2 className="h-3.5 w-3.5 text-emerald-500 flex-shrink-0" />
                  <span>Session restore and reload with zero memory leakage</span>
                </li>
                <li className="flex items-center gap-2">
                  <CheckCircle2 className="h-3.5 w-3.5 text-emerald-500 flex-shrink-0" />
                  <span>Built-in schema inspector with real-time payload editing</span>
                </li>
              </ul>
            </div>
          </div>
        </div>
      </section>

      {/* -------------------------------------------------------------
          Workflow Section ("How It Works")
      ------------------------------------------------------------- */}
      <section id="how-it-works" className="py-20 bg-slate-50 dark:bg-slate-950 transition-colors">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center max-w-3xl mx-auto mb-16">
            <span className="text-xs font-bold uppercase tracking-wider text-brand-600 dark:text-brand-400 mb-2 block">
              Streamlined 3-Step Experience
            </span>
            <h2 className="text-3xl sm:text-4xl font-extrabold text-slate-900 dark:text-white tracking-tight mb-4">
              From Natural Conversation to Legally Sound Document
            </h2>
            <p className="text-sm sm:text-base text-slate-600 dark:text-slate-400 leading-relaxed">
              No complex questionnaires. Just an empathetic, clear dialogue that extracts the right details.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-8 relative">
            {/* Step 1 */}
            <div className="relative p-6 rounded-2xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 shadow-xs">
              <div className="h-10 w-10 rounded-xl bg-brand-600 text-white font-bold text-sm flex items-center justify-center mb-4 shadow-glow-brand">
                01
              </div>
              <h4 className="text-base font-bold text-slate-900 dark:text-white mb-2">
                Conversational Interview
              </h4>
              <p className="text-xs sm:text-sm text-slate-600 dark:text-slate-400 leading-relaxed">
                Provide your full name, residence, asset scope, children, and appointed executor naturally. Answer questions in order, or give multiple details at once.
              </p>
            </div>

            {/* Step 2 */}
            <div className="relative p-6 rounded-2xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 shadow-xs">
              <div className="h-10 w-10 rounded-xl bg-indigo-600 text-white font-bold text-sm flex items-center justify-center mb-4 shadow-glow-brand">
                02
              </div>
              <h4 className="text-base font-bold text-slate-900 dark:text-white mb-2">
                AI Validation & Extraction
              </h4>
              <p className="text-xs sm:text-sm text-slate-600 dark:text-slate-400 leading-relaxed">
                The engine evaluates every input against strict legal schemas. If an answer is unclear, it politely asks follow-ups while preserving all confirmed details.
              </p>
            </div>

            {/* Step 3 */}
            <div className="relative p-6 rounded-2xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 shadow-xs">
              <div className="h-10 w-10 rounded-xl bg-emerald-600 text-white font-bold text-sm flex items-center justify-center mb-4 shadow-glow-emerald">
                03
              </div>
              <h4 className="text-base font-bold text-slate-900 dark:text-white mb-2">
                Live Legal Draft & Export
              </h4>
              <p className="text-xs sm:text-sm text-slate-600 dark:text-slate-400 leading-relaxed">
                Review the formal parchment paper draft and structured JSON in real time. Inspect, modify, or reset anytime with SQLite session persistence.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* -------------------------------------------------------------
          Bottom CTA Banner
      ------------------------------------------------------------- */}
      <section className="py-16 sm:py-20 bg-gradient-to-b from-white to-slate-100 dark:from-slate-900 dark:to-slate-950 transition-colors">
        <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="rounded-3xl p-8 sm:p-12 bg-gradient-to-r from-brand-900 via-indigo-950 to-slate-950 text-white shadow-2xl border border-brand-800/40 relative overflow-hidden text-center">
            {/* Ambient Background glow */}
            <div className="absolute top-0 right-0 w-80 h-80 bg-brand-500/20 blur-3xl rounded-full pointer-events-none" />

            <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-semibold bg-brand-500/20 text-brand-300 border border-brand-500/30 mb-4">
              <Lock className="h-3.5 w-3.5" />
              Production-Grade Legal Workflow
            </span>
            <h2 className="text-2xl sm:text-4xl font-extrabold tracking-tight mb-4 max-w-2xl mx-auto">
              Ready to create your Personal Wishes Document?
            </h2>
            <p className="text-xs sm:text-sm text-slate-300 max-w-xl mx-auto mb-8 leading-relaxed">
              Experience the fast, intelligent intake assistant. Runs completely offline in Mock mode or connected directly to Google Gemini.
            </p>
            <button
              onClick={onLaunch}
              className="inline-flex items-center gap-2.5 px-8 py-4 rounded-2xl text-sm sm:text-base font-bold text-slate-900 bg-white hover:bg-slate-100 shadow-xl hover:shadow-2xl transition-all duration-200 hover:scale-105 active:scale-95"
            >
              <span>Launch Assistant Now</span>
              <ArrowRight className="h-4.5 w-4.5 text-brand-600" />
            </button>
          </div>
        </div>
      </section>

      {/* -------------------------------------------------------------
          Footer
      ------------------------------------------------------------- */}
      <footer className="py-8 bg-slate-100 dark:bg-slate-950 border-t border-slate-200 dark:border-slate-800 text-xs text-slate-500 dark:text-slate-400 transition-colors">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 flex flex-col sm:flex-row items-center justify-between gap-4">
          <div className="flex items-center gap-2">
            <Scale className="h-4 w-4 text-brand-600" />
            <span className="font-semibold text-slate-700 dark:text-slate-300">
              Document Intake Assistant
            </span>
            <span>— Technical Test Implementation</span>
          </div>
          <div className="flex items-center gap-4">
            <span className="font-mono text-[11px] px-2 py-0.5 rounded bg-slate-200 dark:bg-slate-800">
              FastAPI • React • TypeScript • SQLite • Gemini
            </span>
          </div>
        </div>
      </footer>
    </div>
  );
};
