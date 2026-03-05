---
title: "9. Conclusion"
prev:
  text: "8. Integration"
  link: /timelocks/08-integration
next: false
---

# 9. Conclusion

We have presented a ring-buffer data structure for time-locked positions with five key properties:

1. A 16-slot quarterly ring buffer providing bounded storage per user (19 words).
2. Bitmap-guided $O(k)$ sweep with $k \leq 16$, ensuring gas-bounded expiry.
3. An $O(1)$ cached depth metric via the algebraic identity $D = \Sigma Q - Tt + pL$, enabling constant-time token-second queries from three stored values.
4. Proportional lock transfer in $O(k)$ for position fungibility during liquidation.
5. Integration with graduated lock bonus/malus for interest rate scaling in DeFi lending.

The mechanism is deployed in the XPower Banq protocol, where the collision-freedom guarantee ([Theorem 6.1](/timelocks/06-proofs#collision-freedom)) ensures ring-buffer correctness, and the depth identity ([Theorem 5.1](/timelocks/05-time-lock#_5-2-the-o-1-depth-identity)) enables gas-efficient interest rate adjustments. Formal proofs of all invariants are provided in [Section 6](/timelocks/06-proofs).

## Glossary

**Active Slot** — A ring-buffer slot whose epoch $e_i \geq e_{\text{now}}$. Included in `stateAt` queries and not yet eligible for sweep.

**Bitmap** — 16-bit mask tracking which slots contain active locks. Stored in the lower 16 bits of `coded`.

**Coded** — Single storage word packing `[uint240 total | uint16 bits]`. Decoded via shift and mask.

**Collision** — Two distinct active epochs mapping to the same slot index ($e_i \bmod 16 = e_j \bmod 16$ with $e_i \neq e_j$). Proven impossible by [Theorem 6.1](/timelocks/06-proofs#collision-freedom).

**Depth ($\Sigma$)** — Cached epoch-weighted sum $\sum v_i(e_i{+}1)$ enabling $O(1)$ token-second reconstruction.

**Depth Identity** — The algebraic identity $D = \Sigma Q - Tt + pL$ ([Theorem 5.1](/timelocks/05-time-lock#_5-2-the-o-1-depth-identity)) that converts the $O(k)$ token-seconds sum into an $O(1)$ cached computation.

**Epoch** — Absolute quarter index $e = \lfloor t/Q \rfloor$. Each epoch spans exactly $Q$ seconds.

**Lock Ratio ($\lambda$)** — Normalized commitment depth: $\texttt{depthOf}(u) / (\texttt{balanceOf}(u) \cdot L) \in [0,1]$.

**LOCK_TERM ($Q$)** — One quarter $\approx 91.3$ days—the epoch duration and ring-buffer granularity.

**LOCK_TIME ($L$)** — $15 \times Q \approx 45$ months—maximum lock duration and permanent lock depth cap.

**Permanent Lock** — Irrevocable lock with $\texttt{dt\_term} = 2^{256}{-}1$. Stored in `perma`, not in a ring slot. Contributes $p \cdot L$ to token-seconds at query time.

**Position Layer** — The `Position` contract that wraps the `Lock` library, enforcing the `free(tgt)` precondition.

**Ring Buffer** — Circular array of 16 slots indexed by $e \bmod 16$. Overwrites stale entries automatically when epochs advance beyond the window.

**Ring-Lock** — Base mechanism: ring buffer + bitmap + cached total. 18 words per user.

**Self-Healing** — `more()` correcting stale slot contributions during overwrite, maintaining `total` and `depth` consistency per-slot ([Theorem 6.7](/timelocks/06-proofs#self-healing-correctness)).

**Slot** — One of 16 ring buffer entries, indexed by $e \bmod 16$. Packs `uint32 epoch` and `uint224 value` in one storage word.

**Lock Bonus/Malus** — Interest rate scaling driven by lock depth. Suppliers earn a bonus $r_{\text{base}}(1 + \beta_s \lambda)$; borrowers receive a malus $r_{\text{base}}(1 - \beta_b \lambda)$ that reduces their effective cost.

**Stale Slot** — Slot with $e < e_{\text{now}}$—expired but not yet swept by `free()`. Causes `totalOf` inflation and `depthOf` deflation until cleared.

**Time-Lock** — Extension of Ring-Lock adding the `depth` mapping for token-seconds. 19 words per user.

**Token-Seconds** — $\sum v_i \times \text{remaining time}$—integral of locked amount over remaining time. The depth metric that drives graduated commitment.

**Window** — The 16-epoch span $[e_{\text{now}},\, e_{\text{now}}{+}15]$ of valid future slots. Any lock with `dt_term` exceeding the window is rejected, ensuring the collision-free invariant ([Theorem 6.1](/timelocks/06-proofs#collision-freedom)).
