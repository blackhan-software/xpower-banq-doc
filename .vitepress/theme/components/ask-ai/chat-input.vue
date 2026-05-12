<script setup lang="ts">
import { computed, ref } from 'vue'
import { MAX_INPUT_LENGTH } from '../../constants'

const props = defineProps<{
  modelValue: string
  disabled: boolean
  loading: boolean
}>()

const textareaEl = ref<HTMLTextAreaElement | null>(null)

function focus() {
  textareaEl.value?.focus()
}

defineExpose({ focus })

const remaining = computed(
  () => MAX_INPUT_LENGTH - props.modelValue.length
)

const emit = defineEmits<{
  'update:modelValue': [value: string]
  submit: []
}>()

function onInput(e: Event) {
  emit('update:modelValue', (e.target as HTMLTextAreaElement).value)
}

function onKeydown(e: KeyboardEvent) {
  if (e.key === 'Enter' && !e.shiftKey) {
    e.preventDefault()
    emit('submit')
  }
}
</script>

<template>
  <form class="askai-form" @submit.prevent="emit('submit')">
    <div class="askai-input-wrap">
      <textarea
        ref="textareaEl"
        :value="modelValue"
        rows="2"
        :maxlength="MAX_INPUT_LENGTH"
        :disabled="loading || disabled"
        :placeholder="disabled ? 'Ask AI is not configured (missing VITE_AI_WORKER_URL)' : 'Ask about XPower Banq…'"
        @input="onInput"
        @keydown="onKeydown"
      />
    </div>
    <button
      type="submit"
      class="askai-send"
      aria-label="Send"
      data-tip="Send"
      :disabled="loading || disabled || !modelValue.trim()"
    >
      <i class="bi bi-send-fill" aria-hidden="true"></i>
      <span v-if="remaining < 16" class="askai-counter">{{ remaining }}</span>
    </button>
  </form>
</template>

<style scoped>
.askai-form {
  display: flex;
  gap: 0.5rem;
  padding: 0.7rem;
  border-top: 1px solid var(--vp-c-divider);
  background: var(--vp-c-bg);
}
.askai-input-wrap {
  flex: 1;
  position: relative;
  display: flex;
}
.askai-form textarea {
  width: 100%;
  resize: none;
  padding: 0.5rem 0.6rem;
  border: 1px solid var(--vp-c-divider);
  border-radius: 6px;
  background: var(--vp-c-bg-elv);
  color: var(--vp-c-text-1);
  font: inherit;
  font-size: 0.92rem;
  line-height: 1.3;
  scrollbar-width: none; /* Firefox */
}
.askai-form textarea::-webkit-scrollbar {
  display: none; /* Chromium, WebKit */
}
.askai-counter {
  position: absolute;
  left: 0.35rem;
  bottom: 0.2rem;
  font-size: 0.65rem;
  line-height: 1;
  color: var(--vp-c-bg);
  opacity: 0.85;
  pointer-events: none;
  user-select: none;
  font-variant-numeric: tabular-nums;
}
.askai-form textarea:focus {
  outline: none;
  border-color: var(--vp-c-brand-1);
}
@media (pointer: coarse) {
  /* iOS Safari auto-zooms on focus when an input's font-size is below 16px. */
  .askai-form textarea {
    font-size: 16px;
  }
}
.askai-send {
  position: relative;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  flex: 0 0 auto;
  align-self: stretch;
  aspect-ratio: 1 / 1;
  height: auto;
  width: auto;
  min-height: 59.2px;
  min-width: 59.2px;
  padding: 0;
  border: none;
  border-radius: 6px;
  background: var(--vp-c-brand-1);
  color: var(--vp-c-bg);
  font: inherit;
  font-weight: 600;
  cursor: pointer;
}
.askai-send .bi {
  font-size: 1.1rem;
  line-height: 1;
}
.askai-send::after,
.askai-send::before {
  pointer-events: none;
  opacity: 0;
  transition: opacity 0.15s ease;
  transition-delay: 0s;
}
.askai-send::after {
  content: attr(data-tip);
  position: absolute;
  bottom: calc(100% + 6px);
  left: 50%;
  transform: translateX(-50%);
  padding: 0.25rem 0.55rem;
  border-radius: 4px;
  background: var(--vp-c-text-1);
  color: var(--vp-c-bg);
  font-size: 0.75rem;
  font-weight: 500;
  line-height: 1.2;
  white-space: nowrap;
}
.askai-send::before {
  content: "";
  position: absolute;
  bottom: calc(100% + 1px);
  left: 50%;
  transform: translateX(-50%);
  width: 0;
  height: 0;
  border: 4px solid transparent;
  border-top-color: var(--vp-c-text-1);
}
.askai-send:hover:not(:disabled)::after,
.askai-send:hover:not(:disabled)::before,
.askai-send:focus-visible:not(:disabled)::after,
.askai-send:focus-visible:not(:disabled)::before {
  opacity: 1;
  transition-delay: 0.4s;
}
.askai-send:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}
</style>
