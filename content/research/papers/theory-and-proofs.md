# Theory and proofs paper

Formal proofs of the protocol's key security and economic properties.

## Topics

### Cascade Attenuation Theorem

In a pool with permanent-locked fraction ϕ, the maximum cascade amplification factor is bounded by (1 − ϕ).

**Proof sketch.** Liquidations of locked supply transfer position tokens but not underlying tokens. The market sell-pressure that drives the cascade is therefore bounded by the unlocked fraction. □

### Sybil Rate-Limiting Theorem

A patient attacker controlling N Sybil accounts gains at most O(√N) capacity advantage over a single account.

**Proof sketch.** The √(n+2) divisor in the cap function applies per-account. With N Sybils each at iteration `n_avg`, the aggregate cap-per-operation scales as `N / √(n_avg + 2)`. The single-account equivalent is `1 / √(N · n_avg + 2) ≈ 1 / √N · 1/√(n_avg)`. The ratio simplifies to roughly √N. □

### Governance Rate Bound

A multiplicative parameter change of factor M requires ⌈log₂ M⌉ cycles.

**Proof sketch.** Each cycle bounds the change by 2×. After k cycles, the maximum compound factor is 2^k. Solving 2^k ≥ M gives k ≥ log₂ M. □

### MEV Resistance Theorem

The time-weighted parameter mean produces no single-block window where the parameter "snaps." Therefore, no MEV opportunity from front-running governance proposals.

**Proof sketch.** Effective values are read through `Integrator::meanOf`, which returns `area / (now − head_stamp)` over the parameter's history. At commit time `t_s` with prior commit `t_0`, the mean evolves as `θ̄(t) = θ₁ − (θ₁ − θ₀)(t_s − t₀)/(t − t₀)` — a strictly continuous function of `t`, with no time-discontinuity to front-run. □

### Nash Equilibrium Analysis (Lock Adoption)

Two self-reinforcing equilibrium regions exist: a *low-adoption* region where the equilibrium locked fraction `\bar{\rho} < 15%`, and a *high-adoption* region where `\bar{\rho} > 40%`. Selection depends on path. Above 95% utilization, the high-adoption region becomes attractive (cascade protection most valuable).

**Proof sketch.** Standard fixed-point analysis on the user's lock-or-not utility function. See the paper for the full derivation.

## Where to find the paper

- **PDF:** [`banq-mtp.pdf`](https://github.com/blackhan-software/xpower-banq-doc/releases/latest/download/banq-mtp.pdf) (latest release)
- **Unified bundle:** [`banq-all.pdf`](https://github.com/blackhan-software/xpower-banq-doc/releases/latest/download/banq-all.pdf) — this paper is Part III (Mathematical Theory & Proofs).

## Where to go next

- [Cascade protection](/features/locked-positions/cascade-protection) — the user-facing version
- [Position caps](/features/position-caps/overview) — Sybil rate-limiting
- [Lethargic governance](/features/lethargic-governance/overview) — governance bounds
