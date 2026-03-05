# Emergency procedures

What happens when something goes wrong, and what governance can and can't do about it.

## The guard tier as circuit breaker

For every privileged action there is a matching `_GUARD_ROLE`. A guard can call `Acma.cancel(...)` against a pending scheduled operation, reverting the change before its execution delay elapses.

Use cases:

- A miscalibrated parameter change scheduled by an admin.
- A change scheduled by a compromised admin.
- A change whose effects in practice differ unexpectedly from analysis.

Guards cannot *propose* changes — only block them. Once a scheduled change has executed (the delay elapsed and `execute(...)` was called), the guard window has closed.

## What governance cannot do in an emergency

- **Force-unlock locked positions.** Locks are credible commitments.
- **Halt role-holder liquidations.** `square()` cannot be blocked for an address that already holds a pool's `POOL_SQUARE_ROLE` short of revoking that address's role, which itself is subject to the normal execution delay.
- **Drain the protocol.** Even with full role capture, governance can't access user funds directly.
- **Push parameters past the per-cycle bound.** A single emergency change is still capped at 2× / 0.5×.

## What governance can do

- **Cancel a pending scheduled change** (`_GUARD_ROLE`).
- **Enable or disable the permissionless liquidation path (per pool).** `Pool.liquidate(...)` internally invokes `this.square(...)`, where `msg.sender` is the pool itself. The public path therefore works **only when that pool address holds its own `POOL_SQUARE_ROLE`**. Granting that role to the pool turns permissionless liquidations on for that pool; revoking it turns them off (subject to the standard role-execution delay). The role-restricted `square()` path is unaffected — keepers holding the pool's `POOL_SQUARE_ROLE` directly can still liquidate.
- **Lower a PoW difficulty** (e.g. `POW_SQUARE`) to make the permissionless path cheaper when it is enabled.
- **Tighten the supply/borrow weights** to reduce systemic risk during stress (within the per-cycle bound).
- **Shorten an enlistment delay** for an emergency feed swap (`FEED_SET_TARGET_ADMIN_ROLE`).

## Stress checklist

A rough playbook for the protocol's role-holders facing an emergency:

1. **Assess.** What's broken? Smart-contract bug? Oracle anomaly? Market crash?
2. **Cancel pending changes.** If a parameter change is in flight that may worsen the situation, the matching guard should `cancel(...)`.
3. **Tighten parameters.** If market stress, schedule conservative parameter changes (reduce `WEIGHT_SUPPLY`, raise `SPREAD`) — they'll phase in subject to the per-cycle bound.
4. **Communicate.** Public announcement, status page updates.
5. **Coordinate keepers.** If liquidations are bottlenecked in a pool, either grant that pool's `POOL_SQUARE_ROLE` to additional keeper addresses (or to the pool itself, to enable the permissionless `liquidate()` path) or — if the permissionless path is already enabled — lower `POW_SQUARE` to cheapen it. Conversely, if permissionless `liquidate()` is being abused, revoke the pool's `POOL_SQUARE_ROLE` from the pool address to switch that pool's public path off entirely.
6. **Document.** Post-mortem, parameter rollback plan if applicable.

The protocol's design philosophy — slow governance, credible commitments — means there's no "panic button" that makes everything OK. The right move is usually a combination of guard cancellations and slow tightening.

## Where to go next

- [Role management](/governance/role-management) — practical role admin
- [Risks → Governance risk](/risks/governance-risk) — what the threats look like
- [CLI and tools](/for-keepers/cli-and-tools) — `banq acma` for live inspection
