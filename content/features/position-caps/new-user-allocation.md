# New user allocation

A fresh address joining a small pool has a meaningful initial cap. The protocol explicitly avoids "cold-start lockout" where new participants can't get in.

## The first-operation math

The cap formula is `C_max · 12λ(1−λ)² / √(n+2)` where:

- **λ** is the share the deposit would represent (`balanceOf(user) / totalSupply()` after the operation).
- **n** is the protocol-wide `largeHolders()` count: addresses currently holding at least one whole token unit, floored at the governance parameter `MIN_HOLDERS_ID` (`Position.largeHolders()` returns the max of the two). It is *not* a per-user counter. `MIN_HOLDERS_ID` is unset at construction (default `0`), so in a fresh pool `n` starts at the live holder count (zero at genesis) until governance raises the parameter; `Constant.MIN_HOLDERS` (1e18) is the governance *ceiling*, not a default.

So for a brand-new pool just past genesis at default parameters, `n = 0` and the cap divisor is `√(0 + 2)`. If governance raises `MIN_HOLDERS_ID` above the live count, `n` is floored at that value instead. As real depositors arrive and the live holder count rises above the floor, `n` grows accordingly.

For a brand-new user joining a pool where `n` is still at its floor, the first-operation cap is:

$$
\text{cap}_{\text{first}} = C_{\max} \cdot \frac{12 \lambda (1-\lambda)^2}{\sqrt{\text{MIN\_HOLDERS\_ID} + 2}}
$$

The cap is *self-consistent* — the protocol solves for the maximum `λ` such that the cap function evaluated at that `λ` permits the deposit. At default parameters and a near-empty pool, a brand-new user can deposit a meaningful share (well below the 1/3 peak of the beta function); the exact percentage depends on `C_max` (`CAP_ID`, see [position-parameters](/parameters/position-parameters)) and `MIN_HOLDERS_ID`.

## Cap floor

In addition to the formula, the protocol sets an **absolute cap** — the `CAP_ID` parameter on the position — that caps any single user's mint room regardless of pool state. The floor ensures a small new user can always make a meaningful first deposit, even into a deep pool.

The default `CAP_ID` is configured per-pool. Governance can adjust this within the standard lethargic bounds (0.5×–2× per `MONTH`).

## What this means for adoption

- **The very first user of a new pool** can deposit aggressively — the pool is empty, so `λ` can grow large and `n` is still at the `MIN_HOLDERS_ID` floor.
- **Early users in a small pool** also have generous caps relative to the pool size — `n` is still low.
- **New users in a large established pool** face a `√(n+2)` divisor that's tightened by every existing large holder. The absolute `CAP_ID` then dominates.

## What this doesn't allow

- A fresh address can't deposit more than 1/3 of the pool in a single operation, regardless of capital — that's the peak of the `12λ(1−λ)²` factor.
- An attacker can't bypass the cap with a flash loan: the cap is computed on the post-deposit state, including the flash-loan amount.
- Cycling deposits and withdrawals doesn't help — `n` only ticks down when a holder's balance drops below the unit threshold, not when they withdraw to a still-positive balance.

## Where to go next

- [How caps grow](/features/position-caps/how-caps-grow) — the dynamics of subsequent operations
- [Position parameters](/parameters/position-parameters) — the `CAP_ID` and `MIN_HOLDERS_ID` defaults
