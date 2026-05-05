---
title: "4. Ring-Lock Mechanism"
prev:
  text: "3. Preliminaries"
  link: /timelocks/03-preliminaries
next:
  text: "5. Time-Lock Extension"
  link: /timelocks/05-time-lock
---

This section describes the base ring-buffer operations without depth tracking. Each subsection presents the algorithm and a complexity analysis.

## 4.1 `more(user, amount, dt_term)` — O(1) Lock Addition

Given a lock duration, compute which future epoch the tokens will expire in, then map that epoch to one of the 16 ring-buffer slots via modular arithmetic. If the slot already holds tokens for the same epoch, the new amount is simply added; if it is stale (left over from a previous cycle), the old residue is cleaned up first — this "self-healing" step keeps the cached total consistent without requiring a separate garbage-collection pass.

**Algorithm.**

0. Require $\texttt{amount} \leq 2^{112}{-}1$ and $\texttt{dt\_term} > 0$. Revert otherwise.
1. If $\texttt{dt\_term} = 2^{256}{-}1$ (sentinel): execute the **permanent path** — add to the `perma` field of `cache` (single `SSTORE`); no slot write, no bitmap change. Return.
2. Require $\texttt{dt\_term} \leq L - Q = 15Q$. Revert otherwise.
3. Compute target epoch: $e = \lfloor(t + \texttt{dt\_term}) / Q\rfloor$.
4. Compute slot index: $i = e \bmod 16$.
5. If `slot.epoch` $\neq e$ (stale or empty):
    - If the old value is positive, subtract it from `total` (self-healing).
    - Overwrite: `slot.epoch` $\leftarrow e$, `slot.value` $\leftarrow$ `amount`.
6. If `slot.epoch` $= e$ (accumulate): `slot.value` $\mathrel{+}=$ `amount`.
7. Update `cache`: add `amount` to the `total` field, set bit $i$ in `bits`.

**Complexity.** 2 `SSTORE`s (slot + `cache`). Permanent: 1 `SSTORE` (`cache` only). Measured: 179,860 / 66,688 gas (cold/warm) for timed `lockSupply`, 86,712 cold for permanent.

## 4.2 `free(user)` — O(k) Expired Slot Sweep

Because `more()` never deletes old slots, expired tokens can linger in the ring buffer. `free()` walks only the slots marked by the bitmap — skipping empty positions entirely — and removes any whose epoch has already passed. The bitmap serves as a compact "to-do list," so the sweep touches exactly the slots that matter and nothing else.

**Algorithm.**

1. Read `cache` $\to$ extract `bits`. (`perma` and `total` are re-loaded just before the cache write-back.)
2. Iterate bitmap via LSB extraction: for each set bit $i$, load `slots[user][i]`.
3. If `slot.epoch` $< e_{\text{now}}$: accumulate freed amount, delete slot, clear bit $i$.
4. Write back `cache` with updated `total` and `bits` (`perma` preserved).

**Complexity.** $k$ `SLOAD`s + up to $k$ `SSTORE`s (only deleted/decremented slots) + up to 1 `SSTORE` (`cache`; skipped if neither `total` nor `bits` changed). Measured worst-case (free 16 expired slots): 31,157 gas.

## 4.3 `push(src, tgt, mul, div)` — O(k) Proportional Transfer

Transferring locks between two users must preserve both the amounts *and* their expiry schedule. `push()` walks the source's bitmap and moves a proportional fraction $m/d$ of each slot's value into the corresponding slot of the target — same epoch, same remaining duration. The fraction is rounded down per slot to keep all values integral.

**Algorithm.**

1. Walk source bitmap: for each slot, compute $\Delta v = \lfloor v \cdot m / d \rfloor$.
2. Set target slot: if same epoch $\to$ accumulate, else overwrite.
3. Set source slot: subtract $\Delta v$; clear bit if zero.
4. Batch-write both `cache` words (`perma`, `total`, `bits` together per side).

**Precondition.** Caller **must** call `free(tgt)` before `push()` to avoid stale-slot corruption (see [Theorem 6.9](/timelocks/06-proofs#stale-slot-corruption-without-free)).

**Complexity.** $(2k{+}2)$ `SLOAD`s + $2k$ `SSTORE`s + 2 `SSTORE`s (`cache` × 2; `perma` rides along in the same word). Measured `xfer_supply`: 145,251 (perma only) / 191,463 (1 slot) / 402,525 (16 slots, worst case).

## 4.4 `stateAt(user, stamp)` — O(k) Exact Query

While `totalOf()` returns a cheap cached answer, `stateAt()` computes the *exact* locked balance at an arbitrary timestamp by re-scanning the ring buffer. It includes only those slots whose epoch is at or after the query point, thereby filtering out any tokens that will have expired by that time.

**Algorithm.**

1. Read `cache` once; start with $\texttt{total} = \texttt{cache.perma}$.
2. Walk bitmap: for each active slot with $e_i \geq e_{\text{stamp}}$, add $v_i$ to total.
3. Return total.

**Complexity.** 1 `SLOAD` (`cache`, supplies `perma` and `bits`) + $k$ `SLOAD`s (bitmap-guided slot reads). No writes. Measured `lockStateAt` (16-slot view): 17,895 gas.

## 4.5 `roll(user, amount, dt_term)` — O(k) Sweep-and-Re-Lock

`roll()` combines a partial sweep with a new lock in a single call: it drains up to `amount` tokens from the user's earlier active slots (those whose epoch is strictly before the target epoch) and re-locks the drained amount into the target slot. This is useful for extending an existing position's commitment without making separate `free()` and `more()` calls.

**Algorithm.**

1. Compute target stamp $\texttt{stamp} = t + \texttt{dt\_term}$ and target epoch $e_{\text{tgt}} = \lfloor \texttt{stamp}/Q \rfloor$.
2. Walk the user's bitmap and, for each active slot with $e_i < e_{\text{tgt}}$, drain up to the remaining `amount` (using the same `_freeAt` helper as `free()`).
3. Re-lock the drained total into the target slot via `_more` (same code path as `more()`, including self-healing).

**Complexity.** $O(k)$ — one `_freeAt` pass plus one `_more` call. Same `dt_term` semantics as `more()`.

## 4.6 `totalOf(user)` — O(1) Cached Query

Decode the middle 120 bits of `cache`: a single `SLOAD`.

> **Remark.** The cached total may include expired-but-unswept slot values. Thus $\texttt{totalOf}(u) \geq \texttt{stateAt}(u, t_{\text{now}}).\texttt{total}$. Equality is restored after $\texttt{free}(u)$.
