# MEMORY BRIDGE — MASTER BUILD CONTEXT FOR ANTIGRAVITY

## 0. READ THIS FIRST

You are building a **working, public, AI-native MVP prototype** called **Memory Bridge** for a Product Management graduation project based on a Google Photos retrieval problem.

This document is the **single implementation context / source of truth for the MVP build**.

### What you are expected to do

Read this entire document first. Then:

1. Understand the product problem and research evidence.
2. Understand exactly what the MVP is supposed to demonstrate.
3. Propose the implementation plan only if there is a real ambiguity.
4. Otherwise proceed with implementation in the sequence defined below.
5. Build a **fully working end-to-end prototype**, not a set of static mockups.
6. Keep the implementation bounded to the stated MVP scope.
7. Make the product deployable as:
   - **Next.js frontend → Vercel**
   - **FastAPI backend → Render**
8. Ensure the final public URL can be used by an external evaluator without requiring a developer to explain how it works.

### Important product boundary

This is **not** an official Google Photos product and must never be presented as one.

The UI must contain a small statement such as:

> **Prototype concept — not a Google product**

Do **not** attempt unrestricted access to a user's complete Google Photos library.

For this graduation-project MVP, use a **controlled demo photo library with known ground-truth metadata**.

---

# 1. PROJECT CONTEXT

The Product Management project asks us to investigate a specific retrieval problem in Google Photos:

> **Where and why does retrieval break when a user remembers that a photo exists but cannot precisely describe enough details to retrieve it efficiently?**

The strategic product goal is:

> **Increase the percentage of users who successfully retrieve a photo they remember but cannot precisely describe when they start searching.**

This is intentionally **not** a generic "improve photo search" problem.

The project focuses on the **recovery step after partial/incomplete memory**.

Google Photos already supports natural-language and AI-assisted retrieval experiences, so the MVP should not simply recreate a generic conversational search box.

The differentiated hypothesis is:

> When users remember a photo through contextual fragments but lack precise retrieval details, an AI-guided clarification layer that identifies and requests the most useful missing clue can reduce retrieval effort and improve successful identification compared with unguided search.

The core product promise is:

> **Turn an incomplete memory into the next useful retrieval clue.**

---

# 2. WHY THIS PROBLEM WAS SELECTED

Across the project research, a recurring pattern emerged:

### What users remember

Users often retain **contextual meaning**, such as:

- people;
- places;
- events;
- moments;
- approximate time;
- visual/contextual details;
- why the photo mattered.

### What users often do not remember

They may lack **retrieval precision**, such as:

- exact date;
- exact time;
- exact location;
- album/folder;
- filename;
- exact text;
- other highly discriminating details.

### What happens next

When the first retrieval attempt is insufficient, users often compensate manually by:

- changing search wording;
- adding remembered details;
- browsing the timeline;
- checking albums/folders/people;
- trying another search method;
- continuing to search without a clear next step.

The product opportunity is therefore not "make the user type more."

It is to help the system answer:

> **Given what the user already remembers, what is the most useful next clue to ask for?**

---

# 3. RESEARCH EVIDENCE

## 3.1 Directional survey

Final survey:

- **56 total responses**
- **44 respondents reported the target retrieval situation**
- The 44-incident subset is the main denominator for behavior-oriented analysis.

The survey is **directional**, not population-representative.

Do NOT claim that these percentages describe all Google Photos users.

Important signals from the research sample:

- contextual clues such as people, place and event were frequently remembered;
- exact date/time/location were frequently missing;
- many respondents did not report immediate first-attempt resolution;
- changing search words and manual browsing were common recovery behaviors;
- personal memories such as family/friends, moments and events dominated retrieval targets.

More detailed final-sample numbers used in the PM analysis:

### Among the 44 relevant retrieval incidents

Remembered clues:

- Person/people: **24 (54.5%)**
- Event/occasion: **16 (36.4%)**
- Place: **14 (31.8%)**
- Approximate time/year: **7 (15.9%)**
- Why it mattered: 2
- Text: 2
- Object: 1
- Visual: 1
- Something else: 1

A contextual clue set of at least one of **Person + Place + Event** was present in **37/44 (84.1%)**.

Frequently forgotten details:

- Exact date: **27 (61.4%)**
- Exact time: **16 (36.4%)**
- Exact location: **12 (27.3%)**
- Where stored: 8
- Person name: 8
- Filename: 7
- Album/folder: 5
- Exact text: 5

At least one of exact date/time/location was missing for **37/44 (84.1%)**.

Both contextual memory and missing precision were present in **33/44 (75%)**.

### Retrieval outcome

- Immediate: **16 (36.4%)**
- After refining: **20 (45.5%)**
- Workaround: 2
- Not found: 2
- Not sure: 4

Because some survey questions represent slightly different stages, do not construct an artificially precise funnel from these values.

### First-attempt / recovery behavior

Across the 44 incidents:

