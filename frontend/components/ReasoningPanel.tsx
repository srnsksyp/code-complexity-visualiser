"use client";

import React from "react";
import { HelpCircle, CheckCircle2, Lightbulb, AlertCircle, GitBranch, Sigma } from "lucide-react";
import { RecurrenceInfo } from "@/types/analysis";

interface ReasoningPanelProps {
  timeComplexity: string;
  tightBound?: string;
  reasoning: string;
  detectedPatterns: string[];
  optimizationSuggestions: string[];
  recurrence?: RecurrenceInfo;
  confidenceReasons?: string[];
}

export const ReasoningPanel: React.FC<ReasoningPanelProps> = ({
  timeComplexity,
  tightBound,
  reasoning,
  detectedPatterns,
  optimizationSuggestions,
  recurrence,
  confidenceReasons,
}) => {
  return (
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
      {/* Mathematical Explanation Card */}
      <div className="p-4 bg-zinc-900/60 border border-zinc-800 rounded-xl flex flex-col justify-between space-y-4">
        <div>
          <div className="flex items-center justify-between mb-2">
            <div className="flex items-center gap-2 text-zinc-200">
              <HelpCircle className="w-4 h-4 text-emerald-400" />
              <h3 className="text-sm font-semibold">
                Mathematical Asymptotic Derivation
              </h3>
            </div>
            {tightBound && (
              <span className="font-mono text-xs text-emerald-400 font-bold bg-emerald-500/10 border border-emerald-500/20 px-2 py-0.5 rounded">
                {tightBound}
              </span>
            )}
          </div>

          {/* Recurrence Box if present */}
          {recurrence?.present && recurrence.expression && (
            <div className="mb-3 p-3 bg-zinc-950/70 border border-zinc-800 rounded-lg">
              <div className="flex items-center justify-between mb-1.5 text-xs text-zinc-400">
                <div className="flex items-center gap-1.5">
                  <Sigma className="w-3.5 h-3.5 text-indigo-400" />
                  <span className="font-semibold text-zinc-300">Extracted Recurrence</span>
                </div>
                <div className="flex items-center gap-2 font-mono text-[10px]">
                  <span>Branching: {recurrence.branching_factor}</span>
                  <span>•</span>
                  <span>Call Sites: {recurrence.total_call_sites}</span>
                </div>
              </div>
              <div className="font-mono text-xs font-bold text-indigo-300 bg-zinc-900/90 p-2 rounded border border-zinc-800">
                {recurrence.expression}
              </div>
              {recurrence.derivation_steps && recurrence.derivation_steps.length > 0 && (
                <div className="mt-2 space-y-1">
                  {recurrence.derivation_steps.map((step, idx) => (
                    <div key={idx} className="flex items-start gap-1.5 text-[11px] text-zinc-300 leading-tight">
                      <span className="text-emerald-400 font-mono text-[10px] shrink-0 mt-0.5">{idx + 1}.</span>
                      <span>{step}</span>
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}

          {!recurrence?.present && (
            <p className="text-xs text-zinc-300 leading-relaxed font-sans bg-zinc-950/50 p-3 rounded-lg border border-zinc-800/80">
              {reasoning}
            </p>
          )}
        </div>

        {/* Detected Structural Patterns & Confidence Reasons */}
        <div>
          <div className="text-[11px] font-semibold text-zinc-400 uppercase tracking-wider mb-2">
            Static Evidence & Proof Steps
          </div>
          <div className="flex flex-wrap gap-1.5">
            {detectedPatterns.map((pattern, idx) => (
              <div
                key={idx}
                className="flex items-center gap-1.5 px-2.5 py-1 bg-zinc-800/80 border border-zinc-700/60 rounded-md text-xs text-zinc-300 font-mono"
              >
                <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400 shrink-0" />
                <span>{pattern}</span>
              </div>
            ))}
            {confidenceReasons?.map((reason, idx) => (
              <div
                key={`cr-${idx}`}
                className="flex items-center gap-1.5 px-2.5 py-1 bg-indigo-950/40 border border-indigo-500/30 rounded-md text-xs text-indigo-200 font-sans"
              >
                <GitBranch className="w-3 h-3 text-indigo-400 shrink-0" />
                <span>{reason}</span>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Algorithmic Optimizations / Caveats Card */}
      <div className="p-4 bg-zinc-900/60 border border-zinc-800 rounded-xl flex flex-col justify-between">
        <div>
          <div className="flex items-center gap-2 mb-2 text-zinc-200">
            <Lightbulb className="w-4 h-4 text-amber-400" />
            <h3 className="text-sm font-semibold">
              Optimization Opportunities & Considerations
            </h3>
          </div>

          {optimizationSuggestions.length > 0 ? (
            <div className="space-y-2">
              {optimizationSuggestions.map((sug, idx) => (
                <div
                  key={idx}
                  className="flex items-start gap-2.5 p-3 rounded-lg bg-amber-500/5 border border-amber-500/20 text-xs text-amber-200/90 leading-relaxed"
                >
                  <Lightbulb className="w-4 h-4 text-amber-400 shrink-0 mt-0.5" />
                  <p>{sug}</p>
                </div>
              ))}
            </div>
          ) : (
            <div className="p-4 rounded-lg bg-zinc-950/40 border border-zinc-800 text-xs text-zinc-400 flex items-center gap-2">
              <CheckCircle2 className="w-4 h-4 text-emerald-400" />
              <span>
                No obvious algorithmic bottlenecks (e.g. repeated in-loop sorting, list membership, or exponential branching) detected in static analysis.
              </span>
            </div>
          )}
        </div>

        <div className="mt-3 pt-2 border-t border-zinc-800/80 flex items-center gap-1.5 text-[11px] text-zinc-400">
          <AlertCircle className="w-3.5 h-3.5 text-zinc-400 shrink-0" />
          <span>
            Suggestions are algorithmic possibilities derived statically; correctness depends on specific problem semantics.
          </span>
        </div>
      </div>
    </div>
  );
};
