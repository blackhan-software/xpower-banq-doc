---
title: "7. Gas Analysis"
prev:
  text: "6. Invariants & Proofs"
  link: /timelocks/06-proofs
next:
  text: "8. Integration"
  link: /timelocks/08-integration
---

The following table summarises the storage access costs for each operation under both the Ring-Lock base layer and the Time-Lock extension.

| Operation | Ring-Lock | Time-Lock | Δ |
|---|---|---|---|
| `more` (timed) | 2 `SSTORE` | 3 `SSTORE` | +1 |
| `more` (perma) | 1 `SSTORE` | 1 `SSTORE` | 0 |
| `free` | $k{+}1$ `SSTORE` | $k{+}2$ `SSTORE` | +1 |
| `push` | $2k{+}2$ `SSTORE` | $2k{+}4$ `SSTORE` | +2 |
| `totalOf` | 1 `SLOAD` | 1 `SLOAD` | 0 |
| `depthOf` | — | 2 `SLOAD` | new |
| `stateAt` | $k{+}1$ `SLOAD` | $k{+}1$ `SLOAD` | 0 |

The Time-Lock extension adds at most 2 `SSTORE`s per mutating operation. All queries remain bounded. The $O(1)$ `depthOf` avoids the $O(k)$ `stateAt` walk for the common case of checking a user's commitment depth — the primary use case for interest rate adjustments.

Since $k \leq 16$ (ring-buffer width), even the worst-case `push()` has a hard upper bound of 36 `SSTORE`s and 36 `SLOAD`s ($2k$ slots + 4 ancillary: `cache` × 2, `depth` × 2; `perma` packed inside `cache`), ensuring gas predictability regardless of user behavior. Empirically, `xfer_supply` measures 145,251 gas (perma only) up to 402,525 gas (16 active slots, worst case).
