---
title: "6. Invariants & Proofs"
prev:
  text: "5. Time-Lock Extension"
  link: /timelocks/05-time-lock
next:
  text: "7. Gas Analysis"
  link: /timelocks/07-gas-analysis
---

## Collision Freedom

::: theorem
**Theorem 6.1** (Collision Freedom). *For any user $u$ and any two active (non-expired) locks in slots $i$ and $j$ with epochs $e_i$ and $e_j$: if $e_i \bmod 16 = e_j \bmod 16$, then $e_i = e_j$.*
:::

::: proof
**Proof.** By the `more()` require guard, $\texttt{dt\_term} \leq L - Q = 15Q$. A lock created at time $t$ targets epoch $e = \lfloor(t{+}\texttt{dt\_term})/Q\rfloor$. The current epoch is $e_{\text{now}} = \lfloor t/Q \rfloor$. Thus

$$e_{\text{now}} \leq e \leq \left\lfloor \frac{t + 15Q}{Q} \right\rfloor = e_{\text{now}} + 15.$$

All active epochs lie in a window of at most 16 consecutive integers $[e_{\text{now}}, e_{\text{now}}{+}15]$. Two distinct integers in this window with the same residue mod 16 must differ by at least 16. However, the maximum difference between any two elements of $[e_{\text{now}}, e_{\text{now}}{+}15]$ is $15 < 16$ — a contradiction. $\blacksquare$
:::

::: theorem
**Corollary 6.2** (Cross-User Collision). *When `push(src, tgt)` copies a lock from source slot $i$ to target slot $i$, and the target already has an active lock at index $i$, then the target epoch must equal the source epoch (since both are active and share the same mod-16 index). The target-side accumulate-path of `_pushSlot` is therefore always taken for active target slots; empty or swept target slots take the overwrite path.*
:::

::: proof
**Proof.** Follows directly from Theorem 6.1 applied to the target user's active set augmented with the incoming epoch. $\blacksquare$
:::

## Depth Identity Correctness

::: theorem
**Theorem 6.3** (Depth Identity). *After `free(u)`, $\texttt{depthOf}(u) = \texttt{stateAt}(u, t_{\text{now}}).\texttt{depth}$.*
:::

::: proof
**Proof.** By Theorem 5.1, $D = \Sigma Q - Tt + pL$. After `free()`, the expired set $E = \emptyset$, so the stored $\Sigma$ and $T$ exactly represent the active set $A$. The identity reconstructs $D$ identically to the sum in the token-seconds definition. $\blacksquare$
:::

## Cached vs. Exact Invariants

::: theorem
**Theorem 6.4** (Total Inflation). *$\texttt{totalOf}(u) \geq \texttt{stateAt}(u, t_{\text{now}}).\texttt{total}$ at all times.*
:::

::: proof
**Proof.** `totalOf` returns the `total` field from `cache`, which includes contributions from all slots with set bitmap bits — both active and expired. `stateAt` sums only slots with $e_i \geq e_{\text{now}}$. Since every active slot is counted by both, and expired slots are counted only by `totalOf`:

$$\texttt{totalOf}(u) = \texttt{stateAt}(u, t_{\text{now}}).\texttt{total} + \sum_{i \in E} v_i \geq \texttt{stateAt}(u, t_{\text{now}}).\texttt{total}. \qquad \blacksquare$$
:::

::: theorem
**Theorem 6.5** (Depth Deflation). *$\texttt{depthOf}(u) \leq \texttt{stateAt}(u, t_{\text{now}}).\texttt{depth}$ at all times.*
:::

::: proof
**Proof.** Let $E$ be the set of expired slots still in the bitmap, $A$ the active set. Decompose

$$\texttt{depthOf}(u) = \Sigma Q - Tt + pL = \underbrace{[\Sigma_A Q - T_A t + pL]}_{\texttt{stateAt.depth}} + \underbrace{[\Sigma_E Q - T_E t]}_{\leq\, 0}.$$

