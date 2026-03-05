import { defineConfig } from 'vitepress'
import container from 'markdown-it-container'

function createContainer(name: string) {
  return [container, name, {
    render(tokens: any[], idx: number) {
      if (tokens[idx].nesting === 1) {
        return `<div class="custom-block ${name}">\n`
      }
      return '</div>\n'
    }
  }] as const
}

export default defineConfig({
  title: 'XPower Banq',
  description: 'XPower Banq Protocol Documentation',
  srcDir: 'content',
  base: '/',
  appearance: 'dark',

  head: [
    ['link', { rel: 'icon', type: 'image/svg+xml', href: 'data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><text y="80" font-size="80">📖</text></svg>' }],
  ],

  markdown: {
    math: true,
    config: (md) => {
      md.use(...createContainer('definition'))
      md.use(...createContainer('theorem'))
      md.use(...createContainer('proof'))
    }
  },

  themeConfig: {
    logo: '/images/logo.svg',
    siteTitle: 'XPower Banq',

    nav: [
      { text: 'Whitepaper', link: '/whitepaper/01-introduction' },
      { text: 'Time Locks', link: '/timelocks/01-introduction' },
      { text: 'Log-Space Index', link: '/logspace/01-introduction' },
      { text: 'Theory', link: '/theory/01-mathematical-foundations' },
      { text: 'Simulations', link: '/simulations/01-cap-accumulation' },
      { text: 'Reference', link: '/reference/parameters' },
      { text: 'App', link: 'https://www.xpowerbanq.com', target: '_blank' }
    ],

    sidebar: {
      '/whitepaper/': [
        {
          text: 'Protocol Whitepaper',
          items: [
            { text: '1. Introduction', link: '/whitepaper/01-introduction' },
            { text: '2. Related Work', link: '/whitepaper/02-related-work' },
            { text: '3. Protocol Architecture', link: '/whitepaper/03-architecture' },
            { text: '4. Core Mechanisms', link: '/whitepaper/04-mechanisms' },
            { text: '5. Anti-Spam Protection', link: '/whitepaper/05-anti-spam' },
            { text: '6. Governance & Parameters', link: '/whitepaper/06-governance' },
            { text: '7. Security Analysis', link: '/whitepaper/07-security' },
            { text: '8. Evaluation', link: '/whitepaper/08-evaluation' },
            { text: '9. Limitations & Future Work', link: '/whitepaper/09-limitations' },
            { text: '10. Conclusion', link: '/whitepaper/10-conclusion' }
          ]
        }
      ],
      '/timelocks/': [
        {
          text: 'Ring-Buffer Time Locks',
          items: [
            { text: '1. Introduction', link: '/timelocks/01-introduction' },
            { text: '2. Related Work', link: '/timelocks/02-related-work' },
            { text: '3. Preliminaries', link: '/timelocks/03-preliminaries' },
            { text: '4. Ring-Lock Mechanism', link: '/timelocks/04-ring-lock' },
            { text: '5. Time-Lock Extension', link: '/timelocks/05-time-lock' },
            { text: '6. Invariants & Proofs', link: '/timelocks/06-proofs' },
            { text: '7. Gas Analysis', link: '/timelocks/07-gas-analysis' },
            { text: '8. Integration', link: '/timelocks/08-integration' },
            { text: '9. Conclusion', link: '/timelocks/09-conclusion' }
          ]
        }
      ],
      '/logspace/': [
        {
          text: 'Log-Space Compounding Index',
          items: [
            { text: '1. Introduction', link: '/logspace/01-introduction' },
            { text: '2. Related Work', link: '/logspace/02-related-work' },
            { text: '3. Overflow Analysis', link: '/logspace/03-overflow-analysis' },
            { text: '4. Log-Space Index', link: '/logspace/04-log-space-index' },
            { text: '5. Code Transformation', link: '/logspace/05-code-transformation' },
            { text: '6. Gas Analysis', link: '/logspace/06-gas-analysis' },
            { text: '7. Precision Analysis', link: '/logspace/07-precision-analysis' },
            { text: '8. Adversarial Analysis', link: '/logspace/08-adversarial-analysis' },
            { text: '9. Limitations & Future Work', link: '/logspace/09-limitations' },
            { text: '10. Conclusion', link: '/logspace/10-conclusion' }
          ]
        }
      ],
      '/theory/': [
        {
          text: 'Mathematical Theory & Proofs',
          items: [
            { text: '1. Mathematical Foundations', link: '/theory/01-mathematical-foundations' },
            { text: '2. Formal Proofs', link: '/theory/02-formal-proofs' },
            { text: '3. Nash Equilibrium Analysis', link: '/theory/03-nash-equilibrium' }
          ]
        }
      ],
      '/simulations/': [
        {
          text: 'Simulations & Risk Analysis',
          items: [
            { text: '1. Capacity Accumulation', link: '/simulations/01-cap-accumulation' },
            { text: '2. Cascade Simulation', link: '/simulations/02-cascade' },
            { text: '3. TWAP Oracle', link: '/simulations/03-twap-oracle' },
            { text: '4. Bad-Debt Risk', link: '/simulations/04-bad-debt-risk' },
            { text: '5. Conclusion', link: '/simulations/05-conclusion' }
          ]
        }
      ],
      '/reference/': [
        {
          text: 'Reference',
          items: [
            { text: 'Parameters', link: '/reference/parameters' },
            { text: 'Constants', link: '/reference/constants' },
            { text: 'EMA Decay Factors', link: '/reference/ema-decay' },
            { text: 'Bibliography', link: '/reference/bibliography' },
            { text: 'Glossary', link: '/reference/glossary' }
          ]
        }
      ]
    },

    socialLinks: [
      { icon: 'github', link: 'https://github.com/blackhan-software/xpower-banq-doc' }
    ],

    search: {
      provider: 'local'
    },

    footer: {
      message: 'XPower Banq Protocol Documentation',
      copyright: '© 2025 Moorhead LLC'
    }
  },

  vite: {
    build: {
      chunkSizeWarningLimit: 4096,
    },
    server: {
      allowedHosts: ['docs.xpowerbanq.com'],
      host: '0.0.0.0',
      port: 5174,
    }
  },
});
