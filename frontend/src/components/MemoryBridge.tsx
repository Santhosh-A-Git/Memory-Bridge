"use client";

import { useState } from "react";
import Image from "next/image";

type Step = "input" | "parsing" | "parsed" | "clarifying" | "clarify_loading" | "results" | "success" | "fallback" | "baseline";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api";

export default function MemoryBridge() {
  const [step, setStep] = useState<Step>("input");
  const [memoryInput, setMemoryInput] = useState("");
  const [parsedMemory, setParsedMemory] = useState<any>(null);
  const [clueQuestion, setClueQuestion] = useState<any>(null);
  const [candidates, setCandidates] = useState<any[]>([]);
  const [additionalClues, setAdditionalClues] = useState<Record<string, string>>({});
  const [selectedPhoto, setSelectedPhoto] = useState<any>(null);
  const [clarificationCount, setClarificationCount] = useState(0);
  const [baselineMode, setBaselineMode] = useState(false);

  const startTask = () => {
    setMemoryInput("Find the photo of me with my sister at my college farewell around 2022. I don't remember the exact date.");
  };

  const handleParse = async () => {
    if (!memoryInput.trim()) return;
    if (baselineMode) {
        // baseline skip directly to candidates based on text search
        setStep("parsing");
        await fetchCandidates({}, {});
        return;
    }
    
    setStep("parsing");
    try {
      const res = await fetch(`${API_URL}/memory/parse`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ memory: memoryInput })
      });
      const data = await res.json();
      setParsedMemory(data.memory);
      setStep("parsed");
    } catch (e) {
      console.error(e);
      setStep("fallback");
    }
  };

  const handleContinue = async () => {
    if (!parsedMemory?.missing_clues || parsedMemory.missing_clues.length === 0) {
      await fetchCandidates(parsedMemory, additionalClues);
      return;
    }
    setStep("clarify_loading");
    try {
      const res = await fetch(`${API_URL}/memory/next-clue`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ memory: parsedMemory, candidate_ids: [] })
      });
      const data = await res.json();
      setClueQuestion(data);
      setClarificationCount(c => c + 1);
      setStep("clarifying");
    } catch (e) {
      console.error(e);
      await fetchCandidates(parsedMemory, additionalClues);
    }
  };

  const handleAnswer = async (answer: string) => {
    const newClues = { ...additionalClues, [clueQuestion.clue_dimension]: answer };
    setAdditionalClues(newClues);
    
    if (clarificationCount < 2) {
      // optionally ask second question, but for MVP let's just go to results after 1
      await fetchCandidates(parsedMemory, newClues);
    } else {
      await fetchCandidates(parsedMemory, newClues);
    }
  };

  const fetchCandidates = async (memory: any, clues: any) => {
    setStep("clarify_loading");
    try {
      const endpoint = baselineMode ? "/memory/candidates-details" : "/memory/candidates-details";
      // for baseline, we simulate passing just text
      const reqMemory = baselineMode ? { events: [memoryInput], text: [memoryInput] } : memory;
      const res = await fetch(`${API_URL}${endpoint}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ memory: reqMemory, additional_clues: clues })
      });
      const data = await res.json();
      setCandidates(data.results);
      if (data.results.length === 0) {
        setStep("fallback");
      } else {
        setStep("results");
      }
    } catch (e) {
      console.error(e);
      setStep("fallback");
    }
  };

  const handleSelect = (photo: any) => {
    setSelectedPhoto(photo);
    setStep("success");
  };

  const renderClues = (label: string, items: string[]) => {
    if (!items || items.length === 0) return null;
    return (
      <div className="mb-2">
        <span className="font-semibold text-gray-700 dark:text-gray-300">{label}: </span>
        {items.map(i => (
          <span key={i} className="inline-block bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200 rounded px-2 py-1 text-sm mr-2">{i}</span>
        ))}
      </div>
    );
  };

  return (
    <div className="max-w-2xl mx-auto p-4 md:p-8 bg-white dark:bg-gray-900 rounded-2xl shadow-xl min-h-[600px] flex flex-col justify-between">
      <div className="mb-8 text-center">
        <h1 className="text-4xl font-extrabold text-transparent bg-clip-text bg-gradient-to-r from-blue-600 to-purple-600 tracking-tight">MEMORY BRIDGE</h1>
        <p className="text-sm text-gray-500 dark:text-gray-400 mt-2 font-medium uppercase tracking-widest">Turn an incomplete memory into the next useful retrieval clue</p>
      </div>
      <div>
        {step === "input" && (
          <div className="animate-fade-in">
            <div className="flex justify-between items-center mb-6">
                <h1 className="text-3xl font-bold text-gray-900 dark:text-white">What do you remember about the photo?</h1>
                <button onClick={() => setBaselineMode(!baselineMode)} className={`text-xs px-2 py-1 rounded ${baselineMode ? 'bg-orange-500 text-white' : 'bg-gray-200 text-gray-600'}`}>
                    {baselineMode ? "Baseline Mode ON" : "Baseline Mode OFF"}
                </button>
            </div>
            <p className="text-gray-600 dark:text-gray-400 mb-6">You don't need the exact date, filename or album. Start with whatever you remember.</p>
            <textarea 
              value={memoryInput}
              onChange={e => setMemoryInput(e.target.value)}
              className="w-full p-4 border border-gray-300 dark:border-gray-700 rounded-xl bg-gray-50 dark:bg-gray-800 text-gray-900 dark:text-white h-40 focus:ring-2 focus:ring-blue-500 focus:outline-none resize-none transition-all"
              placeholder="e.g. Find the photo of me with my sister..."
            />
            <div className="mt-6 flex flex-wrap gap-4">
              <button 
                onClick={handleParse}
                className="bg-blue-600 hover:bg-blue-700 text-white font-semibold py-3 px-6 rounded-full transition-transform transform active:scale-95"
              >
                Find my memory
              </button>
              <button 
                onClick={startTask}
                className="bg-gray-200 dark:bg-gray-800 hover:bg-gray-300 dark:hover:bg-gray-700 text-gray-800 dark:text-gray-200 font-medium py-3 px-6 rounded-full transition-colors"
              >
                Try a sample task
              </button>
            </div>
          </div>
        )}

        {step === "parsing" && (
          <div className="flex flex-col items-center justify-center h-64 animate-pulse">
            <div className="w-12 h-12 border-4 border-blue-500 border-t-transparent rounded-full animate-spin mb-4"></div>
            <p className="text-lg text-gray-600 dark:text-gray-300">Understanding your memory...</p>
          </div>
        )}

        {step === "parsed" && parsedMemory && (
          <div className="animate-fade-in">
            <h2 className="text-2xl font-bold mb-6 text-gray-900 dark:text-white">Here's what I understood</h2>
            <div className="bg-gray-50 dark:bg-gray-800 p-6 rounded-xl mb-6 shadow-inner">
              {renderClues("People", parsedMemory.people)}
              {renderClues("Event", parsedMemory.events)}
              {parsedMemory.time && renderClues("Time", [parsedMemory.time.value])}
              {renderClues("Other", [...parsedMemory.objects, ...parsedMemory.places])}
            </div>

            <h3 className="text-lg font-semibold text-gray-800 dark:text-gray-200 mb-4">What is missing</h3>
            <div className="flex flex-wrap mb-8">
              {parsedMemory.missing_clues?.map((m: string) => (
                <span key={m} className="inline-block bg-red-50 text-red-700 dark:bg-red-900/30 dark:text-red-300 rounded-full px-3 py-1 text-sm mr-2 mb-2 border border-red-200 dark:border-red-800">
                  {m.replace('_', ' ')}
                </span>
              ))}
            </div>

            <button 
              onClick={handleContinue}
              className="w-full bg-blue-600 hover:bg-blue-700 text-white font-semibold py-3 px-6 rounded-xl transition-all"
            >
              Continue
            </button>
          </div>
        )}

        {step === "clarify_loading" && (
          <div className="flex flex-col items-center justify-center h-64 animate-pulse">
            <div className="w-12 h-12 border-4 border-blue-500 border-t-transparent rounded-full animate-spin mb-4"></div>
            <p className="text-lg text-gray-600 dark:text-gray-300">Narrowing your memory...</p>
          </div>
        )}

        {step === "clarifying" && clueQuestion && (
          <div className="animate-slide-up">
            <div className="bg-blue-50 dark:bg-blue-900/20 text-blue-800 dark:text-blue-300 text-sm font-semibold px-4 py-1 rounded-full inline-block mb-4">
              One detail could narrow this down
            </div>
            <h2 className="text-2xl font-bold mb-8 text-gray-900 dark:text-white">{clueQuestion.question}</h2>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {clueQuestion.options.map((opt: string) => (
                <button 
                  key={opt}
                  onClick={() => handleAnswer(opt)}
                  className="bg-white dark:bg-gray-800 border-2 border-gray-200 dark:border-gray-700 hover:border-blue-500 dark:hover:border-blue-500 hover:shadow-md text-gray-800 dark:text-gray-200 font-medium py-4 px-6 rounded-xl transition-all text-left"
                >
                  {opt}
                </button>
              ))}
            </div>
            <button 
              onClick={() => handleAnswer("Not sure")}
              className="mt-8 text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200 underline"
            >
              Skip this question
            </button>
          </div>
        )}

        {step === "results" && (
          <div className="animate-fade-in">
            <h2 className="text-2xl font-bold mb-6 text-gray-900 dark:text-white">I found {candidates.length} likely memories</h2>
            
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
              {candidates.map((c, i) => (
                <div key={c.photo_id} className="bg-white dark:bg-gray-800 rounded-xl overflow-hidden shadow-lg hover:shadow-xl transition-shadow cursor-pointer border border-gray-100 dark:border-gray-700" onClick={() => handleSelect(c)}>
                  <div className="relative h-48 w-full bg-gray-200 dark:bg-gray-700">
                    <img src={c.photo_details.image_url} alt={c.photo_id} className="object-cover w-full h-full" />
                    <div className="absolute top-2 left-2 bg-black/60 text-white text-xs px-2 py-1 rounded-full backdrop-blur-sm">
                      {i < 3 ? "Strong match" : "Likely match"}
                    </div>
                  </div>
                  <div className="p-4">
                    <p className="text-sm text-gray-600 dark:text-gray-400 truncate">
                      {c.matched_clues.join(" · ")}
                    </p>
                    <div className="mt-4 flex gap-2">
                       <button className="flex-1 bg-blue-100 hover:bg-blue-200 text-blue-800 dark:bg-blue-900/40 dark:hover:bg-blue-900/60 dark:text-blue-200 py-2 rounded font-medium text-sm transition-colors">
                         This is the one
                       </button>
                    </div>
                  </div>
                </div>
              ))}
            </div>
            <div className="mt-8 text-center">
               <button onClick={() => setStep("input")} className="text-gray-500 hover:text-gray-700 dark:hover:text-gray-300">
                  Not seeing it? Start over
               </button>
            </div>
          </div>
        )}

        {step === "success" && selectedPhoto && (
          <div className="text-center animate-scale-in">
            <div className="inline-flex items-center justify-center w-16 h-16 rounded-full bg-green-100 text-green-600 mb-6">
              <svg className="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M5 13l4 4L19 7"></path></svg>
            </div>
            <h2 className="text-3xl font-bold mb-6 text-gray-900 dark:text-white">Memory found</h2>
            
            <div className="max-w-md mx-auto bg-white dark:bg-gray-800 p-4 rounded-2xl shadow-lg border border-gray-100 dark:border-gray-700 mb-8">
               <img src={selectedPhoto.photo_details.image_url} className="w-full h-64 object-cover rounded-xl mb-4" />
               <p className="text-gray-600 dark:text-gray-300 text-sm">
                 Found using: {selectedPhoto.matched_clues.join(" + ")}
               </p>
            </div>

            <button 
              onClick={() => { setStep("input"); setMemoryInput(""); setAdditionalClues({}); setClarificationCount(0); }}
              className="bg-blue-600 hover:bg-blue-700 text-white font-semibold py-3 px-8 rounded-full transition-transform transform active:scale-95"
            >
              Try another memory
            </button>
          </div>
        )}

        {step === "fallback" && (
          <div className="text-center animate-fade-in py-12">
            <h2 className="text-2xl font-bold mb-4 text-gray-900 dark:text-white">I couldn't narrow this down confidently</h2>
            <p className="text-gray-600 dark:text-gray-400 mb-8">Here are the strongest matching memories from what you told me.</p>
            
            <button 
              onClick={() => setStep("input")}
              className="bg-blue-600 hover:bg-blue-700 text-white font-semibold py-3 px-8 rounded-full"
            >
              Start over
            </button>
          </div>
        )}
      </div>

      <div className="mt-12 text-center text-xs text-gray-400 dark:text-gray-500">
        <p>Prototype concept — not a Google product</p>
      </div>
    </div>
  );
}