- 27/44 (**61.4%**) did not report immediate first-attempt resolution.
- 18 changed search words.
- 10 used the timeline.
- 9 used albums/folders.
- 9 added a person.
- 8 added approximate date/time.
- 8 used a different search method.
- 6 added a place.
- 4 tried another app/tool.
- 2 gave up.
- 2 tried later.

Among the 27 non-immediate cases:

- 13 changed words (**48.1%**)
- 9 used the timeline (**33.3%**)

Time spent:

- <1 min: 8
- 1–5 min: 13
- 5–15 min: 11
- 15–30 min: 4
- >30 min: 7
- Never found: 1

Thus:

- 23/44 took **5+ minutes**
- 12/44 took **15+ minutes or never found**
- 8/44 took **>30 minutes or never found**

Retrieval targets:

- Family/friend: 17
- Particular moment/memory: 10
- Event/occasion: 9
- Trip/vacation: 4
- Screenshot: 3
- Document/receipt/prescription: 1

The first three categories account for **36/44 (81.8%)**.

### Survey interpretation

The survey suggests that the problem is not simply "users cannot remember their photo."

Rather, many users remember **meaningful context** while missing **precision**, then compensate with trial-and-error search.

---

## 3.2 Interviews

Six incident-based interviews were conducted.

### Analytical rule

Participants A–E are the **primary analytical set**.

Participant F is retained in the raw record but contains:

- a material outcome contradiction; and
- insufficient detail in some fields.

F may be retained as supplementary/raw evidence where a response is clear, but should **not drive the primary problem diagnosis or MVP design**.

### Interview methodology

The research sequence was:

**AI discovery → directional survey → incident interviews → MVP testing**

The interviews were:

- semi-structured;
- incident-based;
- purposively sampled for behavioral relevance;
- focused on a real photo/document retrieval experience;
- designed to reconstruct the sequence of:
  memory → clues recalled → first attempt → failure/friction → recovery → outcome.

### Primary A–E findings

Across A–E:

- partial/incomplete memory was repeatedly present;
- exact retrieval details were often missing;
- first attempts did not return the exact target in the captured incidents;
- users added details or changed approach;
- manual scrolling / continued searching was used as fallback;
- users expressed a desire for the system to suggest useful information for retrieval.

Representative participant language from the research record:

> “Something like a feature from google photos to find partially remembered phots.”

> “Photos should suggest me the related important information required to retrieve the exact one.”

> “I want the technology to solve my memory issuees.”

> “...it should undersand and retrieve the exact one.”

When these are shown externally, preserve them as participant quotes and do not silently correct wording.

### Primary interview hypothesis signals

For the five primary interviews A–E:

- Memory → query translation: **4/5 supported**
- Missing precision: **5/5 supported**
- Recovery / next-step behavior: **4/5 supported**
- Clear recognition-method evidence: **0/5 clearly established**

The recognition hypothesis therefore remains less certain and should be explored through MVP testing.

---

# 4. TARGET USER

## Provisional behavioral segment

**Context-rich, precision-poor photo retrievers**

These users:

1. know or strongly believe a specific photo exists;
2. can describe contextual fragments;
3. lack one or more high-value precise details;
4. experience friction after the initial retrieval attempt;
5. resort to iterative searching, manual browsing or alternative methods.

This is a **behavioral segment**, not a demographic segment.

---

# 5. TARGET SCENARIO

Canonical example:

> “Find the photo of me with my sister at my college farewell around 2022. I don't remember the exact date.”

The user knows:

- person;
- event;
- approximate time;

but does not know:

- exact date;
- possibly location.

The MVP should demonstrate that the system can use the remembered information to determine a **useful missing discriminator** and ask a focused question.

---

# 6. ROOT-CAUSE HYPOTHESIS

The research supports this PM interpretation:

> **Users often retain contextual fragments but cannot reliably operationalize the missing discriminating details needed for efficient retrieval, and the current experience does not consistently guide them toward the most useful next clue.**

Important:

This is a **research-derived interpretation / hypothesis**.

It is NOT permission to claim anything about Google Photos' internal search implementation.

Do not claim:

- Google Photos requires exact tags.
- OCR is the technical root cause.
- Ask Photos cannot handle contextual queries.
- Google Photos' current ranking algorithm is responsible.
- A specific metadata field is always missing.

Those claims are outside the evidence.

---

# 7. PRODUCT CONCEPT

## Name

**Memory Bridge**

## Core promise

> **Turn an incomplete memory into the next useful retrieval clue.**

## Core idea

Memory Bridge is an **AI-guided retrieval recovery layer**.

It does five key things:

1. interprets the user's partial memory;
2. structures the clues the user already knows;
3. identifies useful missing clue dimensions;
4. asks at most two focused clarifying questions;
5. re-ranks candidate photos after each answer.

The product should then shift from **search formulation** to **visual recognition**.

---

