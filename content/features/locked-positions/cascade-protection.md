# Cascade protection

This is the systemic argument for locking. Locked positions don't just earn you a bonus — they protect everyone in the pool from liquidation cascades. Whether they protect *you* depends on aggregate adoption, which is a coordination game.

![Cascade attenuation](../../diagrams/cascade-attenuation.svg)

## What's a cascade?

A liquidation cascade is the feedback loop:

1. Prices drop. Some borrowers' health factors fall below 100%.
2. Liquidators clear those positions, taking collateral.
3. Liquidators sell the collateral on the open market for stablecoins.
4. The selling pressure pushes prices lower.
5. *More* borrowers' positions become underwater.
6. Loop.

Cascades have been responsible for the largest losses in DeFi history — March 2020's "Black Thursday" cost MakerDAO **$8.3M (USD)** in bad debt; numerous other protocols have lost large amounts in similar circumstances.

## How locks attenuate the loop

Locked supply can't be redeemed for the underlying asset. When a locked position is liquidated, the position tokens transfer to the liquidator — but the underlying tokens stay in the vault.

This breaks step 3 of the loop. The liquidator can hold the locked tokens until expiry, or sell them at a discount on the secondary market — but they can't immediately dump them on the spot market. The selling pressure that drives the cascade is bounded by the **unlocked fraction** of the pool.

The protocol formalises this as the **Cascade Attenuation Theorem**:

> In a pool where fraction ϕ of supply positions are permanently locked, the maximum cascade amplification factor is bounded by (1 − ϕ).

So:

- 0% locked → cascade unaffected (same as traditional protocols).
- 50% locked → cascade depth halved.
- 100% locked → cascade essentially eliminated.

## Simulation results

The whitepaper simulates 1,000 borrowers under different lock fractions and price shocks. Selected results (linear price impact, k = 1.5×10⁻⁴):

| Price shock | 0% locked | 25% locked | 50% locked | 75% locked | 100% locked |
|---|---|---|---|---|---|
| 10% | 8.6% | 8.2% | 7.8% | 7.8% | 7.4% |
| 15% | 19.8% | 16.5% | 14.4% | 13.5% | 12.7% |
| 20% | 36.5% | 30.6% | 26.7% | 22.4% | 19.8% |
| **25%** | **85.7%** | **55.8%** | **37.1%** | **33.3%** | **29.4%** |
| 30% | 99.1% | 84.9% | 61.2% | 47.9% | 38.6% |

The dramatic difference at the 25% shock — 85.7% vs 29.4% — illustrates the kind of regime change locks can create. Cascade dynamics are non-linear: a small attenuation can prevent the runaway loop.

## The coordination problem

Cascade protection is a **public good**. Locking your position protects the whole pool, including everyone who *didn't* lock. So why would you lock?

Three answers:

1. **The bonus.** Locked suppliers earn extra interest; locked borrowers pay less. The protocol pays you to provide the public good.
2. **Self-interest in stable markets.** Cascades hurt everyone with collateral exposure. Even from a purely selfish view, supporting cascade protection is rational if the bonus exceeds the discount cost.
3. **Counter-cyclical equilibrium.** When utilization is high (and cascade risk is highest), the bonus is most attractive. Lock adoption rises naturally during periods when it matters most.

## What governance can and can't do

Governance can adjust the bonus (LOCK_BONUS) and the malus (LOCK_MALUS), within the constraint that both are bounded by the spread `s`. Increasing the bonus encourages more locking but reduces protocol margin.

Governance **cannot** force users to lock. The mechanism is purely incentive-based.

Governance also cannot force-unlock anyone — locks are credible commitments, not parameters that can be retroactively changed.

## What it doesn't fix

Three caveats:

1. **Cascades among unlocked positions still happen.** The (1 − ϕ) bound applies to the *unlocked fraction*. If 20% of the pool is locked and 80% is unlocked, cascade dynamics among that 80% are unchanged.
2. **Adoption is not guaranteed.** The Nash equilibrium analysis identifies *two* self-reinforcing equilibrium regions — low adoption (locked fraction `< 15%`) and high adoption (`> 40%`) — with selection depending on path. A protocol that bootstraps poorly may stay in the low equilibrium.
3. **Locked supply tokens received in liquidation create their own headache for liquidators.** A liquidator who absorbs a fully-locked victim adds debt without gaining redeemable collateral. This may slow the rate of liquidation, which is desirable for cascade protection but reduces keeper economics. See [For keepers](/for-keepers/overview).

## Where to go next

- [Bonus and malus](/features/locked-positions/bonus-and-malus) — what the protocol pays you to lock
- [Theory & proofs](/research/papers/theory-and-proofs) — the formal analysis of the equilibrium
- [Liquidation risk](/risks/liquidation-risk) — what cascade protection means for your individual position
