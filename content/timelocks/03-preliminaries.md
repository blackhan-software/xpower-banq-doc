---
title: "3. Preliminaries"
prev:
  text: "2. Related Work"
  link: /timelocks/02-related-work
next:
  text: "4. Ring-Lock Mechanism"
  link: /timelocks/04-ring-lock
---

## Definitions

::: definition
**Definition 3.1** (Epoch). The *absolute epoch index* at timestamp $t$ is $e = \lfloor t / Q \rfloor$, where $Q = \texttt{LOCK\_TERM} \approx 91.3$ days (one calendar quarter).
:::

::: definition
**Definition 3.2** (Slot Index). The ring-buffer *slot index* for epoch $e$ is $i = e \bmod 16$.
:::

::: definition
**Definition 3.3** (Lock Expiry). A lock in epoch $e$ expires at timestamp $(e{+}1) \times Q$, the start of the next epoch.
:::

::: definition
**Definition 3.4** (Token-Seconds). The *token-second depth* for user $u$ at timestamp $t$ is

$$D(u,t) = \sum_{i \in A} v_i \bigl((e_i{+}1)Q - t\bigr) + p \cdot L$$

where $A$ is the set of active (non-expired) timed slots, $v_i$ and $e_i$ are the value and epoch of slot $i$, $p = \texttt{perma}[u]$ is the permanently locked amount, and $L = \texttt{LOCK\_TIME} = 16Q \approx 48$ months.
:::

## Storage Layout

The complete storage is 10 words per user (most zero-initialized):

```solidity
// 128-bit packed words: [uint16 epoch | uint112 value].
// uint128[16] = 8 storage words, two slots per word.
struct Lock {
    // 16-slot quarterly ring buffer (8 words, 2 per word)
    mapping(address => uint128[16]) slots;
    // [uint120 perma | uint120 total | uint16 bits]
    mapping(address => uint256)     cache;
    // epoch-weighted sum: sigma v_i*(e_i+1)
    mapping(address => uint256)     depth;
}
```

The first 9 words (8 ring slots + `cache`) constitute the Ring-Lock layer. The `depth` mapping is the Time-Lock extension. The `cache` word merges the irrevocable `perma` amount, the cached ring `total`, and the active-slot `bits` bitmap into a single `SLOAD`/`SSTORE` — a key gas optimization, since most operations touch all three fields together. Per-call `amount` is bounded by `uint112`; `perma` saturates at $2^{120}{-}1$ (cumulative permanent deposits would need ~256 max-sized adds before saturation).

## Bitmap Encoding

The `cache` word packs three values: the upper 120 bits store the irrevocable `perma` amount, the middle 120 bits store the cached ring `total`, and the lower 16 bits store the active-slot bitmap. Decoding:

$$\texttt{perma} = \texttt{cache} \gg 136$$

$$\texttt{total} = (\texttt{cache} \gg 16) \mathbin{\&} (2^{120}{-}1)$$

$$\texttt{bits}  = \texttt{cache} \mathbin{\&} \texttt{0xFFFF}$$

LSB extraction uses a de Bruijn sequence [\[debruijn\]](/reference/bibliography#debruijn): the lowest set bit is isolated via $\texttt{lsb} = b \mathbin{\&} (\lnot b + 1)$, then multiplied by the constant `0x09AF` modulo $2^{16}$, producing a unique 4-bit hash in the top nibble that indexes into a 64-bit lookup table. This replaces 16 conditional `SLOAD`s with 1 `SLOAD` plus bit arithmetic.
