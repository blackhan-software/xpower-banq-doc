// Cloudflare Worker proxying an Anthropic-compatible Messages API
// (Anthropic by default, or DeepSeek via API_PROVIDER); for the "Ask
// AI" widget. Two blocks ride together: The ai-system.md (prose style
// guide) and ai-corpus.md (docs-only knowledge bundle, <100K tokens).
//
// The corpus carries a `cache_control` marker, so repeat requests hit
// Anthropic's 1h prompt cache (silently ignored by DeepSeek's compat
// layer); see: ../scripts/ai-corpus/index.mjs.

import { rateLimit as rate_limit } from './rate-limit';

import ai_corpus from './ai-corpus.md';
import ai_system from './ai-system.md';

/**
 * Cloudflare bindings (vars + secrets) injected into each fetch handler.
 */
interface Env {
  // Comma-separated CORS allowlist for /chat.
  ALLOWED_ORIGINS: string;
  // Anthropic Messages API key — Worker secret, never bundled.
  ANTHROPIC_API_KEY: string;
  // Upstream provider; picks base URL + which API-key secret to send.
  API_PROVIDER: 'anthropic' | 'deepseek';
  // DeepSeek Messages API key (Anthropic-compat endpoint) — Worker secret.
  DEEPSEEK_API_KEY: string;
  // Per-request output-token cap, parsed as int with a 1024 fallback.
  MAX_TOKENS: string;
  // Model id (e.g. claude-sonnet-4-6 or deepseek-v4-pro).
  MODEL: string;
  // KV namespace backing per-IP rate-limit counters; absent in local dev.
  RATELIMIT?: KVNamespace;
}

/**
 * One turn of the chat history sent up by the widget.
 */
interface ChatMessage {
  role: 'user' | 'assistant';
  content: string;
}

/**
 * Optional page-context hint sent by the widget: the docs URL and title
 * the user is currently viewing. Injected as a non-cached system block
 * so the AI can resolve deictic phrases like "this page" or "here".
 */
interface PageContext {
  url: string;
  title: string;
}

/**
 * POST /chat body: alternating turns ending on a user turn, plus an
 * optional page-context hint.
 */
interface ChatRequest {
  messages: ChatMessage[];
  page?: PageContext;
}

// Hard cap on conversation history length; the client trims older turns.
const MAX_TURNS = 16;
// Aggregate cap on user-authored bytes per request, to bound prompt-injection surface.
const MAX_USER_BYTES = 8192;
// Max length of the current-page URL path sent as a context hint.
const MAX_PAGE_URL_LENGTH = 256;
// Max length of the current-page title sent as a context hint.
const MAX_PAGE_TITLE_LENGTH = 256;

export default {
  /**
   * Worker entry point: handles CORS preflight, /health, and POST /chat
   * (rate-limited, validated, then streamed from Anthropic).
   */
  async fetch(req: Request, env: Env): Promise<Response> {
    const url = new URL(req.url);
    const origin = req.headers.get('Origin') || '';
    const cors = corsHeaders(origin, env.ALLOWED_ORIGINS);
    if (req.method === 'OPTIONS') {
      return new Response(null, { status: 204, headers: cors });
    }
    if (url.pathname === '/health') {
      return new Response(JSON.stringify({ ok: true, model: env.MODEL }), {
        headers: { 'content-type': 'application/json', ...cors },
      });
    }
    if (url.pathname !== '/chat' || req.method !== 'POST') {
      return new Response('Not found', { status: 404, headers: cors });
    }
    if (!cors['Access-Control-Allow-Origin']) {
      return new Response('Origin not allowed', { status: 403 });
    }
    const ip = req.headers.get('CF-Connecting-IP') || '0.0.0.0';
    const limited = await rate_limit(env.RATELIMIT, ip);
    if (limited) {
      return new Response(limited.body, {
        status: limited.status, headers: {
          ...Object.fromEntries(limited.headers), ...cors,
        },
      });
    }
    let body: ChatRequest;
    try {
      body = await req.json();
    } catch {
      return jsonError(400, 'invalid_json', cors);
    }
    const validation = validate(body);
    if (validation) {
      return jsonError(400, validation, cors);
    }
    return streamChat(body.messages, body.page ?? null, env, cors);
  },
} satisfies ExportedHandler<Env>;

/**
 * Shape-check the request body; returns an error code, or null on success.
 */
