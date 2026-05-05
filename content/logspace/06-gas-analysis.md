---
title: "6. Gas Analysis"
prev:
  text: "5. Code Transformation"
  link: /logspace/05-code-transformation
next:
  text: "7. Precision Analysis"
  link: /logspace/07-precision-analysis
---

## Theoretical Cost Model

The transformation moves the `exp()` call from the global write path to per-user read paths.

**Accrual** (`_reindex`). The multiplicative path calls `Rate.accrue`, wrapping `ud().mul(exp(ud()))` — one `exp` ($\sim 1{,}100$ gas) and one `mulDiv18` ($\sim 100$ gas). Log-space replaces this with a single addition ($\sim 3$ gas). **Saving: $\sim 1{,}200$ gas per accrual.**

**Balance query** (`totalOf`). The multiplicative path performs one `mulDiv(principal, index, userIndex)` ($\sim 100$ gas). Log-space performs one `exp(delta)` ($\sim 1{,}100$ gas) and one `mulDiv` ($\sim 100$ gas). **Cost: $\sim 1{,}100$ gas per read.**

**Break-even.** Define the on-chain read/write ratio $R$ as the number of `totalOf` calls per accrual event. The transformation is gas-positive when

$$1{,}200 > R \times 1{,}100 \quad \Longrightarrow \quad R < 1.09.$$

In XPower Banq, `totalOf` is called on-chain primarily during state transitions (mint, burn, transfer) that co-locate with the accrual that triggered them, giving $R \approx 1$. The net gas effect is approximately neutral per-transaction, with the aggregate saving ($-114{,}447$ gas across 23 benchmarks) arising from cold-storage and multi-position paths where the single write-path saving amortises across multiple reads.

**Off-chain reads.** Liquidation bots, dashboards, and indexers calling `totalOf` via `eth_call` do not pay gas, but the `exp()` adds $\sim 1{,}100$ gas of compute to each call's execution time. For latency-sensitive applications, this overhead is measurable but small relative to RPC round-trip times and block confirmation delays.

**On-chain composability.** An external contract calling `totalOf` mid-transaction pays the full $+1{,}100$ gas with no accompanying write-path offset. This cost is analysed as a potential griefing vector in [Section 8](/logspace/08-adversarial-analysis#gas-griefing-on-read-path).

## Empirical Benchmarks

Measured via `gasleft()` instrumentation in `PoolGasBenchmark` and `OracleGasBenchmark` test contracts, with the Solidity optimizer disabled.

| Operation | RAY | Log | Δ |
|---|---:|---:|---:|
| supply_cold | 330,286 | 310,386 | −19,900 |
| supply_warm | 226,993 | 226,757 | −236 |
| borrow_cold | 506,228 | 485,856 | −20,372 |
| borrow_warm | 402,360 | 401,652 | −708 |
| settle_cold | 164,936 | 164,464 | −472 |
| settle_warm | 161,972 | 161,500 | −472 |
| redeem_cold | 321,118 | 320,174 | −944 |
| redeem_warm | 318,157 | 317,213 | −944 |
| healthOf | 202,130 | 201,658 | −472 |
| liquidate | 4,230,943 | 4,238,801 | +7,858 |
| liquidate_16 | 6,752,266 | 6,746,024 | −6,242 |
| **Total (23 ops)** |  |  | **−114,447** |

<small>Pool operations, optimizer OFF.</small>

| Operation | RAY | Log | Δ |
|---|---:|---:|---:|
| lockSupply_cold | 138,729 | 138,257 | −472 |
| lockSupply_perma | 109,568 | 109,096 | −472 |
| lockSupply_warm | 195,685 | 194,741 | −944 |
| lockBorrow_cold | 140,338 | 139,866 | −472 |
| lockBorrow_warm | 198,993 | 198,049 | −944 |
| lockStateAt_16 | 1,209,816 | 1,202,500 | −7,316 |
| free_16_expired | 990,777 | 984,924 | −5,853 |
| xfer_supply_16 | 1,898,677 | 1,870,703 | −27,974 |
| xfer_supply_1 | 676,260 | 654,894 | −21,366 |
| xfer_supply_perma | 620,564 | 599,198 | −21,366 |

<small>Lock and transfer operations.</small>

**Summary.** Net saving across 23 pool benchmarks: $-114{,}447$ gas ($-0.40\%$). All 8 oracle and 24 lock benchmarks show zero delta (unaffected code paths). The write-path saving dominates. The sole regression is single-position liquidation ($+7{,}858$ gas, $+0.2\%$), where the additional `exp()` in `totalOf` during position transfer is not fully offset by the accrual saving. Multi-slot liquidation ($-6{,}242$) benefits because the accrual saving is amortised across more position reads.
