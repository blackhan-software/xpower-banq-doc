import { resolve } from 'node:path'
import type { HeadConfig, SiteConfig } from 'vitepress'
import { firstParagraph } from './extract'
import {
  DEFAULT_DESCRIPTION,
  DEFAULT_TITLE,
  OG_IMAGE_HEIGHT,
  OG_IMAGE_TYPE,
  OG_IMAGE_WIDTH,
  ORG_NAME,
  SITE_NAME,
  TWITTER_HANDLE,
} from './constants'

/** Best page title: frontmatter → VitePress title → hero name → default. */
export function resolveTitle(pageData: {
  title?: string
  frontmatter: Record<string, unknown>
}): string {
  const fm = pageData.frontmatter.title
  if (typeof fm === 'string' && fm.trim()) return fm.trim()
  if (pageData.title && pageData.title.trim()) return pageData.title.trim()
  const hero = (pageData.frontmatter.hero as { name?: string } | undefined)?.name
  if (typeof hero === 'string' && hero.trim()) return hero.trim()
  return DEFAULT_TITLE
}

/**
 * Best page description: frontmatter → VitePress description (unless it's just
 * the site default) → hero tagline → first prose paragraph → default.
 */
export function resolveDescription(
  pageData: { relativePath: string; frontmatter: Record<string, unknown>; description?: string },
  siteConfig: SiteConfig,
): string {
  const fm = pageData.frontmatter.description
  if (typeof fm === 'string' && fm.trim()) return fm.trim()
  if (pageData.description && pageData.description.trim() && pageData.description !== siteConfig.site.description) {
    return pageData.description.trim()
  }
  const tagline = (pageData.frontmatter.hero as { tagline?: string } | undefined)?.tagline
  if (typeof tagline === 'string' && tagline.trim()) return tagline.trim()
  return firstParagraph(resolve(siteConfig.srcDir, pageData.relativePath)) || DEFAULT_DESCRIPTION
}

export interface MetaContext {
  url: string
  title: string
  description: string
  image: string
  modifiedIso: string
  isResearchPaper: boolean
  tags?: unknown
}

/**
 * Per-page <head> tags: canonical, Open Graph, Twitter card, og:type, and
 * (research papers only) the article:* set. og:type lives here — `website`
 * on normal pages, `article` on research papers — so the SEO hook is the sole
 * owner of it (head.ts no longer emits a global baseline).
 */
export function buildMetaTags(ctx: MetaContext): HeadConfig[] {
  const { url, title, description, image, modifiedIso, isResearchPaper } = ctx
  const head: HeadConfig[] = [
    ['link', { rel: 'canonical', href: url }],
    ['meta', { property: 'og:url', content: url }],
    ['meta', { property: 'og:type', content: isResearchPaper ? 'article' : 'website' }],
    ['meta', { property: 'og:image', content: image }],
    ['meta', { property: 'og:image:width', content: OG_IMAGE_WIDTH }],
    ['meta', { property: 'og:image:height', content: OG_IMAGE_HEIGHT }],
    ['meta', { property: 'og:image:type', content: OG_IMAGE_TYPE }],
    ['meta', { property: 'og:image:alt', content: `${title} — ${ORG_NAME}` }],
    ['meta', { property: 'og:site_name', content: SITE_NAME }],
    ['meta', { property: 'og:locale', content: 'en_US' }],
    ['meta', { name: 'twitter:card', content: 'summary_large_image' }],
    ['meta', { name: 'twitter:site', content: TWITTER_HANDLE }],
    ['meta', { name: 'twitter:title', content: title }],
    ['meta', { name: 'twitter:description', content: description }],
    ['meta', { name: 'twitter:image', content: image }],
    ['meta', { property: 'article:modified_time', content: modifiedIso }],
  ]

  if (isResearchPaper) {
    head.push(
      ['meta', { property: 'article:section', content: 'Research' }],
      ['meta', { property: 'article:author', content: ORG_NAME }],
      ['meta', { property: 'article:published_time', content: modifiedIso }],
    )
    if (Array.isArray(ctx.tags)) {
      for (const tag of ctx.tags) {
        if (typeof tag === 'string' && tag.trim()) {
          head.push(['meta', { property: 'article:tag', content: tag.trim() }])
        }
      }
    }
  }

  return head
}
