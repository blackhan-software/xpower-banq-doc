# XPower Banq: User Acquisition Strategy

## Target Segments

Based on the protocol's design and positioning, three primary user segments emerge:

### Segment 1: Crash Survivors (Primary)
DeFi users who have been liquidated on other protocols during market downturns. They already understand lending, already have capital, and have a concrete pain point XPower Banq solves. They are searching for alternatives after every crash.

### Segment 2: DeFi-Curious Holdouts
Crypto holders who have avoided lending protocols because they perceive them as too risky or too complex to manage. The "go to sleep" promise directly addresses their objection.

### Segment 3: Passive Yield Seekers
Users currently earning yield through staking or LPs who want exposure to lending yields but won't babysit positions. The locked position + secondary market exit path gives them a familiar mental model (stake, earn, sell the token when done).

---

## Phase 1: Pre-Launch — Build Credibility Before Code

### Channel: Technical Content (Owned)
- **Whitepaper as lead magnet.** The 10-chapter whitepaper and appendices are unusually rigorous for DeFi. Publish them prominently and let them do the work of signaling seriousness. The math is the marketing.
- **Simulation results as content.** The Monte Carlo zero-bad-debt results, cascade attenuation charts, and TWAP oracle analysis are inherently shareable. Package them as standalone posts: "We simulated 1,000 crash scenarios. Here's what happened."
- **Crash post-mortems.** The `won't protect` social post demonstrates the template — every major DeFi liquidation event is an acquisition opportunity. Pre-write the framework, fill in the numbers after each crash. Publish within 24 hours while attention is high.

### Channel: Community (Earned)
- **DeFi research communities.** Target forums and groups where protocol mechanics are discussed seriously (DeFi researchers on Twitter/X, Ethereum Research, Avalanche ecosystem channels). The protocol's novel mechanisms — inverted ERC20 debt tokens, beta-distributed caps, PoW-gated liquidation — are genuinely interesting to this audience.
- **Avalanche ecosystem alignment.** Engage with Avalanche Foundation programs, ecosystem grants, and community calls. Being Avalanche-first on a chain with fewer lending competitors means ecosystem support is likely.

### Channel: Partnerships (Strategic)
- **Wallet integrations.** Partner with Avalanche-native wallets (Core, Rabby) for position visibility. The "human-speed" promise only works if users can actually see their positions changing slowly.
- **Oracle providers.** Establish relationships with Chainlink or other oracle providers for the off-chain price anchoring mentioned in the roadmap. These partnerships double as credibility signals.

---

## Phase 2: Launch — Convert During Crisis

### The Crash Acquisition Playbook
The protocol's entire value proposition is most compelling during market downturns. Structure acquisition around this reality:

1. **Pre-position content.** Have crash-response content templates ready (like the `won't protect` post). When BTC drops 20%+, publish within hours showing how XPower Banq positions would have survived with specific numbers.
2. **Real-time dashboards.** Build a public dashboard showing: current protocol health, simulated outcomes of the ongoing crash at default parameters, comparison with liquidation volumes on Aave/Compound/Morpho. This is both a product feature and an acquisition tool.
3. **"Migrate after the crash" campaign.** After each major liquidation event, run targeted content showing users how to move surviving capital into XPower Banq before the next one. The emotional window is 48–72 hours post-crash.

### Referral Mechanism (Built Into Protocol)
The locked position + wrapper + secondary market architecture creates a natural referral loop:
- Locked supply benefits all participants (cascade protection scales with total locked supply)
- Each new locker makes existing positions safer
- This is a genuine network effect, not a manufactured one — communicate it honestly

Maybe, consider a simple referral: referring users who lock positions could earn a small yield bonus funded by the protocol's 1% exit fee revenue. The incentive aligns with protocol health (you want referrals who lock, not who churn).

---

## Phase 3: Growth — Compound the Safety Narrative

### Content Flywheel
- **Monthly "stress test" reports.** Publish monthly analyses of how XPower Banq positions would have performed against actual market movements. Over time, this builds an undeniable track record — especially if markets remain volatile.
- **Governance transparency.** The lethargic governance model (0.5x–2x per month, asymptotic transitions) is itself content. Publish every parameter change weeks before it takes effect, with analysis. "Nothing exciting happened this month" is the brand.
- **Educational series on DeFi risk.** Position XPower Banq as the protocol that teaches users about risk rather than hiding it. Topics: what liquidation cascades are, how oracle manipulation works, why capital efficiency is a tradeoff. Each piece naturally leads to "and here's how XPower Banq handles this."

### Community-Led Growth
- **Liquidator onboarding.** The democratized liquidation model (no capital needed, PoW-gated, MEV-resistant) means liquidation is accessible to anyone with a browser. Build simple liquidation tooling and onboard community liquidators. Each liquidator is an evangelist for the protocol's fairness.
- **Distressed debt market participants.** As the OTC debt market develops, it attracts a new user class — distressed debt traders. These are sophisticated users who bring capital, liquidity, and credibility.

### Channels to Avoid
- **Paid acquisition / yield farming incentives.** Mercenary capital contradicts the protocol's thesis. Users attracted by temporary APY boosts leave when incentives end, and high-velocity capital undermines the rate-limiting mechanisms. The protocol is designed for users who stay.
- **Influencer marketing.** The "boring DeFi" positioning doesn't survive hype cycles. Technical credibility is the asset — protect it.

---

## Metrics That Matter

| Metric | Why It Matters |
|--------|---------------|
| Lock adoption rate | Core safety mechanism — target 40–70% per Nash equilibrium analysis |
| Median position duration | Measures whether you're attracting the right users (long-term holders, not yield farmers) |
| Positions surviving >1 crash | The ultimate proof point — track and publicize |
| Liquidator count | Measures democratization — more liquidators = healthier protocol |
| Secondary market discount to NAV | Measures wrapper token health — tighter spread = more confidence |
| Post-crash deposit inflows | Validates the core acquisition thesis |

---

## The Acquisition Thesis in One Sentence

XPower Banq doesn't need to outspend competitors on acquisition — it needs to **outlast them through crashes**, because every crash that liquidates users on other protocols is a free acquisition event for the protocol that kept its users whole.
