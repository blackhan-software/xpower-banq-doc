import { resolve } from 'node:path'
import type { HeadConfig, SiteConfig } from 'vitepress'
import { slugify, titleCase } from '../../../scripts/shared/markdown.mjs'
import { extractFaq, extractGlossaryTerms, extractHowToSteps } from './extract'
import {
  ORG_ID_SUFFIX,
  ORG_NAME,
  SITE_NAME,
  WEBSITE_ID_SUFFIX,
} from './constants'

export interface LdContext {
  base: string
  url: string
  title: string
  description: string
  image: string
  modifiedIso: string
}

/** Wrap an object as a JSON-LD <script> head tag. */
function ld(obj: object): HeadConfig {
  return ['script', { type: 'application/ld+json' }, JSON.stringify(obj)]
}

/**
 * JSON-LD blocks for a page:
 * - home → Organization + WebSite/SearchAction `@graph`
 * - every other page → BreadcrumbList
 * - research/papers/* → TechArticle
 * - using-the-protocol/* → HowTo (when steps are found)
 * - reference/glossary → DefinedTermSet
 * - reference/faq → FAQPage
 */
export function jsonLdFor(
  pageData: { relativePath: string; lastUpdated?: number },
  siteConfig: SiteConfig,
  ctx: LdContext,
): HeadConfig[] {
  const out: HeadConfig[] = []
  const { base, url, title, description, image, modifiedIso } = ctx

  if (pageData.relativePath === 'index.md') {
    out.push(
      ld({
        '@context': 'https://schema.org',
        '@graph': [
          {
            '@type': 'Organization',
            '@id': `${base}/${ORG_ID_SUFFIX}`,
            name: ORG_NAME,
            url: base,
            logo: `${base}/logo/BANQ-000.svg`,
            sameAs: ['https://x.com/xpowerbanq', 'https://t.me/xpowerbanq'],
          },
          {
            '@type': 'WebSite',
            '@id': `${base}/${WEBSITE_ID_SUFFIX}`,
            url: base,
            name: SITE_NAME,
            publisher: { '@id': `${base}/${ORG_ID_SUFFIX}` },
            potentialAction: {
              '@type': 'SearchAction',
              target: `${base}/?q={search_term_string}`,
              'query-input': 'required name=search_term_string',
            },
          },
        ],
      }),
    )
  } else {
    out.push(breadcrumbLd(pageData.relativePath, base))
  }

  if (/^research\/papers\//.test(pageData.relativePath)) {
    out.push(
      ld({
        '@context': 'https://schema.org',
        '@type': 'TechArticle',
        headline: title,
        description,
        url,
        image,
        datePublished: modifiedIso,
        dateModified: modifiedIso,
        mainEntityOfPage: url,
        author: { '@type': 'Organization', name: ORG_NAME },
        publisher: { '@type': 'Organization', name: ORG_NAME },
      }),
    )
  }

  if (/^using-the-protocol\/(?!index\.md$).+\.md$/.test(pageData.relativePath)) {
    const steps = extractHowToSteps(resolve(siteConfig.srcDir, pageData.relativePath))
    if (steps.length) {
      out.push(
        ld({
          '@context': 'https://schema.org',
          '@type': 'HowTo',
          name: title,
          description,
          step: steps.map((text, i) => ({
            '@type': 'HowToStep',
            position: i + 1,
            text,
          })),
        }),
      )
    }
  }

  if (pageData.relativePath === 'reference/glossary.md') {
    const terms = extractGlossaryTerms(resolve(siteConfig.srcDir, pageData.relativePath))
    if (terms.length) {
      out.push(
        ld({
          '@context': 'https://schema.org',
          '@type': 'DefinedTermSet',
          name: 'XPower Banq Glossary',
          url,
          hasDefinedTerm: terms.map(([term, def]) => ({
            '@type': 'DefinedTerm',
            '@id': `${url}#${slugify(term)}`,
            name: term,
            description: def,
            inDefinedTermSet: url,
          })),
        }),
      )
    }
  }

  if (pageData.relativePath === 'reference/faq.md') {
    const qa = extractFaq(resolve(siteConfig.srcDir, pageData.relativePath))
    if (qa.length) {
      out.push(
        ld({
          '@context': 'https://schema.org',
          '@type': 'FAQPage',
          mainEntity: qa.map(([q, a]) => ({
            '@type': 'Question',
            name: q,
            acceptedAnswer: { '@type': 'Answer', text: a },
          })),
        }),
      )
    }
  }

  return out
}

function breadcrumbLd(relativePath: string, base: string): HeadConfig {
  const segments = relativePath
    .replace(/(^|\/)index\.md$/, '$1')
    .replace(/\.md$/, '')
    .split('/')
    .filter(Boolean)
  return ld({
    '@context': 'https://schema.org',
    '@type': 'BreadcrumbList',
    itemListElement: segments.map((s, i) => ({
      '@type': 'ListItem',
      position: i + 1,
      name: titleCase(s),
      item: `${base}/${segments.slice(0, i + 1).join('/')}`,
    })),
  })
}