function validate(body: ChatRequest): string | null {
  if (!body || !Array.isArray(body.messages) || body.messages.length === 0) {
    return 'messages_required';
  }
  if (body.messages.length > MAX_TURNS) {
    return 'too_many_turns';
  }
  let total_user_bytes = 0;
  for (const m of body.messages) {
    if (m.role !== 'user' && m.role !== 'assistant') {
      return 'bad_role';
    }
    if (typeof m.content !== 'string') {
      return 'bad_content';
    }
    if (m.role === 'user') {
      total_user_bytes += new TextEncoder().encode(m.content).length;
    }
  }
  if (total_user_bytes > MAX_USER_BYTES) {
    return 'user_content_too_large';
  }
  if (body.messages.at(-1)?.role !== 'user') {
    return 'last_turn_must_be_user'; // Anthropic requirement
  }
  if (body.page !== undefined) {
    if (typeof body.page !== 'object' || body.page === null) {
      return 'bad_page';
    }
    if (typeof body.page.url !== 'string' || typeof body.page.title !== 'string') {
      return 'bad_page';
    }
    if (!body.page.url.startsWith('/') || body.page.url.length > MAX_PAGE_URL_LENGTH) {
      return 'bad_page_url';
    }
    if (body.page.title.length > MAX_PAGE_TITLE_LENGTH) {
      return 'bad_page_title';
    }
  }
  return null;
}

/**
 * Render the page-context hint as a short instruction the AI can act on.
 * Returns null if there's nothing useful to inject.
 */
function pageContext(page: PageContext | null): string | null {
  if (!page) {
    return null;
  }
  const url = page.url.trim();
  if (!url || url === '/') {
    return null;
  }
  const title = page.title.trim();
  const titled = title ? ` (titled ${JSON.stringify(title)})` : '';
  return [
    `The user is currently viewing the documentation page at \`${url}\`${titled}.`,
    `When the user refers to "this page", "here", "the current page", or asks a`
    + ` contextual question like "what is this about" without naming a topic, treat`
    + ` the question as being about that page. Find the matching \`## FILE: ${url}\``
    + ` block in the corpus and answer based on it. Otherwise answer normally from`
    + ` the corpus as a whole.`,
  ].join('\n\n');
}

/**
 * Forward the chat history to Anthropic with streaming enabled and pipe
 * the SSE body straight back to the browser.
 */
async function streamChat(
  messages: ChatMessage[], page: PageContext | null,
  env: Env, cors: Record<string, string>,
): Promise<Response> {
  const system: Array<{
    type: 'text'; text: string; cache_control?: {
      type: 'ephemeral'; ttl: '1h',
    };
  }> = [{
    type: 'text', text: ai_system,
  }, {
    type: 'text', text: ai_corpus, cache_control: {
      type: 'ephemeral', ttl: '1h',
    },
  }];
  const ctx = pageContext(page);
  if (ctx) {
    system.push({ type: 'text', text: ctx });
  }
  const provider = env.API_PROVIDER === 'deepseek'
    ? { url: 'https://api.deepseek.com/anthropic/v1/messages', key: env.DEEPSEEK_API_KEY }
    : { url: 'https://api.anthropic.com/v1/messages', key: env.ANTHROPIC_API_KEY };
  const upstream = await fetch(provider.url, {
    method: 'POST',
    headers: {
      'anthropic-version': '2023-06-01',
      'content-type': 'application/json',
      'x-api-key': provider.key,
    },
    body: JSON.stringify({
      max_tokens: parseInt(env.MAX_TOKENS, 10) || 1024,
      model: env.MODEL,
      stream: true,
      system,
      messages,
    }),
  });
  if (!upstream.ok || !upstream.body) {
    const text = await upstream.text().catch(() => '');
    return jsonError(
      502, `upstream_${upstream.status}`, cors, text.slice(0, 500),
    );
  }
  return new Response(upstream.body, {
    status: 200, headers: {
      ...cors,
      'content-type': 'text/event-stream',
      'cache-control': 'no-cache, no-transform',
      'x-accel-buffering': 'no',
    },
  });
}

/**
 * Build CORS response headers; sets Allow-Origin only when the request
 * origin is in ALLOWED_ORIGINS.
 */
function corsHeaders(origin: string, allowed: string): Record<string, string> {
  const list = allowed.split(',').map(s => s.trim()).filter(Boolean);
  const headers: Record<string, string> = {
    'Access-Control-Allow-Methods': 'POST, OPTIONS',
    'Access-Control-Allow-Headers': 'content-type',
    'Access-Control-Max-Age': '86400',
    'Vary': 'Origin',
  };
  const ok = list.includes(origin);
  if (ok) {
    headers['Access-Control-Allow-Origin'] = origin;
  }
  return headers;
}

/**
 * JSON error response with a stable error code and optional detail string.
 */
function jsonError(
  status: number, code: string, cors: Record<string, string>, detail?: string
): Response {
  return new Response(
    JSON.stringify({
      error: code, ...(detail ? { detail } : {})
    }),
    {
      status, headers: {
        'content-type': 'application/json', ...cors,
      },
    }
  );
}
