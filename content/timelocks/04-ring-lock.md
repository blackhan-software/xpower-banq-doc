---
title: "4. Ring-Lock Mechanism"
prev:
  text: "3. Preliminaries"
  link: /timelocks/03-preliminaries
next:
  text: "5. Time-Lock Extension"
  link: /timelocks/05-time-lock
---

# 4. Ring-Lock Mechanism

This section describes the base ring-buffer operations without depth tracking. Each subsection presents the algorithm and a complexity analysis.

## 4.1 `more(user, amount, dt_term)` — $O(1)$ Lock Addition

The idea is straightforward: given a lock duration, compute which future epoch the tokens will expire in, then map that epoch to one of the 16 ring-buffer slots via modular arithmetic. If the slot already holds tokens for the same epoch, the new amount is simply added; if it is stale (left over from a previous cycle), the old residue is cleaned up first—this "self-healing" step keeps the cached total consistent without requiring a separate garbage-collection pass.

**Algorithm.**

1. Compute target epoch: $e = \lfloor(t + \texttt{dt\_term}) / Q\rfloor$.
2. Compute slot index: $i = e \bmod 16$.
3. If `slot.epoch` $\neq e$ (stale or empty):
   - If the old value is positive, subtract it from `total` (self-healing).
   - Overwrite: `slot.epoch` $\leftarrow e$, `slot.value` $\leftarrow$ `amount`.
4. If `slot.epoch` $= e$ (accumulate): `slot.value` $\mathrel{+}=$ `amount`.
5. Update `coded`: add `amount` to total, set bit $i$.
6. **Permanent path** ($\texttt{dt\_term} = 2^{256}{-}1$): add to `perma` and `coded` total; no slot write, no bitmap change.

**Complexity**: 2 `SSTORE`s (slot + coded). Permanent: 2 `SSTORE`s (perma + coded).

## 4.2 `free(user)` — $O(k)$ Expired Slot Sweep

Because `more()` never deletes old slots, expired tokens can linger in the ring buffer. `free()` walks only the slots marked by the bitmap—skipping empty positions entirely—and removes any whose epoch has already passed. The bitmap serves as a compact "to-do list," so the sweep touches exactly the slots that matter and nothing else.

**Algorithm.**

1. Read `coded` $\to$ extract total and bitmap.
2. Iterate bitmap via LSB extraction: for each set bit $i$, load `slots[user][i]`.
3. If `slot.epoch` $< e_{\text{now}}$: accumulate freed amount, delete slot, clear bit $i$.
4. Write back `coded` with updated total and bitmap.

**Complexity**: $k$ `SLOAD`s + $k$ `SSTORE`s (slots) + 1 `SSTORE` (coded), where $k$ is the number of set bitmap bits.

## 4.3 `push(src, tgt, mul, div)` — $O(k)$ Proportional Transfer

Transferring locks between two users must preserve both the amounts *and* their expiry schedule. `push()` achieves this by walking the source's bitmap and moving a proportional fraction $m/d$ of each slot's value into the corresponding slot of the target—same epoch, same remaining duration. The fraction is rounded down per slot to keep all values integral.

**Algorithm.**

1. Walk source bitmap: for each slot, compute $\Delta v = \lfloor v \cdot m / d \rfloor$.
2. Set target slot: if same epoch $\to$ accumulate, else overwrite.
3. Set source slot: subtract $\Delta v$; clear bit if zero.
4. Batch-write both `coded` words.

**Precondition**: Caller **must** call `free(tgt)` before `push()` to avoid stale-slot corruption (see [Theorem 6.6](/timelocks/06-proofs#stale-slot-corruption-without-free)).

**Complexity**: $2k$ `SLOAD`s + $2k$ `SSTORE`s + 4 `SSTORE`s (perma$\times$2, coded$\times$2).

## 4.4 `stateAt(user, stamp)` — $O(k)$ Exact Query

While `totalOf()` returns a cheap cached answer, `stateAt()` computes the *exact* locked balance at an arbitrary timestamp by re-scanning the ring buffer. It includes only those slots whose epoch is at or after the query point, thereby filtering out any tokens that will have expired by that time.

**Algorithm.**

1. Start with $\texttt{total} = \texttt{perma}[u]$.
2. Walk bitmap: for each active slot with $e_i \geq e_{\text{stamp}}$, add $v_i$ to total.
3. Return total.

**Complexity**: $k$ `SLOAD`s (bitmap-guided) + 1 `SLOAD` (perma). No writes.

## 4.5 `totalOf(user)` — $O(1)$ Cached Query

Decode the upper 240 bits of `coded`: a single `SLOAD`.

> **Remark.** The cached total may include expired-but-unswept slot values. Thus $\texttt{totalOf}(u) \geq \texttt{stateAt}(u, t_{\text{now}}).\texttt{total}$. Equality is restored after $\texttt{free}(u)$.
