---
title: EMA Decay Factors
description: Pre-computed EMA decay factors for log-space TWAP oracle smoothing.
---

The table below lists pre-computed EMA decay factors relating half-life (in refresh periods) to the decay coefficient $\alpha$, used for log-space TWAP oracle smoothing.

| Half-life (periods) | Decay $\alpha$ | Use Case |
|---:|---:|---|
| 1 | 0.500000 | Fast response |
| 2 | 0.707107 | Short-term |
| 12 | 0.943874 | Medium-term |
| 24 | 0.971532 | Long-term |

The default oracle decay of 0.944 (12-period half-life) with hourly refreshes means approximately 40 hours of sustained manipulation is required to achieve 90% price deviation. See [Whitepaper §4.6](/whitepaper/04-mechanisms#oracle-twap) for the smoothing equations and [TWAP Simulations](/simulations/03-twap-oracle) for empirical convergence behaviour.
