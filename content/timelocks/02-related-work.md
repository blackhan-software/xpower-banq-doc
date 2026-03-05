---
title: "2. Related Work"
prev:
  text: "1. Introduction"
  link: /timelocks/01-introduction
next:
  text: "3. Preliminaries"
  link: /timelocks/03-preliminaries
---

**Curve veCRV** [\[curve\]](/reference/bibliography#curve)**.** Fixed 4-year linear decay from a single lock slot. $O(1)$ query via closed-form decay, but no support for multiple concurrent locks or variable duration. The bias/slope model requires periodic global checkpoints.

**Convex/Aura vlCVX** [\[convex\]](/reference/bibliography#convex)**.** Epoch-based unlock queues with linear scan for expired epochs. Supports multiple lock durations, but sweep cost is $O(n)$ in the number of distinct epochs — unbounded without a cap on lock granularity.

**Uniswap v3 NFT Locks.** Per-position NFTs carry individual timestamps. No aggregation across positions; each lock is an independent storage entity.

**OpenZeppelin TimelockController** [\[oz-timelock\]](/reference/bibliography#oz-timelock)**.** Designed for governance action delays, not position locks. Single-use: one pending action per hash, no ring or aggregation structure.

**Ring Buffers** [\[ring-buffer\]](/reference/bibliography#ring-buffer)**.** Circular buffers are classical in systems programming: OS scheduling, network packet buffers, Uniswap V3 oracle observation arrays. Our application to on-chain time locks with bitmap-guided sweep and cached depth appears to be novel.

## Comparison of Time-Lock Mechanisms

|  | Duration Range | Storage per User | Lock Cost | Query Cost | Depth Metric |
|---|---|---|---|---|---|
| veCRV | Fixed 4y | 1 word | $O(1)$ | $O(1)$ | Linear |
| vlCVX | Epochs | $O(n)$ | $O(1)$ | $O(n)$ | None |
| NFT | Any | $O(n)$ | $O(1)$ | $O(n)$ | None |
| **Ours** | $[0, 16Q)$ | 10 words | $O(1)$ | $O(1)$ | Token·s |
