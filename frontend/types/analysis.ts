export interface SyntaxErrorInfo {
  line: number;
  column: number;
  message: string;
  snippet?: string;
}

export interface CodeStatistics {
  function_count: number;
  loop_count: number;
  for_loop_count: number;
  while_loop_count: number;
  conditional_count: number;
  max_nesting_depth: number;
  recursion_detected: boolean;
  recursion_count: number;
  operation_count: number;
  comprehension_count: number;
  imported_modules: string[];
}

export interface CodeStructureNode {
  id: string;
  label: string;
  node_type: string;
  line?: number;
  complexity?: string;
  details?: string;
}

export interface CodeStructureEdge {
  id: string;
  source: string;
  target: string;
  label?: string;
}

export interface CodeStructureData {
  nodes: CodeStructureNode[];
  edges: CodeStructureEdge[];
}

export interface SpaceBreakdown {
  auxiliary: string;
  recursion_stack: string;
  output: string;
  total_retained: string;
}

export interface RecurrenceInfo {
  present: boolean;
  expression?: string;
  is_solved: boolean;
  branching_factor: number;
  total_call_sites: number;
  derivation_steps: string[];
}

export interface TheoreticalGraphData {
  active_complexity: string;
  growth_points: Record<string, any>[];
  disclaimer: string;
}

export interface AnalyzeResponse {
  success: boolean;
  time_complexity: string;
  tight_bound?: string;
  space_complexity: string;
  space_breakdown?: SpaceBreakdown;
  confidence: "HIGH" | "MEDIUM" | "LOW" | "UNSUPPORTED";
  confidence_reasons?: string[];
  complexity_reasoning: string;
  recurrence?: RecurrenceInfo;
  statistics: CodeStatistics;
  detected_patterns: string[];
  optimization_suggestions: string[];
  structure: CodeStructureData;
  graph: TheoreticalGraphData;
  functions: Record<string, any>[];
  loops: Record<string, any>[];
  recursion: Record<string, any>;
  error?: SyntaxErrorInfo;
  submission_id?: string;
}

export interface HistoryItem {
  id: string;
  submission_id: string;
  title: string;
  code_snippet: string;
  time_complexity: string;
  space_complexity: string;
  confidence: string;
  created_at: string;
}

export interface HistoryDetail extends HistoryItem {
  code: string;
  complexity_reasoning: string;
  statistics: CodeStatistics;
  structure: CodeStructureData;
  graph_data: TheoreticalGraphData;
  detected_patterns: string[];
  optimization_suggestions: string[];
}
