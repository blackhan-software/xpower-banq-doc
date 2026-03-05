# Ring-buffer locks paper

The 16-slot quarterly ring-buffer time-lock primitive, with O(1) reads and writes.

## The core result

Tracking N concurrent timed locks naively requires O(N) iteration on every read. The ring-buffer construction reduces this to O(1) by exploiting the algebraic identity:

$$
D = \sum_i Q_i - T \cdot t + p \cdot L
$$

where:
- `D` is the total locked depth.
- `Q_i` is the prefix-sum of token-seconds in slot `i`.
- `T` is the total locked balance.
- `t` is the current time.
- `p` is the permanent-locked balance.
- `L` is the elapsed time on the permanent component.

The formula evaluates in constant time regardless of how many slots are populated. The ring buffer lets the protocol amortise lock additions across slots without ever iterating over them.

## Why 16 slots and quarters

- **16 slots × 91.3125 days = 1,461 days = 4 Julian years.** The exact slot length comes from `MAX_LOCK_TERM = MONTH × 3` with `MONTH = YEAR / 12` and `YEAR = CENTURY / 100 = 365.25 days`. Enough horizon to cover most user use cases.
- **Quarterly granularity.** Coarser than monthly (saves storage), finer than yearly (gives meaningful flexibility).
- **Power-of-2 slot count.** Cleaner modular arithmetic for the ring index.

## Self-healing

When a new lock writes to a slot whose existing entry has already expired, the protocol automatically clears the expired entry. No manual cleanup is required from the user. The contract operates correctly even if expired entries linger.

## Why not Heap or sorted list?

Both alternatives have O(log N) cost per operation, with worse constants and more complex code. The ring buffer is conceptually simpler and gas-cheaper for the actual access patterns.

## Where to find the paper

- **PDF:** [`banq-lck.pdf`](https://github.com/blackhan-software/xpower-banq-doc/releases/latest/download/banq-lck.pdf) (latest release)
- **Unified bundle:** [`banq-all.pdf`](https://github.com/blackhan-software/xpower-banq-doc/releases/latest/download/banq-all.pdf) — this paper is one of two engineering primitives in Part II.

## Where to go next

- [Timed vs permanent](/features/locked-positions/timed-vs-permanent) — the user-facing version
- [Bonus and malus](/features/locked-positions/bonus-and-malus) — what the lock pays
