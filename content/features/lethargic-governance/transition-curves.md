# Transition curves

Once a parameter change has been scheduled, the new value doesn't snap into effect immediately. The protocol tracks the parameter's **time-weighted arithmetic mean** since the prior commit, and reads use that mean. As more time elapses at the new value, its weight in the mean grows — so the effective value drifts asymptotically toward the new target along a `1/t`-shaped curve.

## The shape

The on-chain integrator (`Integrator::meanOf`) accumulates `area = Σ value_i · Δt_i` and returns `area / (now − head_stamp)`. For a single instantaneous step at commit time `t_s` (where the parameter jumps from prior value `θ₀` to new target `θ₁`), the effective mean at time `t` is:

$$
\bar{\theta}(t) \;=\; \theta_1 \;-\; \frac{(\theta_1 - \theta_0)\,(t_s - t_0)}{t - t_0}
$$

where `t_0` is the *prior* commit timestamp (the start of the integrator's window). The fraction `(t_s − t_0) / (t − t_0)` is the residual weight of the pre-commit history; it shrinks as `t` grows, so $\bar{\theta}(t) \to \theta_1$ asymptotically.

This is the formula proved in the protocol whitepaper (`paper/001.banq-pro/banq-pro.tex:256-258`) and re-derived in the theory paper (`paper/004.banq-mtp/banq-mtp.tex:85`).

In plain language: the parameter's effective value is a running average over its entire history, weighted by how long each segment held. A fresh commit slowly displaces the old value at a `1/t` rate.

## Why a time-weighted mean?

A snap-change would let governance — or a leaked admin key — produce a single-block step in any parameter. Bots watching commit transactions could front-run by an entire block. The time-weighted mean removes that incentive: there is no single block where the parameter "becomes" the new value; the change leaks in continuously.

The shape also has a useful tail behaviour: even long after the new value has converged for practical purposes, the integrator keeps drifting toward it, so there is no discontinuity at any "cycle boundary".

## Practical interpretation

The effective value's distance from the new target falls as `(t_s − t_0) / (t − t_0)`. Roughly, with a prior commit `t_s − t_0` in the past equal to one "history slice" `Δ`, the residual gap after time `Δ_new` of elapsed time at the new value is `Δ / (Δ + Δ_new)`.

Concrete example: suppose the prior commit was 30 days before the new one (`t_s − t_0 = 30 days`). Then for a 2× change scheduled at `t_s`:

- Right at `t = t_s`: residual gap = 100%, effective value is still θ₀.
- 30 days later (`Δ_new = 30 d`): residual = 30/60 = 50%; effective value is halfway.
- 90 days later (`Δ_new = 90 d`): residual = 30/120 = 25%; effective value is 75% of the way.
- 270 days later (`Δ_new = 270 d`): residual = 30/300 = 10%; effective value is 90% of the way.

So the convergence speed depends on the *prior* commit's age. If governance has been quiet for a long time, a new commit drifts in slowly; if changes have been frequent, each new commit takes effect faster.

## Why not just instant changes within bounds?

The lethargic bound (0.5×–2×) limits the *magnitude* of any one cycle's change. The time-weighted mean limits its *immediacy*.

Without the mean, an approved 2× change would take effect in the next block. Sophisticated actors with bots watching governance proposals could front-run the change. The asymptotic mean removes that incentive — there is no single block where the change "happens".

This is the same reasoning that motivated the rate-limit (one change per `MONTH` per parameter) in the first place: governance shouldn't create exploitable single-block shifts.

## Where to go next

- [Parameter bounds](/features/lethargic-governance/parameter-bounds) — the multiplicative bounds on each cycle's change
- [Role hierarchy](/features/lethargic-governance/role-hierarchy) — who can propose changes
- [Governance overview](/governance/overview) — the full process
