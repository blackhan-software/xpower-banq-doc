# Proposing changes

The on-chain process for changing a governable parameter.

## The flow

The supervisory contracts (`PoolSupervised`, `PositionSupervised`, `OracleSupervised`, `VaultSupervised`) implement parameter changes via a *target* mechanism: a parameter has a current effective value plus a *scheduled target* with a timestamp.

1. **Schedule.** A holder of the matching `_SET_TARGET_ROLE` (or `_TMP_TARGET_ROLE` for short-window overrides) calls the access-managed setter on the supervised contract via Acma. Acma applies its execution-delay timer.
2. **Verify bounds.** The supervisor checks the new value against absolute bounds (e.g. `SPREAD ≤ 50%`) and the per-cycle multiplicative bounds (≤ 2× / ≥ 0.5×).
3. **Verify rate limit.** The supervisor checks this parameter hasn't already moved within the current cycle.
4. **Wait out the delay.** During the Acma execution-delay window, a `_GUARD_ROLE` holder may `cancel(...)` the scheduled change.
5. **Execute.** When the delay elapses, anyone may call `execute(...)`. The asymptotic transition begins from the prior value to the scheduled target.
6. **Cycle ends.** At cycle end, the new value is fully effective. The next scheduling for the same parameter can move it again.

## What "the cycle" means

The cycle is the rate-limit window. By default it's `Constant.MONTH` = `YEAR / 12` ≈ **30.44 days**. A given parameter can change at most once per cycle.

The cycle is *per parameter*, not global. So you can change `WEIGHT_SUPPLY` in one cycle and `SPREAD` in another, with their cycles overlapping.

## Approval at the multisig / DAO level

The on-chain process described above is the *enforcement* layer. Above it sits whatever approval mechanism the `_ADMIN_ROLE` holders use — multisig signatures, DAO vote, etc. The protocol doesn't dictate this.

In practice:

- At launch, the relevant `_ADMIN_ROLE`s are held by a multisig (`BOSS`). Proposals are off-chain coordination → on-chain `schedule(...)` call.
- As the protocol matures, those admin roles will likely be re-assigned to a DAO contract with on-chain voting.

## Frontrunning

Because changes follow the asymptotic transition, there's no "single block" where the change happens. So frontrunning a proposal doesn't yield exploitable arbitrage.

The transition starts the moment the scheduled change executes. By the time observers can react, the change has already begun. But the magnitude is bounded — they can't react after the cycle ends, when ~95% of the change is done.

## Where to go next

- [Parameter catalog](/governance/parameter-catalog) — what's governable
- [Role hierarchy](/features/lethargic-governance/role-hierarchy) — who can do what
- [CLI and tools](/for-keepers/cli-and-tools) — `banq acma` for live inspection
