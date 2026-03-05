# Locking positions

You can lock either a Supply Position or a Borrow Position by passing a non-zero `dt_term` parameter to the appropriate operation. You can also lock retroactively, by calling `lockSupply()` / `lockBorrow()` on the Pool against an existing position.

## Lock parameters

- **`dt_term`** — the lock duration as a **time offset in seconds** (`uint256`). Must be strictly positive; the maximum is 15 quarter-lengths from `now` (≈ 45 months). A special sentinel of `type(uint256).max` denotes a permanent lock.
- **`amount`** — the principal amount to lock (cannot exceed your current position balance).

The protocol stores locks in a 16-slot quarterly ring buffer; the slot a new lock lands in is `(block.timestamp + dt_term) / LOCK_TERM mod 16`, where `LOCK_TERM` is at most one quarter (~3 months). The expiry is the end of that quarter.

A lock with `dt_term = 4 * 3 * 30 days` therefore locks for roughly four quarters (≈ 1 year), expiring at the end of the fourth-future quarter.

## Permanent locks

Pass `dt_term = type(uint256).max` (or the `PERMANENT_LOCK` constant your SDK exposes) to make the lock permanent. The principal is locked forever; it never expires and never returns to the ring buffer.

## Stacking locks

You can have multiple timed locks at once, with different terms. The 16-slot ring buffer allows up to 16 active timed-lock slots — but only the *next 15* slots from `now` are addressable when you create a new lock (the slot already holding the next-expiring lock is reserved). New locks can be added on top of existing ones in the same slot.

A permanent lock is stored in a separate packed field, so it doesn't consume a ring slot.

## Locking on supply

If you supply with a non-zero `dt_term` (via the `supply(user, token, amount, dt_term)` overload), the supplied principal is locked at the moment of supply. You receive Supply Position tokens with the lock encoded.

If you supply unlocked first and lock later, you call `Pool.lockSupply(token, amount, dt_term)`. The protocol updates your lock state without minting or burning.

## Locking on borrow

The same pattern applies — borrow with `dt_term` to lock the borrow at creation, or lock retroactively via `Pool.lockBorrow(token, amount, dt_term)`.

## Reading lock state

The Position contract exposes three lock-state views:

- `lockTotalOf(user)` — cached total locked amount (`O(1)`; may include expired-but-unswept slots, call `free()` first for an exact value).
- `lockDepthOf(user)` — cached committed-tokens-remaining (`O(1)`).
- `lockStateAt(user, stamp)` — `(total, depth)` of locks still active beyond `stamp` (`O(k)`).

Most front-ends combine `lockTotalOf` and the user's `totalOf` balance to display a "locked vs liquid" split.

## Common gotchas

- **You can't unlock.** Locks are credible commitments. The only exits are expiry, transfer, or sale.
- **The 16-slot limit.** If you try to create a 17th active timed-lock slot, the call reverts. You'd need to wait for an existing slot to expire (`free()` will sweep it) or roll an existing lock with `Pool.rollSupply` / `Pool.rollBorrow`.
- **Slots are per-quarter, not per-day.** A lock created in the middle of a quarter expires at the end of the chosen-quarter-from-now boundary. So a `dt_term ≈ 1 quarter` lock created on Day 50 of a quarter actually expires ~40 days later.

## Where to go next

- [Timed vs permanent](/features/locked-positions/timed-vs-permanent) — choose your lock type
- [Bonus and malus](/features/locked-positions/bonus-and-malus) — the rate adjustment
- [Transfers and exits](/features/locked-positions/transfers-and-exits) — how to leave a lock early
