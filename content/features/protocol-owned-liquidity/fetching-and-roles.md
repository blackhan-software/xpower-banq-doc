# Fetching POL: Vault primitive and Pols wrapper

Extraction of [protocol-owned liquidity](/features/protocol-owned-liquidity/overview) flows through two layers: a **raw vault primitive** (`fetchPol`) and a **supervised wrapper** (`Pols`) that adds role separation and stored defaults.

## The vault primitive: `fetchPol`

`Vault.fetchPol(address target, uint256 amount)` is the single extraction entry point. It is `restricted` (ACMA-gated, `VAULT_FETCH_POLS_ROLE`) and implements the share cap exactly as previewed by the view functions:

```solidity
function fetchPol(address target, uint256 amount) external restricted returns (uint256 fetched) {
    fetched = Math.min(_polFetchable(), amount);
    if (fetched > 0) {
        _pol_fetched += fetched;
        if (target != address(0)) {
            // require vault balance >= fetched, then transfer
        }
        emit FetchPol(target, fetched);
    }
}
```

Key semantics:

- **Share-capped.** `fetched = min(polFetchable(), amount)` where `polFetchable() = pol() × share − polFetched()`. Repeated calls can never exceed the ceiling.
- **Amount sentinel.** `type(uint256).max` extracts everything currently allowed.
- **Recipient sentinel.** `target = address(0)` advances the fetched baseline **without** a transfer or liquidity check — a pure bookkeeping "burn".
- **Liquidity guard.** Real transfers revert with `InsufficientLiquidity(fetched)` if the vault lacks the underlying.
- **CEI ordering.** The baseline advances *before* the external transfer, so a reentrant call sees nothing left to fetch.

### View functions

| Function | Returns |
|---|---|
| `pol()` | Total accumulated surplus: `supply.polAccrued() + borrow.polAccrued()` |
| `polFetchable()` | Share-capped remainder still fetchable — exact preview of `fetchPol(target, type(uint256).max)` |
| `polFetched()` | Cumulative amount already extracted (the advanced baseline) |
| `polAccrued()` (position) | Per-position accumulated surplus (supply or borrow side) |

## The `Pols` wrapper

`fetchPol(target, amount)` is a raw primitive: a single role holder controls *both* destination and amount atomically. That is compositionally correct, but operationally awkward for bots:

1. A compromised hot key with `VAULT_FETCH_POLS_ROLE` could siphon the share-capped surplus to an arbitrary address.
2. "Pick a target" and "pick an amount" cannot be granted independently.
3. Bots must hardcode destination and amount, which is fragile across redeployments.

The `Pols` contract wraps `fetchPol` into **three progressively-permissioned `fetch` variants**, each guarded by its own ACMA role triple, and stores a default `target` and `amount` set at construction.

### Function variants

| Function | Target | Amount | Use case |
|---|---|---|---|
| `fetch(vault)` | Stored `_pol_target` | Stored `_pol_amount` | Bot with fixed target & amount; fully constrained |
| `fetch(vault, target)` | Caller-provided | Stored `_pol_amount` | Operator with target choice but no amount discretion |
| `fetch(vault, target, amount)` | Caller-provided | Caller-provided (capped as usual) | Full control; typically a multisig |

All three return the amount actually fetched (after the share cap) and forward to `vault.fetchPol(target, amount)`. Constructor defaults: `target = address(0)` (sentinel burn) and `amount = type(uint256).max` (extract everything allowed).

### Role separation

`Pols` mirrors the `Caps` pattern: one role triple per operation, IDs derived via `role_id("...") = keccak256(label || "pols")`. The `"pols"` suffix prevents collisions with `Caps`, `Acma`, or any other contract's roles.

| Operation | Exec role | Admin role | Guard role |
|---|---|---|---|
| `fetch(vault)` | `POLS_FETCH0_ROLE` | `POLS_FETCH0_ADMIN_ROLE` | `POLS_FETCH0_GUARD_ROLE` |
| `fetch(vault, target)` | `POLS_FETCH1_ROLE` | `POLS_FETCH1_ADMIN_ROLE` | `POLS_FETCH1_GUARD_ROLE` |
| `fetch(vault, target, amount)` | `POLS_FETCH2_ROLE` | `POLS_FETCH2_ADMIN_ROLE` | `POLS_FETCH2_GUARD_ROLE` |
| `setTarget(target)` | `POLS_SET_TARGET_ROLE` | `POLS_SET_TARGET_ADMIN_ROLE` | `POLS_SET_TARGET_GUARD_ROLE` |
| `setAmount(amount)` | `POLS_SET_AMOUNT_ROLE` | `POLS_SET_AMOUNT_ADMIN_ROLE` | `POLS_SET_AMOUNT_GUARD_ROLE` |

Per-pool, the `Pols` singleton is granted `VAULT_FETCH_POLS_ROLE(pool_name)` so its `fetch` calls are authorised by the vault. Admin does **not** imply execution rights — the standard Banq three-tier semantics.

### Properties

- **Cap-respecting** — all `fetch` variants inherit the `polFetchableShare` cap, the monotonic baseline, and CEI ordering from `fetchPol`.
- **Role isolation** — a FETCH0 holder cannot call FETCH1/FETCH2; a `setTarget` holder cannot fetch.
- **Sentinel burn** — the stored target can be `address(0)`, turning `fetch(vault)` into a bookkeeping burn.
- **Non-upgradeable singleton** — no proxy, no `DELEGATECALL`, no `receive()`/`fallback()`; zero token balance.

## Governance

`POL_FETCHABLE_SHARE` is a standard lethargic parameter on the Vault (`POL_FETCHABLE_SHARE_ID = 0x4`), range `[0, 100%]`, default `0`. Governance raises it via `setTarget` under the usual 0.5×–2× per-cycle bound and ~1-month transition. Raising the share does **not** fetch anything by itself — it only expands the ceiling that `fetchPol`/`Pols.fetch` may draw against.

## Where to go next

- [Protocol-owned liquidity](/features/protocol-owned-liquidity/overview) — what POL is and how it accrues
- [Vault parameters](/parameters/vault-parameters) — `POL_FETCHABLE_SHARE` and fees
- [Events and indexing](/for-developers/events-and-indexing) — the `FetchPol` event
- [Role hierarchy](/features/lethargic-governance/role-hierarchy) — how admin/guard triples work
