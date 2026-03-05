# Role hierarchy

Access control in XPower Banq is implemented in **`Acma`** — short for "access control management." Under the hood `Acma` extends OpenZeppelin's `AccessManager`. Every privileged function on every protocol contract is gated by a 64-bit role ID, with the mapping (target × selector → role) stored in `Acma`.

## Three tiers per action

For each privileged *action* the protocol defines **three** related roles:

| Tier | Suffix | Power |
|---|---|---|
| Base | `…_ROLE` | Holders may *call* the gated function. |
| Admin | `…_ADMIN_ROLE` | Holders may *grant* and *revoke* the base role, and may modify the access-manager parameters of the base role (the time-delay, etc). |
| Guard | `…_GUARD_ROLE` | Holders may *cancel* a pending operation scheduled against the base role. |

The base role is what gets things done; the admin is what changes who can do them; the guard is the circuit breaker that can veto a pending change before its delay elapses. This is the `AccessManager` model — XPower Banq does not invent its own ACL.

## The base verbs

Across all the protocol contracts the base actions reduce to a small set of verbs (defined in the `Roles` library):

| Verb | Where it gates | What the holder can do |
|---|---|---|
| `SET_TARGET` | Position / Vault / Pool / Feed | Schedule a new value for a parameter target |
| `TMP_TARGET` | Position / Vault / Pool / Feed | Apply a temporary parameter override |
| `CAP_SUPPLY` | Pool | Set per-token supply cap |
| `TMP_SUPPLY` | Pool | Apply a temporary supply cap override |
| `CAP_BORROW` | Pool | Set per-token borrow cap |
| `TMP_BORROW` | Pool | Apply a temporary borrow cap override |
| `ENLIST` | Pool / Feed | Add a supported token (Pool) or a price source (Feed) |
| `ENWRAP` | Pool | Mint a wrapped position |
| `RETWAP` | Feed | Refresh the TWAP price |
| `FETCH_POLS` | Vault | Extract protocol-owned liquidity (POL) via `fetchPol` |
| `SQUARE` | Pool | Liquidate (the keeper-callable internal entrypoint behind `liquidate`) |
| `RELATE` | Acma | Wire a new (target, selector) into a role |

Combined with the host component prefix (`SUPPLY_…`, `BORROW_…`, `VAULT_…`, `FEED_…`, `POOL_…`, `ACMA_…`) you get the concrete roles named in `Acma`: `POOL_SQUARE_ROLE`, `FEED_RETWAP_ROLE`, `POOL_CAP_SUPPLY_ROLE`, `VAULT_FETCH_POLS_ROLE`, `SUPPLY_SET_TARGET_ROLE`, and so on. Each one has matching `…_ADMIN_ROLE` and `…_GUARD_ROLE` companions.

## Per-pool role scoping

Since the protocol hosts many pools, the roles in `Acma` are **scoped per pool**: every role accessor takes the pool name as its argument, so `POOL_SQUARE_ROLE("P007")` names a *different* role than `POOL_SQUARE_ROLE("P000")`.

The role ID is derived as a 64-bit truncation of a `keccak256` over three parts:

$$
\text{role\_id}(\text{verb}, \text{domain}, \text{pool}) =
\text{uint64}(\text{bytes8}(\text{keccak256}(\text{verb} \cdot \text{domain} \cdot \text{pool})))
$$

Where:

- **verb** — the base action, e.g. `SET_TARGET`, `CAP_SUPPLY`, `SQUARE`, `FETCH_POLS`.
- **domain** — the contract family: `supply`, `borrow`, `vault`, `feed`, or `pool`.
- **pool** — the pool name, e.g. `"P000"` … `"P999"`.

So `POOL_SQUARE_ROLE("P007") = keccak256("SQUARE" + "pool" + "P007")` truncated to 8 bytes. Grants, revokes, delays, and guards all apply to that one pool's role instance — a grant for `P000` gives **no** access to `P007`.

The **only global role** is `ACMA_RELATE_ROLE()` — it takes no pool name because `relate` wires selectors to roles across the whole access manager rather than to any single pool.

This is why, for example, enabling the permissionless `liquidate()` path is a **per-pool** governance decision: granting `POOL_SQUARE_ROLE` to one pool address does not affect any other pool. See [PoW-gated public mode](/for-keepers/pow-gated-public-mode).

The `Caps` and `Pols` wrappers follow a related but distinct pattern: their own internal roles are **singleton-level** (derived with a `"caps"` / `"pols"` suffix, not a pool name), and the singletons are then granted the *per-pool* `Acma` role for each pool they serve. See [Caps wrapper and circuit breaker](/features/position-caps/caps-wrapper-and-circuit-breaker) and [Fetching POL](/features/protocol-owned-liquidity/fetching-and-roles).

## How "lethargic" enters the picture

The `AccessManager` lets a role's *admin* set a per-target *execution delay*. When a parameter change is scheduled through a delayed role:

1. The *admin* schedules the call. The change is not effective yet.
2. A timer counts down for the configured delay.
3. During the wait, a *guard* may call `cancel(...)` to abort.
4. When the timer elapses, anyone can `execute(...)` to apply the scheduled call. The supervisor on the target contract then enforces its own per-cycle multiplicative bound and absolute range before accepting the new value.

So "lethargic governance" is the composition of three things: (1) the access-manager delay between *scheduling* and *executing*, (2) the guard's ability to cancel during that delay, and (3) the supervisor's per-cycle ≤ 2× / ≥ 0.5× bound. Each layer is enforced by code; none can be skipped by the admin.

## What the guard can and cannot do

A guard cannot *propose* changes — only block scheduled ones. It is a circuit-breaker, not a co-author. If a change makes it through both the admin's schedule and the delay window, it lands; the guard's window has closed.

## Beyond parameters

The same role machinery covers non-parameter operations:

- **Adding tokens** to a pool — `POOL_ENLIST_ROLE`
- **Wrapping a position** — `POOL_ENWRAP_ROLE`
- **Refreshing oracles** — `FEED_RETWAP_ROLE`
- **Adjusting the role-to-selector map itself** — `ACMA_RELATE_ROLE`
- **Permissionless paths** — `liquidate`, `retwap`, `supply`, `borrow` etc. additionally support a PoW-gated public mode that bypasses the role check at the cost of compute (see [PoW-gated public mode](/for-keepers/pow-gated-public-mode))

## Where to go next

- [Governance overview](/governance/overview)
- [Role management](/governance/role-management)
- [Parameter bounds](/features/lethargic-governance/parameter-bounds)
- [Emergency procedures](/governance/emergency-procedures)
