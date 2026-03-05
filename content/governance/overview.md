# Governance overview

XPower Banq's governance model is conservative by design. Parameter changes are **bounded multiplicatively** to ≤ 2× per cycle, **phased in asymptotically** rather than instantly, and **rate-limited** to one change per cycle per parameter.

The aim is to make governance attacks slow and expensive rather than impossible — and to give users predictable time to react to legitimate changes.

## The governance model

Three components:

1. **The Acma access-control system.** An OpenZeppelin `AccessManager` extended with the protocol's role IDs. Every privileged action has three companion roles: a base verb (caller), an `_ADMIN_ROLE` (grants/revokes the base role and tunes its delay), and a `_GUARD_ROLE` (cancels pending operations). See [Role hierarchy](/features/lethargic-governance/role-hierarchy).
2. **The lethargic transition logic.** Bounds and phases in parameter changes via the supervisory contracts (`PoolSupervised`, `PositionSupervised`, `OracleSupervised`, `VaultSupervised`).
3. **A governance interface.** Currently a multisig at launch (`BOSS = 0x5630…03c3`); transitioning to a DAO over time.

## Subsections

- **[Parameter catalog](/governance/parameter-catalog)** — every governable parameter with default, range, and rate limit
- **[Proposing changes](/governance/proposing-changes)** — how a parameter change is made
- **[Role management](/governance/role-management)** — granting and revoking roles
- **[Emergency procedures](/governance/emergency-procedures)** — what happens in a crisis

## What governance can change

- **Pool parameters (per token)**: `WEIGHT_SUPPLY` / `WEIGHT_BORROW` (which together determine effective LTV), `MAX/MIN_SUPPLY` and `MAX/MIN_BORROW` rate-limits, `POW_SUPPLY` / `POW_BORROW` / `POW_SQUARE` PoW difficulties.
- **Position parameters**: `CAP`, `UTIL`, `RATE`, `SPREAD`, `LOCK_BONUS`, `LOCK_MALUS`, `MIN_HOLDERS`.
- **Vault parameters**: `FEE_ENTRY`, `FEE_EXIT`.
- **Oracle parameters**: `DECAY`, `LIMIT`, `LEVEL`, `DELAY`.
- **Role assignments**: by the matching `_ADMIN_ROLE` for each base role.
- **Pool / feed enlistment**: adding new tokens (`POOL_ENLIST_ROLE`) or new price sources (`FEED_ENLIST_ROLE`), each subject to a delay.

## What governance cannot change

- The lethargic constraints themselves (these are encoded in the supervisory contracts).
- The cascade attenuation theorem properties.
- The fact that locks are credible commitments (no force-unlock).
- The PoW puzzle structure for permissionless operations.
- Per-cycle multiplicative bounds (these are absolute).

## What governance attacks would look like

A successful attack on Banq governance would require:

1. **Compromising the right `_ADMIN_ROLE` holders** for the action being attacked.
2. **Sustaining control across many cycles** to push parameters far from defaults.
3. **Avoiding the matching `_GUARD_ROLE`** — which can cancel any pending change before its delay elapses.

Even a fully successful attack can't, in a single cycle, do more than a 2× parameter swing. A 64× swing requires 6 cycles, by which time the attack is highly visible.

## Where to go next

- [Parameter catalog](/governance/parameter-catalog)
- [Role hierarchy](/features/lethargic-governance/role-hierarchy)
- [Lethargic governance](/features/lethargic-governance/overview)
