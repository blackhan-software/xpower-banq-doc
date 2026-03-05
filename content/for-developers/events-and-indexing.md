# Events and indexing

XPower Banq emits events for every state-changing operation. This page lists the canonical events and their fields, mirroring the on-chain interfaces.

## Pool events

```solidity
event Supply(
  address indexed user,
  IERC20 indexed token,
  uint256 amount,
  uint256 dt_term
);

event Borrow(
  address indexed user,
  IERC20 indexed token,
  uint256 assets,
  uint256 dt_term,
  IFlash flash,
  bytes data
);

event Settle(
  address indexed user,
  IERC20 indexed token,
  uint256 assets
);

event Redeem(
  address indexed user,
  IERC20 indexed token,
  uint256 assets
);

event Liquidate(
  address indexed user,
  address indexed victim,
  uint8 partial_exp
);

event LockSupply(
  address indexed user,
  IERC20 indexed token,
  uint256 amount,
  uint256 dt_term
);

event LockBorrow(
  address indexed user,
  IERC20 indexed token,
  uint256 amount,
  uint256 dt_term
);

event RollSupply(
  address indexed user,
  IERC20 indexed token,
  uint256 rolled,
  uint256 dt_term
);

event RollBorrow(
  address indexed user,
  IERC20 indexed token,
  uint256 rolled,
  uint256 dt_term
);
```

`dt_term` is a time offset in seconds — `0` means "no lock", `type(uint256).max` means "permanent". `user` in `Liquidate` is the liquidator (caller); `victim` is the under-water borrower.

The flash-loan variant of `Borrow` populates `flash` with the loan callback contract and `data` with the forwarded calldata. For plain borrows these are the zero address and empty bytes.

## Vault events

```solidity
event FetchPol(
  address indexed target,
  uint256 amount
);
```

`FetchPol` fires whenever governance (or the `Pols` wrapper) extracts protocol-owned liquidity from a vault. `target` is the recipient (the zero address for a sentinel bookkeeping burn) and `amount` is the underlying actually transferred. See [protocol-owned liquidity](/features/protocol-owned-liquidity/overview).

## Pool admin / governance events

These are emitted on protocol-administration paths (cap changes, token enlistment, wrapper enwrapping). Indexers tracking config drift should subscribe to them.

```solidity
event CapSupply(
  IERC20 indexed token,
  uint256 limit,
  uint256 dt
);

event CapBorrow(
  IERC20 indexed token,
  uint256 limit,
  uint256 dt
);

event Enlist(
  IERC20 indexed token,
  IVault vault,
  Weight weight,
  RateLimit rate_limit
);

event Enwrap(
  IERC20 indexed token,
  IWPosition wrapper,
  uint256 duration
);
```

`CapSupply` / `CapBorrow` fire when governance changes the per-pool supply or borrow cap on a token (with a transition `dt`). `Enlist` fires once per token, when it's first listed into the pool with its vault, weights, and rate-limit. `Enwrap` fires when an `ERC4626` wrapper is bound to a position for the given duration. Note that the Pool-side `Enlist` is distinct from the Oracle-side `Enlist` below — they are separate events on separate contracts with different field shapes.

## Position events (standard ERC20 + reindex)

```solidity
event Transfer(
  address indexed from,
  address indexed to,
  uint256 value
);

event Approval(
  address indexed owner,
  address indexed spender,
  uint256 value
);

event Reindex(
  uint256 index_log,
  uint256 util_wad,
  uint256 timestamp
);
```

`Transfer` and `Approval` are the standard OpenZeppelin ERC20 events. `Reindex` is emitted when a position advances its log-space interest index (rate-limited to once per minute).

## Oracle events

```solidity
event Enlist(
  IERC20 indexed source,
  IERC20 indexed target,
  IFeed feed,
  uint256 dt
);

event Refresh(
  IERC20 indexed source,
  IERC20 indexed target,
  uint256 quote
);
```

`Enlist` is emitted when a price feed for a `source → target` pair is added (with refresh window `dt`). `Refresh` is emitted on each TWAP-window refresh of an enlisted pair.

## Acma events

Acma extends OpenZeppelin's `AccessManager`, so it emits the standard AccessManager events — most notably:

- `RoleGranted(uint64 indexed roleId, address indexed account, uint32 delay, uint48 since, bool newMember)`
- `RoleRevoked(uint64 indexed roleId, address indexed account)`
- `TargetFunctionRoleUpdated(address indexed target, bytes4 selector, uint64 indexed roleId)`

Refer to the [OpenZeppelin AccessManager documentation](https://docs.openzeppelin.com/contracts/5.x/api/access#AccessManager) for the full event list and field semantics.

## Governance events

Parameter changes flow through a single event:

```solidity
event Target(
  uint256 indexed id,
  uint256 value,
  uint256 dt
);
```

`id` identifies the parameter, `value` is the new target, and `dt` is the duration of the linear transition window. There are no separate propose / commit / veto events — `Target` is emitted once per parameterised change and the on-chain saturator handles the gradual transition. See [Transition curves](/features/lethargic-governance/transition-curves).

## Indexing strategies

For a complete picture of an account's history, subscribe to:

- `Supply`, `Borrow`, `Settle`, `Redeem` events filtered by `indexed user`.
- `Transfer` events on Supply Position and Borrow Position contracts filtered by `from` or `to`.
- `Liquidate` events filtered by `victim` (or `user` for the liquidator side).
- `LockSupply` and `LockBorrow` events filtered by `user`.
- `RollSupply` and `RollBorrow` events filtered by `user` for lock-roll history.

For pool-wide aggregates:

- All Pool events without a user filter.
- `Reindex` events on each Supply Position and Borrow Position for the time-series of log-space interest indices and per-period utilization.
- `FetchPol` events on each Vault for the treasury-extraction time-series.

## Where to go next

- [CLI and tools](/for-keepers/cli-and-tools) — `banq-cli` includes `--watch`-style live event streaming for `retwap`
- [Integration guide](/for-developers/integration-guide) — high-level patterns
