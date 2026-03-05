---
outline: 2
---

# Threat model

A single-page attacker-centric view: what classes of attack the protocol assumes, what the contracts do to defend against each, and what is *not* defended at the contract level. Every entry cites the actual Solidity that implements the defence (or notes its absence).

The complementary [Defensive mechanisms](/security/defensive-mechanisms) page lists the same primitives organised by *defence*; this page organises them by *attack*.

## Attacker assumptions

The contracts assume the attacker can:

- Submit any transaction the EVM allows, including reverting bundles, flash loans, and `tx.origin` spoofing via contract intermediaries.
- Hold any mix of supply and borrow positions, including across many EOAs.
- Move external AMM prices arbitrarily within a block, subject only to capital cost.
- Observe the mempool and front-run any transaction not protected by ordering-resistant mechanisms.
- Compromise *one* role tier at a time. The defences degrade gracefully when an admin is compromised but fail when both `_ADMIN_ROLE` and matching `_GUARD_ROLE` are held by the same key.

The contracts do *not* assume the attacker can break ECDSA, hash collisions, or the underlying L1 consensus.

## Threats and defences

Each entry names a threat, the concrete attack it represents, the on-chain defence (with the contract code that implements it), and the residual risk that remains.

### T1. Single-block oracle manipulation

- **Attack.** Move an AMM price within one block via flash loan, then liquidate or borrow at the manipulated price.
- **Defence.** `LIMIT` rate-limit on `Oracle.refresh` blocks two updates within the same window (`OracleSupervised` `LIMIT_ID`); log-space TWAP averages over the EMA half-life so a single observation cannot dominate (`TWAP` `mean = (mean × decay + last × (1−decay))`).
- **Residual risk.** Sustained multi-block manipulation can still drift the TWAP — see [oracle staleness](/risks/oracle-staleness).

### T2. Multi-block / sustained TWAP manipulation

- **Attack.** Hold an external AMM at a wrong price across many blocks until the EMA tracks it.
- **Defence.** Bidirectional geomean spread auto-widens when one side becomes thin (`Oracle._relOf`); EMA half-life makes 90% deviation cost ~40 hours of capital at the default `DECAY = 0.944`.
- **Residual risk.** Capital-rich attacker with sustained price control still wins eventually; mitigation is governance — narrow `LIMIT`, raise `DECAY`.

### T3. Flash-loan-funded liquidation spam

- **Attack.** Spam `liquidate()` with cheap debt to harvest victims at the boundary.
- **Defence.** `Pool.liquidate(victim, partial_exp)` is `powlimited(liquidateDifficultyOf(partial_exp))` — every call must satisfy a PoW puzzle whose difficulty is governance-set per `partial_exp` value (`POW_SQUARE_ID(partial_exp)`); `keccak256(blockHash, tx.origin, msg.data)` is the puzzle key (`PowLimited`).
- **Residual risk.** None at the contract level if governance sets `POW_SQUARE = 0`; that is the operator's call.

### T4. Liquidator over-extraction

- **Attack.** A privileged liquidator drains an unhealthy position in one shot.
- **Defence.** Liquidations are *partial* by construction — `_square` shifts the seized amount by `partial_exp` (`borrowed >> partial_exp`, `supplied >> partial_exp` in `Pool`), capping each call's bite at $2^{-\text{partial\_exp}}$ of the position.
- **Residual risk.** Repeated calls within the same block can still close most of the position; `partial_exp = 1` slices 50% per call. Combine with PoW gating to bound total work.

### T5. Self-liquidation under leverage to drain

- **Attack.** Liquidate yourself or a controlled address to extract the protocol's collateral.
- **Defence.** `_square` requires `user == msg.sender || address(this) == msg.sender` (`Pool`); after seizure, `_checkHealth(user)` reverts if the *liquidator* would itself become unhealthy (`Pool`).
- **Residual risk.** A solvent attacker with two accounts can still chain liquidations along a price gradient — bounded by partial-exp slicing and the post-liquidation health check.

### T6. Reentrancy via callback tokens or hooks

- **Attack.** A token's `transfer` hook re-enters `Pool.supply` mid-state-update.
- **Defence.** `Pool` inherits `ReentrancyGuardTransient`; `square` is explicitly `nonReentrant`; transient-storage guard so reentry across the same call tree reverts.
- **Residual risk.** Cross-contract reentry via custom token hooks remains a class-of-bug to watch for in audits.

### T7. Sudden parameter swing by compromised governance

- **Attack.** Set `WEIGHT_BORROW = 0` to instantly liquidate everyone, or `SPREAD = 50%` to drain.
- **Defence.** `Parameterized._setTargetIf` rejects `value > 2 × old_value` and `value < 0.5 × old_value`; `limited(Constant.MONTH, ...)` rejects a second change to the same id within ~30 days; transitions are time-weighted via `Integrator` so the new value phases in asymptotically.
- **Residual risk.** A patient attacker can compound 2× per cycle — 16× in 4 cycles, 256× in 8. The `_GUARD_ROLE` `cancel(...)` is the next layer (see T8).

### T8. Compromised admin pushes malicious change

- **Attack.** A captured `_ADMIN_ROLE` schedules a parameter or role grant that benefits the attacker.
- **Defence.** The matching `_GUARD_ROLE` can `cancel(...)` any pending operation during its execution-delay window (the OpenZeppelin `AccessManager` delay path); guard cannot itself propose, only block.
- **Residual risk.** Defence collapses if `_ADMIN` and `_GUARD` for the same action are held by the same multisig — see [governance risk](/risks/governance-risk).

