---
title: "5. Time-Lock Extension"
prev:
  text: "4. Ring-Lock Mechanism"
  link: /timelocks/04-ring-lock
next:
  text: "6. Invariants & Proofs"
  link: /timelocks/06-proofs
---

The Time-Lock layer adds the `depth` mapping to the Ring-Lock structure. Each subsection describes the delta from the corresponding Ring-Lock operation.

## 5.1 The Token-Seconds Integral

Token-seconds measures total commitment depth:

$$D(u,t) = \sum_{i \in A} v_i \bigl((e_i{+}1)Q - t\bigr) + p \cdot L$$

where $A$ is the set of active timed slots, $p = \texttt{perma}[u]$, and $L = 16Q$.

## 5.2 The O(1) Depth Identity

::: theorem
**Theorem 5.1** (Depth Identity). *Let $A$ be the set of active timed slots for user $u$, and define*

$$\Sigma = \sum_{i \in A} v_i (e_i{+}1) \qquad \text{(stored in \texttt{depth})}$$

$$T = \sum_{i \in A} v_i \qquad \text{(timed = total − perma)}$$

*Then $D(u,t) = \Sigma \cdot Q - T \cdot t + p \cdot L$.*
:::

::: proof
**Proof.** Expand the sum:

$$\begin{aligned}
D &= \sum_{i \in A} v_i \bigl((e_i{+}1)Q - t\bigr) + p L \\
  &= Q \sum_{i \in A} v_i(e_i{+}1) - t \sum_{i \in A} v_i + p L \\
  &= \Sigma Q - T t + p L \qquad \blacksquare
\end{aligned}$$
:::

**Implementation form.** To match the token-equivalent units used by the bonus/malus layer ([§8](/timelocks/08-integration)), the implementation returns the normalized quantity $\widehat{D} = D/L + p$ rather than $D$ itself. Both intermediate products are performed with OpenZeppelin's `Math.mulDiv` [\[oz-math\]](/reference/bibliography#oz-math), which carries a 512-bit numerator natively so no separate sub-epoch remainder term is needed:

$$\texttt{gross}    = \lfloor \Sigma \cdot Q / L \rfloor$$

$$\texttt{spent}    = \lfloor \mathit{total} \cdot t / L \rfloor$$

$$\texttt{depthOf}(u) = \texttt{gross} - \texttt{spent} + p$$

where `total` (the timed total stored in `cache`, distinct from `perma`) is exactly $T$.

::: theorem
**Lemma 5.2** (Overflow-Safe Computation). *The equations above compute $\lfloor \Sigma Q/L \rfloor - \lfloor T t/L \rfloor + p$ exactly via two independent 512-bit `mulDiv` operations.*
:::

::: proof
**Proof.** `Math.mulDiv(a, b, c)` returns $\lfloor a \cdot b / c \rfloor$ for any 256-bit $a, b, c$ without intermediate overflow, because the product $a \cdot b$ is held in a 512-bit pair before the final division. Applied to $(\Sigma, Q, L)$ and $(\mathit{total}, t, L)$, this directly yields the two floors above. The closing addition of the 120-bit `perma` field cannot exceed $2^{256}$. $\blacksquare$
:::

::: theorem
**Lemma 5.3** ($\Sigma$ Overflow Safety). *Let $S$ denote the maximum per-user locked total and $E$ the current epoch. If $S \cdot (E{+}16) < 2^{256}$, then the stored $\Sigma$ fits in `uint256`. The intermediate product $\Sigma \cdot Q$ in the gross computation is then carried by `Math.mulDiv` with full 512-bit precision and never materializes as a single 256-bit value.*
:::

::: proof
**Proof.** All active epochs lie in $[E, E{+}15]$ (Theorem 6.1), so $(e_i{+}1) \leq E{+}16$. The sum of slot values satisfies $T = \sum v_i \leq S$. Thus $\Sigma = \sum v_i(e_i{+}1) \leq S(E{+}16) < 2^{256}$.

*Practical margin.* The slot epoch field is a `uint16`, so $E < 2^{16}$. With $E + 16 < 2^{16}$ this leaves $S < 2^{240}$ — far above any realistic ERC-20 token supply. The Position layer's `cap()` mechanism provides the enforcement point. $\blacksquare$
:::

## 5.3 `more()` with Depth Tracking

When a new lock is added, the cached depth accumulator $\Sigma$ must reflect the change. If the target slot was stale, its old contribution is first subtracted; then the new tokens' contribution — weighted by their expiry epoch — is added. This mirrors the self-healing logic of the base `more()`, extended to one additional storage word.

**Delta from §4.1.** Step 1 (permanent sentinel) returns before reaching the depth update — `depth` is untouched for permanent locks. For timed locks, after the slot write, update `ls.depth[user]`:

- Stale overwrite: $\Sigma \mathrel{-}= v_{\text{old}} \cdot (e_{\text{old}}{+}1)$.
- Then: $\Sigma \mathrel{+}= \texttt{amount} \cdot (e_{\text{new}}{+}1)$.

**Complexity.** 3 `SSTORE`s (slot + `cache` + `depth`). Permanent: 1 `SSTORE` (same as Ring-Lock — `depth` unchanged for permanent locks).

## 5.4 `free()` with Depth Tracking

As expired slots are swept away, their epoch-weighted contributions must also leave the depth accumulator. The sweep piggybacks on the same bitmap walk: each deleted slot's $v_i(e_i{+}1)$ term is collected into a single delta, then subtracted in one storage write at the end.