# 8. WHAT MEMORY BRIDGE IS — AND IS NOT

## It IS

- a focused retrieval-recovery intervention;
- AI-assisted memory interpretation;
- missing-clue detection;
- bounded clarification;
- candidate re-ranking;
- recognition-oriented results;
- measurable against a baseline.

## It is NOT

- a generic chatbot;
- an official Google Photos feature;
- a complete Google Photos clone;
- a replacement for Google Photos search;
- a full face-recognition platform;
- a production-scale OCR platform;
- an account-sync system;
- a mobile app;
- a backup/sync solution.

---

# 9. MVP USER EXPERIENCE

## Screen 1 — Memory input

Headline:

> **What do you remember about the photo?**

Supporting copy:

> You don't need the exact date, filename or album. Start with whatever you remember.

Components:

- large multiline text input;
- one example prompt;
- **Find my memory** CTA;
- **Try a sample task** option.

Footer:

> Prototype concept — not a Google product

---

## Screen 2 — Understanding your memory

Header:

> **Here's what I understood**

Show human-readable cards/chips for:

- People
- Place
- Event
- Time
- Other clues

Then:

> **What is missing**

Example:

- People: Sister
- Event: College farewell
- Approx. year: 2022
- Location: Unknown
- Exact date: Unknown

Do not show raw JSON.

Use qualitative confidence only:

- High
- Medium
- Low
- Unknown

No fake probability such as "93% sure".

CTA:

> **Continue**

---

## Screen 3 — Guided clarification

Headline:

> **One detail could narrow this down**

Example question:

> “Do you remember which city this was in?”

Options might be:

- Hyderabad
- Bengaluru
- Other
- Not sure

Also provide:

> **Skip this question**

The exact options must come from the actual photo corpus where possible.

Do not ask for a clue that is already known.

---

## Screen 4 — Refinement

Headline / status:

> **Narrowing your memory…**

Show candidate reduction, for example:

> 48 possible memories → 12 likely memories

This should reflect real candidate counts from the backend.

Do not fake values.

---

## Screen 5 — Results

Headline:

> **I found 12 likely memories**

Show visual cards with:

- thumbnail;
- Strong match / Likely match;
- matched clue chips.

Example:

> Sister · Farewell · 2022

Actions:

- **This is the one**
- **Not this one**

Do not display exact confidence percentages.

---

## Screen 6 — Success

Headline:

> **Memory found**

Show:

- selected image;
- clues that helped;
- elapsed time;
- number of clarification questions;
- number of major retrieval actions.

Example:

> Found using: Sister + Farewell + 2022 + Hyderabad

CTA:

> **Try another memory**

---

## Screen 7 — Graceful fallback

Headline:

> **I couldn't narrow this down confidently**

Copy:

> Here are the strongest matching memories from what you told me.

Actions:

- show candidates;
- add more context / start over.

If the system cannot make a useful next clue decision, it must stop asking questions.

---

## Screen 8 — Baseline mode

Headline:

> **Search your memory**

Components:

- simple text field;
- search button;
- same corpus.

Baseline behavior:

- direct retrieval;
- no proactive clue questions;
- same result card style.

This exists so the evaluator can compare:

**unguided search vs guided retrieval recovery**

---

## Screen 9 — Optional evaluator / benchmark mode

May be hidden from normal users or made accessible via a clearly labelled evaluation route.

Can show:

- task ID;
- timer;
- hidden target information in evaluator-only context;
- success/failure logging.

The target image must remain hidden from the participant before selection.

---

# 10. PRIMARY PRODUCT FLOW

The canonical end-to-end flow is:

```text
User memory
    ↓
Memory parsing
    ↓
Remembered clues extracted
    ↓
Missing / uncertain clues identified
    ↓
Initial candidate retrieval
    ↓
Best missing discriminator selected
    ↓
One focused clarification question
    ↓
User answer / Not sure / Skip
    ↓
Candidate re-ranking
    ↓
Optional second clarification
    ↓
Likely memory results
    ↓
User recognition
    ↓
Success OR graceful fallback
```

Maximum clarification questions:

> **2**

Never turn the experience into a long interview.

---

# 11. INTELLIGENCE DESIGN

## Principle

The LLM provides **bounded reasoning**, not full control of the retrieval system.

Deterministic application code should control:

- session state;
- candidate retrieval;
- ranking;
- candidate counts;
- question limits;
- telemetry;
- success/failure state.

The AI layer should help with:

- structuring the user's natural-language memory;
- understanding clue types;
- deciding which missing clue dimension may be useful;
- generating a human-readable question.

This separation is important for reliability and testability.

---

# 12. MEMORY PARSING

Input:

```json
{
  "memory": "Find my sister at my college farewell around 2022. I don't remember the date."
}
```

Expected structured output:

```json
{
  "people": ["sister"],
  "places": [],
  "events": ["college farewell"],
  "time": {
    "type": "approximate",
    "value": "2022"
  },
  "objects": [],
  "visual": [],
  "text": [],
  "relationship_context": [],
  "missing_clues": ["location", "exact_date"],
  "memory_confidence": "high"
}
```

### Parser rules

The parser MUST:

- extract what the user actually stated or clearly implied;
- distinguish exact vs approximate vs relative time;
- mark unknown dimensions as missing/unknown;
- avoid invented dates;
- avoid invented people;
- avoid invented locations;
- avoid invented filenames;
- return only the agreed schema.

---

# 13. PHOTO DATASET

## Use a controlled demo library

Create approximately:

> **40–50 curated images**

Suggested mix:

- 12 family/friends
- 10 events/occasions
- 8 trips
- 8 personal moments
- 4–5 screenshots/documents

Every benchmark task must have a known target image.

The images can be synthetic/demo assets or otherwise safe-to-use test images.

Do not use personal/private user photo content in the public demo without explicit permission.

---

# 14. PHOTO METADATA MODEL

Each image should have structured metadata.

Example:

```json
{
  "id": "photo_021",
  "image_url": "/photos/photo_021.jpg",
  "date": "2022-11-18",
  "year": 2022,
  "location": "Hyderabad",
  "people": ["sister"],
  "event": ["college farewell"],
  "objects": ["certificate"],
  "visual_description": "A person standing with her sister at a college farewell",
  "text": "Farewell 2022",
  "embedding": [0.0]
}
```

Fields may be null.

Do not force metadata that does not exist.

Every benchmark target must have enough metadata to support its retrieval task.

---

# 15. SEARCH / RETRIEVAL LOGIC

## Candidate retrieval

The system should combine:

- semantic similarity;
- structured clue matching;
- approximate time compatibility;
- people;
- event;
- location;
- visual/context match where useful.

Example prototype score:

```text
final_score =
0.40 * semantic_similarity +
0.20 * people_match +
0.15 * event_match +
0.10 * time_match +
0.10 * location_match +
0.05 * visual_context_match
```

These weights are **prototype heuristics**, not claims about production Google Photos ranking.

Make the weights configurable.

---

# 16. EMBEDDINGS

Recommended approach:

- precompute image embeddings offline;
- store them with photo metadata;
- compute query/memory representation as needed;
- use cosine similarity or another simple normalized similarity method.

Gemini's current embedding capabilities may be used where practical.

For the fastest reliable MVP:

> **precompute the controlled corpus embeddings and avoid generating them repeatedly during every search.**

If embedding integration becomes a blocker, the application must have a deterministic metadata-search fallback.

---

# 17. MISSING-CLUE REASONER

Candidate clue dimensions:

- people
- place
- event
- time
- object
- visual
- text

The reasoner should evaluate each **currently missing or uncertain dimension**.

### Rules

1. Only consider missing or uncertain dimensions.
2. Do not ask for a clue already known.
3. Estimate how much the clue could narrow the actual corpus.
4. Prefer a clue that meaningfully narrows candidates.
5. Prefer answerable questions.
6. Minimize user effort.
7. Never ask more than two clarification questions.
8. Always provide **Not sure**.
9. Do not repeat the same clue dimension.
10. If no useful clue exists, stop asking and show fallback candidates.

### Prototype information-gain heuristic

```text
information_gain =
candidate_count_before - expected_candidate_count_after
```

This is a prototype heuristic.

Do not label it as advanced information theory.

---

# 18. CLARIFICATION QUESTION GENERATION

The system should generate questions that are:

- short;
- specific;
- easy to answer;
- directly connected to the current candidates.

Good:

> “Do you remember which city this was in?”

Good:

> “Was this before or after 2023?”

Poor:

> “Can you provide more details?”

Poor:

> “What else can you tell me?”

Poor:

> “Please provide all missing metadata.”

The UI should make the question feel useful:

> **One detail could narrow this down**

---

# 19. RESULT PRESENTATION

The user should not have to trust an opaque model.

For each candidate, display supporting clues such as:

> Sister · Farewell · 2022

Use:

- Strong match
- Likely match

Do not use:

- 97.43% confidence
- Definitely the correct photo
- Guaranteed match

The result experience is intentionally designed to support **recognition**.

---

# 20. BASELINE VS TREATMENT

## Baseline

The user enters the same memory into a simple search interface.

The system:

- searches the same corpus;
- does not ask proactive clarification questions;
- returns results.

## Treatment — Memory Bridge

The user gets:

- memory extraction;
- missing-clue identification;
- guided clarification;
- candidate re-ranking;
- visual recognition.

The corpus and benchmark tasks must remain the same.

The purpose is to determine whether the intervention changes:

- successful retrieval;
- time;
- effort;
- recovery behavior.

---

# 21. TEST CORPUS / BENCHMARK TASKS

Create benchmark tasks with hidden ground truth.

Example:

### Task

User-facing:

