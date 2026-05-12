// Ask-AI Worker endpoint, injected at build time; empty string disables the widget.
export const WORKER_URL = (import.meta.env.VITE_AI_WORKER_URL as string | undefined) ?? '';
// localStorage key for the persisted chat thread; bump the suffix to invalidate stored threads.
export const STORAGE_KEY = 'askai:thread:v1';
// Per-message character cap on the input box (mirrored by the Worker's byte budget).
export const MAX_INPUT_LENGTH = 256;
// Hard cap on thread length; older turns are trimmed once exceeded.
export const MAX_TURNS = 16;