### T9. Front-running a parameter change

- **Attack.** Read `Pending` events and trade against the upcoming setting.
- **Defence.** The asymptotic transition (`Integrator`) means there is no single block at which the change "happens"; effective value moves continuously over the cycle. Reactive trading captures only the residual delta after the move begins.
- **Residual risk.** Effective value is still observable and predictable; mitigation is "no surprise" governance, not on-chain hiding.

### T10. Sybil capacity grab

- **Attack.** Spawn many EOAs to acquire per-account caps and corner a pool.
- **Defence.** Cap function is `12λ(1−λ)²` (peaks at λ = 1/3, vanishes at boundaries) divided by `√(largeHolders + 2)` (`Position`); creating accounts increases the divisor and shrinks every Sybil's share.
- **Residual risk.** This is *rate*-limiting, not prevention. With unlimited time the Sybil still acquires; mitigation is the iteration cap (`MIN_HOLDERS`) and the time cost of accumulating.

### T11. Hot-swap of a malicious price feed

- **Attack.** Enlist a controlled feed contract just before liquidating.
- **Defence.** `Oracle` enlistment goes through the `Delayed` modifier with `DELAY_ID` ranging from 1 week to 3 months (`OracleSupervised`); two-phase commit — first call schedules, second call after the delay completes the enlistment.
- **Residual risk.** Mitigation only works if the delay is observed by a watchful guard; a sleeping guard plus an enlistment older than the delay is still exploitable.

### T12. Forced unlock / locked-position liquidation

- **Attack.** Liquidate the locked portion of a victim to bypass cascade attenuation.
- **Defence.** `Position._burn` requires `totalOf(user) >= lockTotalOf(user)`, so locked principal cannot be reduced by transfer or liquidation. Locked tokens act as circuit breakers — see [cascade protection](/features/locked-positions/cascade-protection).
- **Residual risk.** Locks reduce the *redeemable* float during a crash; they don't add capital. They are a cascade dampener, not solvency insurance.

### T13. PoW solution replay

- **Attack.** Reuse another caller's PoW solution in your own liquidation.
- **Defence.** The puzzle key includes `tx.origin` and `msg.data` (`PowLimited`), so a solution found by one address with one call payload doesn't validate for another.
- **Residual risk.** A user calling through a contract loses its `tx.origin` advantage to the EOA; this is by design.

### T14. MEV / sandwich on user operations

- **Attack.** Bracket a `supply` or `redeem` to extract slippage.
- **Defence.** The protocol does not run an AMM; user operations are at quoted oracle prices and are not subject to AMM-slippage extraction. Liquidations are by `partial_exp`-shifted amounts, not market-priced sales.
- **Residual risk.** Off-chain MEV (private orderflow, reordering) is not mitigated by the contracts. Users on permissioned mempools or via builder-protected RPCs reduce exposure.

### T15. Cross-collateral correlation crash

- **Attack.** A correlated multi-asset crash (e.g. all stablecoins depeg together) bypasses per-pool risk.
- **Defence.** Each pool's parameters are independent; there is no on-chain correlation modelling. Bad-debt analysis assumes worst-case concurrent crashes — see [bad debt scenarios](/risks/bad-debt-scenarios) and the [simulations paper](/research/papers/simulations).
- **Residual risk.** Real risk; mitigated only by parameter conservatism (low `WEIGHT_SUPPLY/WEIGHT_BORROW`, slow `DECAY`) and by users diversifying across pools.

### T16. Smart-contract bug

- **Attack.** Logic error, integer-handling bug, or invariant violation that the test suite missed.
- **Defence.** Internal Foundry test suite covers the core operations; PRBMath used for transcendental functions; `Saturator` for clamped arithmetic; log-space index avoids the truncation-bias path.
- **Residual risk.** No formal verification yet; no external audit yet — see [audits and reviews](/security/audits-and-reviews). This is the largest residual risk.

## What is explicitly *not* defended at the contract level

These are out of scope for the on-chain code; they are addressed (or not) at the operational layer.

- **Governance key compromise.** The contracts assume key holders are trusted and that the admin/guard split is enforced off-chain (multisig with disjoint signer sets, ideally hardware-isolated).
- **Off-chain MEV** (private orderflow, builder collusion). Mitigated by user choice of RPC / mempool, not by the contracts.
- **Social engineering** of governance. Out of scope.
- **Bridge / cross-chain custody.** Not in this protocol's scope; cross-chain risk is the bridge's risk.
- **Oracle source liveness.** If TraderJoe or Chainlink stops publishing, `Oracle.refresh` cannot run; positions become stale. Mitigated by `LIMIT` (the rate-limit floor still allows manual refresh) and by governance enlisting alternative feeds — but not by the contract acting alone.
- **Protocol-margin compression at full lock adoption.** When every position is locked, the protocol earns no spread on flow. This is an *economic* failure mode, not a security failure — see [secondary market risk](/risks/secondary-market-risk).

## Where to go next

- [Defensive mechanisms](/security/defensive-mechanisms) — the same list organised by defence, with code references
- [Audits and reviews](/security/audits-and-reviews) — current external review status
- [Risks](/risks/overview) — user-facing economic risk catalogue
- [Role hierarchy](/features/lethargic-governance/role-hierarchy) — the three-tier access control that backs T7 / T8 / T11
