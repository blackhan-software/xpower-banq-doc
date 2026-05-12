import { readFileSync } from 'node:fs'
import { stripFrontmatter, stripMarkdownInline } from '../../../scripts/shared/markdown.mjs'

// Markdown-parsing helpers that scrape structured content out of source pages
// for JSON-LD (HowTo steps, glossary terms, FAQ pairs) and meta descriptions
// (first prose paragraph). Each reads a page off disk; a missing/empty file
// yields an empty result so callers fall back cleanly.

/** Read a page and strip its frontmatter; '' on any read error. */
function readBody(absPath: string): string {
  try {
    return stripFrontmatter(readFileSync(absPath, 'utf8'))
  } catch {
    return ''
  }
}

/**
 * First real prose paragraph of a page, flattened to plain text and capped at
 * 300 chars — used as a meta-description fallback. Skips headings, HTML,
 * container fences, tables, images, links, and short lines (< 40 chars).
 */
export function firstParagraph(absPath: string): string {
  for (const line of readBody(absPath).split(/\n/)) {
    const t = line.trim()
    if (!t) continue
    if (/^(#|<|::|\||!\[|\[)/.test(t)) continue
    if (t.length < 40) continue
    return stripMarkdownInline(t).slice(0, 300)
  }
  return ''
}

/**
 * Q→A pairs from an FAQ page: each `### Question` heading followed by its
 * paragraph(s) up to the next `###`/`##`.
 */
export function extractFaq(absPath: string): Array<[string, string]> {
  const out: Array<[string, string]> = []
  let q: string | null = null
  let buf: string[] = []
  const flush = () => {
    if (q !== null) {
      const a = buf.join(' ').trim()
      if (a) out.push([q, a])
    }
    q = null
    buf = []
  }
  for (const line of readBody(absPath).split(/\n/)) {
    const m = /^###\s+(.+?)\s*$/.exec(line)
    if (m) { flush(); q = m[1]; continue }
    if (/^##\s+/.test(line)) { flush(); continue }
    if (q === null) continue
    if (!line.trim()) { if (buf.length) buf.push(' '); continue }
    buf.push(stripMarkdownInline(line))
  }
  flush()
  return out
}

// "What you'll do" is the canonical procedural H2 on using-the-protocol pages.
// We also accept "Steps" as a fallback for any future page that doesn't follow
// the established phrasing.
const HOWTO_HEADING_RE = /^##\s+(?:What you(?:'|’)ll do|Steps?)\s*$/i

/**
 * Ordered step texts from the "What you'll do" / "Steps" section of a page:
 * the numbered or bulleted list items until the next heading.
 */
export function extractHowToSteps(absPath: string): string[] {
  const steps: string[] = []
  let inSection = false
  for (const line of readBody(absPath).split(/\n/)) {
    if (HOWTO_HEADING_RE.test(line)) { inSection = true; continue }
    if (!inSection) continue
    if (/^#{1,3}\s+/.test(line)) break
    const m = /^\s*(?:\d+\.|[-*])\s+(.+?)\s*$/.exec(line)
    if (m) steps.push(stripMarkdownInline(m[1]))
  }
  return steps
}

// Glossary entries are paragraphs that start with a bolded term followed by
// a period: `**Accrual.** The periodic update of...`. The term may contain
// inline math (`**$A(n)$ †.**`) or parentheses (`**Annualised Rate ($r$).**`).
// Letter headings (`## A`) just partition the file alphabetically; they are
// skipped here because we extract terms, not sections.
const GLOSSARY_TERM_RE = /^\*\*([^*]+?)\.\*\*\s+(.+)$/

/** Term→definition pairs from the glossary page. */
export function extractGlossaryTerms(absPath: string): Array<[string, string]> {
  const out: Array<[string, string]> = []
  // Split on blank lines so each paragraph is one chunk; the term-and-definition
  // pattern is always confined to a single paragraph in this glossary.
  for (const para of readBody(absPath).split(/\n\s*\n/)) {
    const flat = para.replace(/\n/g, ' ').trim()
    const m = GLOSSARY_TERM_RE.exec(flat)
    if (!m) continue
    const term = stripMarkdownInline(m[1]).replace(/\s+†$/, '')
    const def = stripMarkdownInline(m[2]).slice(0, 500)
    if (term && def) out.push([term, def])
  }
  return out
}
