# Debt-assumption liquidation

In most lending protocols, liquidating someone means *paying off their debt* with your own cash, in exchange for their discounted collateral. You need liquid stablecoins on hand. This concentrates liquidation revenue in a small number of well-capitalised firms.

XPower Banq inverts this. Liquidation is **debt assumption**: the liquidator takes on a slice of the victim's debt *and* their collateral atomically. They need collateral headroom in their own position — but no liquid capital.

![Debt assumption flow](../../diagrams/debt-assumption.svg)

## Why this matters

The traditional model has a structural problem: most users who can spot a liquidation opportunity can't act on it because they don't have stablecoins ready to deploy. The result is that liquidation is an oligopoly. Top-5 liquidators capture over 80% of value in established lending markets.

Debt assumption changes the entry requirement from "liquid stablecoins" to "any healthy collateral." That's a much wider pool of potential liquidators — anyone with a position on the protocol can participate.

The economics are equivalent. The liquidator still profits from the [implicit liquidation bonus](/concepts/liquidation) — up to 50% at the H = 100% boundary, set by the default weight ratio (255/170 − 1). What changes is the *capital they need to commit*: collateral instead of cash.

## How it works in one paragraph

When `Pool.liquidate(victim, partial_exp)` (public, PoW-gated) or `Pool.square(user, victim, partial_exp)` (role-restricted) is called against an underwater address:

1. The protocol takes a fraction `2^-partial_exp` of the victim's debt **and** the same fraction of their collateral. `partial_exp` is supplied by the caller — `1` for a 50% slice, `2` for 25%, and so on. There is no protocol-stored default.
2. Both transfer to the liquidator atomically.
3. The protocol verifies the liquidator's post-transfer health factor is ≥ 100%.
4. If the check passes, the operation completes. If not, it reverts.

There's no cash flow into or out of the protocol. The vault's underlying tokens don't move. Only ERC20 position tokens change hands.

Because the slice is uniform across debt and collateral, **the victim's health factor is preserved** by every partial liquidation (any `partial_exp ≥ 1`). The position shrinks but its H is unchanged, so it remains liquidatable until H recovers or until a `partial_exp = 0` call closes it entirely (at which point H is undefined). See [Liquidation](/concepts/liquidation).

## Two entry points

| Selector | Caller | Gating | Notes |
|---|---|---|---|
| `liquidate(victim, partial_exp)` | Anyone | PoW (difficulty from `POW_SQUARE`) **and** the pool must hold its own `POOL_SQUARE_ROLE` | Public path. Internally invokes `this.square(...)`, so `msg.sender` on the inner call is the pool itself. |
| `square(user, victim, partial_exp)` | Holder of that pool's `POOL_SQUARE_ROLE` | Role check (`restricted`) | Direct path. No PoW. |

Both selectors run the same debt-assumption logic and emit the same `Liquidate` event. The difference is gating.

Because `liquidate()` reaches `square()` with `msg.sender = address(this)`, the *pool address itself* must be in that pool's `POOL_SQUARE_ROLE` set for the permissionless path to work. This is the **per-pool** governance switch for the public path: granting the pool's `POOL_SQUARE_ROLE` to the pool turns permissionless liquidations on for that pool; revoking it turns them off without affecting direct `square()` calls by other role-holders. See [How liquidations work](/features/debt-assumption-liquidation/how-liquidations-work) and [PoW-gated public mode](/for-keepers/pow-gated-public-mode).

## What this enables

- **More distributed keepers.** A user with a healthy supply position can liquidate other users without acquiring liquid capital first.
- **Faster crash response.** During a market-wide crash, liquid capital becomes scarce and expensive. Debt assumption removes this bottleneck.
- **Lower barrier for monitoring.** Anyone watching the pool can be a liquidator candidate. This is good for decentralisation and for cascade protection (more eyes mean faster response).

## What this doesn't do

- **It doesn't make liquidation free.** The liquidator still ties up collateral capacity (their own headroom) when they assume debt. There's an opportunity cost.
- **It doesn't change the victim's outcome.** From your perspective as a borrower being liquidated, debt-assumption looks identical to traditional liquidation: a slice of your debt and collateral disappear, the liquidator profits from the bonus, and you're left with the rest.
- **It doesn't eliminate keeper centralisation.** Sophisticated keepers will still capture the majority of liquidation flow because they monitor more efficiently. The barrier is just lower.

## Locked positions in the picture

If the victim has a locked position, the liquidator inherits the lock proportionally. This complicates the keeper economics: locked supply they receive can't be immediately redeemed.

Two consequences:

1. **Liquidators prefer unlocked positions.** This creates de-facto liquidation seniority for locked positions during cascades.
2. **Keeper headroom requirements are larger.** A keeper absorbing a fully-locked position needs collateral headroom for the new debt without gaining redeemable collateral.

See [Cascade dynamics and keeper sizing](/research/papers/theory-and-proofs#cascade-dynamics-and-keeper-sizing) in the theory paper.

## Subsections

- **[How liquidations work](/features/debt-assumption-liquidation/how-liquidations-work)** — the call flow in detail
- **[For liquidators](/features/debt-assumption-liquidation/for-liquidators)** — running a keeper
