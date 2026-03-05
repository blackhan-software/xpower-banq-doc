# Risks

This is a first-class section, not a footnote. XPower Banq is a young protocol with measurable strengths and measurable limitations. We want users to understand both before committing capital.

## What we mean by "risk" here

We mean: things that could cause you to lose money in ways that aren't obvious from the headline mechanics. Not regulatory risk, not "DeFi is risky," but specific protocol behaviours that have negative tail outcomes.

## The major categories

- **[Liquidation risk](/risks/liquidation-risk).** Your borrow position can be liquidated when H drops below 100%. Cascade attenuation reduces the systemic dimension but doesn't eliminate the individual outcome.
- **[Oracle staleness](/risks/oracle-staleness).** TWAP smoothing means the protocol's view of price lags the true market. This is a feature for security but a liability during fast moves.
- **[Bad debt scenarios](/risks/bad-debt-scenarios).** When a position can't be fully liquidated — e.g., extreme crash before the buffer is consumed — the protocol absorbs bad debt. The buffer is sized to make this rare, but it's not zero.
- **[Governance risk](/risks/governance-risk).** Parameter changes within the lethargic bound can still hurt you over time. Compromised `_ADMIN_ROLE` keys can do real damage, slowly — though the matching `_GUARD_ROLE` can cancel pending changes during their delay window.
- **[Smart contract risk](/risks/smart-contract-risk).** The contracts have been internally tested but not yet formally verified. Bugs are possible.
- **[Secondary market risk](/risks/secondary-market-risk).** Locked positions trade at a discount on secondary markets, which can be wide and volatile.

## What you can do about it

For most users, the practical risk-management actions are:

- **Don't go all-in.** Allocate to Banq the share of your portfolio you can afford to lose to a worst-case bad-debt scenario.
- **Maintain healthy H.** H ≥ 150% covers most volatility; H ≥ 200% covers most bear markets.
- **Don't permanently lock more than you'd accept losing access to.**
- **Watch the audits page.** Formal verification and additional audits change the smart-contract risk profile.
- **Diversify lock terms.** Don't put all your capital into a single timed lock that all expires at once.

## Honest disclosure

The protocol's whitepaper is candid about limitations: no formal verification yet, simulations use only 1,000 agents, the Sybil mechanism is rate-limiting (not prevention), full lock adoption zeroes the protocol margin. We've reflected those candidly in the per-page risk descriptions below.

## Where to go next

- [Liquidation risk](/risks/liquidation-risk)
- [Oracle staleness](/risks/oracle-staleness)
- [Bad debt scenarios](/risks/bad-debt-scenarios)
- [Smart contract risk](/risks/smart-contract-risk)
