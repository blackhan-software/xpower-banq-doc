---
title: "8. Adversarial Analysis"
prev:
  text: "7. Precision Analysis"
  link: /logspace/07-precision-analysis
next:
  text: "9. Limitations & Future Work"
  link: /logspace/09-limitations
---

The [precision analysis](/logspace/07-precision-analysis) covers the honest case. This section examines whether the log-space transformation introduces, removes, or preserves attack surface.

## Rounding Manipulation

In the multiplicative form, each accrual truncates twice ([Theorem 7.1](/logspace/07-precision-analysis#theoretical-bound)), producing a systematic negative bias. An attacker forcing many small accruals — e.g., by triggering reindexing with minimal time deltas — amplifies this bias across all users' balances.

The log-space form eliminates this vector: accrual is exact integer addition, so no sequence of reindex calls can introduce truncation error into the stored index.

**Verdict.** Attack surface *removed*.

## Dust Extraction via Read-Time Rounding

The read-time `exp()` and subsequent `mulDiv` each round independently, introducing at most 2 ULP of error per `totalOf` query ([Theorem 7.1](/logspace/07-precision-analysis#theoretical-bound)). An attacker attempting to extract value via repeated deposit/withdrawal cycles can gain at most 2 wei per cycle, while a single `mint`/`burn` pair costs $>100{,}000$ gas ($\sim 0.003$ USD at 30 gwei) — unprofitable by a factor of $>10^{12}$.

**Verdict.** Theoretically present, economically *infeasible*.

## Gas Griefing on Read Path

The log-space `totalOf` adds $\sim 1{,}100$ gas (one `exp()` call) compared to the multiplicative form. An attacker who can force another user's `totalOf` to execute on-chain — e.g., during liquidation — imposes this additional cost on the caller.

**Bound.** The $+1{,}100$ gas overhead is $<0.03\%$ of a typical liquidation transaction ($\sim 4.2$M gas, see [Gas Analysis](/logspace/06-gas-analysis#empirical-benchmarks)). Liquidation bots operate on profit margins orders of magnitude larger than this cost. The overhead is not controllable by the attacker (it is a fixed function of the `exp()` implementation) and cannot be amplified.

**Verdict.** Measurable but *not exploitable*.

## Timestamp Sensitivity

The yield computation $r_{\text{wad}} = r_{\text{annual}} \times \Delta t / \text{YEAR}$ depends on `block.timestamp`. This is identical in both representations — the log-space form does not change the yield calculation, only how the result is stored. Block proposers can manipulate timestamps by $\sim 12$ seconds (one slot), affecting $\Delta t$ by $< 4 \times 10^{-7}$ of the annual rate per accrual. This bound is *unchanged* from the multiplicative form.

## Summary

The log-space transformation has a strictly smaller attack surface. The compounded truncation manipulation vector is eliminated, and no new economically viable attack vector is introduced.
