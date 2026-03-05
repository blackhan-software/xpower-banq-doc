<figure class="cover">
  <img src="../images/banq-cover.webp" alt="XPower Banq cover">
</figure>

# What is XPower Banq?

XPower Banq is a **permissionless DeFi lending protocol** running on the Ethereum Virtual Machine. You supply tokens to earn interest, you borrow against your supply, and the protocol takes care of pricing, liquidations, and risk parameters.

If you've used Compound, Aave, or Euler, the basic shape will feel familiar. The differences are in how the protocol behaves under stress.

## The one-paragraph version

Most lending protocols share a structural weakness: when prices move sharply, liquidations dump collateral, the dumped collateral pushes prices lower, and a cascade follows. XPower Banq dampens these cascades through a handful of design choices — optional position locks that can't be dumped during a crash, parameter changes that have to phase in slowly, and a liquidation model that doesn't require keepers to put up liquid capital. The cost is some flexibility for users; the benefit is a protocol that degrades gracefully instead of catastrophically.

## What you get as a supplier

You deposit collateral and earn the **supply rate**, which depends on how much of the pool is borrowed (utilization). You can withdraw any time — unless you've chosen to lock your position, in which case the principal stays put for the term you chose. Even when locked, accrued interest is always redeemable.

## What you get as a borrower

You post collateral and borrow against it, up to **66.67% LTV** by default. You pay the **borrow rate**. Your **health factor** must stay above 100%, or you can be liquidated. Locking your borrow position reduces your effective interest rate, in exchange for losing the ability to repay early.

## What's actually different

Five things, summarised on one screen:

- **Optionally locked positions.** Lock for a term (3–48 months) or permanently. Locked supply can't be redeemed; locked borrow can't be repaid early. In return, you earn a bonus or pay a malus on interest.
- **Lethargic governance.** No parameter can change by more than 2× per month, and changes phase in asymptotically rather than instantly. Catastrophic governance attacks would take half a year of sustained malicious control.
- **Debt-assumption liquidation.** When you're liquidated, the liquidator *takes on your debt and collateral atomically* rather than paying off your loan in cash. They need collateral headroom, not liquid capital.
- **Beta-distributed position caps.** The protocol rate-limits how fast any one account can grow. Combined with a √(n+2) divisor, this makes Sybil monopolisation slow and expensive — though not impossible.
- **Log-space TWAP oracle.** Prices are smoothed geometrically over time, with a built-in two-tick delay that makes flash-loan manipulation infeasible.

## What it doesn't do

XPower Banq is honest about its limits — see the [Risks](/risks/overview) section for the full picture. In short:

- The smart contracts have **not yet been formally verified**.
- The Sybil mechanism is **rate-limiting**, not Sybil-prevention. A patient attacker with capital can still accumulate.
- During a real crash, the oracle can be **2+ hours blind** to true prices. The over-collateralisation buffer is sized for this — but at the most aggressive LTV settings, tail-event bad debt is bounded but non-zero.
- At full lock adoption, **protocol margin approaches zero**.

## Where to go next

- **For an analogy-driven explanation:** [How it works](/introduction/how-it-works)
- **To compare against incumbents:** [Why XPower Banq](/introduction/why-xpower-banq)
- **To start using it:** [Quickstart](/introduction/quickstart)
