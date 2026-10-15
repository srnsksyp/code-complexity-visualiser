"use client";

import React from "react";
import { Activity, History, FileText, CheckCircle2, AlertCircle } from "lucide-react";

interface NavbarProps {
  backendStatus: { status: string; dbConnected: boolean; dbType: string };
  onOpenHistory: () => void;
  onOpenReport: () => void;
  hasResult: boolean;
}

export const Navbar: React.FC<NavbarProps> = ({
  backendStatus,
  onOpenHistory,
  onOpenReport,
  hasResult,
}) => {
  return (
    <header className="border-b border-zinc-800 bg-zinc-950/80 backdrop-blur-md sticky top-0 z-40">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 h-14 flex items-center justify-between">
        {/* Brand */}
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-emerald-500 to-teal-700 flex items-center justify-center text-white shadow-md shadow-emerald-950/50">
            <Activity className="w-5 h-5" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h1 className="text-sm font-bold tracking-tight text-white">
                CODE COMPLEXITY VISUALIZER
              </h1>
              <span className="text-[10px] font-mono px-1.5 py-0.5 rounded bg-zinc-800 text-zinc-400 border border-zinc-700/60">
                v1.0
              </span>
            </div>
            <p className="text-[11px] text-zinc-400 hidden sm:block">
              Static Python AST Analyzer • Supabase PostgreSQL • Big-O Derivation
            </p>
          </div>
        </div>

        {/* Right Tools and Status */}
        <div className="flex items-center gap-3">
          {/* Backend / DB Status indicator */}
          <div
            className="flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-zinc-900 border border-zinc-800 text-[11px] font-mono text-zinc-400"
            title={`Database: ${backendStatus.dbType}`}
          >
            <div
              className={`w-2 h-2 rounded-full ${
                backendStatus.status === "healthy"
                  ? "bg-emerald-400 shadow-sm shadow-emerald-400/80 animate-pulse"
                  : backendStatus.status === "degraded"
                  ? "bg-amber-400"
                  : "bg-rose-400"
              }`}
            />
            <span className="hidden sm:inline">
              {backendStatus.status === "healthy"
                ? backendStatus.dbType.includes("Supabase")
                  ? "Supabase Connected"
                  : "Engine Active"
                : "Engine Offline"}
            </span>
          </div>

          {/* Export Report Button */}
          <button
            onClick={onOpenReport}
            disabled={!hasResult}
            className="flex items-center gap-1.5 px-3 py-1.5 text-xs text-zinc-300 hover:text-white bg-zinc-900 hover:bg-zinc-800 border border-zinc-800 rounded-lg transition disabled:opacity-40 disabled:cursor-not-allowed"
            title="Generate & Export Report"
          >
            <FileText className="w-3.5 h-3.5 text-emerald-400" />
            <span className="hidden sm:inline">Export Report</span>
          </button>

          {/* History Button */}
          <button
            onClick={onOpenHistory}
            className="flex items-center gap-1.5 px-3 py-1.5 text-xs text-zinc-300 hover:text-white bg-zinc-900 hover:bg-zinc-800 border border-zinc-800 rounded-lg transition"
            title="View Analysis History"
          >
            <History className="w-3.5 h-3.5 text-indigo-400" />
            <span className="hidden sm:inline">History</span>
          </button>
        </div>
      </div>
    </header>
  );
};
