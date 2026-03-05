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
      { text: 'Appendices', link: '/appendices/part-i-math/mathematical-foundations' },
      { text: 'Reference', link: '/reference/parameters' },
      { text: 'App', link: 'https://www.xpowerbanq.com', target: '_blank' }
    ],

    sidebar: {
      '/whitepaper/': [
        {
          text: 'Whitepaper',
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
      '/appendices/': [
        {
          text: 'Part I: Math & Proofs',
          items: [
            { text: 'A. Mathematical Foundations', link: '/appendices/part-i-math/mathematical-foundations' },
            { text: 'B. Security Proofs', link: '/appendices/part-i-math/security-proofs' },
            { text: 'C. Lock Incentive Analysis', link: '/appendices/part-i-math/lock-incentive-analysis' }
          ]
        },
        {
          text: 'Part II: Simulations & Risk',
          items: [
            { text: 'D. Cap Simulations', link: '/appendices/part-ii-simulations/cap-simulations' },
            { text: 'E. Cascade Simulations', link: '/appendices/part-ii-simulations/cascade-simulations' },
            { text: 'F. TWAP Simulations', link: '/appendices/part-ii-simulations/twap-simulations' },
            { text: 'G. Bad-Debt Risk Analysis', link: '/appendices/part-ii-simulations/bad-debt-risk' }
          ]
        },
        {
          text: 'Part III: Reference',
          items: [
            { text: 'Glossary', link: '/appendices/part-iii-reference/glossary' }
          ]
        }
      ],
      '/reference/': [
        {
          text: 'Reference',
          items: [
            { text: 'Parameters', link: '/reference/parameters' },
            { text: 'Constants', link: '/reference/constants' },
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
