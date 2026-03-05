# Contract addresses

Latest deployment: **v11b** on **Avalanche C-Chain** (chain ID 43114).

## Governance

| Contract | Address | Role |
|---|---|---|
| BOSS | [`0x5630140E6eCB6242615E9E628095E1A4Ce3903c3`](https://snowscan.xyz/address/0x5630140E6eCB6242615E9E628095E1A4Ce3903c3) | Protocol owner (multisig) |
| ACMA | [`0x61ea9e262D959506E3Fe6AF153C66058ff62A1Bf`](https://snowscan.xyz/address/0x61ea9e262D959506E3Fe6AF153C66058ff62A1Bf) | Access-control manager (OpenZeppelin `AccessManager`) |
| CAPS | [`0x682Af53E936c78f9A976176d822482952f7D4c86`](https://snowscan.xyz/address/0x682Af53E936c78f9A976176d822482952f7D4c86) | Delta-based cap wrapper (`incSupply`/`decSupply`/`incBorrow`/`decBorrow`) |
| POLS | [`0x1953410bdFFfc7E706f21F293fb4002D5aF7C9d6`](https://snowscan.xyz/address/0x1953410bdFFfc7E706f21F293fb4002D5aF7C9d6) | Protocol-owned-liquidity fetch wrapper (`fetch` variants) |

`CAPS` and `POLS` are supervised singletons deployed alongside the core contracts; they receive per-pool roles at enrollment. See [Caps wrapper and circuit breaker](/features/position-caps/caps-wrapper-and-circuit-breaker) and [Fetching POL](/features/protocol-owned-liquidity/fetching-and-roles).

## Tokens

| Symbol | Address |
|---|---|
| APOW | [`0x83C644bF682D331E65973e884d69541dF002Ae6E`](https://snowscan.xyz/address/0x83C644bF682D331E65973e884d69541dF002Ae6E) |
| XPOW | [`0xd57CAe4D54F7a8119119136d578e8dC743cF708e`](https://snowscan.xyz/address/0xd57CAe4D54F7a8119119136d578e8dC743cF708e) |
| WAVAX | [`0xB31f66AA3C1e785363F0875A1B74E27b85FD66c7`](https://snowscan.xyz/address/0xB31f66AA3C1e785363F0875A1B74E27b85FD66c7) |
| USDC | [`0xB97EF9Ef8734C71904D8002F8b6Bc66Dd9c48a6E`](https://snowscan.xyz/address/0xB97EF9Ef8734C71904D8002F8b6Bc66Dd9c48a6E) |
| USDT | [`0x9702230A8Ea53601f5cD2dc00fDBc13d4dF4A8c7`](https://snowscan.xyz/address/0x9702230A8Ea53601f5cD2dc00fDBc13d4dF4A8c7) |
| BTC.b | [`0x152b9d0FdC40C096757F570A51E494bd4b943E50`](https://snowscan.xyz/address/0x152b9d0FdC40C096757F570A51E494bd4b943E50) |

`BTC.b` is deployed as a recognised collateral token but has no live pool yet.

## Pools and oracles

Each pool pairs two tokens; the oracle (a `Seer` EWMA price-tracker) reports the spot/TWAP price of one asset in units of the other. The first column is the pool's canonical pair name.

| Pair | Pool | Oracle |
|---|---|---|
| APOW /&nbsp;XPOW | [`0xF800FD1fCF74a5aB583A32E336dd126d360712dB`](https://snowscan.xyz/address/0xF800FD1fCF74a5aB583A32E336dd126d360712dB) | [`0x38227EA4864589e521B242B3C0D19d3f1512f39E`](https://snowscan.xyz/address/0x38227EA4864589e521B242B3C0D19d3f1512f39E) |
| APOW /&nbsp;WAVAX | [`0xbFF714538E6eeD640fb2b33944154679F3489F4A`](https://snowscan.xyz/address/0xbFF714538E6eeD640fb2b33944154679F3489F4A) | [`0x552806eB1576a863f6dD0847876f5D9BE4472cE0`](https://snowscan.xyz/address/0x552806eB1576a863f6dD0847876f5D9BE4472cE0) |
| APOW /&nbsp;USDC | [`0xab07DD4c8E6c0E8330BdceF422F0c6D0Cdf49c31`](https://snowscan.xyz/address/0xab07DD4c8E6c0E8330BdceF422F0c6D0Cdf49c31) | [`0x63E1F57B221EC4D120d059a0881579b816E5bCB1`](https://snowscan.xyz/address/0x63E1F57B221EC4D120d059a0881579b816E5bCB1) |
| APOW /&nbsp;USDT | [`0x3E50e681BC2f9d348D21C58e82ADb671f713a6B3`](https://snowscan.xyz/address/0x3E50e681BC2f9d348D21C58e82ADb671f713a6B3) | [`0x2244f7B8F04ca0f648651883120DF1768A44B1A0`](https://snowscan.xyz/address/0x2244f7B8F04ca0f648651883120DF1768A44B1A0) |
| XPOW /&nbsp;WAVAX | [`0x73380d71F590083Fc648249DF175024940F14A5A`](https://snowscan.xyz/address/0x73380d71F590083Fc648249DF175024940F14A5A) | [`0x5A11310E6281489868F5C285c9fAa6Cc74cEB158`](https://snowscan.xyz/address/0x5A11310E6281489868F5C285c9fAa6Cc74cEB158) |
| XPOW /&nbsp;USDC | [`0x0f01Bbc86B68e56a13a43Ef6af73DB3d1494eF09`](https://snowscan.xyz/address/0x0f01Bbc86B68e56a13a43Ef6af73DB3d1494eF09) | [`0x7f27B630c6Da43e67C15d8818e7e9B1784CEcd18`](https://snowscan.xyz/address/0x7f27B630c6Da43e67C15d8818e7e9B1784CEcd18) |
| XPOW /&nbsp;USDT | [`0xA42F3d7b3676AcAfdF4417bD3923000725B9B241`](https://snowscan.xyz/address/0xA42F3d7b3676AcAfdF4417bD3923000725B9B241) | [`0xaA2b4c0F3565cF95Bc22aBD83Dfd5c1b42D9D45D`](https://snowscan.xyz/address/0xaA2b4c0F3565cF95Bc22aBD83Dfd5c1b42D9D45D) |

Per-pool position contracts (supply position, borrow position, vault) are read off the pool itself:

```solidity
IPool pool = IPool(0xF800FD1fCF74a5aB583A32E336dd126d360712dB);
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
