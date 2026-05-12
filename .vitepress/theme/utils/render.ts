import MarkdownIt from 'markdown-it'
import { inlineMath } from './inline-math'
import { normalizeCitations } from './citations'

const md = new MarkdownIt({ html: false, linkify: true, breaks: false })

export function render(text: string): string {
  return md.render(normalizeCitations(inlineMath(text || '')))
}
