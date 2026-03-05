# Change-rate constraints

The implementation of the lethargic governance bounds.

## The bound

For any parameter `θ`, prior value `θ₀`, proposed value `θ₁`, the contract enforces:

$$
\frac{1}{2} \cdot \theta_0 \;\leq\; \theta_1 \;\leq\; 2 \cdot \theta_0
$$

This is a per-window bound enforced inside `Parameterized._setTargetIf`. It cannot be bypassed by governance.

## Per-parameter rate limit

The rate limit is **timestamp-based**, not cycle-numbered. The `Limited` modifier is wired into `Parameterized` with window `Constant.MONTH` ≈ 30.44 days. Mechanically:

- A per-parameter mapping `_times[key]` stores the earliest `block.timestamp` at which the next change is allowed.
- On a successful change, `_times[key]` is set to `block.timestamp + Constant.MONTH`.
- Any subsequent change to the same parameter before that timestamp reverts.

There is no separate cycle counter, no `lastChangeCycle` field, and no `CYCLE` constant — just per-parameter timestamps and the `MONTH`-wide window.

## What this enforces

With a 2× per-window upper-bound:

- A 10× change requires at least **4 windows** (`2⁴ = 16 ≥ 10`) — ≈ 4 months.
- A 64× change requires **6 windows** (`2⁶ = 64`) — ≈ 6 months.
- A 1024× change requires **10 windows** (`2¹⁰ = 1024`) — ≈ 10 months.

The protocol cannot accelerate this. Even with unlimited governance power, the contract will reject changes that exceed the per-window 2× upper bound or arrive before the window timer has elapsed.

## Asymptotic transition

In addition to the bound, each approved change phases in via the asymptotic curve described in [Transition curves](/features/lethargic-governance/transition-curves). The effective value is a function of time since the proposal was committed.

## Where to go next

- [Lethargic governance overview](/features/lethargic-governance/overview)
- [Parameter bounds](/features/lethargic-governance/parameter-bounds)
- [Transition curves](/features/lethargic-governance/transition-curves)