> Find the photo of your sister at your college farewell around 2022. You do not remember the exact date.

Hidden ground truth:

```json
{
  "target_id": "photo_021",
  "remembered": ["sister", "college farewell", "2022"],
  "missing": ["exact date", "location"]
}
```

Create a diverse set of tasks across:

- person-heavy memories;
- event-heavy memories;
- place-heavy memories;
- approximate-time memories;
- family/friend moments;
- trips;
- screenshots/documents.

Do not make every task solvable with the same missing clue.

---

# 22. EVALUATION METRICS

## North-star / primary metric

### Successful retrieval rate

```text
successful retrievals / attempted retrieval tasks
```

This is the main product outcome.

## Secondary metrics

- median time-to-retrieval;
- number of clarification steps;
- number of user-generated reformulations;
- manual browsing/fallback rate;
- abandonment rate.

## Diagnostic metrics

### AI clue acceptance rate

```text
accepted suggested clues / suggested clues
```

### Candidate reduction

```text
candidate count before clue - candidate count after clue
```

### Retrieval efficiency

```text
successful retrieval / number of major retrieval actions
```

Also log:

- selected result rank;
- clue accepted/skipped;
- whether the question was understood;
- whether the question was perceived as helpful/annoying;
- whether candidate quality improved after clarification.

---

# 23. USER TESTING

Minimum requirement:

> **3 target users**

Prefer more where available, but do not claim statistical significance from a tiny prototype sample.

Test users who resemble the behavioral segment:

- know the target exists;
- remember some context;
- do not know all exact retrieval details.

### Test design

Run comparable tasks under:

1. Baseline
2. Memory Bridge treatment

Capture:

- completion;
- target identified or not;
- time;
- actions;
- fallback;
- abandonment;
- qualitative reaction.

### What to watch for

- Was the suggested clue actually helpful?
- Did the user understand why the question was being asked?
- Were the options easy to answer from memory?
- Did the candidate set get better?
- Did the user prefer direct browsing?
- Did the AI ask annoying or repetitive questions?
- Did the user reach the correct result but fail to recognize it?

---

# 24. MVP ITERATION RULES

Change the product after testing when:

- users frequently reject/skip the suggested clue;
- questions feel intrusive;
- questions repeat;
- candidate quality worsens after clarification;
- candidate counts do not change meaningfully;
- users do not understand the purpose of a question;
- users still need excessive manual browsing;
- users reach results but cannot recognize the intended photo.

Do not change the product merely because one participant expresses a preference.

Look for repeated behavioral evidence.

---

# 25. API CONTRACT

## `GET /healthz`

Response:

```json
{
  "status": "ok"
}
```

---

## `POST /api/memory/parse`

Input:

```json
{
  "memory": "Find my sister at my college farewell around 2022"
}
```

Output:

```json
{
  "memory": {
    "people": ["sister"],
    "places": [],
    "events": ["college farewell"],
    "time": {
      "type": "approximate",
      "value": "2022"
    },
    "objects": [],
    "visual": [],
    "text": [],
    "relationship_context": [],
    "missing_clues": ["location", "exact_date"],
    "memory_confidence": "high"
  }
}
```

---

## `POST /api/memory/candidates`

Input:

```json
{
  "memory": {},
  "additional_clues": {}
}
```

Output:

```json
{
  "candidate_count": 12,
  "results": [
    {
      "photo_id": "photo_021",
      "score": 0.84,
      "matched_clues": ["sister", "farewell", "2022"]
    }
  ]
}
```

The UI may translate scores into human-readable labels but must not present raw score values as certainty.

---

## `POST /api/memory/next-clue`

Input:

```json
{
  "memory": {},
  "candidate_ids": ["photo_1", "photo_2"]
}
```

Output:

```json
{
  "clue_dimension": "location",
  "question": "Do you remember which city this was in?",
  "options": [
    "Hyderabad",
    "Bengaluru",
    "Other",
    "Not sure"
  ]
}
```

---

## `POST /api/session/event`

Input:

```json
{
  "session_id": "session_123",
  "event": "clue_accepted",
  "metadata": {}
}
```

---

# 26. SESSION STATE

Maintain:

```json
{
  "session_id": "session_123",
  "initial_memory": "Find my sister at my college farewell around 2022",
  "parsed_memory": {},
  "asked_clues": [],
  "accepted_clues": {},
  "candidate_count_history": [],
  "selected_photo_id": null,
  "status": "active"
}
```

Supported status values:

- active
- success
- fallback
- abandoned

---

# 27. TELEMETRY

Minimum events:

- `session_started`
- `memory_submitted`
- `memory_parsed`
- `clue_suggested`
- `clue_accepted`
- `clue_rejected`
- `results_shown`
- `candidate_opened`
- `retrieval_success`
- `retrieval_failed`
- `fallback_shown`
- `session_abandoned`

Do not capture private photo content beyond what is required for the controlled benchmark.

