import type { Message } from '../composables/use-ask-ai-thread'

export interface PageContext { url: string; title: string }

export async function streamChat(
  workerUrl: string,
  messages: Message[],
  page: PageContext | null,
  onChunk: (delta: string) => void,
): Promise<void> {
  const res = await fetch(`${workerUrl}/chat`, {
    method: 'POST',
    headers: { 'content-type': 'application/json' },
    body: JSON.stringify(page ? { messages, page } : { messages }),
  })

  if (!res.ok || !res.body) {
    const raw = await res.text().catch(() => '')
    let code: string | undefined
    let detail = raw
    try {
      const parsed = JSON.parse(raw)
      code = parsed.error
      if (parsed.detail) detail = parsed.detail
    } catch { /* non-JSON body — keep raw text as detail */ }
    const err = new Error(code ?? `http_${res.status}`) as Error & {
      code?: string; detail?: string; status?: number
    }
    err.code = code
    err.detail = detail
    err.status = res.status
    throw err
  }

  const reader = res.body.getReader()
  const decoder = new TextDecoder()
  let buf = ''

  while (true) {
    const { done, value } = await reader.read()
    if (done) break
    buf += decoder.decode(value, { stream: true })

    let idx
    while ((idx = buf.indexOf('\n\n')) >= 0) {
      const event = buf.slice(0, idx)
      buf = buf.slice(idx + 2)
      const dataLine = event.split('\n').find(l => l.startsWith('data: '))
      if (!dataLine) continue
      try {
        const payload = JSON.parse(dataLine.slice(6))
        if (payload.type === 'content_block_delta' && payload.delta?.type === 'text_delta') {
          onChunk(payload.delta.text)
        }
      } catch {}
    }
  }
}
