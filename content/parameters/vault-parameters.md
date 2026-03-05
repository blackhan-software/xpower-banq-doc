# Vault parameters

Parameters specific to the Vault contract (`VaultSupervised`). The Vault is intentionally minimal: three governable parameters live here, the rest live on the Pool or the Position.

## Defaults

| ID | Parameter | Range | Notes |
|---|---|---|---|
| `0x1` | `FEE_ENTRY` | 0 – 50% | Fraction skimmed on `depositAssets`. v10c default: `0.1%`. |
| `0x2` | `FEE_EXIT` | 0 – 50% | Fraction skimmed on `redeemAssets`. v10c default: `0.1%`. |
| `0x4` | `POL_FETCHABLE_SHARE` | 0 – 100% | Max share of the accumulated [POL](/features/protocol-owned-liquidity/overview) surplus that may be fetched. Default `0` (nothing extractable until governance raises it). |

The fee recipients are configured separately in the constructor: the entry fee can flow to a treasury address; an exit-fee recipient of the zero address is mapped to the vault itself, so the fee is retained in the vault (increasing the pool's per-share value) rather than transferred out. `POL_FETCHABLE_SHARE` is also seeded at construction from the `VaultFee` struct and defaults to `0` — the vault is born "locked".

## Reading from the contract

```solidity
IVault vault = IVault(vaultAddress);
(uint256 entryFee,)   = vault.getTarget(vault.FEE_ENTRY_ID());
(uint256 exitFee,)    = vault.getTarget(vault.FEE_EXIT_ID());
(uint256 fetchShare,) = vault.getTarget(vault.POL_FETCHABLE_SHARE_ID());
```

## Vault interface

The Vault implements `ERC4626` (`depositAssets` / `mintShares` / `redeemAssets` / `burnShares`) plus the POL read/write surface (`pol` / `polFetchable` / `polFetched` / `fetchPol`). For tooling that doesn't speak ERC-4626, prefer the Pool's higher-level `supply` / `redeem` / `borrow` / `settle`, which compose vault operations with the protocol's health checks.

Direct vault interaction bypasses the Pool's health checks. Use the Pool, not the Vault, for normal user operations.

## Where to go next

- [ERC4626 vaults](/for-developers/erc4626-vaults)
- [Pool parameters](/parameters/pool-parameters)
- [Position parameters](/parameters/position-parameters)
