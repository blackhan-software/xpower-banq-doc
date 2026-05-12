<script setup lang="ts">
import { computed } from 'vue'
import { render } from '../../utils/render'

const props = defineProps<{
  role: 'user' | 'assistant'
  content: string
}>()

const html = computed(() => render(props.content))
</script>

<template>
  <article :class="['askai-msg', role]">
    <div v-if="role === 'user'" class="askai-user">{{ content }}</div>
    <div v-else class="askai-bot vp-doc" v-html="html"></div>
  </article>
</template>

<style scoped>
.askai-msg {
  margin: 0.6rem 0;
  animation: askai-msg-in 0.35s both;
}
.askai-msg.user { display: flex; justify-content: flex-end; }

@keyframes askai-msg-in {
  0%   { filter: blur(4px); opacity: 0; transform: translateY(4px); }
  100% { filter: blur(0);   opacity: 1; transform: translateY(0); }
}
@media (prefers-reduced-motion: reduce) {
  .askai-msg { animation: none; }
}

.askai-user {
  max-width: 85%;
  padding: 0.5rem 0.75rem;
  border-radius: 12px 12px 2px 12px;
  background: var(--vp-c-brand-soft);
  color: var(--vp-c-text-1);
  font-size: 0.92rem;
  line-height: 1.3;
  white-space: pre-wrap;
  word-wrap: break-word;
}

.askai-bot {
  font-size: 0.92rem;
  line-height: 1.3;
}
.askai-bot :deep(p) { margin: 0.4rem 0; line-height: 1.3; text-align: justify; text-justify: inter-word; hyphens: none; }
.askai-bot :deep(p:first-child) { margin-top: 0; }
.askai-bot :deep(p:last-child) { margin-bottom: 0; }
.askai-bot :deep(a) { color: var(--vp-c-brand-1); text-decoration: underline; }
.askai-bot :deep(code) {
  padding: 1px 4px;
  border-radius: 3px;
  background: var(--vp-c-bg-soft);
  font-size: 0.85em;
}
.askai-bot :deep(pre) {
  padding: 0.6rem;
  border-radius: 6px;
  background: var(--vp-c-bg);
  overflow-x: auto;
  font-size: 0.82em;
  line-height: 1.3;
}
.askai-bot :deep(ul),
.askai-bot :deep(ol) { padding-left: 1.2rem; margin: 0.4rem 0; }
.askai-bot :deep(li) { line-height: 1.3; margin: 0.3rem 0; }
</style>
