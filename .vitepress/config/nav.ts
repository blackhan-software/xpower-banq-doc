import type { DefaultTheme } from 'vitepress'
import { appUrl } from './env'

export const nav: DefaultTheme.NavItem[] = [
  { text: 'Introduction', link: '/introduction/what-is-xpower-banq' },
  { text: 'Concepts', link: '/concepts/lending-basics' },
  { text: 'Features', link: '/features/locked-positions/overview' },
  { text: 'Use it', link: '/using-the-protocol/supplying-assets' },
  { text: 'Build', link: '/for-developers/architecture-overview' },
  { text: 'Risks', link: '/risks/overview' },
  { text: 'Security', link: '/security/threat-model' },
  { text: 'Reference', link: '/reference/comparison-table' },
  { text: 'App', link: appUrl, target: '_blank' },
]
