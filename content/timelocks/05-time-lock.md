---
title: "5. Time-Lock Extension"
prev:
  text: "4. Ring-Lock Mechanism"
  link: /timelocks/04-ring-lock
next:
  text: "6. Invariants & Proofs"
  link: /timelocks/06-proofs
---

# 5. Time-Lock Extension

The Time-Lock layer adds the `depth` mapping to the Ring-Lock structure. Each subsection describes the delta from the corresponding Ring-Lock operation.

## 5.1 The Token-Seconds Integral

Token-seconds measures total commitment depth:

$$D(u,t) = \sum_{i \in A} v_i \bigl((e_i{+}1)Q - t\bigr) + p \cdot L$$

where $A$ is the set of active timed slots, $p = \texttt{perma}[u]$, and $L = 15Q$.

## 5.2 The $O(1)$ Depth Identity

::: theorem
**Theorem 5.1** (Depth Identity). Let $A$ be the set of active timed slots for user $u$, and define:

$$\Sigma = \sum_{i \in A} v_i (e_i{+}1) \qquad \text{(stored in \texttt{depth})}$$

$$T = \sum_{i \in A} v_i \qquad \text{(timed = total - perma)}$$

Then $D(u,t) = \Sigma \cdot Q - T \cdot t + p \cdot L$.
:::

::: proof
Expand the sum:

$$D = \sum_{i \in A} v_i \bigl((e_i{+}1)Q - t\bigr) + p L = Q \sum_{i \in A} v_i(e_i{+}1) - t \sum_{i \in A} v_i + p L = \Sigma Q - T t + p L \qquad \blacksquare$$
:::

**Overflow handling.** The product $T \cdot t$ can exceed 256 bits. The Solidity implementation splits the computation via OpenZeppelin's `Math.mulDiv`:

$$\texttt{spent}  = \lfloor T \cdot t / Q \rfloor \qquad \text{(512-bit intermediate)}$$

$$\texttt{fract}  = T \cdot t \bmod Q \qquad \text{(sub-epoch remainder)}$$

$$\texttt{gross}  = (\Sigma - \texttt{spent}) \cdot Q$$

$$\texttt{result} = \texttt{gross} - \texttt{fract} + p \cdot L$$

::: theorem
**Lemma 5.2** (Overflow-Safe Decomposition). The equations above compute $\Sigma Q - T t + pL$ exactly.
:::

::: proof
Write $Tt = qQ + r$ where $q = \lfloor Tt/Q \rfloor$ and $r = Tt \bmod Q$. Then:

$$\Sigma Q - Tt = \Sigma Q - qQ - r = (\Sigma - q)Q - r = \texttt{gross} - \texttt{fract} \qquad \blacksquare$$
:::

## 5.3 `more()` with Depth Tracking

When a new lock is added, the cached depth accumulator $\Sigma$ must reflect the change. If the target slot was stale, its old contribution is first subtracted; then the new tokens' contribution—weighted by their expiry epoch—is added. This mirrors the self-healing logic of the base `more()`, extended to one additional storage word.

