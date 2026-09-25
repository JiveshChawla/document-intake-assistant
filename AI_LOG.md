# AI Development Log: Document Intake Assistant

**Candidate:** Engineering Candidate  
**Date:** September 2026  
**Project:** Document Intake Assistant (Wenup Technical Test)

---

## 1. Initial Prompt & System Architecture Design

### Initial System Prompt (LLM Extraction Contract)
```text
You are the Document Intake Assistant for a fictional "Personal Wishes Document".
Your role is to conduct an empathetic, professional legal-intake interview to collect:
1. full_name: Full legal name
2. home_address: Primary residential address
3. covers_worldwide_assets: Boolean (true for worldwide, false for domestic only)
4. has_children: Boolean (true if user has children, false if none)
5. children: Array of children's legal names (if has_children is true; empty array if false)
6. executor: Object with "name" and "relationship" (both must be gathered)
7. specific_gifts: Array of objects with "item" and "recipient"
8. additional_wishes: Array of strings (funeral preferences, memorial directives, etc.)

CRITICAL GUIDELINES:
- Separate state from conversation: Provide extracted updates in structured JSON.
- Never invent facts. If a value is unknown, represent it as null or omit it.
- Ask sensible follow-up questions when information is missing, unclear, or contradictory.
- If the user specifies an executor relationship (e.g. "my brother") but no name, or a name without relationship, flag this ambiguity and ask for the missing detail.
- Handle multi-field answers in any order.
- Respect corrections cleanly (e.g. "Actually, my executor is Sarah").
- Avoid repeatedly asking for information that has already been captured.
```

### Rationale & Design Decisions
- **Separation of State from Conversation:** Rather than asking an LLM to "rewrite the document" or track state inside its sliding context window, we treat the LLM as an extraction & conversational agent that returns proposed deltas. The backend Pydantic model (`PersonalWishesState`) remains the strict single source of truth.
- **Explicit Unknowns (`None`):** Rather than defaulting uncollected values to empty strings or placeholders, unconfirmed fields are explicitly `None`. This prevents downstream components from misinterpreting missing data as confirmed negative answers.

---

## 2. Notable Iterations & Decisions

### Iteration 1: Invariant Enforcement for Children State
- **Problem:** If a user first mentioned having children ("I have a son named Lucas"), and later issued a correction ("Actually, I don't have children"), a naive JSON merge would update `has_children: false` while leaving `children: ["Lucas"]` in the structured state.
- **Correction:** We added domain-level invariant validation to `StateManager.apply_validated_updates`:
  ```python
  elif field == "has_children":
      bool_val = bool(value) if not isinstance(value, str) else value.lower() in ["true", "yes"]
      working_data["has_children"] = bool_val
      actual_delta["has_children"] = bool_val
      # Domain invariant: If no children, purge children array
      if not bool_val:
          working_data["children"] = []
          actual_delta["children"] = []
  ```

