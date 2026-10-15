"use client";

import React, { useEffect, useState } from "react";
import { HistoryItem } from "@/types/analysis";
import { getHistory } from "@/lib/api";
import { History, X, Clock, ArrowRight, Trash2, RefreshCw } from "lucide-react";

interface HistoryDrawerProps {
  isOpen: boolean;
  onClose: () => void;
  onSelectSubmission: (submissionId: string) => void;
}

export const HistoryDrawer: React.FC<HistoryDrawerProps> = ({
  isOpen,
  onClose,
  onSelectSubmission,
}) => {
  const [historyItems, setHistoryItems] = useState<HistoryItem[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchHistory = async () => {
    setIsLoading(true);
    setError(null);
    try {
      const items = await getHistory();
      setHistoryItems(items);
    } catch (err: any) {
      setError(err.message || "Failed to load history");
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    if (isOpen) {
      fetchHistory();
    }
  }, [isOpen]);

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex justify-end bg-black/60 backdrop-blur-xs">
      <div className="w-full max-w-md h-full bg-zinc-900 border-l border-zinc-800 shadow-2xl flex flex-col p-4">
        {/* Header */}
        <div className="flex items-center justify-between pb-3 border-b border-zinc-800">
          <div className="flex items-center gap-2 text-zinc-100 font-semibold text-sm">
            <History className="w-4 h-4 text-emerald-400" />
            <span>Analysis History</span>
          </div>
          <div className="flex items-center gap-2">
            <button
              onClick={fetchHistory}
              className="p-1 text-zinc-400 hover:text-zinc-200 transition"
              title="Refresh History"
            >
              <RefreshCw className={`w-4 h-4 ${isLoading ? "animate-spin" : ""}`} />
            </button>
            <button
              onClick={onClose}
              className="p-1 text-zinc-400 hover:text-zinc-200 transition"
              title="Close Drawer"
            >
              <X className="w-4 h-4" />
            </button>
          </div>
        </div>

        {/* Content */}
        <div className="flex-1 overflow-y-auto py-3 space-y-2.5">
          {isLoading ? (
            <div className="flex flex-col items-center justify-center h-48 text-zinc-400 gap-2">
              <div className="w-5 h-5 border-2 border-emerald-400 border-t-transparent rounded-full animate-spin" />
              <span className="text-xs">Loading database records...</span>
            </div>
          ) : error ? (
            <div className="p-3 bg-rose-500/10 border border-rose-500/20 text-rose-300 text-xs rounded-lg">
              {error}
            </div>
          ) : historyItems.length === 0 ? (
            <div className="flex flex-col items-center justify-center h-48 text-zinc-500 text-xs text-center px-4">
              <Clock className="w-8 h-8 stroke-[1.5] mb-2 opacity-40" />
              <p>No past analysis records found.</p>
              <p className="text-[11px] text-zinc-600 mt-1">
                Analyses are saved to Supabase / PostgreSQL database automatically.
              </p>
            </div>
          ) : (
            historyItems.map((item) => (
              <div
                key={item.id}
                onClick={() => {
                  onSelectSubmission(item.submission_id);
                  onClose();
                }}
                className="p-3 bg-zinc-950/60 border border-zinc-800 hover:border-zinc-700 rounded-lg cursor-pointer transition group"
              >
                <div className="flex items-center justify-between mb-1.5">
                  <span className="text-xs font-semibold text-zinc-200 group-hover:text-emerald-400 transition truncate">
                    {item.title}
                  </span>
                  <span className="text-[11px] font-mono px-2 py-0.5 rounded bg-zinc-800 text-zinc-300 border border-zinc-700/60">
                    {item.time_complexity}
                  </span>
                </div>

                <div className="text-[11px] font-mono text-zinc-400 bg-zinc-900/80 p-2 rounded border border-zinc-800/80 truncate mb-2">
                  {item.code_snippet}
                </div>

                <div className="flex items-center justify-between text-[10px] text-zinc-400">
                  <span>
                    {new Date(item.created_at).toLocaleTimeString([], {
                      hour: "2-digit",
                      minute: "2-digit",
                    })}
                  </span>
                  <div className="flex items-center gap-1 text-emerald-400 opacity-0 group-hover:opacity-100 transition">
                    <span>Load to Editor</span>
                    <ArrowRight className="w-3 h-3" />
                  </div>
                </div>
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  );
};
