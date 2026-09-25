# Document Intake Assistant

A production-grade, full-stack conversational application that conducts guided legal-intake interviews to assemble a **Personal Wishes Document** (Last Will & Personal Directives), maintains structured JSON state as the single source of truth, and renders a real-time live preview of the formal draft document.

> **LEGAL NOTICE & DISCLAIMER:**  
> This application generates a **fictional draft document for demonstration and testing purposes only**. It does not provide legal advice, estate planning advice, or create binding statutory instruments.

---

## 🏛️ System Architecture

The application is structured as a full-stack monorepo with strict architectural separation of concerns:

```
document-intake-assistant/
├── backend/
│   ├── app/
│   │   ├── api/routes.py            # REST endpoints (/chat, /session, /reset, /state/manual-edit, /fixtures)
│   │   ├── config.py                # Environment and provider configuration
│   │   ├── models/                  # Pydantic schemas (State, Chat, API contracts)
│   │   │   ├── state.py             # PersonalWishesState (Single source of truth)
│   │   │   ├── chat.py              # ChatMessage schema & turn metadata
│   │   │   └── api.py               # Request/Response DTO contracts
│   │   ├── services/
│   │   │   ├── state_manager.py     # State mutation validation, delta tracking, conflict resolution
│   │   │   ├── document_generator.py# Formal legal draft generation (HTML & Markdown)
│   │   │   ├── fixtures.py          # Valid, ambiguous, and malformed evaluation fixtures
│   │   │   └── llm/                 # Pluggable LLM provider layer
│   │   │       ├── base.py          # BaseLLMProvider interface & extraction contract
│   │   │       ├── mock_provider.py # High-fidelity, deterministic offline pattern engine
│   │   │       ├── openai_provider.py# OpenAI structured output provider
│   │   │       ├── gemini_provider.py# Google Gemini SDK provider
│   │   │       └── factory.py       # Provider instantiation & automatic key fallback
│   │   └── main.py                  # FastAPI initialization, CORS, and error handlers
│   ├── tests/                       # Automated pytest suite (28 test cases)
│   ├── requirements.txt             # Python dependencies
│   ├── .env.example                 # Configuration template
│   └── pytest.ini                   # Pytest test runner settings
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── Chat/                # Conversational interview UI & Quick Test chips
│   │   │   ├── Preview/             # Real-time legal draft paper preview & state inspector
│   │   │   └── UI/                  # Modal & reusable elements
│   │   ├── services/api.ts          # Typed REST API client
│   │   ├── types/index.ts           # Shared TypeScript interfaces
│   │   ├── App.tsx                  # Split-screen responsive layout
│   │   └── index.css                # Parchment typography & Tailwind styling
│   ├── package.json
│   ├── vite.config.ts
│   └── tailwind.config.js
├── README.md                        # Setup and architecture documentation
├── AI_LOG.md                        # Candid log of prompts, iterations & corrections
└── PRODUCTION_NOTES.md              # Production hardening, scalability, and legal tech roadmap
```

---

## 🔑 Core Features & Design Principles

### 1. State Separation (Single Source of Truth)
- **Problem Solved:** LLM chat transcripts are unstructured, context-window-limited, and vulnerable to hallucination or drift.
- **Solution:** Structured state is maintained in an explicit Pydantic schema (`PersonalWishesState`).
- The LLM outputs only *proposed deltas*. The backend `StateManager` validates fields against strict schema constraints before committing any mutation.
- Unknown or unconfirmed values are explicitly represented as `None` / `null` rather than assumed or hallucinated.

### 2. Ambiguity & Conflict Handling
- When a user provides incomplete information (e.g., *"My brother is my executor"* without providing his name, or *"I have overseas property"* without confirming worldwide scope), the assistant detects the missing sub-fields, flags the ambiguity, and asks targeted follow-up questions.
- Handles multi-field input in any order (e.g. name, address, worldwide asset flag, and children status provided in a single prompt).

### 3. Corrections Without Regressions
- Users can correct previous details at any time (e.g., *"Actually, change my executor to my sister Sarah"* or *"Wait, I don't have children"*).
- The `StateManager` ensures child lists are safely purged if `has_children` is toggled to `false`, preserving domain invariants.

### 4. Zero-Dependency Deterministic Mock Mode
- Runs **100% offline out-of-the-box** using `MockLLMProvider`.
- No paid API keys or external network connections required.
- Easily toggleable to **OpenAI** (`gpt-4o-mini`) or **Gemini** (`gemini-1.5-flash`) by setting environment variables in `backend/.env`.

