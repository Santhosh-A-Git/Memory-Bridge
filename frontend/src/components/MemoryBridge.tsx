"use client";

import { useState } from "react";

type Step =
  | "input"
  | "parsing"
  | "parsed"
  | "clarifying"
  | "clarify_loading"
  | "results"
  | "success"
  | "fallback";

const API_URL =
  process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api";

function resetState() {
  return {
    step: "input" as Step,
    memoryInput: "",
    parsedMemory: null as any,
    clueQuestion: null as any,
    candidates: [] as any[],
    additionalClues: {} as Record<string, string>,
    selectedPhoto: null as any,
    clarificationCount: 0,
    errorMessage: "",
  };
}

export default function MemoryBridge() {
  const [step, setStep] = useState<Step>("input");
  const [memoryInput, setMemoryInput] = useState("");
  const [parsedMemory, setParsedMemory] = useState<any>(null);
  const [clueQuestion, setClueQuestion] = useState<any>(null);
  const [candidates, setCandidates] = useState<any[]>([]);
  const [additionalClues, setAdditionalClues] = useState<
    Record<string, string>
  >({});
  const [selectedPhoto, setSelectedPhoto] = useState<any>(null);
  const [clarificationCount, setClarificationCount] = useState(0);
  const [errorMessage, setErrorMessage] = useState("");

  const doReset = () => {
    const s = resetState();
    setStep(s.step);
    setMemoryInput(s.memoryInput);
    setParsedMemory(s.parsedMemory);
    setClueQuestion(s.clueQuestion);
    setCandidates(s.candidates);
    setAdditionalClues(s.additionalClues);
    setSelectedPhoto(s.selectedPhoto);
    setClarificationCount(s.clarificationCount);
    setErrorMessage(s.errorMessage);
  };

  // ── Step 1 : Parse the natural-language memory ─────────────────────────────
  const handleParse = async () => {
    if (!memoryInput.trim()) return;
    setStep("parsing");
    setErrorMessage("");
    try {
      const res = await fetch(`${API_URL}/memory/parse`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ memory: memoryInput }),
      });
      if (!res.ok) throw new Error(`Server error ${res.status}`);
      const data = await res.json();
      setParsedMemory(data.memory);
      setAdditionalClues({});
      setClarificationCount(0);
      setStep("parsed");
    } catch (e: any) {
      console.error(e);
      setErrorMessage(String(e));
      setStep("fallback");
    }
  };

  // ── Step 2 : Continue — either ask a clue question or fetch results directly
  const handleContinue = async () => {
    const missing = parsedMemory?.missing_clues ?? [];
    if (missing.length === 0) {
      // Nothing missing — go straight to results
      await fetchCandidates(parsedMemory, additionalClues);
      return;
    }
    // Ask the most important missing clue
    setStep("clarify_loading");
    try {
      const res = await fetch(`${API_URL}/memory/next-clue`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ memory: parsedMemory, candidate_ids: [] }),
      });
      if (!res.ok) throw new Error(`Server error ${res.status}`);
      const data = await res.json();
      setClueQuestion(data);
      setClarificationCount((c) => c + 1);
      setStep("clarifying");
    } catch (e) {
      console.error(e);
      // If next-clue fails, just show results with what we have
      await fetchCandidates(parsedMemory, additionalClues);
    }
  };

  // ── Step 3 : User answered a clue question ─────────────────────────────────
  const handleAnswer = async (answer: string) => {
    const dim = clueQuestion?.clue_dimension ?? "unknown";
    const newClues = { ...additionalClues, [dim]: answer };
    setAdditionalClues(newClues);

    // Update parsedMemory to remove that dimension from missing_clues
    // so the next Continue won't ask the same question again
    const updatedMissing = (parsedMemory?.missing_clues ?? []).filter(
      (m: string) => m !== dim
    );
    const updatedMemory = { ...parsedMemory, missing_clues: updatedMissing };
    setParsedMemory(updatedMemory);

    if (updatedMissing.length > 0 && clarificationCount < 2) {
      // There are more missing clues and we haven't hit the 2-question limit
      // Show the updated "what I understood" view so user can continue
      setStep("parsed");
    } else {
      // Either no more missing clues, or we've asked enough — fetch results
      await fetchCandidates(updatedMemory, newClues);
    }
  };

  // ── Fetch candidates from backend ──────────────────────────────────────────
  const fetchCandidates = async (memory: any, clues: any) => {
    setStep("clarify_loading");
    try {
      const res = await fetch(`${API_URL}/memory/candidates-details`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ memory, additional_clues: clues }),
      });
      if (!res.ok) throw new Error(`Server error ${res.status}`);
      const data = await res.json();
      const results = data.results ?? [];
      setCandidates(results);
      setStep(results.length > 0 ? "results" : "fallback");
    } catch (e: any) {
      console.error(e);
      setErrorMessage(String(e));
      setStep("fallback");
    }
  };

  const handleSelect = (photo: any) => {
    setSelectedPhoto(photo);
    setStep("success");
  };

  // ── Render helpers ─────────────────────────────────────────────────────────
  const renderClues = (label: string, items: any[]) => {
    const safe = (items ?? []).filter(Boolean);
    if (safe.length === 0) return null;
    return (
      <div className="mb-2">
        <span className="font-semibold text-gray-700 dark:text-gray-300">
          {label}:{" "}
        </span>
        {safe.map((i: any) => (
          <span
            key={String(i)}
            className="inline-block bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200 rounded px-2 py-1 text-sm mr-2 mb-1"
          >
            {String(i)}
          </span>
        ))}
      </div>
    );
  };

  const missingBadgeLabel: Record<string, string> = {
    location: "📍 City / Location",
    event:    "🎉 Occasion / Event",
    people:   "👥 People",
    time:     "📅 Year / Time",
  };

  // ── Render ─────────────────────────────────────────────────────────────────
  return (
    <div className="max-w-2xl mx-auto p-4 md:p-8 bg-white dark:bg-gray-900 rounded-2xl shadow-xl min-h-[600px] flex flex-col">
      {/* ── Brand header (always visible) ── */}
      <div className="mb-8 text-center">
        <h1 className="text-4xl font-extrabold text-transparent bg-clip-text bg-gradient-to-r from-blue-600 to-purple-600 tracking-tight">
          MEMORY BRIDGE
        </h1>
        <p className="text-sm text-gray-500 dark:text-gray-400 mt-2 font-medium uppercase tracking-widest">
          Turn an incomplete memory into the next useful retrieval clue
        </p>
      </div>

      <div className="flex-1">
        {/* ── INPUT ── */}
        {step === "input" && (
          <div className="animate-fade-in">
            <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-2">
              What do you remember about the photo?
            </h2>
            <p className="text-gray-500 dark:text-gray-400 mb-6 text-sm">
              You don't need the exact date, filename or album — start with
              whatever you remember.
            </p>
            <textarea
              id="memory-input"
              value={memoryInput}
              onChange={(e) => setMemoryInput(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === "Enter" && !e.shiftKey) {
                  e.preventDefault();
                  handleParse();
                }
              }}
              className="w-full p-4 border border-gray-300 dark:border-gray-700 rounded-xl bg-gray-50 dark:bg-gray-800 text-gray-900 dark:text-white h-36 focus:ring-2 focus:ring-blue-500 focus:outline-none resize-none transition-all text-sm"
              placeholder="e.g. Find the photo of me with my friends in Hyderabad around 2020…"
            />
            <div className="mt-4 flex flex-wrap gap-3">
              <button
                id="find-memory-btn"
                onClick={handleParse}
                disabled={!memoryInput.trim()}
                className="bg-blue-600 hover:bg-blue-700 disabled:opacity-50 text-white font-semibold py-3 px-6 rounded-full transition-all active:scale-95"
              >
                Find my memory
              </button>
              <button
                onClick={() =>
                  setMemoryInput(
                    "Find the photo of me with my sister at my college farewell around 2022. I don't remember the exact date."
                  )
                }
                className="bg-gray-100 dark:bg-gray-800 hover:bg-gray-200 dark:hover:bg-gray-700 text-gray-700 dark:text-gray-300 font-medium py-3 px-6 rounded-full transition-colors text-sm"
              >
                Try sample query
              </button>
            </div>
          </div>
        )}

        {/* ── PARSING / LOADING SPINNER ── */}
        {(step === "parsing" || step === "clarify_loading") && (
          <div className="flex flex-col items-center justify-center h-64">
            <div className="w-12 h-12 border-4 border-blue-500 border-t-transparent rounded-full animate-spin mb-4" />
            <p className="text-gray-500 dark:text-gray-400 text-sm">
              {step === "parsing"
                ? "Understanding your memory…"
                : "Narrowing down photos…"}
            </p>
          </div>
        )}

        {/* ── PARSED — show what was understood + missing details ── */}
        {step === "parsed" && parsedMemory && (
          <div className="animate-fade-in">
            <h2 className="text-2xl font-bold mb-1 text-gray-900 dark:text-white">
              Here's what I understood
            </h2>
            <p className="text-sm text-gray-500 dark:text-gray-400 mb-5">
              Review and continue — I'll ask for any missing details.
            </p>
            <div className="bg-gray-50 dark:bg-gray-800 p-5 rounded-xl mb-5 shadow-inner space-y-1">
              {renderClues("People", parsedMemory.people)}
              {renderClues("Event", parsedMemory.events)}
              {renderClues(
                "Location",
                parsedMemory.places?.length ? parsedMemory.places : []
              )}
              {parsedMemory.time?.value &&
                renderClues("Time", [parsedMemory.time.value])}
              {renderClues("Other", [
                ...(parsedMemory.objects ?? []),
              ])}
              {parsedMemory.people?.length === 0 &&
                parsedMemory.events?.length === 0 &&
                (parsedMemory.places?.length ?? 0) === 0 &&
                !parsedMemory.time?.value && (
                  <p className="text-sm text-gray-400 italic">
                    Hmm, I couldn't extract specific details — I'll ask you some
                    questions to narrow it down.
                  </p>
                )}
            </div>

            {/* Missing clue badges */}
            {(parsedMemory.missing_clues?.length ?? 0) > 0 && (
              <>
                <h3 className="text-sm font-semibold text-gray-600 dark:text-gray-300 uppercase tracking-wide mb-2">
                  Missing details
                </h3>
                <div className="flex flex-wrap gap-2 mb-6">
                  {parsedMemory.missing_clues.map((m: string) => (
                    <span
                      key={m}
                      className="inline-flex items-center gap-1 bg-red-50 text-red-700 dark:bg-red-900/30 dark:text-red-300 rounded-full px-3 py-1 text-xs font-medium border border-red-200 dark:border-red-700"
                    >
                      {missingBadgeLabel[m] ?? m}
                    </span>
                  ))}
                </div>
              </>
            )}

            <button
              id="continue-btn"
              onClick={handleContinue}
              className="w-full bg-blue-600 hover:bg-blue-700 text-white font-semibold py-3 px-6 rounded-xl transition-all active:scale-95"
            >
              {(parsedMemory.missing_clues?.length ?? 0) > 0
                ? "Continue — answer missing details"
                : "Show matching photos"}
            </button>
          </div>
        )}

        {/* ── CLARIFYING QUESTION ── */}
        {step === "clarifying" && clueQuestion && (
          <div>
            <div className="inline-block bg-blue-50 dark:bg-blue-900/20 text-blue-700 dark:text-blue-300 text-xs font-semibold px-3 py-1 rounded-full mb-4 uppercase tracking-wide">
              One more detail
            </div>
            <h2 className="text-2xl font-bold mb-6 text-gray-900 dark:text-white">
              {clueQuestion.question}
            </h2>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
              {(clueQuestion.options ?? []).map((opt: string) => (
                <button
                  key={opt}
                  id={`clue-opt-${opt.replace(/\s+/g, "-").toLowerCase()}`}
                  onClick={() => handleAnswer(opt)}
                  className="bg-white dark:bg-gray-800 border-2 border-gray-200 dark:border-gray-700 hover:border-blue-500 dark:hover:border-blue-500 hover:shadow-md text-gray-800 dark:text-gray-200 font-medium py-4 px-5 rounded-xl transition-all text-left text-sm"
                >
                  {opt}
                </button>
              ))}
            </div>
            <button
              onClick={() => fetchCandidates(parsedMemory, additionalClues)}
              className="mt-6 text-xs text-gray-400 hover:text-gray-600 dark:hover:text-gray-200 underline block"
            >
              Skip and show results anyway
            </button>
          </div>
        )}

        {/* ── RESULTS ── */}
        {step === "results" && (
          <div className="animate-fade-in">
            <h2 className="text-2xl font-bold mb-1 text-gray-900 dark:text-white">
              Found {candidates.length} matching photo
              {candidates.length !== 1 ? "s" : ""}
            </h2>
            <p className="text-sm text-gray-500 dark:text-gray-400 mb-6">
              Click a photo to confirm it's the one.
            </p>
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
              {candidates.map((c, i) => (
                <div
                  key={c.photo_id}
                  onClick={() => handleSelect(c)}
                  className="bg-white dark:bg-gray-800 rounded-xl overflow-hidden shadow hover:shadow-lg transition-shadow cursor-pointer border border-gray-100 dark:border-gray-700"
                >
                  <div className="relative h-44 w-full bg-gray-200 dark:bg-gray-700">
                    <img
                      src={c.photo_details?.image_url ?? "https://placehold.co/600x400?text=Photo"}
                      alt={c.photo_id}
                      className="object-cover w-full h-full"
                      onError={(e) => {
                        (e.target as HTMLImageElement).src =
                          "https://placehold.co/600x400?text=No+Preview";
                      }}
                    />
                    <div className="absolute top-2 left-2 bg-black/60 text-white text-xs px-2 py-0.5 rounded-full backdrop-blur-sm">
                      {i < 3 ? "⭐ Strong match" : "Likely match"}
                    </div>
                  </div>
                  <div className="p-3">
                    <p className="text-xs text-gray-500 dark:text-gray-400 truncate mb-2">
                      {c.matched_clues?.join(" · ") ?? ""}
                    </p>
                    <button className="w-full bg-blue-50 hover:bg-blue-100 dark:bg-blue-900/30 dark:hover:bg-blue-900/50 text-blue-700 dark:text-blue-300 py-2 rounded-lg font-medium text-xs transition-colors">
                      This is the one ✓
                    </button>
                  </div>
                </div>
              ))}
            </div>
            <div className="mt-6 text-center">
              <button
                onClick={doReset}
                className="text-sm text-gray-400 hover:text-gray-600 dark:hover:text-gray-200 underline"
              >
                Not seeing it? Start over
              </button>
            </div>
          </div>
        )}

        {/* ── SUCCESS ── */}
        {step === "success" && selectedPhoto && (
          <div className="text-center">
            <div className="inline-flex items-center justify-center w-14 h-14 rounded-full bg-green-100 dark:bg-green-900/30 text-green-600 mb-4">
              <svg className="w-7 h-7" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M5 13l4 4L19 7" />
              </svg>
            </div>
            <h2 className="text-3xl font-bold mb-5 text-gray-900 dark:text-white">
              Memory found! 🎉
            </h2>
            <div className="max-w-sm mx-auto bg-white dark:bg-gray-800 p-4 rounded-2xl shadow-lg border border-gray-100 dark:border-gray-700 mb-6">
              <img
                src={selectedPhoto.photo_details?.image_url ?? "https://placehold.co/600x400?text=Photo"}
                className="w-full h-56 object-cover rounded-xl mb-3"
                onError={(e) => {
                  (e.target as HTMLImageElement).src =
                    "https://placehold.co/600x400?text=No+Preview";
                }}
              />
              <p className="text-sm text-gray-500 dark:text-gray-400">
                Found using:{" "}
                <span className="font-medium text-gray-700 dark:text-gray-200">
                  {selectedPhoto.matched_clues?.join(" + ") ?? "memory clues"}
                </span>
              </p>
            </div>
            <button
              onClick={doReset}
              className="bg-blue-600 hover:bg-blue-700 text-white font-semibold py-3 px-8 rounded-full transition-all active:scale-95"
            >
              Try another memory
            </button>
          </div>
        )}

        {/* ── FALLBACK ── */}
        {step === "fallback" && (
          <div className="text-center py-10">
            <div className="text-4xl mb-4">🔍</div>
            <h2 className="text-2xl font-bold mb-2 text-gray-900 dark:text-white">
              No matching photos found
            </h2>
            <p className="text-gray-500 dark:text-gray-400 mb-2 text-sm">
              Try adding more details like the city, the year, or who was there.
            </p>
            {errorMessage && (
              <p className="text-xs text-red-400 font-mono mb-4 max-w-md mx-auto break-all">
                {errorMessage}
              </p>
            )}
            <button
              id="start-over-btn"
              onClick={doReset}
              className="mt-4 bg-blue-600 hover:bg-blue-700 text-white font-semibold py-3 px-8 rounded-full transition-all"
            >
              Start over
            </button>
          </div>
        )}
      </div>

      <div className="mt-10 text-center text-xs text-gray-300 dark:text-gray-600">
        Prototype concept — not a Google product
      </div>
    </div>
  );
}