Avoid logging sensitive raw user text unnecessarily.

---

# 28. TECHNICAL ARCHITECTURE

Recommended:

```text
Browser
   |
   v
Next.js + React + TypeScript
(Vercel)
   |
   | HTTPS / JSON
   v
FastAPI backend
(Render)
   |
   +--------------------+
   |                    |
   v                    v
Gemini API          Photo index / DB
                       |
                       +-- metadata
                       +-- embeddings
                       +-- image URLs
```

---

# 29. RECOMMENDED TECH STACK

## Frontend

- Next.js
- TypeScript
- React
- Tailwind CSS or lightweight custom CSS

## Backend

- Python 3.x
- FastAPI
- Pydantic
- Uvicorn

## AI

- Gemini API for structured memory parsing and bounded reasoning;
- Gemini embeddings where practical.

## Persistence

Preferred:

- Supabase Postgres
- pgvector
- Supabase Storage or safe public/static image hosting

Fastest fallback:

- JSON metadata;
- precomputed embeddings;
- in-memory index.

The MVP should be able to run reliably without introducing unnecessary infrastructure.

---

# 30. PROJECT STRUCTURE

Create approximately:

```text
/memory-bridge
  /frontend
  /backend
  /data
    /photos
    photos.json
  /scripts
  /tests
  README.md
```

Suggested backend organization:

```text
/backend
  main.py
  requirements.txt
  /app
    /api
    /models
    /services
    /retrieval
    /ai
    /telemetry
```

Suggested frontend organization:

```text
/frontend
  package.json
  /app
  /components
  /lib
  /public
```

Keep the structure simple enough for a graduation-project MVP.

---

# 31. ENVIRONMENT VARIABLES

Backend:

```text
GEMINI_API_KEY=
GEMINI_TEXT_MODEL=
GEMINI_EMBEDDING_MODEL=
DATABASE_URL=
SUPABASE_URL=
SUPABASE_SERVICE_ROLE_KEY=
CORS_ORIGIN=
```

Frontend:

```text
NEXT_PUBLIC_API_URL=
```

Never place private server credentials in client-side code.

---

# 32. DEPLOYMENT

## Backend — Render

Use a Python web service.

Typical commands:

Build:

```text
pip install -r requirements.txt
```

Start:

```text
uvicorn main:app --host 0.0.0.0 --port $PORT
```

Configure required environment variables.

Expose:

```text
/healthz
```

---

## Frontend — Vercel

Deploy the Next.js application.

Configure:

```text
NEXT_PUBLIC_API_URL=https://<render-service>.onrender.com
```

Backend CORS should allow the deployed Vercel domain.

---

# 33. PRIVACY / SECURITY

Do not:

- store Google login credentials;
- request broad Google Photos account access;
- expose server API keys;
- use private photos in the public demo without permission;
- log unnecessary sensitive photo content.

Use only the controlled benchmark library for the primary evaluation.

---

# 34. GOOGLE PHOTOS INTEGRATION BOUNDARY

The public Google Photos API/access model has constraints.

For this project:

> **Do not attempt unrestricted full-library Google Photos integration.**

The prototype should operate on:

- a controlled demo library; or
- later, optionally, explicitly user-selected media using supported Google Photos mechanisms.

That is outside the first MVP implementation.

---

# 35. ERROR HANDLING

## Gemini fails

Show a recoverable message.

Do not show stack traces.

Allow retry.

## Embeddings/search fail

Fall back to deterministic metadata search.

Do not crash the experience.

## No confident results

Show:

> **I couldn't narrow this down confidently**

Then present strongest candidates or allow restart.

## Backend unavailable

Show a simple human-readable error and retry.

---

# 36. ACCESSIBILITY / UI QUALITY

Use a clean visual language inspired by Google Photos without copying its interface.

Requirements:

- strong contrast;
- readable typography;
- color must not be the sole indicator of state;
- responsive layout;
- keyboard-friendly controls;
- clear button states;
- no tiny body text;
- limited visual clutter;
- Google colors may be used only as accents.

Interaction principles:

- one major action per screen;
- no long forms;
- max two clarification rounds;
- plain language;
- always include Not sure;
- explain why a question is useful.

---

# 37. CRITICAL ACCEPTANCE CRITERIA

The MVP is not complete until all of the following work:

### Functional

- user can enter vague memory;
- system parses it;
- remembered clues are displayed;
- missing clues are displayed;
- system can ask a relevant missing-clue question;
- user can answer / choose Not sure / skip;
- candidate ranking changes after additional clues;
- results display real demo images;
- user can select the target;
- success state is shown;
- fallback state works;
- baseline mode works.

### Measurement

- session events are recorded;
- time-to-retrieval can be measured;
- clarification count can be measured;
- candidate count before/after clue can be measured;
- success/failure can be logged.

### Engineering

