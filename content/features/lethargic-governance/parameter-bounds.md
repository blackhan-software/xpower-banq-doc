# Parameter bounds

Every governable parameter in XPower Banq has two kinds of bounds: **absolute bounds** (hard limits enforced by the supervisory contract) and **per-cycle multiplicative bounds** (the lethargic constraint).

## Absolute bounds

These are encoded into the supervisory contracts (`PoolSupervised`, `PositionSupervised`, `OracleSupervised`, `VaultSupervised`) and cannot be changed by governance. They define the universe of valid parameter values.

| Parameter | Min | Max | Default | Notes |
|---|---|---|---|---|
| `WEIGHT_SUPPLY` | 0 | 255 | 170 | Supply-side weight (per token); `170/255 ≈ 66.67%` LTV |
| `WEIGHT_BORROW` | 0 | 255 | 255 | Borrow-side weight (per token) |
| `BASE` | 0% | 50% | 0% | Base risk premium (flat lift on the kinked curve) |
| `SPREAD` | 0% | 50% | 10% | Half-width interest spread |
| `UTIL` | 0% | &lt;100% | 90% | Target utilisation |
| `RATE` | 0% | &lt;100% | 10% | Target rate at `UTIL` |
| `LOCK_BONUS` | 0% | `SPREAD` | 10% | Max supply bonus on full lock |
| `LOCK_MALUS` | 0% | `SPREAD` | 10% | Max borrow malus on full lock |
| `FEE_ENTRY` | 0% | 50% | 0.1% | One-shot deposit fee |
| `FEE_EXIT` | 0% | 50% | 0.1% | One-shot redemption fee |
| `POL_FETCHABLE_SHARE` | 0% | 100% | 0% | Max share of the POL surplus extractable by governance |
| `DECAY` | 0.5 | 1.0 | 0.944 | Oracle EWMA decay (`α`) |
| `LIMIT` | 1 second | 1 day | 1 hour | Oracle refresh interval |
| `DELAY` | 1 week | 3 months | 14 days | Feed-enlist delay |

The bounds for `LOCK_BONUS` and `LOCK_MALUS` against `SPREAD` are dynamic — the supervisor refuses any new `SPREAD` value below either the bonus or the malus.

## Per-cycle multiplicative bounds

Within a single governance cycle, each parameter can change by at most a factor of 2× (and at least a factor of 0.5×). Repeated cycles can compound, but each individual change is bounded.

The general form, where `θ₀` is the prior parameter value and `θ₁` the proposed:

$$
\frac{1}{2} \cdot \theta_0 \;\leq\; \theta_1 \;\leq\; 2 \cdot \theta_0
$$

So:

- `WEIGHT_SUPPLY = 170` can be moved to anywhere between 85 and 255 (capped at the absolute max) in one cycle — i.e. effective LTV between roughly 33% and 100%.
- `SPREAD = 10%` can be moved to anywhere between 5% and 20% in one cycle.
- A larger move requires multiple cycles.

## How long a "big" change takes

| Multiplier | Cycles needed | Time at 1-month cycles |
|---|---|---|
| 2× | 1 | 1 month |
| 4× | 2 | 2 months |
| 10× | 4 | 4 months |
| 32× | 5 | 5 months |
| 64× | 6 | 6 months |

The arithmetic: ⌈log₂(M)⌉ cycles to compound to a multiplier M. The supervisor verifies these bounds inside the contract, so a malicious or compromised governor cannot bypass them.

## Where to go next

- [Transition curves](/features/lethargic-governance/transition-curves) — how each approved change is phased in
- [Parameter catalog](/governance/parameter-catalog) — the full list of governable parameters
- [Change-rate constraints](/parameters/change-rate-constraints) — the implementation of these bounds
