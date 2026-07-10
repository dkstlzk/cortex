'use client';

import type {
  GraphData, ComplianceReport, DiagnoseJob, MaintenanceEvent,
  LinkedDocument, RiskAssessment, EntityFeedback,
} from './types';

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
const API_V1 = `${API_BASE}/api/v1`;

function getToken(): string | null {
  if (typeof window === 'undefined') return null;
  try {
    const auth = localStorage.getItem('cortex_auth');
    return auth ? JSON.parse(auth).token : null;
  } catch {
    return null;
  }
}

async function apiFetch<T>(path: string, options: RequestInit = {}): Promise<T> {
  const token = getToken();
  const res = await fetch(`${API_V1}${path}`, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
      ...options.headers,
    },
  });
  if (!res.ok) throw new Error(`API error: ${res.status} ${res.statusText}`);
  return res.json();
}

export interface HealthStatus {
  ready: boolean;
  services: Record<string, string | null>;
}

export async function checkHealth(): Promise<HealthStatus> {
  return apiFetch('/ready');
}

export async function checkLiveness(): Promise<{ status: string }> {
  return apiFetch('/live');
}

export async function uploadDocument(file: File): Promise<{ document_id: string; job_id: string; status: string }> {
  const token = getToken();
  const form = new FormData();
  form.append('file', file);

  const res = await fetch(`${API_V1}/upload`, {
    method: 'POST',
    headers: token ? { Authorization: `Bearer ${token}` } : {},
    body: form,
  });

  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(err.detail || `Upload failed: ${res.status}`);
  }
  return res.json();
}

// SSE streaming for copilot query
export interface SSECallbacks {
  onToken: (text: string) => void;
  onCitation: (citation: { doc_id: string; passage_id: string; page: number | null }) => void;
  onAgentTrigger: (trigger: { worker: string; job_id: string }) => void;
  onReasoning: (content: string) => void;
  onToolCall: (toolName: string, toolArgs: Record<string, unknown>) => void;
  onToolResult: (toolName: string, result: unknown) => void;
  onError: (error: Error) => void;
  onDone: (answerId: string) => void;
}

function parseSSEStream(reader: ReadableStreamDefaultReader<Uint8Array>, callbacks: SSECallbacks, cancelled: { value: boolean }): void {
  const decoder = new TextDecoder();
  let buffer = '';

  const processLines = (lines: string[]) => {
    let currentEvent = '';
    for (const line of lines) {
      if (cancelled.value) return;
      if (line.startsWith('event: ')) {
        currentEvent = line.slice(7).trim();
      } else if (line.startsWith('data: ')) {
        try {
          const data = JSON.parse(line.slice(6));
          switch (currentEvent) {
            case 'token': callbacks.onToken(data.text); break;
            case 'citation': callbacks.onCitation(data); break;
            case 'agent_trigger': callbacks.onAgentTrigger(data); break;
            case 'reasoning': callbacks.onReasoning(data.content); break;
            case 'tool_call': callbacks.onToolCall(data.tool_name, data.tool_args); break;
            case 'tool_result': callbacks.onToolResult(data.tool_name, data.result); break;
            case 'error': callbacks.onError(new Error(data.message)); break;
            case 'done': callbacks.onDone(data.answer_id); break;
          }
        } catch {}
        currentEvent = '';
      }
    }
  };

  (async () => {
    try {
      while (true) {
        const { done, value } = await reader.read();
        if (done || cancelled.value) break;
        buffer += decoder.decode(value, { stream: true });
        const parts = buffer.split('\n');
        buffer = parts.pop() || '';
        processLines(parts);
      }
      if (buffer.trim()) processLines(buffer.split('\n'));
    } catch (err) {
      if (!cancelled.value) callbacks.onError(err as Error);
    }
  })();
}