- backend health endpoint works;
- frontend builds successfully;
- API tests pass;
- core unit tests pass;
- browser smoke test passes;
- production frontend communicates with production backend.

### UX

- product is understandable without live explanation;
- no fake confidence percentages;
- no misleading Google branding;
- no accidental private-data access;
- interface is responsive and polished.

---

# 38. BROWSER SMOKE TEST

Before calling the MVP complete, verify:

1. Landing page loads.
2. Sample task works.
3. Memory parsing works.
4. Remembered/missing clues appear.
5. Missing-clue question appears where appropriate.
6. User can answer.
7. Candidate count changes.
8. Results display.
9. User can select intended photo.
10. Success state appears.
11. Baseline mode works.
12. Fallback works.
13. Error recovery works.

Run the test against the **actual deployed public environment**, not only localhost.

---

# 39. TESTABILITY REQUIREMENTS

The prototype must be easy to demonstrate.

Include:

## Sample task

A one-click "Try a sample task" that loads a representative vague memory.

Example:

> “Find the photo of me with my sister at my college farewell around 2022. I don't remember the exact date.”

## Reset

Provide:

> Try another memory

## Reproducibility

The same benchmark task should map to the same known target.

Avoid nondeterministic behavior that makes testing impossible.

---

# 40. DEMO MODE REQUIREMENT

For evaluation, it should be possible to demonstrate the product in approximately 2–3 minutes.

Ideal demo sequence:

```text
1. Enter vague memory
2. Show remembered clues
3. Show missing clue
4. Ask one useful question
5. Answer it
6. Show candidate reduction
7. Show visually ranked results
8. Select target
9. Show success + retrieval time
10. Optionally repeat with baseline
```

The product must make the **mechanism** visible.

The evaluator should be able to see:

> partial memory → useful next clue → narrowed candidate set → recognition

---

# 41. PRODUCT SUCCESS STORY

The MVP is designed to test this hypothesis:

### Without Memory Bridge

```text
Partial memory
   ↓
Generic search attempt
   ↓
Results are not exact
   ↓
User guesses another search wording
   ↓
More browsing / refinement
   ↓
More effort
```

### With Memory Bridge

```text
Partial memory
   ↓
System understands what is remembered
   ↓
System identifies a useful missing discriminator
   ↓
One focused question
   ↓
Candidate set narrows
   ↓
User recognizes the memory
```

The MVP succeeds conceptually only if this second path creates measurable improvement.

---

# 42. WHAT NOT TO BUILD

Do NOT spend MVP time on:

- authentication;
- user profiles;
- Google account OAuth;
- full Google Photos synchronization;
- mobile app;
- album redesign;
- backup settings;
- social sharing;
- full OCR pipeline;
- advanced face recognition;
- video understanding;
- production-grade ranking;
- generic AI assistant capabilities;
- analytics dashboards unrelated to retrieval;
- unnecessary settings pages.

Do not expand the scope just because a feature sounds impressive.

---

# 43. RESEARCH GUARDRAILS FOR IMPLEMENTATION

Keep these distinctions clear:

### Observation

Something the user actually did or said.

### Interpretation

Our PM explanation of what that behavior may mean.

### Hypothesis

A causal/product explanation that still needs testing.

Never convert a PM interpretation into a participant quote.

Never build a product feature on an unsupported claim about Google Photos' internal implementation.

The MVP exists to test the **Memory Bridge intervention**, not to prove how Google Photos internally works.

---

# 44. IMPLEMENTATION ORDER

Build in this exact order.

## Phase 1 — Project scaffold

Create:

```text
/frontend
/backend
/data
/scripts
/tests
```

Set up:

- Next.js frontend;
- FastAPI backend;
- shared configuration;
- local run commands.

Do not start with visual polish before the core data flow exists.

---

## Phase 2 — Backend foundations

Implement:

- `/healthz`
- Pydantic schemas;
- basic CORS;
- configuration;
- error handling.

Add API tests.

---

## Phase 3 — Dataset

Create the controlled dataset.

Implement:

```text
scripts/build_index.py
```

Responsibilities:

1. validate image files;
2. validate metadata;
3. create canonical text representation;
4. compute/store embeddings where enabled;
5. store metadata;
6. print index statistics.

Every benchmark task must have a target ID.

---

## Phase 4 — Memory parser

Implement `/api/memory/parse`.

Use Gemini structured output where available.

Add parser tests covering:

- person + event + year;
- place + event + approximate time;
- screenshot/document;
- ambiguous memory;
- missing details.

The parser must not invent facts.

---

## Phase 5 — Candidate retrieval

Implement deterministic candidate retrieval.

Support:

- semantic similarity;
- structured metadata matching;
- configurable weights;
- fallback metadata search.

Add tests proving that relevant clues influence ranking.

---

## Phase 6 — Missing-clue reasoner

Implement `/api/memory/next-clue`.

The reasoner must:

