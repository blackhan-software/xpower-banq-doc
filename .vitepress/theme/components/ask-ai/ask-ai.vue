<script setup lang="ts">
import { ref, computed, watch, nextTick } from 'vue'
import { useRoute, useData } from 'vitepress'
import { WORKER_URL, MAX_TURNS } from '../../constants'
import { useAskAIThread } from '../../composables/use-ask-ai-thread'
import { streamChat } from '../../utils/chat-stream'
import { typesetMath } from '../../utils/mathjax'
import ChatMessage from './chat-message.vue'
import ChatInput from './chat-input.vue'

const {
  messages, input, streaming, loading, error,
  persist, clear,
} = useAskAIThread()

const route = useRoute()
const { title } = useData()

const open = ref(false)
const msgsEl = ref<HTMLElement | null>(null)
const chatInputEl = ref<InstanceType<typeof ChatInput> | null>(null)
const disabled = computed(() => !WORKER_URL)

function currentPage() {
  const path = route.path || '/'
  return { url: path, title: title.value || '' }
}

async function scrollToBottom() {
  await nextTick()
  msgsEl.value?.scrollTo({ top: msgsEl.value.scrollHeight, behavior: 'smooth' })
}

async function send() {
  const text = input.value.trim()
  if (!text || loading.value || disabled.value) return

  error.value = ''
  messages.value.push({ role: 'user', content: text })
  input.value = ''
  persist()
  await scrollToBottom()

  loading.value = true
  streaming.value = ''

  try {
    await streamChat(WORKER_URL, messages.value.slice(-MAX_TURNS), currentPage(), (delta) => {
      streaming.value += delta
      scrollToBottom()
    })
    if (streaming.value) {
      messages.value.push({ role: 'assistant', content: streaming.value })
      persist()
    }
  } catch (e) {
    const err = e as Error & { code?: string; detail?: string; status?: number }
    console.error('[Ask AI] request failed',
      { code: err.code, status: err.status, detail: err.detail, message: err.message })
    error.value = 'unavailable'
  } finally {
    streaming.value = ''
    loading.value = false
    scrollToBottom()
    await nextTick()
    typesetMath(msgsEl.value)
  }
}

watch(open, (v) => {
  if (v) {
    scrollToBottom()
    nextTick(() => {
      typesetMath(msgsEl.value)
      chatInputEl.value?.focus()
    })
  }
})
</script>

<template>
  <button
    v-if="!open"
    class="askai-fab"
    aria-label="Ask AI"
    @click="open = true"
  >
    <svg viewBox="0 0 24 24" width="22" height="22" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
      <path d="M12 3l1.8 4.7L18.5 9l-4.7 1.8L12 15l-1.8-4.2L5.5 9l4.7-1.3z"/>
      <path d="M19 14l.7 1.8L21.5 16.5l-1.8.7L19 19l-.7-1.8L16.5 16.5l1.8-.7z"/>
    </svg>
    <span>Ask AI</span>
  </button>

  <section v-else class="askai-panel" role="dialog" aria-label="Ask AI">
    <header class="askai-head">
      <strong>Ask AI</strong>
      <span class="askai-sub">XPower Banq</span>
      <button class="askai-icon" @click="clear" title="Clear conversation" aria-label="Clear">↺</button>
      <button class="askai-icon" @click="open = false" title="Close" aria-label="Close">×</button>
    </header>

    <div ref="msgsEl" class="askai-msgs">
      <p v-if="messages.length === 0 && !loading" class="askai-hint">
        Ask anything about the protocol — mechanisms, parameters, proofs, simulations. Answers cite the canonical documentation.
      </p>

      <ChatMessage
        v-for="(m, i) in messages"
        :key="i"
        :role="m.role"
        :content="m.content"
      />

      <article v-if="loading && !streaming" class="askai-msg assistant">
        <div class="askai-thinking">
          <span></span><span></span><span></span>
        </div>
      </article>
      <ChatMessage
        v-else-if="loading && streaming"
        role="assistant"
        :content="streaming"
      />

      <div v-if="error" class="askai-unavailable" role="status">
        <p><strong>💤 AI unavailable:</strong> Something just went
          wrong; please retry later to reach the assistant.</p>
      </div>
    </div>

    <ChatInput
      ref="chatInputEl"
      v-model="input"
      :loading="loading"
      :disabled="disabled"
      @submit="send"
    />
  </section>
</template>

