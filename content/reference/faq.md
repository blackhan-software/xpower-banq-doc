# FAQ

## Basics

### Is XPower Banq audited?

Not yet. The contracts have been internally tested with comprehensive Foundry test suites. External audits and formal verification are flagged as the highest-priority pre-launch work. See [Audits and reviews](/security/audits-and-reviews) for current status.

### What chains does it run on?

The current v10c deployment is on **Avalanche C-Chain**. Other EVM-compatible chains are planned. See [Contract addresses](/for-developers/contract-addresses).

### Is the source code open?

Yes. The full source is in the project's GitHub repository. Linked in the footer.

### Where is the app?

The XPower Banq app is at [app.xpowerbanq.com](https://app.xpowerbanq.com). The top-bar **App** link on every page of this site points there too.

## Locks

### Can I unlock early?

No. Locks are credible commitments. The only exit before expiry is to transfer the position to another address (or sell it on a secondary market at a discount).

### What if I permanently lock and change my mind in 5 years?

You're stuck with the position. You'll continue earning interest on it, but the principal is locked forever. You can transfer it to another address, but if no one wants to buy it, you hold it until you find a buyer.

### Why not allow early unlock with a penalty?

It would defeat cascade attenuation. The whole point of locks is that they're *credibly* uncallable during a crash. A "lock with escape hatch" is just a slow withdraw, which is much weaker protection.

## Liquidation

### Can I be liquidated even if I'm right at H = 100%?

No. The contract check rejects liquidation when `wnav_supply >= wnav_borrow` (i.e. `H ≥ 100%`). Liquidation requires `H < 100%` strictly. So at exactly `H = 100%` you're not yet liquidatable — the *moment after* you cross below 100% you are.

### How much do I lose in a liquidation?

50% of the cleared debt, paid in collateral. If half your 1,000 XPOW debt is cleared, you lose 250 XPOW in collateral on top of the 500 XPOW of debt clearance.

### Can the protocol auto-rebalance my position to avoid liquidation?

No. You're responsible for maintaining H ≥ 100%. The protocol provides view functions to check H but doesn't act on your behalf.

## Governance

### Who controls the protocol?

At launch, a multisig (`BOSS = 0x5630…03c3`) holds the various `_ADMIN_ROLE`s in Acma. The plan is progressive transition to a DAO contract holding those same admin roles.

### How do I propose a parameter change?

You can't directly. Scheduling a change requires the matching `_SET_TARGET_ROLE` (or `_TMP_TARGET_ROLE`), held by the multisig (or eventually a DAO). You can lobby for changes through the protocol's communication channels.

### Can governance freeze my position?

No. The protocol has **no pause / halt / freeze function** at all — neither global nor per-pool, neither time-bounded nor unbounded. The only emergency lever is the `_GUARD_ROLE` family, which can call `Acma.cancel(...)` (inherited from OpenZeppelin's `AccessManager`) to abort a *pending scheduled* operation before it executes. Admins (`_ADMIN_ROLE`) can also revoke an executor's role to stop them performing *future* privileged actions. Neither lever affects positions you already hold.

## Risks

### What's the worst-case scenario for me?

A successful smart-contract exploit. This could result in total loss of your supplied capital. The protocol is designed to make this unlikely through extensive testing, but until formal verification is complete, the risk is non-trivial.

### What's the worst case for the protocol as a whole?

A combination of (1) a flash crash that exceeds the over-collateralisation buffer, (2) compromised governance key, and (3) an unaddressed contract bug. Each of these is individually low-probability; the joint probability is much lower.

### Where can I see protocol-wide risk metrics?

`banq-cli` exposes per-pool reads: `banq health-of $USER`, `banq rates-of $TOKEN --at=all`, and `banq acma logs` cover the bulk of what a monitoring dashboard would track. See [CLI and tools](/for-keepers/cli-and-tools).

## Where to go next

- [Risks](/risks/overview) — full risk assessment
- [Comparison table](/reference/comparison-table) — Banq vs other protocols