For each expired slot $i \in E$: $e_i < e_{\text{now}} = \lfloor t/Q \rfloor$, so $(e_i{+}1)Q \leq t$, giving $v_i((e_i{+}1)Q - t) \leq 0$. $\blacksquare$
:::

::: theorem
**Theorem 6.6** (Equality After Free). *After `free(u)`: $\texttt{totalOf}(u) = \texttt{stateAt}(u, t_{\text{now}}).\texttt{total}$ and $\texttt{depthOf}(u) = \texttt{stateAt}(u, t_{\text{now}}).\texttt{depth}$.*
:::

::: proof
**Proof.** `free()` deletes every slot with $e_i < e_{\text{now}}$, making $E = \emptyset$. The expired-set contributions in Theorems 6.4 and 6.5 vanish. $\blacksquare$
:::

## Self-Healing Correctness

::: theorem
**Theorem 6.7** (Self-Healing). *If `more(u, amount, dt_term)` overwrites a stale slot at index $i$, then after the operation, the cached `total` and `depth` are consistent with the new slot value.*
:::

::: proof
**Proof.** When `more()` finds $e_{\text{slot}} \neq e_{\text{target}}$ and $v_{\text{slot}} > 0$:

1. $\Sigma \mathrel{-}= v_{\text{old}}(e_{\text{old}}{+}1)$; $T \mathrel{-}= v_{\text{old}}$.
2. Overwrite slot: $e \leftarrow e_{\text{target}}$, $v \leftarrow \texttt{amount}$.
3. $\Sigma \mathrel{+}= \texttt{amount} \cdot (e_{\text{target}}{+}1)$; $T \mathrel{+}= \texttt{amount}$.

The net effect is as if the stale slot had been freed first, then the new lock created. $\blacksquare$
:::

> **Remark.** Self-healing is per-slot. Other stale slots remain uncorrected until `free()` or their own overwrite by a future `more()`.

## Depth Conservation Under Push

::: theorem
**Theorem 6.8** (Push Depth Conservation). *Let $D_{\text{before}} = \texttt{depthOf}(\texttt{src}) + \texttt{depthOf}(\texttt{tgt})$ before the call. After `push(src, tgt, m, d)` with prior `free(src)` and `free(tgt)`:*

$$\texttt{depthOf}(\texttt{src}) + \texttt{depthOf}(\texttt{tgt}) = D_{\text{before}}.$$

*That is, the combined depth is exactly conserved.*
:::

::: proof
**Proof.** For each source slot, $\Delta v = \lfloor v \cdot m/d \rfloor$ is subtracted from `depth[src]` and added to `depth[tgt]` as $\Delta v \cdot (e{+}1)$. The same $\Delta v$ is subtracted from $T_{\text{src}}$ and added to $T_{\text{tgt}}$. Thus the aggregate $\Sigma = \Sigma_{\text{src}} + \Sigma_{\text{tgt}}$ and $T = T_{\text{src}} + T_{\text{tgt}}$ are each invariant across the transfer. Since both users were freed,

$$D_{\text{src}} + D_{\text{tgt}} = (\Sigma_{\text{src}} + \Sigma_{\text{tgt}})Q - (T_{\text{src}} + T_{\text{tgt}})t + (p_{\text{src}} + p_{\text{tgt}})L,$$

and all three aggregate terms are unchanged. $\blacksquare$
:::

> **Remark.** While the combined depth is exactly conserved, the *split* between source and target is subject to integer rounding: each slot transfers $\lfloor v \cdot m/d \rfloor$ instead of the ideal $v \cdot m/d$. The per-slot depth rounding error is bounded by $16Q$ per slot. The aggregate rounding error across $k$ active slots is bounded by $k \cdot 16Q \leq 256Q$. For typical operations with $k = 1$–$3$ active slots, this is negligible relative to lock values of order $10^{18}$.

## Stale-Slot Corruption Without Free

