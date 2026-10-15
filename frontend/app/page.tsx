"use client";

import React, { useState, useEffect } from "react";
import { CodeEditor } from "@/components/CodeEditor";
import { ComplexityOverview } from "@/components/ComplexityOverview";
import { StatisticsGrid } from "@/components/StatisticsGrid";
import { ComplexityChart } from "@/components/ComplexityChart";
import { StructureFlow } from "@/components/StructureFlow";
import { ReasoningPanel } from "@/components/ReasoningPanel";
import { HistoryDrawer } from "@/components/HistoryDrawer";
import { ReportModal } from "@/components/ReportModal";
import { Navbar } from "@/components/Navbar";
import { CODE_EXAMPLES, CodeExample } from "@/lib/examples";
import { analyzeCode, checkBackendHealth, getHistoryDetail } from "@/lib/api";
import { AnalyzeResponse } from "@/types/analysis";
import {
  AlertTriangle,
  Code2,
  TrendingUp,
  Network,
  Sparkles,
  Layers,
  Terminal,
} from "lucide-react";

export default function Home() {
  const [code, setCode] = useState(CODE_EXAMPLES[0].code);
  const [activeTab, setActiveTab] = useState<"chart" | "structure">("chart");
  const [isLoading, setIsLoading] = useState(false);
  const [analysisResult, setAnalysisResult] = useState<AnalyzeResponse | null>(null);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [isHistoryOpen, setIsHistoryOpen] = useState(false);
  const [isReportOpen, setIsReportOpen] = useState(false);
  const [backendHealth, setBackendHealth] = useState({
    status: "checking",
    dbConnected: false,
    dbType: "Checking...",
  });

  // Verify backend health on mount
  useEffect(() => {
    const checkHealth = async () => {
      try {
        const health = await checkBackendHealth();
        setBackendHealth({
          status: health.status,
          dbConnected: health.database.connected,
          dbType: health.database.type,
        });
      } catch (e) {
        setBackendHealth({
          status: "offline",
          dbConnected: false,
          dbType: "Disconnected",
        });
      }
    };
    checkHealth();
    const interval = setInterval(checkHealth, 15000);
    return () => clearInterval(interval);
  }, []);

  const handleAnalyze = async () => {
    if (!code.trim() || isLoading) return;
    setIsLoading(true);
    setErrorMessage(null);

    try {
      const res = await analyzeCode(code);
      setAnalysisResult(res);
      if (!res.success && res.error) {
        setErrorMessage(
          `Syntax Error on Line ${res.error.line}, Column ${res.error.column}: ${res.error.message}`
        );
      }
    } catch (err: any) {
      setErrorMessage(
        err.message || "Failed to connect to Python static analysis service."
      );
    } finally {
      setIsLoading(false);
    }
  };

  const handleSelectExample = (example: CodeExample) => {
    setCode(example.code);
    setErrorMessage(null);
  };

  const handleRestoreFromHistory = async (submissionId: string) => {
    try {
      setIsLoading(true);
      const detail = await getHistoryDetail(submissionId);
      setCode(detail.code);
      // Construct analyze response from history detail
      setAnalysisResult({
        success: true,
        time_complexity: detail.time_complexity,
        space_complexity: detail.space_complexity,
        confidence: detail.confidence as any,
        complexity_reasoning: detail.complexity_reasoning,
        statistics: detail.statistics,
        structure: detail.structure,
        graph: detail.graph_data as any,
        detected_patterns: detail.detected_patterns,
        optimization_suggestions: detail.optimization_suggestions,
        functions: [],
        loops: [],
        recursion: {},
        submission_id: detail.submission_id,
      });
    } catch (err: any) {
      setErrorMessage("Could not retrieve past analysis record: " + err.message);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-[#09090b] text-zinc-100 flex flex-col font-sans selection:bg-emerald-500/20 selection:text-emerald-300">
      {/* Top Navigation */}
      <Navbar
        backendStatus={backendHealth}
        onOpenHistory={() => setIsHistoryOpen(true)}
        onOpenReport={() => setIsReportOpen(true)}
        hasResult={!!analysisResult && analysisResult.success}
      />

      {/* Main Workspace */}
      <main className="flex-1 max-w-7xl w-full mx-auto p-4 sm:p-6 grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Left Column: Monaco Code Editor */}
        <section className="lg:col-span-5 flex flex-col h-[750px] lg:h-auto">
          <CodeEditor
            code={code}
            onChange={setCode}
            onAnalyze={handleAnalyze}
            isLoading={isLoading}
            onSelectExample={handleSelectExample}
          />
        </section>

        {/* Right Column: Visual Complexity Dashboard */}
        <section className="lg:col-span-7 flex flex-col space-y-4">
          {/* Syntax Error Alert */}
          {errorMessage && (
            <div className="p-4 rounded-xl bg-rose-500/10 border border-rose-500/30 text-rose-300 text-xs flex items-start gap-3 shadow-lg">
              <AlertTriangle className="w-5 h-5 text-rose-400 shrink-0 mt-0.5" />
              <div className="space-y-1">
                <div className="font-semibold text-rose-200">
                  Static Analysis Parsing Notice
                </div>
                <p className="font-mono">{errorMessage}</p>
                {analysisResult?.error?.snippet && (
                  <div className="p-2 rounded bg-black/40 border border-rose-500/20 font-mono text-[11px] text-zinc-300 mt-2">
                    Line {analysisResult.error.line}: {analysisResult.error.snippet}
                  </div>
                )}
              </div>
            </div>
          )}

          {/* Loading State */}
          {isLoading && (
            <div className="flex-1 min-h-[400px] flex flex-col items-center justify-center bg-zinc-900/40 border border-zinc-800 rounded-xl p-8 text-center">
              <div className="relative mb-4">
                <div className="w-12 h-12 rounded-full border-2 border-emerald-500/20 border-t-emerald-400 animate-spin" />
                <Sparkles className="w-5 h-5 text-emerald-400 absolute inset-0 m-auto animate-pulse" />
              </div>
              <h3 className="text-sm font-semibold text-zinc-200 mb-1">
                Analyzing Python Source Code
              </h3>
              <p className="text-xs text-zinc-400 max-w-sm">
                Parsing AST nodes, tracing loop bounds, detecting recursive branches, and deriving asymptotic growth...
              </p>
            </div>
          )}

          {/* Empty State */}
          {!isLoading && !analysisResult && !errorMessage && (
            <div className="flex-1 min-h-[500px] flex flex-col items-center justify-center bg-zinc-900/40 border border-zinc-800 rounded-xl p-8 text-center">
              <div className="w-14 h-14 rounded-2xl bg-zinc-800/80 border border-zinc-700/60 flex items-center justify-center text-zinc-400 mb-4 shadow-inner">
                <Code2 className="w-7 h-7 text-emerald-400" />
              </div>
              <h3 className="text-base font-semibold text-zinc-200 mb-1">
                Ready for Static Complexity Inspection
              </h3>
              <p className="text-xs text-zinc-400 max-w-md leading-relaxed mb-6">
                Paste Python source code into the Monaco Editor or pick an example preset, then click{" "}
                <span className="text-emerald-400 font-medium">Analyze Code</span> to derive time & space complexity, AST flow graph, and theoretical growth curves.
              </p>
              <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 w-full max-w-md text-left">
                <div className="p-3 rounded-lg bg-zinc-950/60 border border-zinc-800/80">
                  <div className="text-[11px] font-semibold text-zinc-300">Deterministic AST</div>
                  <div className="text-[10px] text-zinc-500 mt-0.5">No arbitrary execution; safe static parsing</div>
                </div>
                <div className="p-3 rounded-lg bg-zinc-950/60 border border-zinc-800/80">
                  <div className="text-[11px] font-semibold text-zinc-300">Asymptotic Bounds</div>
                  <div className="text-[10px] text-zinc-500 mt-0.5">O(1), O(log n), O(n), O(n²), O(2^n)</div>
                </div>
                <div className="p-3 rounded-lg bg-zinc-950/60 border border-zinc-800/80">
                  <div className="text-[11px] font-semibold text-zinc-300">PostgreSQL History</div>
                  <div className="text-[10px] text-zinc-500 mt-0.5">Saved automatically to database</div>
                </div>
              </div>
            </div>
          )}

          {/* Active Analysis Dashboard */}
          {!isLoading && analysisResult && analysisResult.success && (
            <div className="space-y-4">
              {/* 1. Complexity Metric Cards */}
              <ComplexityOverview
                timeComplexity={analysisResult.time_complexity}
                tightBound={analysisResult.tight_bound}
                spaceComplexity={analysisResult.space_complexity}
                spaceBreakdown={analysisResult.space_breakdown}
                confidence={analysisResult.confidence}
                maxNesting={analysisResult.statistics.max_nesting_depth}
              />

              {/* 2. Analysis Statistics */}
              <StatisticsGrid stats={analysisResult.statistics} />

              {/* 3. Deep Dive Visualizations (Chart vs React Flow Graph) */}
              <div className="bg-zinc-900/40 border border-zinc-800 rounded-xl overflow-hidden">
                {/* Visualizer Tabs Header */}
                <div className="flex items-center justify-between px-4 py-2 bg-zinc-900/90 border-b border-zinc-800">
                  <div className="flex items-center gap-1">
                    <button
                      onClick={() => setActiveTab("chart")}
                      className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium transition ${
                        activeTab === "chart"
                          ? "bg-zinc-800 text-emerald-400 border border-zinc-700 shadow-xs"
                          : "text-zinc-400 hover:text-zinc-200"
                      }`}
                    >
                      <TrendingUp className="w-3.5 h-3.5" />
                      <span>Growth Curve (Recharts)</span>
                    </button>
                    <button
                      onClick={() => setActiveTab("structure")}
                      className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium transition ${
                        activeTab === "structure"
                          ? "bg-zinc-800 text-emerald-400 border border-zinc-700 shadow-xs"
                          : "text-zinc-400 hover:text-zinc-200"
                      }`}
                    >
                      <Network className="w-3.5 h-3.5" />
                      <span>Code Structure (React Flow)</span>
                    </button>
                  </div>

                  <span className="text-[10px] font-mono text-zinc-500">
                    Interactive Inspection
                  </span>
                </div>

                {/* Tab Body */}
                <div className="p-3">
                  {activeTab === "chart" ? (
                    <ComplexityChart graphData={analysisResult.graph} />
                  ) : (
                    <StructureFlow structure={analysisResult.structure} />
                  )}
                </div>
              </div>

              {/* 4. Complexity Explanation, Evidence & Optimization Notes */}
              <ReasoningPanel
                timeComplexity={analysisResult.time_complexity}
                tightBound={analysisResult.tight_bound}
                reasoning={analysisResult.complexity_reasoning}
                detectedPatterns={analysisResult.detected_patterns}
                optimizationSuggestions={analysisResult.optimization_suggestions}
                recurrence={analysisResult.recurrence}
                confidenceReasons={analysisResult.confidence_reasons}
              />
            </div>
          )}
        </section>
      </main>

      {/* History Drawer Modal */}
      <HistoryDrawer
        isOpen={isHistoryOpen}
        onClose={() => setIsHistoryOpen(false)}
        onSelectSubmission={handleRestoreFromHistory}
      />

      {/* Export Report Modal */}
      {analysisResult && (
        <ReportModal
          isOpen={isReportOpen}
          onClose={() => setIsReportOpen(false)}
          result={analysisResult}
          code={code}
        />
      )}
    </div>
  );
}
