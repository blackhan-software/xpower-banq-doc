---
title: "3. Preliminaries"
prev:
  text: "2. Related Work"
  link: /timelocks/02-related-work
next:
  text: "4. Ring-Lock Mechanism"
  link: /timelocks/04-ring-lock
---

# 3. Preliminaries

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
**Definition 3.4** (Token-Seconds). The *token-second depth* for user $u$ at timestamp $t$ is:

$$D(u,t) = \sum_{i \in A} v_i \bigl((e_i{+}1)Q - t\bigr) + p \cdot L$$

where $A$ is the set of active (non-expired) timed slots, $v_i$ and $e_i$ are the value and epoch of slot $i$, $p = \texttt{perma}[u]$ is the permanently locked amount, and $L = \texttt{LOCK\_TIME} = 15Q \approx 45$ months.
:::

## Storage Layout

The complete storage is 19 words per user:

```solidity
struct LockSlot {
    uint32 epoch;  // absolute epoch index
    uint224 value; // locked amount
}  // 1 word (256 bits packed)

struct Lock {
    // 16-slot quarterly ring buffer
    mapping(address => LockSlot[16]) slots;
    // permanent (irrevocable) locked amount
    mapping(address => uint256) perma;
    // [uint240 total | uint16 bits]
    mapping(address => uint256) coded;
    // epoch-weighted sum: sigma v_i*(e_i+1)
    mapping(address => uint256) depth;
}
```

The first 18 words (16 slots + `perma` + `coded`) constitute the Ring-Lock layer. The `depth` mapping is the Time-Lock extension.

## Bitmap Encoding

The `coded` word packs two values: the upper 240 bits store the cached total locked amount, and the lower 16 bits store the active-slot bitmap. Decoding:

$$\texttt{total} = \texttt{coded} \gg 16$$

$$\texttt{bits} = \texttt{coded} \mathbin{\&} \texttt{0xFFFF}$$

LSB extraction uses a de Bruijn sequence: the lowest set bit is isolated via $\texttt{lsb} = b \mathbin{\&} (\lnot b + 1)$, then multiplied by the constant `0x09AF` modulo $2^{16}$, producing a unique 4-bit hash in the top nibble that indexes into a 64-bit lookup table. This replaces 16 conditional `SLOAD`s with 1 `SLOAD` plus bit arithmetic.
