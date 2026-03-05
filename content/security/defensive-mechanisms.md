# Defensive mechanisms

A code-grounded catalogue of every protocol-level safety primitive in XPower Banq, with file references into the canonical Solidity source. Each row is the *defence*; the [Threat model](/security/threat-model) page maps these defences onto specific attack classes.

## At-a-glance

| Layer | Primitives |
|---|---|
| **Access control** | OpenZeppelin `AccessManager` via `Acma`; three-tier base / `_ADMIN` / `_GUARD` roles per action |
| **Rate-limit modifiers** | `powlimited`, `limited`, `delayed`, `nonReentrant` (transient) |
| **Lethargic governance** | 0.5×–2× per-cycle bound + `Constant.MONTH` rate-limit + asymptotic `Integrator` transition |
| **Oracle defences** | `LIMIT` rate-limit, log-space TWAP via EMA, bidirectional geomean spread, `DELAY` on feed enlistment |
| **Liquidation safety** | Public PoW-gated `liquidate()`, role-restricted `square()`, `partial_exp` slicing, post-liquidation health check |
| **Sybil rate-limit** | $12\lambda(1-\lambda)^2$ beta-cap divided by $\sqrt{n+2}$ holder count |
| **Lock circuit-breaker** | Ring-buffer + permanent-slot principal lock; `_burn` rejects below `lockTotalOf` |
| **Numerical correctness** | PRBMath UD60x18, log-space accrual, saturating arithmetic |

## Access control

**Where it lives.** The `Acma` contract; role IDs in the `Roles` library.

`Acma` extends OpenZeppelin's `AccessManager` and exposes role IDs derived as a 64-bit truncation of `keccak256(<verb>, <domain>, <pool-name>)` — the `uint64(bytes8(...))` of the concatenated triple. Roles are **scoped per pool**: `POOL_SQUARE_ROLE("P007")` and `POOL_SQUARE_ROLE("P000")` are different roles. Every privileged action has three roles:

- **Base role** — actually permits the call (e.g. `POOL_SQUARE_ROLE`, `FEED_RETWAP_ROLE`, `POOL_ENLIST_ROLE`, `SUPPLY_SET_TARGET_ROLE`).
- **`..._ADMIN_ROLE`** — can grant or revoke the base role and edit its parameters (e.g. its execution delay).
- **`..._GUARD_ROLE`** — can `cancel(...)` a pending scheduled operation during its delay window. Cannot itself propose changes.

Action verbs covered: `SET_TARGET`, `TMP_TARGET`, `CAP_SUPPLY`, `CAP_BORROW`, `TMP_SUPPLY`, `TMP_BORROW`, `ENLIST`, `ENWRAP`, `RETWAP`, `FETCH_POLS`, `SQUARE`, `RELATE`. The full mapping is in [role hierarchy](/features/lethargic-governance/role-hierarchy).

**What it defends.** T7 (sudden parameter swing), T8 (compromised admin), T11 (hot-swap of a feed).

**Caveat.** The split only protects the protocol when the `_ADMIN` and `_GUARD` keys for the *same* action are held by *different* parties. Co-located admin+guard keys collapse the defence — see [governance risk](/risks/governance-risk).

## Modifiers

**Where they live.** The `PowLimited`, `Limited`, `Delayed`, and `RateLimited` modifiers; `Pool` inherits all of them plus OpenZeppelin's `ReentrancyGuardTransient`.

### `powlimited(difficulty)` — proof-of-work gate

The `PowLimited` modifier computes `key = keccak256(blockHash, tx.origin, msg.data)` and reverts if `key.zeros() < difficulty` (where `zeros()` counts leading zero *bits*). The `blockHash` is cached per `_cacheTime` constructor argument; on `Oracle` it is 1 hour, so all callers solve against the same recent hash and there is a level playing field within the cache window.

