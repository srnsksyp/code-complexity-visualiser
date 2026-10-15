"use client";

import React from "react";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from "recharts";
import { TheoreticalGraphData } from "@/types/analysis";
import { Info, TrendingUp } from "lucide-react";

interface ComplexityChartProps {
  graphData: TheoreticalGraphData;
}

export const ComplexityChart: React.FC<ComplexityChartProps> = ({ graphData }) => {
  const active = graphData.active_complexity;

  // Visual styling dictionary for each curve
  const curveConfigs: Record<
    string,
    { color: string; strokeWidth: number; strokeDasharray?: string }
  > = {
    "O(1)": {
      color: active === "O(1)" ? "#10b981" : "#4b5563",
      strokeWidth: active === "O(1)" ? 3.5 : 1.5,
    },
    "O(log n)": {
      color: active === "O(log n)" ? "#10b981" : "#6b7280",
      strokeWidth: active === "O(log n)" ? 3.5 : 1.5,
    },
    "O(n)": {
      color: active === "O(n)" ? "#3b82f6" : "#475569",
      strokeWidth: active === "O(n)" ? 3.5 : 1.5,
    },
    "O(n log n)": {
      color: active === "O(n log n)" ? "#06b6d4" : "#4b5563",
      strokeWidth: active === "O(n log n)" ? 3.5 : 1.5,
    },
    "O(n²)": {
      color: active === "O(n²)" ? "#f59e0b" : "#64748b",
      strokeWidth: active === "O(n²)" ? 3.5 : 1.5,
    },
    "O(n³)": {
      color: active === "O(n³)" ? "#f97316" : "#52525b",
      strokeWidth: active === "O(n³)" ? 3.5 : 1.5,
    },
    "O(2^n)": {
      color: active === "O(2^n)" ? "#a855f7" : "#581c87",
      strokeWidth: active === "O(2^n)" ? 3.5 : 1.5,
    },
    "O(3^n)": {
      color: active === "O(3^n)" ? "#d946ef" : "#701a75",
      strokeWidth: active === "O(3^n)" ? 3.5 : 1.5,
    },
    "O(n!)": {
      color: active === "O(n!)" ? "#ef4444" : "#7f1d1d",
      strokeWidth: active === "O(n!)" ? 3.5 : 1.5,
    },
  };

  return (
    <div className="flex flex-col h-full bg-zinc-900/60 border border-zinc-800 rounded-xl p-4">
      {/* Chart Title and Header */}
      <div className="flex items-center justify-between mb-2">
        <div className="flex items-center gap-2">
          <TrendingUp className="w-4 h-4 text-emerald-400" />
          <h3 className="text-sm font-semibold text-zinc-200">
            Asymptotic Growth Comparison
          </h3>
        </div>
        <div className="flex items-center gap-2 text-xs">
          <span className="text-zinc-400">Class:</span>
          <span className="font-mono font-bold px-2 py-0.5 rounded bg-zinc-800 text-emerald-400 border border-zinc-700">
            {active}
          </span>
        </div>
      </div>

      {/* Recharts Container */}
      <div className="w-full h-64 min-h-[250px] relative">
        <ResponsiveContainer width="100%" height="100%">
          <LineChart
            data={graphData.growth_points}
            margin={{ top: 10, right: 20, left: 0, bottom: 5 }}
          >
            <CartesianGrid strokeDasharray="3 3" stroke="#27272a" />
            <XAxis
              dataKey="n"
              stroke="#71717a"
              fontSize={11}
              label={{
                value: "Input Size (n)",
                position: "insideBottomRight",
                offset: -5,
                fill: "#71717a",
                fontSize: 10,
              }}
            />
            <YAxis
              stroke="#71717a"
              fontSize={11}
              domain={[0, 4500]}
              label={{
                value: "Normalized Operations",
                angle: -90,
                position: "insideLeft",
                fill: "#71717a",
                fontSize: 10,
              }}
            />
            <Tooltip
              contentStyle={{
                backgroundColor: "#18181b",
                borderColor: "#3f3f46",
                borderRadius: "0.5rem",
                color: "#f4f4f5",
                fontSize: "12px",
                fontFamily: "monospace",
              }}
            />
            <Legend
              verticalAlign="top"
              height={32}
              wrapperStyle={{ fontSize: "10px", color: "#a1a1aa" }}
            />

            <Line
              type="monotone"
              dataKey="O(1)"
              stroke={curveConfigs["O(1)"].color}
              strokeWidth={curveConfigs["O(1)"].strokeWidth}
              dot={active === "O(1)"}
              isAnimationActive={true}
            />
            <Line
              type="monotone"
              dataKey="O(log n)"
              stroke={curveConfigs["O(log n)"].color}
              strokeWidth={curveConfigs["O(log n)"].strokeWidth}
              dot={active === "O(log n)"}
              isAnimationActive={true}
            />
            <Line
              type="monotone"
              dataKey="O(n)"
              stroke={curveConfigs["O(n)"].color}
              strokeWidth={curveConfigs["O(n)"].strokeWidth}
              dot={active === "O(n)"}
              isAnimationActive={true}
            />
            <Line
              type="monotone"
              dataKey="O(n log n)"
              stroke={curveConfigs["O(n log n)"].color}
              strokeWidth={curveConfigs["O(n log n)"].strokeWidth}
              dot={active === "O(n log n)"}
              isAnimationActive={true}
            />
            <Line
              type="monotone"
              dataKey="O(n²)"
              stroke={curveConfigs["O(n²)"].color}
              strokeWidth={curveConfigs["O(n²)"].strokeWidth}
              dot={active === "O(n²)"}
              isAnimationActive={true}
            />
            <Line
              type="monotone"
              dataKey="O(n³)"
              stroke={curveConfigs["O(n³)"].color}
              strokeWidth={curveConfigs["O(n³)"].strokeWidth}
              dot={active === "O(n³)"}
              isAnimationActive={true}
            />
            <Line
              type="monotone"
              dataKey="O(2^n)"
              stroke={curveConfigs["O(2^n)"].color}
              strokeWidth={curveConfigs["O(2^n)"].strokeWidth}
              dot={active === "O(2^n)"}
              isAnimationActive={true}
            />
            <Line
              type="monotone"
              dataKey="O(3^n)"
              stroke={curveConfigs["O(3^n)"].color}
              strokeWidth={curveConfigs["O(3^n)"].strokeWidth}
              dot={active === "O(3^n)"}
              isAnimationActive={true}
            />
            <Line
              type="monotone"
              dataKey="O(n!)"
              stroke={curveConfigs["O(n!)"].color}
              strokeWidth={curveConfigs["O(n!)"].strokeWidth}
              dot={active === "O(n!)"}
              isAnimationActive={true}
            />
          </LineChart>
        </ResponsiveContainer>
      </div>

      {/* Theoretical Disclaimer Note */}
      <div className="flex items-start gap-2 mt-2 pt-2 border-t border-zinc-800 text-[11px] text-zinc-400">
        <Info className="w-3.5 h-3.5 text-zinc-400 shrink-0 mt-0.5" />
        <p>
          <span className="text-zinc-300 font-medium">Theoretical Asymptotic Model: </span>
          {graphData.disclaimer}
        </p>
      </div>
    </div>
  );
};
