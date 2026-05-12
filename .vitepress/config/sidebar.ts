import type { DefaultTheme } from 'vitepress'

export const sidebar: DefaultTheme.Sidebar = {
  '/introduction/': [
    {
      text: 'Introduction',
      items: [
        { text: 'What is XPower Banq', link: '/introduction/what-is-xpower-banq' },
        { text: 'Why XPower Banq', link: '/introduction/why-xpower-banq' },
        { text: 'How it works', link: '/introduction/how-it-works' },
        { text: 'Quickstart', link: '/introduction/quickstart' },
      ],
    },
  ],

  '/concepts/': [
    {
      text: 'Concepts',
      items: [
        { text: 'Lending basics', link: '/concepts/lending-basics' },
        { text: 'Health factor', link: '/concepts/health-factor' },
        { text: 'Interest rates', link: '/concepts/interest-rates' },
        { text: 'Liquidation', link: '/concepts/liquidation' },
        { text: 'Positions as tokens', link: '/concepts/positions-as-tokens' },
      ],
    },
  ],

  '/features/': [
    {
      text: 'Locked Positions',
      collapsed: false,
      items: [
        { text: 'Overview', link: '/features/locked-positions/overview' },
        { text: 'Timed vs permanent', link: '/features/locked-positions/timed-vs-permanent' },
        { text: 'Bonus and malus', link: '/features/locked-positions/bonus-and-malus' },
        { text: 'Transfers and exits', link: '/features/locked-positions/transfers-and-exits' },
        { text: 'Cascade protection', link: '/features/locked-positions/cascade-protection' },
      ],
    },
    {
      text: 'Debt-Assumption Liquidation',
      collapsed: false,
      items: [
        { text: 'Overview', link: '/features/debt-assumption-liquidation/overview' },
        { text: 'How liquidations work', link: '/features/debt-assumption-liquidation/how-liquidations-work' },
        { text: 'For liquidators', link: '/features/debt-assumption-liquidation/for-liquidators' },
      ],
    },
    {
      text: 'Lethargic Governance',
      collapsed: false,
      items: [
        { text: 'Overview', link: '/features/lethargic-governance/overview' },
        { text: 'Parameter bounds', link: '/features/lethargic-governance/parameter-bounds' },
        { text: 'Transition curves', link: '/features/lethargic-governance/transition-curves' },
        { text: 'Role hierarchy', link: '/features/lethargic-governance/role-hierarchy' },
      ],
    },
    {
      text: 'Position Caps',
      collapsed: false,
      items: [
        { text: 'Overview', link: '/features/position-caps/overview' },
        { text: 'How caps grow', link: '/features/position-caps/how-caps-grow' },
        { text: 'New user allocation', link: '/features/position-caps/new-user-allocation' },
        { text: 'Caps wrapper and circuit breaker', link: '/features/position-caps/caps-wrapper-and-circuit-breaker' },
      ],
    },
    {
      text: 'Protocol-Owned Liquidity',
      collapsed: false,
      items: [
        { text: 'Overview', link: '/features/protocol-owned-liquidity/overview' },
        { text: 'Fetching and roles', link: '/features/protocol-owned-liquidity/fetching-and-roles' },
      ],
    },
    {
      text: 'TWAP Oracle',
      collapsed: false,
      items: [
        { text: 'Overview', link: '/features/twap-oracle/overview' },
        { text: 'Manipulation resistance', link: '/features/twap-oracle/manipulation-resistance' },
        { text: 'Spread and slippage', link: '/features/twap-oracle/spread-and-slippage' },
      ],
    },
  ],

  '/using-the-protocol/': [
    {
      text: 'Using the Protocol',
      items: [
        { text: 'Supplying assets', link: '/using-the-protocol/supplying-assets' },
        { text: 'Borrowing assets', link: '/using-the-protocol/borrowing-assets' },
        { text: 'Repaying debt', link: '/using-the-protocol/repaying-debt' },
        { text: 'Withdrawing assets', link: '/using-the-protocol/withdrawing-assets' },
        { text: 'Locking positions', link: '/using-the-protocol/locking-positions' },
        { text: 'Transferring positions', link: '/using-the-protocol/transferring-positions' },
        { text: 'Monitoring health', link: '/using-the-protocol/monitoring-health' },
        { text: 'Wrapped positions', link: '/using-the-protocol/wrapped-positions' },
      ],
    },
  ],

  '/for-developers/': [
    {
      text: 'For Developers',
      items: [
        { text: 'Architecture overview', link: '/for-developers/architecture-overview' },
        { text: 'Contract addresses', link: '/for-developers/contract-addresses' },
        { text: 'Integration guide', link: '/for-developers/integration-guide' },
        { text: 'ERC20 semantics', link: '/for-developers/erc20-semantics' },
        { text: 'ERC4626 vaults', link: '/for-developers/erc4626-vaults' },
        { text: 'Events and indexing', link: '/for-developers/events-and-indexing' },
        { text: 'Gas costs', link: '/for-developers/gas-costs' },
      ],
    },
  ],

  '/for-keepers/': [
    {
      text: 'For Keepers',
      items: [
        { text: 'Overview', link: '/for-keepers/overview' },
        { text: 'Running a liquidator', link: '/for-keepers/running-a-liquidator' },
        { text: 'PoW-gated public mode', link: '/for-keepers/pow-gated-public-mode' },
        { text: 'CLI and tools', link: '/for-keepers/cli-and-tools' },
        { text: 'Monitoring and tooling', link: '/for-keepers/monitoring-and-tooling' },
      ],
    },
  ],

  '/governance/': [
    {
      text: 'Governance',
      items: [
        { text: 'Overview', link: '/governance/overview' },
        { text: 'Parameter catalog', link: '/governance/parameter-catalog' },
        { text: 'Proposing changes', link: '/governance/proposing-changes' },
        { text: 'Role management', link: '/governance/role-management' },
        { text: 'Emergency procedures', link: '/governance/emergency-procedures' },
      ],
    },
  ],

  '/parameters/': [
    {
      text: 'Parameters',
      items: [
        { text: 'Pool', link: '/parameters/pool-parameters' },
        { text: 'Position', link: '/parameters/position-parameters' },
        { text: 'Oracle', link: '/parameters/oracle-parameters' },
        { text: 'Vault', link: '/parameters/vault-parameters' },
        { text: 'Change-rate constraints', link: '/parameters/change-rate-constraints' },
      ],
    },
  ],

  '/risks/': [
    {
      text: 'Risks',
      items: [
        { text: 'Overview', link: '/risks/overview' },
        { text: 'Liquidation risk', link: '/risks/liquidation-risk' },
        { text: 'Oracle staleness', link: '/risks/oracle-staleness' },
        { text: 'Bad debt scenarios', link: '/risks/bad-debt-scenarios' },
        { text: 'Governance risk', link: '/risks/governance-risk' },
        { text: 'Smart contract risk', link: '/risks/smart-contract-risk' },
        { text: 'Secondary market risk', link: '/risks/secondary-market-risk' },
      ],
    },
  ],

  '/security/': [
    {
      text: 'Security',
      items: [
        { text: 'Threat model', link: '/security/threat-model' },
        { text: 'Defensive mechanisms', link: '/security/defensive-mechanisms' },
        { text: 'Audits and reviews', link: '/security/audits-and-reviews' },
      ],
    },
  ],

  '/research/': [
    {
      text: 'Research',
      items: [
        { text: 'Whitepaper', link: '/research/whitepaper' },
        {
          text: 'Companion Papers',
          collapsed: false,
          items: [
            { text: 'Protocol', link: '/research/papers/protocol' },
            { text: 'Ring-buffer locks', link: '/research/papers/ring-buffer-locks' },
            { text: 'Log-space index', link: '/research/papers/log-space-index' },
            { text: 'Theory & proofs', link: '/research/papers/theory-and-proofs' },
            { text: 'Simulations', link: '/research/papers/simulations' },
          ],
        },
      ],
    },
  ],

  '/reference/': [
    {
      text: 'Reference',
      items: [
        { text: 'Comparison table', link: '/reference/comparison-table' },
        { text: 'Bibliography', link: '/reference/bibliography' },
        { text: 'Glossary', link: '/reference/glossary' },
        { text: 'FAQ', link: '/reference/faq' },
      ],
    },
  ],
}