`tx.origin` is part of the key, so a solution mined by one EOA does not validate for another. `msg.data` is part of the key, so the same solution does not work for two different `partial_exp` arguments to `liquidate`.

**Used by.** `Oracle.retwap` (with difficulty = `LEVEL`); `Pool.supply` / `borrow` (`POW_SUPPLY` / `POW_BORROW`); `Pool.liquidate` (`POW_SQUARE` per `partial_exp`).

### `limited(dt, key)` — one-shot rate-limit

The `Limited` modifier: the first call sets `_times[key] = block.timestamp + dt`; any second call before that timestamp reverts. After expiry the key is reset on next use. Used by `Parameterized.setTarget(id, ...)` with `dt = Constant.MONTH` to enforce *one parameter change per id per month*.

### `delayed(dt, key)` — two-phase commit

The `Delayed` modifier: first call records a future timestamp and emits `Pending(key, timestamp)` *without* executing the body; only a second call **after** the delay elapses runs the body. Used by `Oracle.enlist` with `DELAY` (1 week to 3 months) — gives observers a window to react before a new feed becomes live.

### `nonReentrant` (`Pool.square`)

OZ's transient-storage variant — the lock lives in EIP-1153 transient storage so it auto-clears at end of transaction without a storage write. Pool also inherits `ReentrancyGuardTransient` at the contract level, guarding all entry points.

**What they defend.** T1, T3 (PoW); T7 (Limited); T11 (Delayed); T6 (nonReentrant).

## Lethargic-governance bounds

**Where it lives.** The `Parameterized` governance contract for the bound check; the `Integrator` library for the asymptotic transition.

The `_setTargetIf` helper enforces three rules atomically:

1. **Multiplicative ceiling** — `value > old_value << 1` reverts with `TooLarge`. New value cannot exceed 2× the current effective value.
2. **Multiplicative floor** — `value < old_value >> 1` reverts with `TooSmall`. New value cannot fall below 0.5× the current.
3. **Cycle exclusivity** — combined with the `limited(MONTH, ...)` modifier on `setTarget`, the same id cannot be re-targeted within the cycle window (default 30 days).

Once accepted, the parameter does not jump. `Integrator` records (timestamp, value) tuples and `meanOf()` returns the time-weighted area integral divided by elapsed time, so the *effective* value walks asymptotically from the prior value to the new target across the cycle. Readers of the parameter (e.g. the IRM) consume this integrated mean, not the bare target.

**What it defends.** T7, T9, partially T8.

**Absolute caps** (per supervised contract):

- Pool weights `WEIGHT_SUPPLY`, `WEIGHT_BORROW` ∈ [0, 255] (`PoolSupervised`).
- Oracle `DECAY` ∈ [0.5e18, 1.0e18] (`OracleSupervised`).
- Position `SPREAD` ≤ 0.5e18; `RATE`, `UTIL` < 1.0e18 (`PositionSupervised`).
- Vault `FEE_ENTRY`, `FEE_EXIT` ≤ 0.5e18 (`VaultSupervised`).

These bound the worst case even after compounding 2× multiplicatively across cycles.

## Oracle defences

**Where it lives.** The `Oracle` contract, the `TWAP` library, and the supervised `Oracle` extension.

| Defence | Mechanism | Reference |
|---|---|---|
| **Refresh rate-limit (`LIMIT`)** | `Oracle.retwap` is `limited(LIMIT_ID, ...)` so two refreshes within the limit window revert | `Oracle`, `OracleSupervised` `LIMIT_ID` |
| **Log-space TWAP** | EMA in log₂ space: $\text{mean} = (\text{mean} \times \alpha + \text{last} \times (1-\alpha)) / 10^{18}$ — geometric mean of past observations | `TWAP` library |
| **Two-tick immunity** | `mean` only updates if the *new* observation has a strictly later timestamp than `last` (`utc_ > utcOf(last)`); a single block cannot move both `last` and `mean` | `TWAP` library |
| **Bidirectional geomean spread** | $\text{rel} = \log_2((s_{2t}+1)(s_{t2s}+1))/2$ — geometric mean of forward and reverse AMM spreads; widens automatically when one side becomes thin | `Oracle._relOf` |
| **Feed enlist delay (`DELAY`)** | Two-phase `delayed` enlist; 1 week to 3 months observable window before a new feed becomes live | `Oracle` enlist path; `OracleSupervised` `DELAY_ID` |
| **PoW on `retwap` (`LEVEL`)** | Permissionless callers must satisfy a leading-zero-bits puzzle | `Oracle`; difficulty from `LEVEL_ID` |