- inspect missing dimensions;
- estimate narrowing using the actual dataset;
- select one useful clue;
- generate one concise question;
- produce answer choices based on the corpus where possible;
- include Not sure;
- stop after two questions.

Add tests for:

- known clues never being requested;
- no repeated clue dimension;
- maximum 2 questions;
- no useful clue → fallback.

---

## Phase 7 — Frontend

Build all main screens.

Start with a functional journey.

Then polish:

- hierarchy;
- spacing;
- typography;
- responsive states;
- accessibility;
- error states.

---

## Phase 8 — Baseline

Implement the unguided search route.

It must use the same:

- corpus;
- benchmark tasks;
- result visual design.

Only the intervention logic differs.

---

## Phase 9 — Telemetry

Implement session event logging.

Make sure the evaluator can derive:

- success;
- time;
- attempts/actions;
- clarification usage;
- candidate reduction;
- fallback.

---

## Phase 10 — Evaluation mode

Add benchmark/task support.

The UI should be able to run a known task while keeping the target hidden.

---

## Phase 11 — Local testing

Run:

- unit tests;
- API tests;
- frontend build;
- linting/type checks;
- browser smoke test.

Fix all blocking defects.

---

## Phase 12 — Deployment

Deploy:

- backend to Render;
- frontend to Vercel.

Configure environment variables and CORS.

---

## Phase 13 — Production verification

Using the public Vercel URL:

- run sample task;
- verify backend calls;
- verify retrieval;
- verify event logging;
- verify baseline;
- verify error recovery.

Do not call the project complete until the public URL works end-to-end.

---

# 45. REQUIRED OUTPUT FROM ANTIGRAVITY

At the end of implementation, provide a concise engineering handoff with:

1. **What was built**
2. **Project structure**
3. **How to run locally**
4. **Environment variables required**
5. **Dataset generation / ingestion instructions**
6. **Benchmark task list**
7. **API endpoints**
8. **Tests run and results**
9. **Deployment details**
10. **Frontend URL**
11. **Backend URL**
12. **Known limitations**
13. **Any deviations from this specification**
14. **Any remaining bugs or risks**

Do not hide deviations.

---

# 46. DEVIATION POLICY

If implementation needs to differ from this specification:

1. keep the change as small as possible;
2. preserve the core product hypothesis;
3. do not silently change product behavior;
4. document what changed and why.

Example:

If Supabase causes unnecessary complexity for the MVP, a JSON + in-memory implementation is acceptable **provided the prototype remains testable and deployable**.

Do not remove:

- baseline;
- missing-clue reasoning;
- max-two-question constraint;
- telemetry;
- success measurement;
- controlled ground-truth corpus.

These are core to the evaluation.

---

# 47. CURRENT RESEARCH / PRODUCT ARTIFACTS

Supporting project artifacts:

### AI Discovery Engine — live

https://google-photos-ai-discovery-engine-i6pyk20di.vercel.app/queries

### AI Discovery Engine — GitHub

https://github.com/Santhosh-A-Git/Google-Photos--AI-Discovery-Engine

### Survey

Final 56-response survey / response artifact is part of the project evidence set.

### Interviews

The six interview response document is part of the project evidence set. A–E are the primary analytical set; F remains raw/supplementary.

---

# 48. OFFICIAL TECHNICAL REFERENCES

Use these for implementation details where appropriate.

### Gemini

Gemini API getting started:
https://ai.google.dev/gemini-api/docs/get-started

Structured outputs:
https://ai.google.dev/gemini-api/docs/structured-output

Embeddings:
https://ai.google.dev/gemini-api/docs/embeddings

### Google Photos API / current access model

https://developers.google.com/photos/support/updates

Google Photos Picker:
https://developers.google.com/photos/picker/guides/get-started-picker

### Deployment

Render FastAPI:
https://render.com/docs/deploy-fastapi

Vercel Next.js:
https://vercel.com/frameworks/nextjs

---

# 49. FINAL PRODUCT DEFINITION IN ONE PARAGRAPH

**Memory Bridge is a bounded AI-guided retrieval recovery experience for vaguely remembered photos. A user describes what they remember in natural language. The system structures those contextual memories, identifies what important retrieval clue is missing, asks at most two focused questions, re-ranks candidates using the new information, and presents likely memories for visual recognition. The MVP runs on a controlled 40–50 image corpus, includes a simple unguided-search baseline, records retrieval outcomes and effort, and is deployable as Next.js on Vercel with FastAPI on Render. The product is a prototype concept for a PM research project, not an official Google Photos feature and not a full Google Photos integration.**

---

# 50. DEFINITION OF DONE

Memory Bridge is DONE when:

> A new user can open the public URL, enter a vague photo memory, see what the system understood, receive a useful missing-clue question, answer it, see the candidate set change, recognize and select the correct image, and finish in a measurable success state — while a comparable baseline experience exists for evaluation and all core interactions are logged.

That is the exact outcome this MVP is intended to demonstrate.
