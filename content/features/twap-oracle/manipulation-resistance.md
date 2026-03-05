# Manipulation resistance

The TWAP oracle is designed to resist three classes of price manipulation: flash-loan single-block, sandwich, and sustained.

## Flash-loan single-block

The classical lending-protocol attack: an attacker uses a flash loan to move a spot price (e.g., on a thin AMM pool), reads the manipulated price into the lending protocol, and exploits the discrepancy.

XPower Banq is **immune to this class of attack** because:

1. The oracle refreshes at most once per `LIMIT` (default 1 hour).
2. The new sample, when it does arrive, is weighted by `(1 − α) ≈ 5.6%`.
3. By the next refresh, the manipulated spot price has reverted (the flash loan has unwound).

The 60-scenario Foundry test suite in the whitepaper verifies two-tick immunity across diverse manipulation patterns.

## Sandwich attacks

In a sandwich attack, an attacker observes a pending oracle update and front-runs it with a price-moving trade, then back-runs it after the update completes. This requires the attacker to control the price *during* the oracle's read.

XPower Banq's oracle reads from enlistable sources at the moment of refresh. The v10c deployment uses **AMM TWAPs** — already smoothed by the AMM itself — so the attacker would need to control the TWAP for the duration of the read, not just the moment. That requires sustained manipulation, not a single-block trade.

Chainlink-style aggregators (median of multiple oracle nodes, on-chain since the previous heartbeat) are also supported and can be enlisted; against those, a sandwich attack would require compromising multiple nodes.

## Sustained manipulation

A sufficiently capitalised and patient attacker can sustain a manipulated price across multiple oracle refreshes. The TWAP eventually reflects the manipulated price.

XPower Banq's defence here is:

1. **The 12-hour half-life** means meaningful TWAP drift requires hours of sustained manipulation.
2. **The 90%-deviation threshold** requires ~40 hours of sustained manipulation at default settings.
3. **Cost.** Sustaining a manipulated price across 40 hours, against arbitrageurs, requires very deep capital. The total cost grows as the square of the deviation × time.

For tokens with thin natural liquidity, this defence is weaker. The protocol's onboarding guidance recommends using only assets with deep, multi-source price feeds.

## What the oracle doesn't protect against

- **Genuine price moves.** If the actual market price drops 50%, the oracle eventually reports that — and positions get liquidated. This is correct behaviour, not an attack.
- **Source corruption.** If an enlisted upstream feed itself reports a wrong value (AMM-pool dislocation, or — for any future enlisted aggregator — infrastructure failure), the protocol smooths and uses that value. The oracle is only as good as its sources.
- **Empty or thin markets.** If trading volume is too low for the source feed to produce reliable quotes, the oracle inherits that unreliability.

## Where to go next

- [Spread and slippage](/features/twap-oracle/spread-and-slippage) — the bidirectional spread mechanism
- [Oracle staleness](/risks/oracle-staleness) — what slow oracles cost you
