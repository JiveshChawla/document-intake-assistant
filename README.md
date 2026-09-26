# Document Intake Assistant

[![FastAPI](https://img.shields.io/badge/FastAPI-0.110.0-009688?style=flat&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-18.2.0-61DAFB?style=flat&logo=react&logoColor=black)](https://react.dev)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.3-3178C6?style=flat&logo=typescript&logoColor=white)](https://www.typescriptlang.org)
[![Tailwind CSS](https://img.shields.io/badge/Tailwind_CSS-3.4-38B2AC?style=flat&logo=tailwind-css&logoColor=white)](https://tailwindcss.com)
[![SQLite](https://img.shields.io/badge/SQLite-SQLAlchemy-003B57?style=flat&logo=sqlite&logoColor=white)](https://www.sqlite.org)
[![Gemini](https://img.shields.io/badge/Google_Gemini-1.5_Flash-4285F4?style=flat&logo=google&logoColor=white)](https://ai.google.dev)
[![Pytest](https://img.shields.io/badge/Pytest-77%20Passed-green?style=flat&logo=pytest&logoColor=white)](https://docs.pytest.org)

**Live Production Deployment:** [🌐 View Live Application on Vercel](https://document-intake-assistant-seven.vercel.app/) 


A production-grade, enterprise legal-tech conversational intake assistant that conducts guided estate and testamentary interviews. It dynamically extracts user inputs into a validated **Personal Wishes Document** (Last Will & Personal Directives), maintains a single source of truth structured JSON state backed by SQLite persistence, and renders a live, real-time draft paper with isolated print/PDF export.

> **LEGAL NOTICE & DISCLAIMER:**  
> This application generates a **fictional draft document for demonstration and technical assessment purposes only**. It does not provide legal advice, estate planning advice, or create binding statutory instruments.

---

## 📸 Screenshots & Visual Walkthrough

Below are key views showcasing the user experience, real-time document drafting, and technical depth of the application:

### 1. Professional Landing Page
*High-end enterprise landing page featuring bold typography, vibrant accent badges, a live-turn mockup preview, and a 4-card feature value proposition grid.*

![Landing Page](./screenshots/landing-page.png)

---

### 2. Conversational Intake & Split-Screen Workspace
*Multi-turn conversational intake interface running side-by-side with the 3-tab workspace (Intake Completeness, Live Legal Paper Draft, and Structured JSON State).*

![Chat and Preview Workspace](./screenshots/chat-and-preview.png)

---

### 3. Non-Linear Mid-Interview Field Correction
*Proactive correction handling: The user updates their address mid-interview out of order, and the state manager instantly pivots and updates the field.*

![Mid-Interview Correction](./screenshots/mid-interview-edit.png)

---

### 4. Isolated Print / PDF Legal Export View
*Isolated print view: Suppresses all application UI chrome and formats the document on clean parchment-style serif typography with protected signature and witness blocks.*

![Print and PDF View](./screenshots/print-pdf-view.png)

---

## 🏛️ System Architecture

The application is structured as a full-stack monorepo featuring decoupled state management, pluggable LLM orchestration, SQLite persistence, and an enterprise split-screen frontend:

```plaintext
document-intake-assistant/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   └── routes.py            # REST endpoints (/chat, /session, /reset, /state/manual-edit, /fixtures)
│   │   ├── config.py                # Environment, model, and provider settings
│   │   ├── db/                      # SQLite Persistence Layer (SQLAlchemy ORM)
│   │   │   ├── models.py            # ConversationSession, ChatMessageModel, StructuredStateModel
│   │   │   └── session.py           # DB engine, sessionmaker, and table initialization
│   │   ├── models/                  # Pydantic Schemas (Single source of truth & contracts)
│   │   │   ├── state.py             # PersonalWishesState, Executor, Child models
│   │   │   ├── chat.py              # ChatMessage schema & turn metadata
│   │   │   └── api.py               # Request/Response DTO contracts
│   │   ├── services/
│   │   │   ├── state_manager.py     # State mutation validation, delta tracking, invariant protection
│   │   │   ├── document_generator.py# Formal legal draft generation (HTML & Markdown)
│   │   │   ├── fixtures.py          # Valid, ambiguous, and malformed evaluation fixtures
│   │   │   └── llm/                 # Pluggable LLM Provider Layer (Strategy Pattern)
│   │   │       ├── base.py          # BaseLLMProvider interface & extraction contract
│   │   │       ├── mock_provider.py # Deterministic offline pattern & intent routing engine
│   │   │       ├── openai_provider.py# OpenAI structured output provider
│   │   │       ├── gemini_provider.py# Google Gemini SDK provider with strict guardrails
│   │   │       └── factory.py       # Dynamic provider instantiation & automatic fallback
│   │   └── main.py                  # FastAPI app factory, CORS, and lifecycle handlers
│   ├── tests/                       # Automated pytest suite (77 tests, 100% passing)
│   │   ├── test_api_routes.py
│   │   ├── test_database.py
│   │   ├── test_document_generator.py
│   │   ├── test_error_handling.py
│   │   ├── test_input_validation_and_guardrails.py
│   │   ├── test_mock_llm.py
│   │   ├── test_non_linear_overrides.py
│   │   ├── test_state_manager.py
│   │   └── test_state_validation.py
│   ├── app.db                       # Local SQLite database file
│   ├── requirements.txt             # Python dependencies
│   ├── .env.example                 # Environment configuration template
│   └── pytest.ini                   # Pytest configuration
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── LandingPage.tsx      # Enterprise hero, feature showcase, and workflow guide
│   │   │   ├── Header.tsx           # Navbar: Overview, LLM, Progress, Inspect JSON, Reset, Theme
│   │   │   ├── Chat/                # Conversational interview UI & Quick Test chips
│   │   │   │   ├── ChatContainer.tsx
│   │   │   │   ├── MessageList.tsx
│   │   │   │   ├── MessageItem.tsx
│   │   │   │   ├── ChatInput.tsx
│   │   │   │   ├── TypingIndicator.tsx
│   │   │   │   └── QuickTestChips.tsx
│   │   │   ├── Preview/             # 3-Tab Workspace (Completeness, Legal Paper, JSON State)
│   │   │   │   ├── PreviewContainer.tsx
│   │   │   │   ├── ProgressTracker.tsx
│   │   │   │   ├── DocumentPreview.tsx
│   │   │   │   └── StateViewer.tsx
│   │   │   └── UI/
│   │   │       └── StateEditModal.tsx# Bidirectional manual state editor & validator
│   │   ├── context/
│   │   │   └── ThemeContext.tsx     # Light / Dark mode theme provider with localStorage memory
│   │   ├── services/
│   │   │   └── api.ts               # Typed REST client with error interception
│   │   ├── types/
│   │   │   └── index.ts             # Shared TypeScript models
│   │   ├── App.tsx                  # Root application router (Landing vs. Dashboard views)
│   │   ├── index.css                # Typography, parchment paper styling & isolated @media print rules
│   │   └── main.tsx
│   ├── package.json
│   ├── vite.config.ts
│   └── tailwind.config.js
├── vercel.json                      # Multi-service Vercel deployment configuration
├── README.md                        # Project documentation
├── AI_LOG.md                        # Development prompts, iterations, and corrections log
└── PRODUCTION_NOTES.md              # Production hardening, security, and scalability guide
```

---

## 🔑 Core Capabilities & Engineering Innovations

### State Separation & SQLite Persistence
- **Single Source of Truth:** Structured data is strictly isolated from unstructured chat history using the `PersonalWishesState` Pydantic model.
- **Relational Persistence:** Backed by SQLite (`app.db`) via SQLAlchemy. Conversation messages, turn timestamps, and validated structured JSON state persist across sessions and server restarts with zero in-memory data loss.
- **Deterministic Delta Validation:** The LLM produces candidate deltas, but only the backend `StateManager` commits changes to the database after verifying field invariants.

### Context-Aware Extraction & Guardrails
- **Turn-Specific Field Mapping:** The extraction engine evaluates what question the assistant just asked. When questioning the user about an executor, responses strictly map to the executor object (`name` and `relationship`) and never inadvertently alter `full_name`.
- **Strict Hallucination & Gibberish Rejection:** Inputs containing nonsensical strings or random keyboard mashes are rejected; the state field remains unconfirmed/empty and the assistant politely asks for valid clarification.
- **Universal Address Acceptance:** Robust address recognition accommodates global formats (European, North American, Asian) without rejecting valid international residences.

### Non-Linear Overrides & Mid-Interview Corrections
- **Proactive Edit Intent Detection:** Users are never locked into a rigid step-by-step sequence. At any point, a user can say *"Actually, change my address to London"* or *"Update my executor to Jane Doe"*.
- **Focus Shift State Machine:** The router detects the correction intent, acknowledges the requested modification, captures the new value, immediately updates the structured state, and seamlessly resumes incomplete required questions.
- **Dependency Invariant Protection:** If `has_children` is toggled from `true` to `false`, dependent children lists are automatically purged to prevent stale orphan data.

### Optional Fields Multi-Turn Handling
- **Specific Gifts & Additional Wishes:** If the assistant asks about specific gifts or wishes, affirmative answers (e.g., *"Yes, my vintage watch to my son"* or *"Yes"*) are captured accurately. If the user replies *"Yes"* without details, the assistant prompts them to specify rather than skipping ahead.

### High-End Modern Frontend & Design System
- **Hero & Landing Page:** High-impact landing page featuring bold gradient typography, vibrant accent badges, interactive live-turn mockup cards, and a 4-card feature value proposition grid.
- **Organized Tabbed Workspace (Right Panel):**
  - **Tab 1: Intake Completeness & Edit:** Progress bar, percentage gauge, missing field warnings, and inline edit cards.
  - **Tab 2: Live Document Draft:** Real-time formal parchment legal paper preview with serif typography, legal clauses, execution block, and raw Markdown source toggle.
  - **Tab 3: Structured JSON State:** Clean JSON tree inspector with direct manual payload editor modal.
- **Light & Dark Mode Support:** Theme toggle seamlessly switches between an elegant dark slate palette (`slate-900`/`slate-950`) with glowing violet accents and a vibrant enterprise light palette with localStorage memory.
- **Isolated Clean Print / PDF Export:** Dedicated `@media print` styling isolates the legal document container element, hides all UI chrome (chat sidebar, navigation headers, tabs, buttons, modals), un-constrains multi-page scroll viewports, and protects signature and witness blocks against awkward page splits.

---

## 🚀 Quick Start Guide

### Prerequisites
- **Python**: 3.10+ (tested on Python 3.11)
- **Node.js**: 18+ (tested on Node v20/v22)
- **npm** or **yarn**

---

### Step 1: Start the Backend Service

1. Open a terminal and navigate to `backend/`:
   ```bash
   cd backend
   ```

2. (Recommended) Create and activate a virtual environment:
   ```bash
   # Windows (PowerShell):
   python -m venv venv
   .\venv\Scripts\activate

   # macOS / Linux:
   python3 -m venv venv
   source venv/bin/activate
   ```

3. Install backend dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Configure environment variables:
   ```bash
   cp .env.example .env
   ```
   *(By default, `LLM_PROVIDER=mock` runs 100% offline with zero external dependencies. See the [LLM Provider Configuration](#-pluggable-llm-provider-configuration) section to enable Google Gemini or OpenAI).*

5. Start the FastAPI server:
   ```bash
   python -m uvicorn app.main:app --reload --port 8000
   ```
   - API Root: `http://127.0.0.1:8000`
   - Interactive Swagger Docs: `http://127.0.0.1:8000/docs`
   - SQLite Database created automatically at `backend/app.db`.

---

### Step 2: Start the Frontend Application

1. Open a second terminal and navigate to `frontend/`:
   ```bash
   cd frontend
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Launch Vite development server:
   ```bash
   npm run dev
   ```

4. Open your browser and navigate to:
   ```
   http://localhost:5173
   ```

---

## 🧪 Comprehensive Automated Test Suite

The backend contains **77 comprehensive pytest tests** testing state validation, database persistence, mock intent heuristics, non-linear overrides, and error resilience.

To execute the full test suite:
```bash
cd backend
python -m pytest -v
```

### Test Suite Coverage Breakdown:
| Test File | Test Count | Scope & Behaviors Tested |
| :--- | :---: | :--- |
| `test_api_routes.py` | 6 | REST endpoints (`/health`, `/session`, `/chat`, `/reset`, `/state/manual-edit`, `/fixtures`) |
| `test_database.py` | 6 | SQLite session creation, message history persistence, state recovery across reconnects |
| `test_document_generator.py` | 3 | Legal clause formatting, mandatory fictional disclaimers, Markdown/HTML fidelity |
| `test_error_handling.py` | 3 | Invalid payload handling, malformed JSON recovery, server exception resilience |
| `test_input_validation_and_guardrails.py` | 15 | Nonsensical/gibberish rejection, universal address formats, executor mapping integrity |
| `test_mock_llm.py` | 19 | Heuristic intent matching, multi-field capture, ambiguity detection, sequential flow |
| `test_non_linear_overrides.py` | 14 | Mid-interview field updates, focus shifting, out-of-order gift/wish capture |
| `test_state_manager.py` | 5 | Invariant enforcement, child list cleanup on toggle, delta application |
| `test_state_validation.py` | 6 | Pydantic schema validation, percentage computation, unknown field handling |
| **Total** | **77 Passed** | **Full system verification across all layers** |

To verify the frontend build:
```bash
cd frontend
npm run build
```

---

## 🔌 Pluggable LLM Provider Configuration

The application implements the **Strategy Pattern** via `BaseLLMProvider`. You can switch providers at any time without changing application logic:

### Offline Deterministic Mock (Default)
Runs with no external API calls, offline-ready, and ideal for automated testing and CI:
```env
LLM_PROVIDER=mock
```

### Google Gemini (Recommended for Production LLM)
Uses the official Google GenAI SDK with structured prompt schemas and guardrails:
```env
LLM_PROVIDER=gemini
GEMINI_API_KEY=AIzaSy...your-gemini-api-key
GEMINI_MODEL=gemini-1.5-flash
```

### OpenAI
Supports structured outputs via OpenAI JSON mode:
```env
LLM_PROVIDER=openai
OPENAI_API_KEY=sk-...your-openai-api-key
OPENAI_MODEL=gpt-4o-mini
```

*Note: If a cloud provider's API key is absent or invalid, the backend automatically logs a warning and falls back to the deterministic Mock engine.*

---

## 📡 REST API Reference

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/health` | Service health check and active provider status |
| `GET` | `/session` | Retrieves current session messages, structured state, and generated document |
| `POST` | `/chat` | Submits user response, processes extraction, updates SQLite state, and returns response |
| `POST` | `/reset` | Clears conversation history and resets structured state to initial defaults |
| `PUT` | `/state/manual-edit` | Direct manual override of structured state JSON with validation |
| `GET` | `/fixtures` | Lists pre-configured test fixtures (valid, ambiguous, malformed inputs) |

---

## 📑 Additional Documentation

- [AI_LOG.md](AI_LOG.md): Candid log of all design prompts, iterations, architectural refactors, and corrections made during development.
- [PRODUCTION_NOTES.md](PRODUCTION_NOTES.md): Production hardening roadmap covering data security, HIPAA/GDPR considerations, audit logging, and legal-tech compliance.

---

## ⚖️ License & Attribution

Distributed under the MIT License for technical assessment and demonstration purposes. See [PRODUCTION_NOTES.md](PRODUCTION_NOTES.md) for enterprise deployment guidelines.
