# Lethargic governance

XPower Banq's governance is deliberately slow. Every parameter change is bounded multiplicatively, phased in asymptotically, and rate-limited to one change per cycle. A 10× change requires 4 months. A 64× change requires 6 months.

This is by design. Most lending-protocol failures with a governance dimension share a common shape: a vote passes, a parameter flips immediately, and either an attacker exploits the new state or users get caught off-guard. Slow governance breaks that pattern.

![Lethargic governance transition](../../diagrams/lethargic-transition.svg)

## The three constraints

1. **Multiplicative bound.** Any new value `θ₁` must satisfy `0.5 × θ₀ ≤ θ₁ ≤ 2 × θ₀`. You cannot, in a single proposal, halve or double-and-then-some. The full safe-corridor is encoded on-chain.
2. **Asymptotic transition.** When a change is approved, the protocol's *effective* parameter doesn't snap to the new target. It approaches the new target asymptotically over the cycle, leaving the prior value as the dominant influence at the start of the cycle and the new value as the dominant influence by its end.
3. **One change per cycle per parameter.** Within a cycle, a given parameter can be touched only once. This prevents 2x-2x-2x in rapid succession.

The cycle length is itself a parameter (default 1 month). It can be changed, but only via the same lethargic mechanism.

## What this protects against

- **Compromised governors.** An attacker who briefly controls governance can do real damage but cannot drain the protocol in a single block.
- **Honest mistakes.** A miscalibrated parameter can be reversed within the same cycle's bound, before the new value's effect dominates.
- **Coordinated exits.** Users always have at least one cycle to react to changes. A 2× change in LTV gives users 30 days to reposition before the new value is in full effect.

## What this doesn't fix

- **Sustained malicious control.** A persistent attacker holding governance for 4+ months can still push parameters anywhere they want. The protocol's bound is a deceleration, not a hard ceiling.
- **Slow legitimate response.** If something genuinely needs to change *fast* — say, an emergency parameter tightening during a market crash — lethargic governance will frustrate that. The protocol provides a separate **emergency veto** path (see [Role hierarchy](/features/lethargic-governance/role-hierarchy)) but no emergency *acceleration*.
- **Protocol-level vulnerabilities.** Lethargic governance is about parameter changes. It doesn't help if the underlying contracts have a bug.

## Subsections

- **[Parameter bounds](/features/lethargic-governance/parameter-bounds)** — the per-parameter ranges and rate limits
- **[Transition curves](/features/lethargic-governance/transition-curves)** — the math of the asymptotic phase-in
- **[Role hierarchy](/features/lethargic-governance/role-hierarchy)** — who can do what
