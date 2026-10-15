"use client";

import React from "react";
import { CodeStatistics } from "@/types/analysis";
import { FunctionSquare, Repeat, GitFork, Split, Cpu, Layers } from "lucide-react";

interface StatisticsGridProps {
  stats: CodeStatistics;
}

export const StatisticsGrid: React.FC<StatisticsGridProps> = ({ stats }) => {
  const items = [
    {
      label: "Functions",
      value: stats.function_count,
      icon: <FunctionSquare className="w-4 h-4 text-indigo-400" />,
      sub: `${stats.imported_modules.length} modules imported`,
    },
    {
      label: "Loops",
      value: stats.loop_count,
      icon: <Repeat className="w-4 h-4 text-emerald-400" />,
      sub: `${stats.for_loop_count} For, ${stats.while_loop_count} While`,
    },
    {
      label: "Max Depth",
      value: `${stats.max_nesting_depth}`,
      icon: <Layers className="w-4 h-4 text-amber-400" />,
      sub: "Block nesting depth",
    },
    {
      label: "Conditionals",
      value: stats.conditional_count,
      icon: <GitFork className="w-4 h-4 text-blue-400" />,
      sub: "Branching statements",
    },
    {
      label: "Recursion",
      value: stats.recursion_detected ? "Yes" : "None",
      icon: <Split className="w-4 h-4 text-purple-400" />,
      sub: stats.recursion_detected ? `${stats.recursion_count} recursive calls` : "Iterative execution",
      highlight: stats.recursion_detected,
    },
    {
      label: "Operations",
      value: stats.operation_count,
      icon: <Cpu className="w-4 h-4 text-teal-400" />,
      sub: `${stats.comprehension_count} comprehensions`,
    },
  ];

  return (
    <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-2">
      {items.map((item, idx) => (
        <div
          key={idx}
          className="p-3 bg-zinc-900/60 border border-zinc-800/80 rounded-xl flex flex-col justify-between hover:border-zinc-700 transition"
        >
          <div className="flex items-center justify-between text-zinc-400 mb-1">
            <span className="text-[11px] font-medium uppercase tracking-wider">{item.label}</span>
            {item.icon}
          </div>
          <div>
            <div className={`text-xl font-mono font-bold ${item.highlight ? "text-purple-400" : "text-white"}`}>
              {item.value}
            </div>
            <div className="text-[10px] text-zinc-400 truncate mt-0.5" title={item.sub}>
              {item.sub}
            </div>
          </div>
        </div>
      ))}
    </div>
  );
};
