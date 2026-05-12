import type { UserConfig } from 'vitepress'
import { appUrl, wwwUrl } from '../env'
import { OG_IMAGE_PATH } from './constants'
import { buildMetaTags, resolveDescription, resolveTitle } from './meta'
import { jsonLdFor } from './json-ld'

export const sitemap: UserConfig['sitemap'] = {
  hostname: wwwUrl,
  transformItems: (items) =>
    items.map((i) => ({
      ...i,
      changefreq: 'weekly',
      priority: i.url === '' ? 1.0 : 0.7,
    })),
}

export const transformPageData: UserConfig['transformPageData'] = (
  pageData,
  { siteConfig },
) => {
  // Home hero "Launch App" pill is env-driven from BANQ_APP_URL (single source,
  // same var as the top-nav "App" link). VitePress frontmatter can't interpolate
  // env vars, so rewrite the link here at build time. The pill is the only hero
  // action with `target: _blank`, so match on that rather than a hardcoded URL.
  if (pageData.relativePath === 'index.md') {
    const hero = pageData.frontmatter.hero as
      | { actions?: Array<{ target?: string; link?: string }> }
      | undefined
    for (const action of hero?.actions ?? []) {
      if (action?.target === '_blank') action.link = appUrl
    }
  }

  const base = wwwUrl
  const slug = pageData.relativePath
    .replace(/(^|\/)index\.md$/, '$1')
    .replace(/\.md$/, '')
  const url = slug ? `${base}/${slug}` : `${base}/`
  const title = resolveTitle(pageData)
  const description = resolveDescription(pageData, siteConfig)
  // lastUpdated comes from the git log; new/uncommitted files yield NaN.
  // Fall back to now rather than letting Date.toISOString throw.
  const ts = Number(pageData.lastUpdated)
  const modifiedIso = new Date(Number.isFinite(ts) && ts > 0 ? ts : Date.now()).toISOString()
  const image = `${base}${OG_IMAGE_PATH}`
  const isResearchPaper = /^research\/papers\//.test(pageData.relativePath)

  // VitePress emits `<meta name="description">` and `<meta property="og:title|og:description">`
  // from pageData.title/description and dedupes by tag key, so set these directly rather
  // than pushing duplicates that lose to the auto-emitted ones.
  pageData.title = title
  pageData.description = description

  pageData.frontmatter.head ??= []
  pageData.frontmatter.head.push(
    ...buildMetaTags({
      url,
      title,
      description,
      image,
      modifiedIso,
      isResearchPaper,
      tags: pageData.frontmatter.tags,
    }),
    ...jsonLdFor(pageData, siteConfig, { base, url, title, description, image, modifiedIso }),
  )
}