### 5. Split-Screen Real-Time Interface
- **Left Pane:** Conversational chat interface with quick test scenario chips, field extraction badges, and ambiguity warnings.
- **Right Pane:** 
  - **Live Draft Legal Document:** Formatted legal parchment view with prominent disclaimer banner, formal clauses, execution and attestation blocks, and live pending indicators.
  - **Structured State (JSON):** Real-time JSON viewer displaying the underlying single source of truth.
  - **Manual State Override:** Ability to directly edit the state to test bidirectional synchronization.

---

## 🚀 Quick Start Guide

### Prerequisites
- **Python**: 3.10+ (tested on Python 3.11)
- **Node.js**: 18+ (tested on Node v22)
- **npm** or **yarn**

---

### Step 1: Start the Backend

1. Navigate to the `backend/` directory:
   ```bash
   cd backend
   ```

2. (Optional) Create and activate a virtual environment:
   ```bash
   python -m venv venv
   # Windows:
   .\venv\Scripts\activate
   # macOS/Linux:
   source venv/bin/activate
   ```

3. Install backend dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Configure environment (optional - defaults to offline Mock mode):
   ```bash
   cp .env.example .env
   ```
   *(To use OpenAI or Gemini, set `LLM_PROVIDER=openai` or `LLM_PROVIDER=gemini` and enter your API key in `.env`).*

5. Run the FastAPI development server:
   ```bash
   python -m uvicorn app.main:app --reload --port 8000
   ```
   The backend API is accessible at `http://127.0.0.1:8000`.  
   Interactive Swagger documentation is available at `http://127.0.0.1:8000/docs`.

---

### Step 2: Start the Frontend

1. Open a new terminal and navigate to `frontend/`:
   ```bash
   cd frontend
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Start the Vite development server:
   ```bash
   npm run dev
   ```

4. Open your browser and navigate to:
   ```
   http://localhost:5173
   ```

---

## 🧪 Running Automated Tests

The backend includes a comprehensive automated test suite covering state validation, mock LLM heuristics, ambiguity detection, error recovery, document generation, and REST endpoints.

Run the test suite from the `backend/` directory:
```bash
cd backend
python -m pytest -v
```

### Test Suite Summary:
- `test_state_validation.py`: Tests initial state defaults, explicit unknowns (`None`), completion percentage, and Pydantic validation error raising.
- `test_state_manager.py`: Tests multi-field state updates, corrections, child dependency cleanup, malformed update rejection, and session resets.
- `test_mock_llm.py`: Tests single-turn multi-field parsing, ambiguity flagging on missing executor name, correction parsing, triggered fixtures, and sequential follow-up questions.
- `test_document_generator.py`: Tests mandatory fictional legal disclaimers, pending placeholder badges, and complete multi-clause document formatting.
- `test_api_routes.py`: Tests all FastAPI endpoints (`/health`, `/session`, `/chat`, `/reset`, `/state/manual-edit`, `/fixtures`).
- `test_error_handling.py`: Tests malformed model recovery, empty payload rejection (422), and resilience against state corruption.

---

## 🔌 Replacing Mock Provider with Real LLM Provider

The application uses the **Strategy Pattern** behind `BaseLLMProvider`:

```python
class BaseLLMProvider(ABC):
    @abstractmethod
    async def process_turn(
        self,
        user_message: str,
        history: List[ChatMessage],
        current_state: PersonalWishesState,
    ) -> LLMExtractionResult:
        pass
```

To switch to a live LLM:
1. Open `backend/.env`.
2. Set:
   ```env
   LLM_PROVIDER=openai
   OPENAI_API_KEY=sk-your-openai-api-key
   OPENAI_MODEL=gpt-4o-mini
   ```
   Or for Google Gemini:
   ```env
   LLM_PROVIDER=gemini
   GEMINI_API_KEY=your-gemini-api-key
   GEMINI_MODEL=gemini-1.5-flash
   ```
3. Restart the backend server. The application will automatically detect the configuration and route requests through the selected provider. If an API key is missing or invalid, it gracefully falls back to the deterministic mock provider.

---

## 📑 Additional Documentation

- [AI_LOG.md](AI_LOG.md): Comprehensive log of prompts, iterations, decisions, and outputs questioned/corrected during development.
- [PRODUCTION_NOTES.md](PRODUCTION_NOTES.md): Engineering roadmap for productionizing this system (data persistence, PII protection, audit logs, evaluation benchmarks, and legal compliance).