<style scoped>
.askai-fab {
  position: fixed;
  bottom: 1.25rem;
  right: 1.25rem;
  z-index: 100;
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
  padding: 0.6rem 0.95rem;
  border: 1px solid var(--vp-c-brand-1);
  border-radius: 999px;
  background: var(--vp-c-bg-elv);
  color: var(--vp-c-brand-1);
  font: inherit;
  font-weight: 600;
  font-size: 0.9rem;
  cursor: pointer;
  box-shadow: 0 4px 14px rgba(0, 0, 0, 0.18);
  transition: transform 0.15s ease, background 0.15s ease, color 0.15s ease;
}
.askai-fab:hover {
  transform: translateY(-1px);
  background: var(--vp-c-brand-1);
  color: var(--vp-c-bg);
}

.askai-panel {
  position: fixed;
  bottom: 1.25rem;
  right: 1.25rem;
  z-index: 100;
  display: flex;
  flex-direction: column;
  width: min(420px, calc(100vw - 2rem));
  height: min(700px, calc(100vh - 2rem));
  border: 1px solid var(--vp-c-divider);
  border-radius: 14px;
  background: color-mix(in srgb, var(--vp-c-bg-elv) 88%, transparent);
  backdrop-filter: saturate(160%) blur(10px);
  -webkit-backdrop-filter: saturate(160%) blur(10px);
  box-shadow:
    0 12px 36px rgba(0, 0, 0, 0.28),
    0 0 0 1px color-mix(in srgb, var(--vp-c-brand-1) 14%, transparent),
    0 24px 60px -20px color-mix(in srgb, var(--vp-c-brand-1) 22%, transparent);
  overflow: hidden;
}

.askai-head {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.7rem 0.9rem;
  border-bottom: 1px solid var(--vp-c-divider);
  background: var(--vp-c-bg-soft);
}
.askai-head strong { color: var(--vp-c-brand-1); }
.askai-sub {
  flex: 1;
  font-size: 0.78rem;
  color: var(--vp-c-text-2);
}
.askai-icon {
  width: 1.6rem;
  height: 1.6rem;
  border: none;
  background: transparent;
  color: var(--vp-c-text-2);
  font-size: 1.1rem;
  line-height: 1;
  cursor: pointer;
  border-radius: 6px;
}
.askai-icon:hover {
  background: var(--vp-c-bg);
  color: var(--vp-c-text-1);
}

.askai-msgs {
  flex: 1;
  overflow-y: auto;
  padding: 0.9rem;
  scroll-behavior: smooth;
  background: linear-gradient(180deg,
    transparent 0%,
    transparent 40%,
    color-mix(in srgb, var(--vp-c-brand-soft) 75%, transparent) 100%);
}
.askai-hint {
  margin: 0;
  padding: 0.8rem;
  border-radius: 8px;
  background: var(--vp-c-bg-soft);
  color: var(--vp-c-text-2);
  font-size: 0.85rem;
  line-height: 1.3;
  text-align: justify;
  hyphens: auto;
  -webkit-hyphens: auto;
  overflow-wrap: break-word;
  animation: askai-blur-in 0.5s both;
}

.askai-msg { margin: 0.6rem 0; }

.askai-thinking {
  display: inline-flex;
  gap: 0.25rem;
  padding: 0.3rem 0;
}
.askai-thinking span {
  width: 6px; height: 6px;
  border-radius: 50%;
  background: var(--vp-c-brand-1);
  animation: askai-pulse 1.2s infinite ease-in-out;
}
.askai-thinking span:nth-child(2) { animation-delay: 0.15s; }
.askai-thinking span:nth-child(3) { animation-delay: 0.3s; }
@keyframes askai-pulse {
  0%, 80%, 100% { opacity: 0.3; transform: scale(0.85); }
  40% { opacity: 1; transform: scale(1); }
}
@keyframes askai-blur-in {
  0%   { filter: blur(6px); opacity: 0; transform: scale(0.97); }
  100% { filter: blur(0);   opacity: 1; transform: scale(1); }
}
@media (prefers-reduced-motion: reduce) {
  .askai-hint { animation: none; }
  .askai-thinking span { animation: none; }
}

.askai-unavailable {
  margin: 0.6rem 0 0;
  padding: 0.7rem 0.85rem;
  border-radius: 8px;
  background: var(--vp-c-default-soft);
  color: var(--vp-c-text-2);
  font-size: 0.85rem;
  line-height: 1.35;
}
.askai-unavailable p { margin: 0; }
.askai-unavailable p + p { margin-top: 0.25rem; }
.askai-unavailable strong { color: var(--vp-c-text-1); }

@media (max-width: 640px) {
  .askai-panel {
    bottom: 0;
    right: 0;
    width: 100vw;
    height: 100vh;
    border-radius: 0;
  }
}
</style>
