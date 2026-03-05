# Log-space index paper

A storage-efficient cumulative interest index using log-space arithmetic.

## The core result

Standard lending-protocol designs accumulate compound interest as a multiplicative index:

$$
I_{t+1} = I_t \cdot (1 + r \cdot \Delta t)
$$

This is conceptually simple but suffers two problems:

1. **Overflow.** At default rates, the index overflows uint256 in ~29 years. A protocol expected to last decades hits this limit.
2. **Precision loss.** Each multiplication truncates fractional bits. Across many compoundings, this accumulates.

XPower Banq uses **log-space accumulation** instead:

$$
L_{t+1} = L_t + r \cdot \Delta t
$$

The actual index is recovered as `I = exp(L)` only when needed for balance computations.

## Properties

- **Overflow horizon ≈ 10⁵⁸ years** (effectively unlimited).
- **Tighter precision bound** than the multiplicative approach (2 ULP worst-case per the log-space paper, vs. 2N ULP after N multiplicative compoundings — empirically +10–20 wei closer to the mathematical ideal).
- **Gas cost ~1,200 less per accrual** (addition is cheaper than multiplication).

## Why this works

Adding logs is mathematically equivalent to multiplying linears. The log-space sum is exact (no per-step truncation), and the exponentiation at read time is a single operation with bounded error.

## Implementation

The protocol uses a high-precision fixed-point representation for `L`. The exponentiation function is taken from the OpenZeppelin Math library or equivalent.

## Where this matters

For users: invisibly. Your balance is computed correctly across decades.

For developers: you need to be aware that `L` is the stored value, not `I`. SDK calls handle the conversion.

## Where to find the paper

- **PDF:** [`banq-log.pdf`](https://github.com/blackhan-software/xpower-banq-doc/releases/latest/download/banq-log.pdf) (latest release)
- **Unified bundle:** [`banq-all.pdf`](https://github.com/blackhan-software/xpower-banq-doc/releases/latest/download/banq-all.pdf) — this paper is one of two engineering primitives in Part II.

## Where to go next

- [Interest rates](/concepts/interest-rates) — the rate model
- [Architecture overview](/for-developers/architecture-overview) — where this lives
