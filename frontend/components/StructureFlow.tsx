"use client";

import React, { useMemo } from "react";
import {
  ReactFlow,
  Controls,
  Background,
  MiniMap,
  Node,
  Edge,
  MarkerType,
} from "@xyflow/react";
import "@xyflow/react/dist/style.css";
import { CodeStructureData } from "@/types/analysis";
import { Network, Terminal, GitBranch, Repeat, CornerDownLeft, Play } from "lucide-react";

interface StructureFlowProps {
  structure: CodeStructureData;
}

// Custom Node Component
const CustomStructureNode = ({ data }: { data: any }) => {
  const getNodeBadge = () => {
    switch (data.node_type) {
      case "function":
        return {
          icon: <Terminal className="w-3 h-3 text-indigo-400" />,
          border: "border-indigo-500/50 bg-indigo-950/40 text-indigo-200",
          tag: "DEF",
        };
      case "loop":
        return {
          icon: <Repeat className="w-3 h-3 text-emerald-400" />,
          border: "border-emerald-500/50 bg-emerald-950/40 text-emerald-200",
          tag: data.complexity || "LOOP",
        };
      case "conditional":
        return {
          icon: <GitBranch className="w-3 h-3 text-blue-400" />,
          border: "border-blue-500/50 bg-blue-950/40 text-blue-200",
          tag: "IF",
        };
      case "return":
        return {
          icon: <CornerDownLeft className="w-3 h-3 text-amber-400" />,
          border: "border-amber-500/50 bg-amber-950/40 text-amber-200",
          tag: "RET",
        };
      case "root":
        return {
          icon: <Play className="w-3 h-3 text-teal-400" />,
          border: "border-teal-500/50 bg-teal-950/40 text-teal-200",
          tag: "ENTRY",
        };
      default:
        return {
          icon: <Terminal className="w-3 h-3 text-zinc-400" />,
          border: "border-zinc-700 bg-zinc-800/80 text-zinc-300",
          tag: "STEP",
        };
    }
  };

  const badge = getNodeBadge();

  return (
    <div
      className={`px-3 py-2 rounded-lg border shadow-lg backdrop-blur min-w-[150px] max-w-[260px] ${badge.border}`}
    >
      <div className="flex items-center justify-between gap-2 mb-1">
        <div className="flex items-center gap-1.5">
          {badge.icon}
          <span className="text-[10px] font-mono font-bold uppercase tracking-wider text-zinc-400">
            {badge.tag}
          </span>
        </div>
        {data.line && (
          <span className="text-[9px] font-mono px-1.5 py-0.2 rounded bg-black/40 text-zinc-400 border border-zinc-700/50">
            L{data.line}
          </span>
        )}
      </div>

      <div className="text-xs font-mono font-semibold truncate text-zinc-100" title={data.label}>
        {data.label}
      </div>

      {data.details && (
        <div className="text-[10px] text-zinc-400 truncate mt-0.5">
          {data.details}
        </div>
      )}
    </div>
  );
};

const nodeTypes = {
  custom: CustomStructureNode,
};

export const StructureFlow: React.FC<StructureFlowProps> = ({ structure }) => {
  // Convert backend nodes & edges into React Flow format with calculated hierarchical positions
  const { flowNodes, flowEdges } = useMemo(() => {
    if (!structure.nodes || structure.nodes.length === 0) {
      return { flowNodes: [], flowEdges: [] };
    }

    // Map children adjacency
    const childrenMap: Record<string, string[]> = {};
    structure.edges.forEach((e) => {
      if (!childrenMap[e.source]) childrenMap[e.source] = [];
      childrenMap[e.source].push(e.target);
    });

    // Compute levels via BFS/DFS from root node
    const levelMap: Record<string, number> = {};
    const orderInLevel: Record<number, number> = {};

    const rootId = structure.nodes[0]?.id || "";
    levelMap[rootId] = 0;

    const queue = [rootId];
    const visited = new Set<string>([rootId]);

    while (queue.length > 0) {
      const current = queue.shift()!;
      const curLevel = levelMap[current] || 0;
      const children = childrenMap[current] || [];

      children.forEach((childId) => {
        if (!visited.has(childId)) {
          visited.add(childId);
          levelMap[childId] = curLevel + 1;
          queue.push(childId);
        }
      });
    }

    // Assign any unvisited nodes
    structure.nodes.forEach((n) => {
      if (levelMap[n.id] === undefined) {
        levelMap[n.id] = 1;
      }
    });

    const flowNodes: Node[] = structure.nodes.map((n) => {
      const level = levelMap[n.id] || 0;
      const countAtLevel = orderInLevel[level] || 0;
      orderInLevel[level] = countAtLevel + 1;

      // Layout coordinates: X spaced per sibling, Y spaced per level
      const x = 50 + countAtLevel * 220;
      const y = 40 + level * 95;

      return {
        id: n.id,
        type: "custom",
        position: { x, y },
        data: {
          label: n.label,
          node_type: n.node_type,
          line: n.line,
          complexity: n.complexity,
          details: n.details,
        },
      };
    });

    const flowEdges: Edge[] = structure.edges.map((e) => ({
      id: e.id,
      source: e.source,
      target: e.target,
      label: e.label,
      animated: true,
      style: { stroke: "#52525b", strokeWidth: 1.5 },
      markerEnd: {
        type: MarkerType.ArrowClosed,
        color: "#71717a",
        width: 15,
        height: 15,
      },
      labelStyle: { fill: "#a1a1aa", fontSize: 10, fontFamily: "monospace" },
      labelBgStyle: { fill: "#18181b", stroke: "#27272a", rx: 4, ry: 4 },
    }));

    return { flowNodes, flowEdges };
  }, [structure]);

  return (
    <div className="flex flex-col h-full bg-zinc-900/60 border border-zinc-800 rounded-xl overflow-hidden p-4">
      <div className="flex items-center justify-between mb-2">
        <div className="flex items-center gap-2">
          <Network className="w-4 h-4 text-emerald-400" />
          <h3 className="text-sm font-semibold text-zinc-200">
            AST Control Flow & Hierarchy
          </h3>
        </div>
        <span className="text-xs text-zinc-400 font-mono">
          {structure.nodes.length} Nodes • {structure.edges.length} Edges
        </span>
      </div>

      <div className="w-full h-72 min-h-[280px] bg-zinc-950/80 rounded-lg border border-zinc-800/80 relative">
        <ReactFlow
          nodes={flowNodes}
          edges={flowEdges}
          nodeTypes={nodeTypes}
          fitView
          fitViewOptions={{ padding: 0.2 }}
          minZoom={0.2}
          maxZoom={1.5}
        >
          <Background color="#27272a" gap={16} size={1} />
          <Controls className="!bg-zinc-800 !border-zinc-700 !fill-zinc-300" />
          <MiniMap
            nodeColor="#3f3f46"
            maskColor="rgba(0, 0, 0, 0.6)"
            className="!bg-zinc-900 !border-zinc-800 rounded-lg"
          />
        </ReactFlow>
      </div>
    </div>
  );
};