**What it defends.** T1, T2, T11.

## Liquidation safety

**Where it lives.** The `Pool` contract's liquidation path.

```solidity
function liquidate(address victim, uint8 partial_exp)
    external
    powlimited(liquidateDifficultyOf(partial_exp))
{
    this.square(msg.sender, victim, partial_exp); // if square-role!
}

function square(address user, address victim, uint8 partial_exp)
    external nonReentrant restricted
{ ... }
```

Five concentric defences:

1. **PoW gate on the public path.** `liquidate` is `powlimited(POW_SQUARE_ID(partial_exp))` — every call burns work. Difficulty is governance-set per `partial_exp`, so a 50% slice and a 25% slice can have different costs.
2. **Role-restricted internal path.** `square` is `restricted` (gated by the pool's per-pool `POOL_SQUARE_ROLE`) plus `nonReentrant`. The public `liquidate` calls `this.square(...)` so it crosses the access-control boundary on the role check — and because that internal hop is an external self-call, `msg.sender` on the inner call is the pool address, meaning the role check tests the **pool itself**. Granting that pool's `POOL_SQUARE_ROLE` to the pool enables the permissionless `liquidate()` path; revoking it disables that path (for that pool) while leaving direct `square()` calls by other role-holders unaffected. This is the per-pool governance switch for permissionless liquidations.
3. **Health pre-check.** `square` reverts `SufficientHealth` if `wnav_supply >= wnav_borrow`. Treats $H = 100\%$ as solvent; only strictly underwater positions can be liquidated.
4. **Partial slicing.** `_square` shifts the seized amount by `partial_exp`: `borrowed = borrowed_total >> partial_exp`, `supplied = supplied_total >> partial_exp`. Each call seizes at most $2^{-\text{partial\_exp}}$ of the position. There is no full-clear path.
5. **Liquidator post-check.** After all transfers, `_checkHealth(user)` runs on the *liquidator*. If they would themselves become unhealthy from absorbing the bad debt, the entire transaction reverts.

A sixth implicit defence: `_square` requires `user == msg.sender || address(this) == msg.sender`, so role-holders can liquidate only on their own behalf or via the trusted public path — they cannot front a third party.

**What it defends.** T3, T4, T5, T6.

## Lock circuit-breaker

**Where it lives.** The `Lock` library; balance check in the `Position` contract.

Locked principal is recorded in two storage shapes:

- **Ring-buffer** of 16 quarterly slots (`slots[user][i]` packs `epoch | value`). Each slot expires when its epoch passes; `free()` releases expired slots back to fungible balance.
- **Permanent slot** (`cache.perma`) for principal locked with `dt_term = type(uint256).max`. Never freed.

The Position's `_burn` path requires `totalOf(user) >= lockTotalOf(user)`, reverting with `Locked(user, total)` if the burn would dip below the locked floor. Liquidations route through `transferFrom` (not `_burn`), so locked principal is *unreachable* by liquidators — the locked share is a circuit-breaker against cascades.

This is the central result of the [cascade protection](/features/locked-positions/cascade-protection) page: a locked fraction $\phi$ scales cascade depth by $(1 - \phi)$, with formal proof in the [theory paper](/research/papers/theory-and-proofs).

**What it defends.** T12 (forced unlock), and indirectly the cascade dimension of T3 / T4.

## Sybil rate-limit

**Where it lives.** The `Position` contract (cap path).

Per-account capacity is the product of two factors:

1. **Beta-distributed cap** — $12\lambda(1-\lambda)^2$ where $\lambda = B/S$ (user balance / total supply). Peaks at $\lambda = 1/3$ and vanishes at the boundaries; concentrated holders can't keep adding.
2. **Holder-count divisor** — divide by $\sqrt{\text{largeHolders} + 2}$. As more accounts cross the `MIN_HOLDERS` threshold, every account's individual cap shrinks, including the Sybil's clones.

`MIN_HOLDERS` is governable (lethargic-bounded) up to `Constant.MIN_HOLDERS = 10^{18}` to prevent governance from collapsing the divisor. Together these make Sybil capacity-grabs *rate-limited* (not impossible — patient attackers can still accumulate).

**What it defends.** T10. Honest disclosure: this is rate-limiting, not prevention; see [position caps](/features/position-caps/overview).

## Numerical correctness

**Where it lives.** The `Calculator`, `Constant`, `Saturator`, `TWAP`, and `Lock` libraries.

- **PRBMath UD60x18** wraps `exp()`, `ln()`, `log2()`, `mul()` at WAD precision. `Calculator` adds the bias constant `LOG2_ONE` $= \log_2(10^{18})$ and exposes `Log2()` / `Exp2()` for the oracle path.
- **Log-space accrual.** The compounding index is stored as the *log* of the multiplicative index. Accrual is a single addition (`L += r`); per-user balance is recovered via `principal × exp(L − L_u)`. Truncation bias from repeated multiplication does not occur on the write path.
- **Saturating arithmetic.** `Saturator.add256/sub256/mul256` clamp to `type(uint256).max / min` instead of overflowing. Used by the lock depth accounting and the integrator area.
- **Constants.** The `Constant` library defines `RAY = 10^{27}`, `WAD = ONE = 10^{18}`, `HLF = 0.5 × 10^{18}`, time units (`YEAR`, `MONTH`, `DAY`, `HOUR`), and bounds (`MAX_DIFFICULTY = 64`, `MIN_HOLDERS = 10^{18}`).

**What it defends.** T16 partially — they reduce the *class* of bug surface but cannot rule out logic errors. Formal verification, when complete, will close more.

## Position and Vault inheritance

**Where it lives.** The `Position`, `Vault`, and `WPosition` contracts.

- **`Position is ERC20Permit`** — the supply/borrow tokens are plain ERC20 with EIP-2612 `permit`. Borrow positions implement [inverted transfer](/concepts/positions-as-tokens) semantics so a sender's *gain* is the receiver's *liability*.
- **`Vault is ERC4626`** — the asset-custody contract is the ERC-4626 vault. `Vault` deposit/redeem are `onlyOwner`-gated; only the Pool can move assets in or out.
- **`WSupplyPosition is IWPosition, ERC4626, ERC20Permit`** (in the `WPosition` contract) — an *optional* wrapper around a Supply Position that strips the lock-aware-transfer feature for compatibility with vanilla ERC-4626 integrators. Only Supply positions are wrappable; there is no `WBorrowPosition`. See [wrapped positions](/using-the-protocol/wrapped-positions).

**What it defends.** T6 (the `onlyOwner` gate on Vault deposit/redeem); not a defence per se but a clear inheritance boundary that makes audits easier.

## Where to go next

- [Threat model](/security/threat-model) — the same primitives indexed by attack class
- [Audits and reviews](/security/audits-and-reviews) — external review status
- [Role hierarchy](/features/lethargic-governance/role-hierarchy) — full Acma role table
- [PoW-gated public mode](/for-keepers/pow-gated-public-mode) — `powlimited` mechanics for keepers
- [Parameter catalog](/governance/parameter-catalog) — every governable parameter, with the supervisor that bounds it