### Iteration 2: Partial Executor Ambiguity
- **Problem:** Users commonly answer questions like *"Who would you like as executor?"* with relational answers: *"My brother"* or *"My friend John"*.
- **Questioned Output:** Initially, an unconstrained prompt might hallucinate a generic surname (e.g., matching the user's surname) or assume the relationship was a name.
- **Correction:** We decomposed the executor into `{ "name": Optional[str], "relationship": Optional[str] }`.
  - If only relationship is provided: Flag ambiguity `Executor name is missing` and prompt: *"What is your brother's full name?"*
  - If only name is provided: Flag ambiguity `Executor relationship is missing` and prompt: *"What is [Name]'s relationship to you?"*

### Iteration 3: Pluggable Fallback Provider (Zero-API-Key Resilience)
- **Problem:** Requirement specifies that access to a paid API is not required, yet candidates should demonstrate real LLM integration contracts.
- **Solution:** Designed the `BaseLLMProvider` abstract contract with a `MockLLMProvider`, `OpenAILLMProvider`, and `GeminiLLMProvider`. The `ProviderFactory` auto-detects credentials: if keys are missing or invalid, it gracefully falls back to `MockLLMProvider` without disruption.

---

## 3. Examples of Output Questioned and Corrected

### Case A: Regex Over-Capture in Mock Provider
- **Prompt:** `"I am Jane Doe living at 10 Downing St, London. I want worldwide coverage and I don't have children."`
- **First Model / Rule Output:** `full_name: "Jane Doe living at"`
- **Why It Was Questioned:** The case-insensitive regex `[A-Z][a-z]+(?:\s+[A-Z][a-z]+)+` greedily matched lowercase words following the name because `re.IGNORECASE` was active.
- **Correction Made:** Added positive lookaheads for delimiters (`living`, `residing`, `at`, `,`, `.`) and explicitly split on prepositional boundary markers before validating length.

### Case B: Boolean Coercion Security Flaw
- **Malformed Test Payload:** `{"covers_worldwide_assets": "INVALID_TYPE"}`
- **First Implementation Output:** `state["covers_worldwide_assets"] == False`
- **Why It Was Questioned:** The Python code was doing `value.lower() in ["true", "yes", "worldwide"]`. Because `"invalid_type"` is not in that list, it evaluated to `False` and silently set `covers_worldwide_assets: False`, turning a malformed type error into a confirmed domestic asset selection!
- **Correction Made:** Implemented strict bifurcation:
  ```python
  elif isinstance(value, str):
      v_lower = value.strip().lower()
      if v_lower in ["true", "yes", "worldwide"]:
          working_data["covers_worldwide_assets"] = True
      elif v_lower in ["false", "no", "domestic", "domestic only"]:
          working_data["covers_worldwide_assets"] = False
      else:
          validation_warnings.append(f"Invalid covers_worldwide_assets value: {value}")
  ```
  Malformed strings now trigger a validation warning and leave the field intact as `None`.

### Case C: Negation Conflict in Multi-Turn Parsing
- **User Input:** `"I want worldwide coverage and I don't have children."`
- **First Output:** `has_children: True`
- **Why It Was Questioned:** The regex pattern `have children` was matched inside `"don't have children"` because the negative check searched for `"don't have any children"`.
- **Correction Made:** Updated the negative regex to make `any` optional `r"\b(don't have (?:any )?children)\b"` and added negative lookbehinds on positive patterns.

### Case D: Rigid Street Keywords Failing International Addresses
- **User Feedback / Test:** Users typing addresses from non-English countries (e.g. `14 Rue de la Paix, 75002 Paris, France`, `Apartment 4B, Shibuya, Tokyo, Japan`, `Plot 42, Sector 18, Gurgaon, India`) were ignored because address extraction depended on English street markers (`Street`, `Road`, `Ave`, `London`, `New York`).
- **Correction Made:** Implemented conversational turn awareness (`_get_last_question_topic`). When the assistant asks for the residential address, the user's direct free-text response is captured as their address without artificial geographic or linguistic constraints, supporting addresses from any country worldwide.

### Case E: "Yes" to Children Causing Loops & Ambiguous Name Capture
- **User Feedback / Test:** Users answering simply `"Yes"` or `"Yes I do"` to `"Do you have any children?"` were ignored because the positive matcher required `"have children"`.
- **Correction Made:** Added direct affirmative recognition for children (`yes`, `yeah`, `yep`, `yes I do`, `sure`). If names are included in the same message (`Yes, Lucas and Emma`), both status and names are parsed in one turn. If only `"Yes"` is provided, `has_children` is marked `True` and the assistant seamlessly asks for children's names.

---

## 4. Key Takeaways
1. **Context-Aware Intent Disambiguation:** By tracking the conversational topic of the preceding assistant prompt (`last_topic`), the mock engine can accurately interpret terse user replies (`"Yes"`, `"Worldwide"`, `"Pierre and Sophie"`, `"Flat 4B, Tokyo"`) without requiring users to speak in rigid template sentences.
2. **Never rely on the LLM as the database:** LLMs are great reasoning and extraction engines, but horrible databases. Isolating state in a Pydantic schema and only applying validated deltas eliminated state drift and hallucinated data.
3. **Ambiguity must be explicit:** Making ambiguity a first-class citizen in the response model (`ambiguities: List[str]`) allows both the assistant and the UI to communicate uncertainties clearly to the user.
