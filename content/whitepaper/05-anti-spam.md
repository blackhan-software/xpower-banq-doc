---
title: "5. Anti-Spam Protection"
prev:
  text: "4. Core Mechanisms"
  link: /whitepaper/04-mechanisms
next:
  text: "6. Governance & Parameters"
  link: /whitepaper/06-governance
---

When governance enables public operations — such as liquidation via `liquidate()` or oracle refresh via `refresh()` — proof-of-work gates prevent spam. The PoW requires:

$$\text{zeros}\bigl(\text{keccak256}(\text{blockHash} \,\|\, \text{tx.origin} \,\|\, \text{msg.data})\bigr) \geq d$$

where each difficulty level requires $16\times$ more computational work. Combined with token-bucket rate limiting (capacity $C$, regeneration 1/second), this prevents mempool flooding and block stuffing. By default, operations are restricted to authorized keepers; PoW only applies in governance-enabled public mode.

## Fairness Limitations

PoW shifts the advantage from capital (gas wars) to computation. Professional miners achieve 10–20× higher hash rates than browser-based implementations, and on PoS chains (e.g., Avalanche) validators who know they will propose a block can pre-compute favorable nonces, creating a validator-advantage vector. In short, PoW provides anti-spam friction rather than fair access — it changes the extraction mechanism from capital to computation without eliminating it.
