import { AnalyzeResponse, HistoryItem, HistoryDetail } from "@/types/analysis";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api";

export async function analyzeCode(code: string, title?: string): Promise<AnalyzeResponse> {
  const response = await fetch(`${API_BASE}/analyze`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      code,
      title: title || "Analysis Session",
    }),
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({ detail: "Network request failed" }));
    throw new Error(errorData.detail || `Server error: ${response.status}`);
  }

  return response.json();
}

export async function getHistory(): Promise<HistoryItem[]> {
  const response = await fetch(`${API_BASE}/history`, {
    method: "GET",
    headers: {
      "Content-Type": "application/json",
    },
  });

  if (!response.ok) {
    throw new Error(`Failed to load history: ${response.status}`);
  }

  return response.json();
}

export async function getHistoryDetail(submissionId: string): Promise<HistoryDetail> {
  const response = await fetch(`${API_BASE}/history/${submissionId}`, {
    method: "GET",
    headers: {
      "Content-Type": "application/json",
    },
  });

  if (!response.ok) {
    throw new Error(`Failed to load analysis detail: ${response.status}`);
  }

  return response.json();
}

export async function checkBackendHealth(): Promise<{
  status: string;
  database: { connected: boolean; type: string; error?: string };
}> {
  try {
    const response = await fetch(`${API_BASE}/health`, {
      method: "GET",
      headers: { "Content-Type": "application/json" },
      signal: AbortSignal.timeout(3000),
    });
    if (!response.ok) {
      return { status: "degraded", database: { connected: false, type: "none" } };
    }
    return response.json();
  } catch (err) {
    return { status: "offline", database: { connected: false, type: "disconnected" } };
  }
}