**Delta from [Section 4.1](/timelocks/04-ring-lock#_4-1-more-user-amount-dt-term-o-1-lock-addition)**: After the slot write, update `ls.depth[user]`:

- Stale overwrite: $\Sigma \mathrel{-}= v_{\text{old}} \cdot (e_{\text{old}}{+}1)$.
- Then: $\Sigma \mathrel{+}= \texttt{amount} \cdot (e_{\text{new}}{+}1)$.

**Complexity**: 3 `SSTORE`s (slot + coded + depth). Permanent: 2 `SSTORE`s (same as Ring-Lock—depth unchanged for permanent locks).

## 5.4 `free()` with Depth Tracking

As expired slots are swept away, their epoch-weighted contributions must also leave the depth accumulator. The sweep piggybacks on the same bitmap walk: each deleted slot's $v_i(e_i{+}1)$ term is collected into a single delta, then subtracted in one storage write at the end.

**Delta from [Section 4.2](/timelocks/04-ring-lock#_4-2-free-user-o-k-expired-slot-sweep)**: Accumulate $\Delta\Sigma = \sum_{\text{expired}} v_i(e_i{+}1)$ during the sweep. After the loop: $\texttt{depth}[u] \mathrel{-}= \Delta\Sigma$.

**Complexity**: $k$ `SSTORE`s (slots) + 2 `SSTORE`s (coded + depth).

## 5.5 `push()` with Depth Tracking

Because depth is an additive quantity, transferring locks between users is a zero-sum operation on $\Sigma$: whatever epoch-weighted value leaves the source's accumulator enters the target's. The loop collects the total delta once, then applies symmetric updates to both depth words.

**Delta from [Section 4.3](/timelocks/04-ring-lock#_4-3-push-src-tgt-mul-div-o-k-proportional-transfer)**: Within the source-bitmap loop, accumulate $\Delta\Sigma = \sum \Delta v_i \cdot (e_i{+}1)$. After the loop:

$$\texttt{depth}[\texttt{src}] \mathrel{-}= \Delta\Sigma$$

$$\texttt{depth}[\texttt{tgt}] \mathrel{+}= \Delta\Sigma$$

**Complexity**: $2k$ `SSTORE`s + 6 `SSTORE`s (perma$\times$2, coded$\times$2, depth$\times$2).

## 5.6 `stateAt()` with Depth

The exact query now returns a depth alongside the total. For each included slot the remaining token$\cdot$seconds contribution $(e_i{+}1)Q - t_{\text{eff}}$ is accumulated on the fly, plus the permanent lock's constant contribution $p \cdot L$.

**Delta from [Section 4.4](/timelocks/04-ring-lock#_4-4-stateat-user-stamp-o-k-exact-query)**: Returns $(\texttt{total}, \texttt{depth})$. For each active slot with $e_i \geq e_{\text{stamp}}$:

$$\texttt{depth} \mathrel{+}= v_i \bigl((e_i{+}1)Q - t_{\text{eff}}\bigr)$$

where $t_{\text{eff}} = \max(t_{\text{stamp}}, t_{\text{now}})$. Permanent contribution: $\texttt{depth} \mathrel{+}= p \cdot L$.

**Complexity**: $k$ `SLOAD`s + multiply/add per slot. No additional storage reads.

## 5.7 `depthOf(user)` — $O(1)$ Cached Depth

This is the key operation. Rather than looping over every active slot, `depthOf()` reconstructs the exact token-seconds value from three cached storage words ($\Sigma$, $T$, $p$) and the current timestamp, using the Depth Identity $D = \Sigma Q - Tt + pL$. The only subtlety is avoiding 256-bit overflow in the product $Tt$: the function splits it into a quotient via `mulDiv` and a remainder via `mulmod`, keeping all intermediate values within range. The result is a single $O(1)$ read with no loops and no bitmap traversal.

```solidity
function depthOf(Lock storage ls, address user)
    internal view returns (uint256)
{
    (uint240 total,) = _de(ls.coded[user]);
    uint256 perma = ls.perma[user];
    uint256 depth = ls.depth[user];
    uint256 timed = sub256(total, perma);
    uint256 spent = Math.mulDiv(
        timed, block.timestamp, LOCK_TERM);
    uint256 fract = mulmod(
        timed, block.timestamp, LOCK_TERM);
    uint256 gross = mul256(
        sub256(depth, spent), LOCK_TERM);
    return add256(
        sub256(gross, fract),
        mul256(perma, LOCK_TIME));
}
```

**Complexity**: 3 `SLOAD`s (`coded`, `perma`, `depth`). No loops, no bitmap iteration.

## 5.8 Worked Example

::: definition
**Setup.** $Q = 7{,}889{,}400$ s, $t = 100Q$ (start of epoch 100). Lock 40 tokens for 1 Q (epoch 101, slot $101 \bmod 16 = 5$) and 60 tokens for 6 Q (epoch 106, slot $106 \bmod 16 = 10$). No permanent locks.
:::

Stored values:

$$\Sigma = 40 \times 102 + 60 \times 107 = 4{,}080 + 6{,}420 = 10{,}500$$

$$T = 100 \quad (\text{timed} = 100, \; p = 0)$$

$$t = 100Q$$

**Via `depthOf`** ($O(1)$):

$$D = \Sigma Q - Tt + pL = 10{,}500Q - 100 \cdot 100Q + 0 = 10{,}500Q - 10{,}000Q = 500Q \text{ token-seconds}$$

**Via `stateAt`** ($O(k)$, verification):

$$\text{slot 5:}\quad 40 \times (102Q - 100Q) = 80Q$$

$$\text{slot 10:}\quad 60 \times (107Q - 100Q) = 420Q$$

$$\text{total:}\quad 80Q + 420Q = 500Q \;\checkmark$$
