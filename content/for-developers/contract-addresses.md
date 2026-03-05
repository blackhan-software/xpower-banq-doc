# Contract addresses

Latest deployment: **v10c** on **Avalanche C-Chain** (chain ID 43114).

## Governance

| Contract | Address | Role |
|---|---|---|
| BOSS | [`0x5630140E6eCB6242615E9E628095E1A4Ce3903c3`](https://snowscan.xyz/address/0x5630140E6eCB6242615E9E628095E1A4Ce3903c3) | Protocol owner (multisig) |
| ACMA | [`0x2087e2115a419d81d2F5c13fD4B3d8aa187bF9d1`](https://snowscan.xyz/address/0x2087e2115a419d81d2F5c13fD4B3d8aa187bF9d1) | Access-control manager (OpenZeppelin `AccessManager`) |
| CAPS | [`0xD7e571faa68653D01a6282bB25F03B360eDf57B9`](https://snowscan.xyz/address/0xD7e571faa68653D01a6282bB25F03B360eDf57B9) | Delta-based cap wrapper (`incSupply`/`decSupply`/`incBorrow`/`decBorrow`) |
| POLS | [`0xb7320eD834b564416693687B365b4A1fF17Dedc8`](https://snowscan.xyz/address/0xb7320eD834b564416693687B365b4A1fF17Dedc8) | Protocol-owned-liquidity fetch wrapper (`fetch` variants) |

`CAPS` and `POLS` are supervised singletons deployed alongside the core contracts; they receive per-pool roles at enrollment. See [Caps wrapper and circuit breaker](/features/position-caps/caps-wrapper-and-circuit-breaker) and [Fetching POL](/features/protocol-owned-liquidity/fetching-and-roles).

## Tokens

| Symbol | Address |
|---|---|
| APOW | [`0x3ceeb67533E494C0dC6Be579585E3c62916062e0`](https://snowscan.xyz/address/0x3ceeb67533E494C0dC6Be579585E3c62916062e0) |
| XPOW | [`0x9a1d15DB004dce608DC738bC6762f384FD3d1a9F`](https://snowscan.xyz/address/0x9a1d15DB004dce608DC738bC6762f384FD3d1a9F) |
| WAVAX | [`0xB31f66AA3C1e785363F0875A1B74E27b85FD66c7`](https://snowscan.xyz/address/0xB31f66AA3C1e785363F0875A1B74E27b85FD66c7) |
| USDC | [`0xB97EF9Ef8734C71904D8002F8b6Bc66Dd9c48a6E`](https://snowscan.xyz/address/0xB97EF9Ef8734C71904D8002F8b6Bc66Dd9c48a6E) |
| USDT | [`0x9702230A8Ea53601f5cD2dc00fDBc13d4dF4A8c7`](https://snowscan.xyz/address/0x9702230A8Ea53601f5cD2dc00fDBc13d4dF4A8c7) |
| BTC.b | [`0x152b9d0FdC40C096757F570A51E494bd4b943E50`](https://snowscan.xyz/address/0x152b9d0FdC40C096757F570A51E494bd4b943E50) |

`BTC.b` is deployed as a recognised collateral token but has no live pool yet.

## Pools and oracles

Each pool pairs two tokens; the oracle (a `Seer` EWMA price-tracker) reports the spot/TWAP price of one asset in units of the other. The first column is the pool's canonical pair name.

| Pair | Pool | Oracle |
|---|---|---|
| APOW /&nbsp;XPOW | [`0xBEB2fE4e7Db535aE25A08EFac1d523F373435E1D`](https://snowscan.xyz/address/0xBEB2fE4e7Db535aE25A08EFac1d523F373435E1D) | [`0x965A5B2e3fe812F0483034b4f0b110F663B09Cd5`](https://snowscan.xyz/address/0x965A5B2e3fe812F0483034b4f0b110F663B09Cd5) |
| APOW /&nbsp;WAVAX | [`0x4e9Ab34bC184209AaBf63e2f72Da87a6011C6B08`](https://snowscan.xyz/address/0x4e9Ab34bC184209AaBf63e2f72Da87a6011C6B08) | [`0xAFC3dAe30B179d606E4E752Bcaf3222e25c1a933`](https://snowscan.xyz/address/0xAFC3dAe30B179d606E4E752Bcaf3222e25c1a933) |
| APOW /&nbsp;USDC | [`0xdbAad16f18f1f5DDB6A6CE3C4B3319c0A141D5b0`](https://snowscan.xyz/address/0xdbAad16f18f1f5DDB6A6CE3C4B3319c0A141D5b0) | [`0x5c348eC3821542E28Ac82507504703D4Baa28170`](https://snowscan.xyz/address/0x5c348eC3821542E28Ac82507504703D4Baa28170) |
| APOW /&nbsp;USDT | [`0x7Ff502c86904270dA4Ef1330c9f598B8757bfd05`](https://snowscan.xyz/address/0x7Ff502c86904270dA4Ef1330c9f598B8757bfd05) | [`0xAd74640e6131b414312c57fF73701E55De0a94B1`](https://snowscan.xyz/address/0xAd74640e6131b414312c57fF73701E55De0a94B1) |
| XPOW /&nbsp;WAVAX | [`0xb041AB22E469a8a589AF7696A3e60e14b658Dc41`](https://snowscan.xyz/address/0xb041AB22E469a8a589AF7696A3e60e14b658Dc41) | [`0x66E2D02Fe53c050dfE3af07154F8e59b37A3878B`](https://snowscan.xyz/address/0x66E2D02Fe53c050dfE3af07154F8e59b37A3878B) |
| XPOW /&nbsp;USDC | [`0x67BF6217250a8B49071EA3782815007576aC8C83`](https://snowscan.xyz/address/0x67BF6217250a8B49071EA3782815007576aC8C83) | [`0x96F556A9B8AcAb0FC9951229469D29B38b446495`](https://snowscan.xyz/address/0x96F556A9B8AcAb0FC9951229469D29B38b446495) |
| XPOW /&nbsp;USDT | [`0x9b937C1EB4773D79B79E08AAb976cbe3206f0018`](https://snowscan.xyz/address/0x9b937C1EB4773D79B79E08AAb976cbe3206f0018) | [`0x053c546bCf0999FEC41B10EAe6F1A46eE31c62e8`](https://snowscan.xyz/address/0x053c546bCf0999FEC41B10EAe6F1A46eE31c62e8) |

Per-pool position contracts (supply position, borrow position, vault) are read off the pool itself:

```solidity
IPool pool = IPool(0xBEB2fE4e7Db535aE25A08EFac1d523F373435E1D);
ISupplyPosition supply = pool.supplyOf(IERC20(APOW));
IBorrowPosition borrow = pool.borrowOf(IERC20(XPOW));
```

The supply/borrow positions are `ERC20Permit` tokens (with the protocol's locking and cap features). A separate `ERC4626` wrapper, `WSupplyPosition` (interface `IWPosition`), is available for tooling that expects a vault interface. **Only supply positions are wrappable** — there is no `WBorrowPosition`.

## Source verification

All deployed contracts have verified source on [snowscan.xyz](https://snowscan.xyz). The deployment commit hash matches the corresponding tag in the source repository.

## Where to go next

- [Integration guide](/for-developers/integration-guide) — how to wire up to these contracts
- [Architecture overview](/for-developers/architecture-overview) — what each contract does
- [CLI and tools](/for-keepers/cli-and-tools) — interact from the command line via `banq-cli`
