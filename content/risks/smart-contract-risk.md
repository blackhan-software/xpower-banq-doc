# Smart contract risk

The contracts implementing XPower Banq are non-trivial. This page is honest about what's been verified and what hasn't.

## What's been done

- **Internal testing.** A comprehensive Foundry test suite covers core operations (supply, borrow, settle, redeem, liquidate, lock, transfer).
- **Property tests.** Invariants like "total supply equals sum of balances" and "post-tx H ≥ 100% after liquidation" are tested.
- **Simulation.** Cascade dynamics, capacity dynamics, and TWAP manipulation are simulated across diverse scenarios.

## What hasn't been done

- **Formal verification.** No formal proof of contract correctness has been performed. The whitepaper explicitly flags this as the highest-priority future work.
- **External audit.** The protocol's plan is to engage external auditors before mainnet launch. Until and unless these are completed and published, the contracts have not been audited.

## What this means for users

Smart-contract risk is binary at the worst end: a bug in the Pool, Position, or Vault contracts could cause catastrophic loss of funds. Until formal verification and external audits are completed, this risk is non-trivial.

## Mitigations

- **Wait for audits if you're capital-conservative.** If your goal is capital preservation, wait until the audit page reports completed audits.
- **Limit exposure.** Allocate to Banq only what you can afford to lose to a smart-contract bug.
- **Watch the audit page.** Once audits are completed and published, they update the risk profile materially.
- **Stay informed.** Subscribe to the protocol's incident-reporting channel.

## What's likely to be safer than dangerous

The contracts borrow heavily from established patterns:

- ERC20 from OpenZeppelin (well-tested).
- ERC4626 from OpenZeppelin (recent but well-tested).
- AccessControl-style roles (well-tested).

The protocol-specific logic (cap function, lock state, debt-assumption liquidation, log-space TWAP) is novel and is where most of the smart-contract risk concentrates.

## Where to go next

- [Audits and reviews](/security/audits-and-reviews) — current audit status
- [Architecture overview](/for-developers/architecture-overview) — what the contracts do