export function streamQuery(query: string, entityTag: string | null, callbacks: SSECallbacks): () => void {
  const cancelled = { value: false };
  const controller = new AbortController();
  const sessionId = `session-${Date.now()}`;

  (async () => {
    try {
      const token = getToken();
      const res = await fetch(`${API_V1}/query`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          ...(token ? { Authorization: `Bearer ${token}` } : {}),
        },
        body: JSON.stringify({
          query,
          session_id: sessionId,
          focused_tag: entityTag || null,
        }),
        signal: controller.signal,
      });

      if (!res.ok) {
        const err = await res.json().catch(() => ({ detail: res.statusText }));
        callbacks.onError(new Error(err.detail || `Query failed: ${res.status}`));
        return;
      }

      const reader = res.body?.getReader();
      if (!reader) { callbacks.onError(new Error('No response body')); return; }
      parseSSEStream(reader, callbacks, cancelled);
    } catch (err) {
      if (!cancelled.value) callbacks.onError(err as Error);
    }
  })();

  return () => {
    cancelled.value = true;
    controller.abort();
  };
}

// Direct agent invocation (bypasses copilot/supervisor)
export function streamAgent(
  worker: 'asset' | 'diagnose' | 'comply',
  query: string,
  entityTag: string | null,
  callbacks: SSECallbacks,
): () => void {
  const cancelled = { value: false };
  const controller = new AbortController();
  const sessionId = `agent-${worker}-${Date.now()}`;

  (async () => {
    try {
      const token = getToken();
      const res = await fetch(`${API_V1}/agents/${worker}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          ...(token ? { Authorization: `Bearer ${token}` } : {}),
        },
        body: JSON.stringify({
          query,
          session_id: sessionId,
          focused_tag: entityTag || null,
        }),
        signal: controller.signal,
      });

      if (!res.ok) {
        const err = await res.json().catch(() => ({ detail: res.statusText }));
        callbacks.onError(new Error(err.detail || `Agent ${worker} failed: ${res.status}`));
        return;
      }

      const reader = res.body?.getReader();
      if (!reader) { callbacks.onError(new Error('No response body')); return; }
      parseSSEStream(reader, callbacks, cancelled);
    } catch (err) {
      if (!cancelled.value) callbacks.onError(err as Error);
    }
  })();

  return () => {
    cancelled.value = true;
    controller.abort();
  };
}

// Neo4j graph data - fetched via the diagnose agent asking about relationships
// Since there's no dedicated graph endpoint, we query Neo4j context through the agent
export async function fetchGraphFromAgent(tag: string): Promise<{ nodes: any[]; edges: any[]; center: string }> {
  return new Promise((resolve, reject) => {
    let fullText = '';
    const nodes: any[] = [];
    const edges: any[] = [];
    let graphContext: any = null;

    streamAgent('asset', `Show me all equipment, documents, and relationships connected to ${tag}. Include component details, failure modes, and related procedures.`, tag, {
      onToken: (text) => { fullText += text; },
      onCitation: () => {},
      onAgentTrigger: () => {},
      onReasoning: () => {},
      onToolCall: () => {},
      onToolResult: (_name, result) => {
        // The tool_result from context_graph_query contains the graph data
        if (result && typeof result === 'object') {
          graphContext = result;
        }
      },
      onError: (err) => reject(err),
      onDone: () => {
        // Try to extract graph structure from tool results
        if (graphContext) {
          try {
            const ctx = typeof graphContext === 'string' ? JSON.parse(graphContext) : graphContext;
            if (ctx.entities) {
              ctx.entities.forEach((e: any, i: number) => {
                nodes.push({
                  id: e.id || e.tag || `node-${i}`,
                  tag: e.tag || e.id || `node-${i}`,
                  label: e.name || e.label || e.tag || `Node ${i}`,
                  type: e.type || 'equipment',
                  properties: e.properties || {},
                  confidence: e.confidence ?? 1.0,
                });
              });
            }
            if (ctx.relationships) {
              ctx.relationships.forEach((r: any, i: number) => {
                edges.push({
                  id: r.id || `edge-${i}`,
                  source: r.source || r.from,
                  target: r.target || r.to,
                  relationship: r.type || r.relationship || 'related_to',
                  confidence: r.confidence ?? 0.9,
                });
              });
            }
          } catch {}
        }

        resolve({ nodes, edges, center: tag });
      },
    });
  });
}

// Upload document to real backend
export async function uploadDocumentFile(file: File, onProgress?: (pct: number) => void): Promise<{ document_id: string; job_id: string; status: string }> {
  return uploadDocument(file);
}