::: theorem
**Theorem 6.9** (Push Corruption). *If `push(src, tgt, m, d)` is called without prior `free(tgt)`, and the target has a stale slot at index $i$ that is overwritten by an incoming active slot, then:*

1. *`totalOf(tgt)` is permanently inflated by the stale slot's value.*
2. *`depthOf(tgt)` is permanently corrupted.*
3. *Subsequent `free(tgt)` cannot recover correctness, because the stale epoch was overwritten with an active epoch.*
:::

::: proof
**Proof.** The stale target slot has $(e_{\text{stale}}, v_{\text{stale}})$ with $e_{\text{stale}} < e_{\text{now}}$. When the target-side branch of `_pushSlot` finds $e_{\text{slot}} \neq e_{\text{incoming}}$, it overwrites: $v \leftarrow \Delta v$, $e \leftarrow e_{\text{incoming}}$. The overwritten $v_{\text{stale}}$ was still counted in `cache[tgt].total` and `depth[tgt]`, but is now lost — `free()` will see the new active epoch and skip the slot. $\blacksquare$
:::

> **Remark.** This is a known design constraint. The `push()` function requires the `free(tgt)` precondition. The Position layer enforces it via `_lockFree(from, to)` before `_lockPush()`.

## Non-Negativity

::: theorem
**Theorem 6.10** (Depth Non-Negativity). *$\texttt{stateAt}(u, t).\texttt{depth} \geq 0$ for all users and timestamps $t \geq t_{\text{now}}$. $\texttt{depthOf}(u) \geq 0$ when saturating arithmetic is used.*
:::

::: proof
**Proof.** *For `stateAt`* ($t \geq t_{\text{now}}$): The effective time is $t_{\text{eff}} = \max(t, t_{\text{now}}) = t$. Each included slot satisfies $e_i \geq e_{\text{stamp}} = \lfloor t/Q \rfloor$, so $(e_i{+}1)Q \geq (\lfloor t/Q \rfloor + 1)Q > t$. Each term $v_i((e_i{+}1)Q - t) > 0$. The permanent contribution $pL \geq 0$.

*For `depthOf`*: When expired slots exist, the expired contribution is negative (Theorem 6.5), potentially driving the total negative. Saturating arithmetic (`sub256`) clamps to zero. $\blacksquare$
:::

## Bitmap Consistency

::: theorem
**Theorem 6.11** (Bitmap Invariant). *A bitmap bit at index $i$ is set if and only if $\texttt{slots}[u][i].\texttt{value} > 0$.*
:::

::: proof
**Proof.** By induction on operations:

- **Base.** All slots zero-initialized, bitmap = 0.
- **`more()`.** Sets bit $i$ when writing a non-zero value.
- **`free()`.** Clears bit $i$ only when deleting slot $i$ (value $\to 0$).
- **`push()` source.** The source-side branch of `_pushSlot` returns $\lnot \texttt{mask}(i)$ (clearing bit) only when $v = 0$ after subtraction.
- **`push()` target.** The target-side branch of `_pushSlot` returns $\texttt{mask}(i)$ (setting bit), and the loop skips $\Delta v = 0$.

In all cases the invariant is preserved. $\blacksquare$
:::

## Permanent Lock Invariance

::: theorem
**Theorem 6.12** (Permanent Depth Independence). *The `depth` register is independent of permanent locks. Permanent contributions to token-seconds are computed at query time as $p \cdot L$.*
:::

::: proof
**Proof.** In `more()` with $\texttt{dt\_term} = 2^{256}{-}1$: only the `cache` word is updated (the `perma` field, alongside the unchanged `total` and `bits`); `depth` is untouched. In `free()`: only timed slots are swept. In `push()`: the `perma` block of `_push` transfers between `cache[src].perma` and `cache[tgt].perma` without touching `depth`. The `depth` register exclusively tracks $\sum v_i(e_i{+}1)$ for timed slots. $\blacksquare$
:::