**Delta from §4.2.** Accumulate $\Delta\Sigma = \sum_{\text{expired}} v_i(e_i{+}1)$ during the sweep. After the loop: $\texttt{depth}[u] \mathrel{-}= \Delta\Sigma$.

**Complexity.** $k$ `SSTORE`s (slots) + 2 `SSTORE`s (`cache` + `depth`).

## 5.5 `push()` with Depth Tracking

Because depth is an additive quantity, transferring locks between users is a zero-sum operation on $\Sigma$: whatever epoch-weighted value leaves the source's accumulator enters the target's. The loop collects the total delta once, then applies symmetric updates to both depth words.

**Delta from §4.3.** Within the source-bitmap loop, accumulate $\Delta\Sigma = \sum \Delta v_i \cdot (e_i{+}1)$. After the loop:

$$\texttt{depth}[\texttt{src}] \mathrel{-}= \Delta\Sigma$$

$$\texttt{depth}[\texttt{tgt}] \mathrel{+}= \Delta\Sigma$$

**Complexity.** $2k$ `SSTORE`s + 4 `SSTORE`s (`cache` × 2, `depth` × 2; `perma` packed in `cache`).

## 5.6 `stateAt()` with Depth

The exact query now returns a depth alongside the total. For each included slot the remaining token·seconds contribution $(e_i{+}1)Q - t_{\text{eff}}$ is accumulated on the fly, plus the permanent lock's constant contribution $p \cdot L$.

**Delta from §4.4.** Returns $(\texttt{total}, \texttt{depth})$. For each active slot with $e_i \geq e_{\text{stamp}}$:

$$\texttt{depth} \mathrel{+}= v_i \bigl((e_i{+}1)Q - t_{\text{eff}}\bigr)$$

where $t_{\text{eff}} = \max(t_{\text{stamp}}, t_{\text{now}})$. Permanent contribution: $\texttt{depth} \mathrel{+}= p \cdot L$.

> **Units.** The accumulator above is in raw token-seconds, but `stateAt` applies the same $/L$ normalization as `depthOf` before returning, so the reported depth is in token-equivalent units (committed tokens remaining), not token-seconds.

**Complexity.** $k$ `SLOAD`s + multiply/add per slot. No additional storage reads.

## 5.7 `depthOf(user)` — O(1) Cached Depth

Rather than looping over every active slot, `depthOf()` reconstructs the token-seconds value from three cached storage words ($\Sigma$, `total`, $p$) and the current timestamp, using the Depth Identity. To match the units used by the bonus/malus layer, the function returns

$$\widehat{D}(u,t) = \bigl\lfloor \Sigma \cdot Q / L \bigr\rfloor - \bigl\lfloor \mathit{total} \cdot t / L \bigr\rfloor + p$$

i.e. $D/L + p$ expressed in token units (with `mulDiv` performing each division with full 512-bit intermediate precision so no overflow can occur). The result is a single $O(1)$ read with no loops and no bitmap traversal.

```solidity
function depthOf(Lock storage ls, address user)
    internal view returns (uint256)
{
    (uint120 perma, uint120 total,) = _full(ls.cache[user]);
    uint256 depth = ls.depth[user];
    uint256 gross = Math.mulDiv(
        depth, LOCK_TERM, LOCK_TIME);
    uint256 spent = Math.mulDiv(
        total, block.timestamp, LOCK_TIME);
    return add256(sub256(gross, spent), perma);
}
```

`cache` stores `perma` and `total` as *independent* fields (`total` is the timed total; permanent locks are not part of it), so no $\mathit{total} - \mathit{perma}$ subtraction is needed.

**Complexity.** 2 `SLOAD`s (`cache` supplies `perma` + `total`; `depth` loaded separately). No loops, no bitmap iteration.

## 5.8 Worked Example

::: definition
**Setup.** $Q = 7{,}889{,}400$ s, $t = 100Q$ (start of epoch 100). Lock 40 tokens for 1 Q (epoch 101, slot $101 \bmod 16 = 5$) and 60 tokens for 6 Q (epoch 106, slot $106 \bmod 16 = 10$). No permanent locks.
:::

Stored values:

$$\Sigma = 40 \times 102 + 60 \times 107 = 4{,}080 + 6{,}420 = 10{,}500$$

$$T = 100 \quad (\text{timed} = 100, \; p = 0), \quad t = 100Q$$

**Idealized depth** (token-seconds, for intuition):

$$D = \Sigma Q - Tt + pL = 10{,}500 Q - 100 \cdot 100 Q + 0 = 500 Q \text{ token-seconds}$$

**Via `depthOf`** ($O(1)$, normalized form, $L = 16Q$):

$$\texttt{gross}      = \lfloor 10{,}500 \cdot Q / (16Q) \rfloor = \lfloor 10{,}500/16 \rfloor = 656$$

$$\texttt{spent}      = \lfloor 100 \cdot 100Q / (16Q) \rfloor   = \lfloor 10{,}000/16 \rfloor = 625$$

$$\texttt{depthOf}(u) = 656 - 625 + 0 = 31$$

This is $\lfloor D/L \rfloor + p = \lfloor 500Q/(16Q) \rfloor + 0 = 31$ in token units, as expected.

**Via `stateAt`** ($O(k)$, verification of the idealized $D$):

$$\text{slot 5:}\quad 40 \times (102Q - 100Q) = 80Q$$

$$\text{slot 10:}\quad 60 \times (107Q - 100Q) = 420Q$$

$$\text{total:}\quad 80Q + 420Q = 500Q \;\checkmark$$
