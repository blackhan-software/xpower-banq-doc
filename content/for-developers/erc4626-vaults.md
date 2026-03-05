# ERC4626 vaults

Each Pool's underlying assets are custodied in an **ERC4626 vault**. The read-only half of ERC4626 (`asset`, `totalAssets`, `convertTo*`, `preview*`, `max*`) is fully public, enabling standard integration tooling. The mutating half (`deposit`, `mint`, `withdraw`, `redeem`) is restricted to the Pool alone.

## What ERC4626 provides

ERC4626 is the tokenised vault standard. It defines:

- `asset()` — the underlying token.
- `totalAssets()` — total underlying held.
- `convertToShares(assets)` and `convertToAssets(shares)` — conversion.
- `deposit(assets, receiver)`, `mint(shares, receiver)` — entries (Pool-only).
- `withdraw(assets, receiver, owner)`, `redeem(shares, receiver, owner)` — exits (Pool-only).
- `maxDeposit`, `maxMint`, `maxWithdraw`, `maxRedeem` — limits (public).
- `previewDeposit`, `previewMint`, `previewWithdraw`, `previewRedeem` — quote functions (public).

## Access control

The Vault inherits `Ownable` and its mutating functions — `deposit`, `mint`, `withdraw`, `redeem`, `depositAssets`, `redeemAssets` — are all guarded by `onlyOwner`. The `VaultMill` factory sets the Pool as the owner at deploy time, so only the Pool can move tokens in or out of the Vault. No other address can trigger a state change.

::: info Why is the Vault locked?
The Pool enforces health checks (H ≥ 100%) before calling into the Vault. If the Vault were open for direct calls, a depositor could withdraw collateral without repaying debt, leaving a liquidatable position. The `onlyOwner` gate makes the footgun impossible rather than just warned against.
:::

This means the Vault is **not** a standard open-deposit ERC4626. Third-party vault aggregators cannot deposit into a Banq Vault; integration happens at the Pool layer instead.

## Read-only integration

The Vault's entire ERC4626 read surface is publicly callable:

- `asset()`, `totalAssets()`, `totalSupply()` — state queries.
- `convertToShares(assets)` / `convertToAssets(shares)` — conversion rates.
- `previewDeposit`, `previewMint`, `previewWithdraw`, `previewRedeem` — fee-aware quotes.
- `maxDeposit`, `maxMint`, `maxWithdraw`, `maxRedeem` — capacity limits.

Use these in your contracts or off-chain scripts to compute pool conditions without calling the Pool directly.

## Protocol-owned liquidity (POL) surface

Beyond ERC4626, the Vault exposes the [protocol-owned liquidity](/features/protocol-owned-liquidity/overview) read/write surface:

- `pol()` — total accumulated spread surplus (`supply.polAccrued() + borrow.polAccrued()`).
- `polFetchable()` — share-capped remainder still extractable.
- `polFetched()` — cumulative amount already extracted.
- `fetchPol(target, amount)` — governance-gated extraction primitive (`VAULT_FETCH_POLS_ROLE`), capped by `polFetchableShare`.

The views are fully public; `fetchPol` is restricted. Indexers tracking treasury activity subscribe to the `FetchPol(address indexed target, uint256 amount)` event. See [Fetching POL](/features/protocol-owned-liquidity/fetching-and-roles) for the full semantics and the `Pols` wrapper.

## Vault and Pool relationship

- Vault holds the underlying tokens.
- Pool reads the Vault's `totalAssets()` and routes deposits/withdrawals through it.
- The Pool is the Vault's `Ownable` owner — only the Pool can call `deposit`/`mint`/`withdraw`/`redeem`.

Vault bindings are **permanent**. `Pool.enlist(...)` requires `unlisted(token)` and emits `Listed.enlisted` — there is no inverse function and no way to swap a token's Vault after enlistment. Migrating to a different Vault implementation would require deploying a new Pool.

## Where to go next

- [Architecture overview](/for-developers/architecture-overview) — the contract relationships
- [Vault parameters](/parameters/vault-parameters) — vault-specific defaults
