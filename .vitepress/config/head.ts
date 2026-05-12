import type { HeadConfig } from 'vitepress'
import { aiWorkerUrl, appUrl, paperUrl } from './env'

// Only emit preconnect when the worker is on a real host — preconnecting to
// localhost or an unset URL produces a warning and burns a render slot.
const aiWorkerHost = (() => {
  try {
    const { protocol, host } = new URL(aiWorkerUrl)
    if (!host || protocol === 'file:') return ''
    if (/^(localhost|127\.0\.0\.1|0\.0\.0\.0)/.test(host)) return ''
    return `${protocol}//${host}`
  } catch {
    return ''
  }
})()

export const head: HeadConfig[] = [
  ['link', { rel: 'icon', type: 'image/svg+xml', href: '/logo/BANQ-000.svg', media: '(prefers-color-scheme: light)' }],
  ['link', { rel: 'icon', type: 'image/svg+xml', href: '/logo/BANQ-fff.svg', media: '(prefers-color-scheme: dark)' }],
  ['link', { rel: 'apple-touch-icon', sizes: '180x180', href: '/apple-touch-icon.png' }],
  ['meta', { name: 'theme-color', content: '#ffffff', media: '(prefers-color-scheme: light)' }],
  ['meta', { name: 'theme-color', content: '#0f172a', media: '(prefers-color-scheme: dark)' }],
  // og:type is emitted per-page by the SEO transformPageData hook (seo/meta.ts):
  // `website` on normal pages, `article` on research-paper pages.
  ['link', { rel: 'alternate', type: 'text/html', title: 'XPower Banq App', href: appUrl }],
  ['link', { rel: 'alternate', type: 'application/pdf', title: 'XPower Banq Whitepaper', href: paperUrl }],
  ...(aiWorkerHost
    ? ([
        ['link', { rel: 'preconnect', href: aiWorkerHost, crossorigin: '' }],
        ['link', { rel: 'dns-prefetch', href: aiWorkerHost }],
      ] as HeadConfig[])
    : []),
]
