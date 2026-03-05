# Governance risk

Even with lethargic constraints, governance is a real attack surface.

## What an attacker could do

A successful attacker who compromises the right `_ADMIN_ROLE` holders can:

- **Push parameters slowly.** Each cycle moves a parameter by up to 2×. After 4 months, parameters are 16× from defaults.
- **Add malicious tokens** (`POOL_ENLIST_ROLE`) — subject to the enlistment delay.
- **Update oracle sources** (`FEED_ENLIST_ROLE`, `FEED_RETWAP_ROLE`) — slowly, within bounds and the enlistment delay.
- **Drain the protocol indirectly** by raising `WEIGHT_SUPPLY`, lowering `SPREAD`, attracting users to over-borrow, then crashing the oracle.

## What an attacker can't do

- **Single-block exploitation.** All changes are bounded per cycle.
- **Force-unlock positions.** Locks are credible commitments.
- **Bypass the per-cycle bounds.** These are encoded in the supervisory contracts.
- **Reset the position-cap holder count.** The `largeHolders()` count is a direct read of the population of addresses holding at least one whole token unit; there is no governance lever to clear it.

## The guard tier as defence

Each `_ADMIN_ROLE` has a matching `_GUARD_ROLE` whose only power is to `cancel(...)` a pending scheduled operation before its execution delay elapses. A guard cannot propose changes — only block them.

For this to work, the guard key for an action must be held *independently* from the admin key for the same action. If both `..._ADMIN_ROLE` and `..._GUARD_ROLE` for `POOL_CAP_SUPPLY` (say) are held by the same multisig, the guard provides no protection.

## What users should watch

- **Recent scheduled parameter changes.** If `WEIGHT_SUPPLY` is climbing every cycle without an obvious reason, that's a warning.
- **Role assignments.** Sudden grants of any `_ADMIN_ROLE` to unfamiliar addresses are concerning. `banq acma logs` makes this auditable.
- **Communications.** A protocol that announces and explains changes is healthier than one that doesn't.

## Mitigations as a user

- **Match your time horizon to the cycle length.** If you're committed for years, monitor governance quarterly. If you're using the protocol tactically, stay close.
- **Don't ignore alerts.** Most off-chain monitoring services include governance event tracking.
- **Have an exit plan.** Know how you'd respond to a parameter change you don't like.

## Where to go next

- [Lethargic governance](/features/lethargic-governance/overview) — the bounds
- [Role hierarchy](/features/lethargic-governance/role-hierarchy) — who can do what
- [Emergency procedures](/governance/emergency-procedures) — what happens in a crisis
