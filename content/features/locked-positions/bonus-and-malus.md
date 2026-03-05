# Bonus and malus

Locked positions adjust your effective interest rate. Suppliers earn a **bonus**; borrowers pay a **reduced rate** (the "malus" — meaning a smaller magnitude of interest, not a penalty). Both come out of the protocol's spread.

## The mechanism

The default protocol spread is **s = 10%**. This is the half-width applied symmetrically to the gross rate **R(U)** (the utilization-dependent rate — kinked curve plus base risk premium):

- Borrow rate = R(U) × (1 + s) = R(U) × 1.10
- Supply rate = U × R(U) × (1 − s) = U × R(U) × 0.90

The supply rate carries an extra utilization factor **U**: interest is only earned on the borrowed portion of the pool, so idle supply earns nothing (see [Interest rates](/concepts/interest-rates)).

When you lock, your effective spread shrinks by an amount proportional to your lock ratio λ:

- Locked supplier effective rate ≈ U × R(U) × (1 − s + s · λ)
- Locked borrower effective rate ≈ R(U) × (1 + s − s · λ)

At λ = 1 (fully locked), the spread compresses to zero: the borrow rate equals the gross rate `R(U)`, and the supply rate equals `U × R(U)`. The two sides do **not** converge to the same number — the supply side keeps its utilization scaling. The protocol earns nothing in spread.

## What is λ exactly?

λ is the **time-weighted lock ratio**. It accounts for both *how much* of your balance is locked and *how long* the locks remain.

The protocol uses an O(1) algorithm to compute a normalised commitment depth in token-equivalent units — see [Ring-buffer locks](/research/papers/ring-buffer-locks) if you want the details. For the user-facing intuition:

- A permanent lock of all your principal → λ = 1.
- A 1-quarter timed lock of all your principal → λ ≈ 1/16 (since the maximum horizon is 16 quarters).
- A 4-year timed lock of all your principal → λ ≈ 1.
- A permanent lock of half your principal → λ ≈ 0.5.

The bonus scales linearly with λ.

## Ceiling

The bonus is capped by governance parameters:

- **LOCK_BONUS** — maximum supply bonus (default = s = 10%)
- **LOCK_MALUS** — maximum borrow reduction (default = s = 10%)

Both are bounded above by the spread `s` *per parameter*. The protocol enforces this on-chain (the supervisor rejects any new `LOCK_BONUS`/`LOCK_MALUS` above `SPREAD`, and any new `SPREAD` below the existing bonus or malus) — it's not possible for governance to set a bonus larger than the spread itself.

As a corollary, the combined constraint `LOCK_BONUS + LOCK_MALUS ≤ 2s` holds whenever the per-parameter bounds hold. This isn't enforced as a separate `require`, but it's a theorem about the per-parameter constraints. The practical consequence: even at full lock and maximum bonus, the protocol's spread margin can compress to zero but never go negative — if everyone locks, the protocol simply earns no spread, it doesn't lose money.

## Worked example: locked supplier

Suppose:
- Pool utilization is 50%, gross rate R(U) is 5%.
- You supply 1,000 XPOW and lock it permanently.
- Default parameters: s = 10%, LOCK_BONUS = 10%.

Your effective supply rate at λ = 1:

```
rate = 50% × 5% × (1 - 0.10 + 0.10 × 1) = 0.5 × 5% × 1.00 = 2.50%
```

Compared to an unlocked supplier in the same pool:

```
rate = 50% × 5% × (1 - 0.10) = 0.5 × 5% × 0.90 = 2.25%
```

You earn an extra 25 bps annualised by locking permanently. Over a year on 1,000 XPOW, that's 2.5 XPOW — which sounds small but is meaningful at scale, especially if you're locked anyway for cascade-protection reasons. Note both rates are roughly half the gross rate R(U): the supply rate is scaled by utilization (50%), so it never approaches the full 5% regardless of lock state.

## Worked example: locked borrower

Suppose:
- Pool utilization is 95%, gross rate R(U) is 50% (post-kink).
- You borrow 1,000 XPOW and lock it for 4 years.
- Default parameters: s = 10%, LOCK_MALUS = 10%.

Your effective borrow rate at λ ≈ 1:

```
rate = 50% × (1 + 0.10 - 0.10 × 1) = 50% × 1.00 = 50.00%
```

Compared to an unlocked borrower:

```
rate = 50% × 1.10 = 55.00%
```

You save 500 bps annualised. On 1,000 XPOW, that's 50 XPOW/year — substantial.

## When the bonus matters most

The bonus is structurally most attractive at high utilization. From the [Nash equilibrium analysis](/research/papers/theory-and-proofs):

- Below 90% utilization: lock breakeven period is several years. Locking is marginal.
- 90–95% utilization: breakeven drops to ~3 years.
- 95–98% utilization: breakeven drops to under a year.
- Above 98%: breakeven drops to a few months.

This is by design: when the protocol most needs cascade protection (high utilization, stressed market), locking is most attractive. The mechanism is **counter-cyclical**.

## What about the protocol margin?

At full lock adoption (everyone locked, λ = 1 for all users), the protocol earns zero spread on locked positions. This is solvent — the protocol doesn't *lose* money — but it earns nothing.

In practice, full adoption is unlikely. Realistic equilibria are 10–20% lock adoption in calm markets, 40–70% in stressed markets, with the protocol margin landing in the 8–18% range of base interest. See [the theory paper](/research/papers/theory-and-proofs) for the analysis.

## Where to go next

- [Cascade protection](/features/locked-positions/cascade-protection) — the systemic benefit you pay for with your lock
- [Locking positions](/using-the-protocol/locking-positions) — how to lock in the app
- [Position parameters](/parameters/position-parameters) — LOCK_BONUS, LOCK_MALUS, SPREAD defaults
