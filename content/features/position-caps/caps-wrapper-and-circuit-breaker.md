# Caps wrapper and circuit breaker

The beta-distributed [position caps](/features/position-caps/overview) limit how fast a *single account* can grow. Separately, each Pool token also has an absolute **supply cap** and **borrow cap** (`capSupply` / `capBorrow`) set by governance. This page documents the **Caps** wrapper contract that adjusts those caps, and the **circuit-breaker bot** that uses it to lower a cap when on-chain activity looks anomalous.

## The Caps wrapper

`Pool.capSupply(token, limit, dt)` and `Pool.capBorrow(...)` are raw, restricted functions that take an absolute limit. The `Caps` contract wraps them into **delta-based** moves, so a caller changes the cap *relative to its current value* rather than needing to read-and-rewrite the absolute number:

| Function | Effect |
|---|---|
| `incSupply(pool, token, delta)` | Raise the supply cap by `delta` (saturating at `2¹¹² − 1`) |
| `decSupply(pool, token, delta)` | Lower the supply cap by `delta` (saturating at `0`) |
| `incBorrow(pool, token, delta)` | Raise the borrow cap by `delta` (saturating at `2¹¹² − 1`) |
| `decBorrow(pool, token, delta)` | Lower the borrow cap by `delta` (saturating at `0`) |

Each function is gated by its **own ACMA role triple**, mirroring the standard Banq pattern:

| Operation | Exec role | Admin role | Guard role |
|---|---|---|---|
| `incSupply` | `CAPS_INC_SUPPLY_ROLE` | `CAPS_INC_SUPPLY_ADMIN_ROLE` | `CAPS_INC_SUPPLY_GUARD_ROLE` |
| `decSupply` | `CAPS_DEC_SUPPLY_ROLE` | `CAPS_DEC_SUPPLY_ADMIN_ROLE` | `CAPS_DEC_SUPPLY_GUARD_ROLE` |
| `incBorrow` | `CAPS_INC_BORROW_ROLE` | `CAPS_INC_BORROW_ADMIN_ROLE` | `CAPS_INC_BORROW_GUARD_ROLE` |
| `decBorrow` | `CAPS_DEC_BORROW_ROLE` | `CAPS_DEC_BORROW_ADMIN_ROLE` | `CAPS_DEC_BORROW_GUARD_ROLE` |

Role IDs are derived as `role_id("...") = keccak256(label || "caps")` — the `"caps"` suffix prevents collisions with other contracts' roles. The `dec*` roles can be granted to an automated operator while `inc*` roles stay with a multisig, so a bot can *tighten* caps but never *loosen* them.

A lowered cap still respects the pool's cap semantics: a *decrease* below the current value is applied immediately (the protocol treats this as a circuit-breaker), while an *increase* is only accepted when no transition is active and then glides in asymptotically. Both restrictions are enforced on-chain by `Position.cap`.

## The circuit-breaker bot (`banq-cl`)

XPower Banq operates a **cap-limit monitor** — the `banq-cl` service family — that watches per-token, per-side activity and can **lower a cap to zero** when it detects an anomalous pattern (a potential sybil fan-out or a rapid drain). It does *not* set rates, move funds, or touch any other parameter: its only action is to pull the relevant supply or borrow cap down.

The bot runs one instance per pool token and side (e.g. `banq-cl@APOW:supply:P000`) on a fixed cadence, reading the same on-chain transfer data the tracking services ingest. When its detection logic trips for an instance:

1. It issues `banq cap-limit <TOKEN> 2¹¹²−1 --pool <P> --mode <side> --dec -Y` — a **decrease** by the maximum sentinel, which saturates the cap to zero.
2. A **cooldown** after each trip prevents the breaker from being spammed into repeated use.
3. A **dry-run mode** (via `banq-cl.dry-run.sh`, or `DRY=1`) logs the detection without executing any on-chain action, for safe rehearsal.

The bot is deliberately narrow: it can only ever *lower* caps (via the `dec*` roles), and a human multisig retains the `inc*` roles to restore caps after review. The precise trigger conditions it evaluates are intentionally **not** documented here — they are operational detail, not protocol interface. What matters for integration is that a trip results in a saturating `dec` cap move through the Caps contract, subject to the cooldown, with each move recorded by the `CapSupply` / `CapBorrow` events on the pool.

## Why a separate wrapper?

A bot with direct `POOL_CAP_ROLE` could set *any* cap to *any* value, including raising it. Splitting `inc` from `dec` into separate roles on the `Caps` wrapper means the automated operator holds a **one-way valve**: it can always make the protocol *safer* (smaller caps), never *riskier* (larger caps). That single-direction privilege is the safety property the circuit-breaker design depends on.

## Where to go next

- [Position caps](/features/position-caps/overview) — the beta-distributed per-account rate-limiting
- [How caps grow](/features/position-caps/how-caps-grow) — cap evolution dynamics
- [Emergency procedures](/governance/emergency-procedures) — the guard tier as a human circuit breaker
- [Parameter catalog](/governance/parameter-catalog) — cap parameters and per-cycle constraints
