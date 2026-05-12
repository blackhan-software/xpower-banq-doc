import { MAX_TURNS, STORAGE_KEY } from '../constants';
import { onMounted, ref } from 'vue';

/** One turn in the Ask-AI conversation. */
export interface Message {
  role: 'user' | 'assistant';
  content: string;
}

/**
 * Reactive state and persistence for a single Ask-AI thread.
 *
 * Owns the message list, the draft `input`, the in-flight `streaming`
 * assistant text, and `loading`/`error` flags. The thread is mirrored to
 * `localStorage` (capped at `MAX_TURNS`) and restored on mount.
 *
 * @returns the reactive refs plus `persist()` and `clear()` helpers.
 */
export function useAskAIThread() {
  const messages = ref<Message[]>([])
  const input = ref('')
  const streaming = ref('')
  const loading = ref(false)
  const error = ref('')
  /**
   * Write the most recent `MAX_TURNS` messages to localStorage; failures are ignored.
   */
  function persist() {
    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(
        messages.value.slice(-MAX_TURNS)
      ))
    } catch { }
  }
  /**
   * Load the persisted thread from localStorage; failures leave messages empty.
   */
  function restore() {
    try {
      const raw = localStorage.getItem(STORAGE_KEY)
      if (raw) messages.value = JSON.parse(raw)
    } catch { }
  }
  /**
   * Reset the thread (messages, streaming text, error) and persist the empty state.
   */
  function clear() {
    messages.value = []
    streaming.value = ''
    error.value = ''
    persist()
  }

  onMounted(restore)
  return {
    messages, input, streaming, loading, error,
    persist, clear,
  }
}
