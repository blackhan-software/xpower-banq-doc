---
title: "1. Introduction"
prev: false
next:
  text: "2. Related Work"
  link: /timelocks/02-related-work
---

Time-locked positions are a recurring primitive in DeFi. Vote-escrow protocols (Curve veCRV [\[curve\]](/reference/bibliography#curve)), liquid staking wrappers (Convex vlCVX [\[convex\]](/reference/bibliography#convex)), and lending protocols all require users to commit tokens for a bounded duration. Beyond binary locked/unlocked status, protocols benefit from a measure of *commitment depth* — the integral of locked amount over remaining time, which we call *token-seconds*.

Computing token-seconds on-chain presents a tension: the naive $O(n)$ summation over all lock entries is unbounded in gas, while maintaining a single aggregated counter sacrifices the ability to support multiple concurrent locks with different expiry dates.

## Contributions

We resolve this tension with two mechanisms layered on a shared ring-buffer data structure:

1. **Ring-Lock.** A 16-slot quarterly ring buffer with a bitmap-guided $O(k)$ sweep for expired slots, providing bounded-gas lock creation and expiry ([Section 4](/timelocks/04-ring-lock)).
2. **Time-Lock.** An extension that adds a single stored value — the epoch-weighted sum $\Sigma = \sum v_i(e_i{+}1)$ — enabling $O(1)$ reconstruction of exact token-seconds via an algebraic identity ([Section 5](/timelocks/05-time-lock)).

The protocol context is the [XPower Banq lending protocol](/whitepaper/01-introduction), where lock depth drives graduated interest rate adjustments ([Section 8](/timelocks/08-integration)). The locked-positions mechanism is described in [Whitepaper §4.1](/whitepaper/04-mechanisms#locked-positions-and-cascade-attenuation) and the interest rate application in [§4.7](/whitepaper/04-mechanisms#interest-rates). Formal proofs of the ring-buffer invariants and depth identity appear in [Section 6](/timelocks/06-proofs).
