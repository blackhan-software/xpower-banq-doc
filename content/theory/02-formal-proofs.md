---
title: "2. Formal Proofs"
prev:
  text: "1. Mathematical Foundations"
  link: /theory/01-mathematical-foundations
next:
  text: "3. Nash Equilibrium Analysis"
  link: /theory/03-nash-equilibrium
---

## Cascade Attenuation

::: proof
**Proof of [Cascade Attenuation Theorem](/whitepaper/04-mechanisms#locked-positions-and-cascade-attenuation).** Let liquidation of position $P$ with lock fraction $\phi$ transfer supply tokens $S$ to liquidator $L$.

**Step 1.** By `Position.burn`, `redeem` reverts when the post-burn balance would fall below the user's aggregate lock total: the post-condition asserts `totalOf(user) >= _lock.totalOf(user)` after burning the requested amount, raising `Locked(user, total)` otherwise. There is no per-token "locked vs. unlocked" tag; the lock is a reservation against the aggregate balance. Hence the locked share $\phi \cdot S$ of any position cannot leave the protocol; only the unlocked surplus $(1{-}\phi) \cdot S$ is available for redemption and resale.

**Step 2.** Liquidator $L$ receives position tokens, not underlying assets. The underlying assets remain in the Vault.

**Step 3.** Only unlocked fraction $(1{-}\phi)$ can generate sell pressure. Price impact: $\Delta p = f((1{-}\phi) \cdot V_{\text{sold}})$.

**Step 4.** Lock property is preserved through transfer: by `Position._lockPush` → `LockLib.push`, each ring-buffer slot's value is scaled by `mulDiv(src_value, amount, balance)` and added to the target. This is invoked unconditionally on every `transferFrom`, including the liquidation path. Hence the per-user lock fraction $\phi_{\text{user}} = \texttt{depthOf}(\text{user})/\texttt{balance}(\text{user})$ is preserved across any transfer of size $\leq$ `balance`. Therefore the cascade amplification factor is bounded by $(1{-}\phi)$. $\blacksquare$
:::

## Sybil Rate-Limiting

::: definition
**Definition 2.1** (Sybil Resistance Scope). The cap system bounds accumulation *rate* via holder-count scaling. It does **not** guarantee that more accounts hurts an attacker's long-term equilibrium share — simulation shows $<2\%$ penalty over 60 weeks.
:::

::: theorem
**Theorem 2.2** (Sybil Attack Cost). *Assume each of the $k$ Sybil accounts holds a positive balance of at least one whole position token (`balance >= unit_token = 10^decimals`), so that it is counted as a large holder by `Position._largeHolders` (the running counter incremented in `_update` only when an account crosses `balance >= unit`). Assume further that the per-account cap considered is for a subsequent deposit on top of an existing positive balance, so that the $\beta(\lambda) = 12\lambda(1{-}\lambda)^2$ weighting of `_capOf` (gated on `balance > 0 && total > balance`) applies. Then for the attacker to increase total cap gain by factor $F$, they must create $k > F^2 \cdot (n{+}2) - (n{+}2)$ such large-holder Sybils. This quadratic scaling makes large gains expensive.*
:::

::: proof
**Proof.** Under the large-holder hypothesis the denominator $\sqrt{\texttt{largeHolders()}+2}$ scales from $\sqrt{n+2}$ to $\sqrt{n+k+2}$ when $k$ funded Sybils are added; a Sybil account with `balance < unit` would not advance the counter and is excluded by hypothesis. Under the existing-holder hypothesis, the beta block of `_capOf` is active. With 1 account: $C_1 = C_{\max} \cdot \beta(\lambda) / \sqrt{n{+}2}$. With $k$ equal accounts and small $\lambda/k$: $C_k \approx 12\lambda C_{\max}/\sqrt{n{+}k{+}2}$. For $C_k > F \cdot C_1$: $\sqrt{n{+}2}/\sqrt{n{+}k{+}2} > F/k$, yielding the stated bound. (A floor `MIN_HOLDERS_ID` on `largeHolders()` prevents the denominator from collapsing when $n$ is small.) $\blacksquare$
:::

## Governance Rate Bound

::: proof
**Proof of [Governance Rate Bound](/whitepaper/06-governance#governance-rate-bound).**

**Step 1 (Single bound).** Each transition satisfies $\theta_0/\mu \leq \theta_1 \leq \mu \cdot \theta_0$, enforced inline by `Parameterized._setTargetIf`, which compares the proposed value against `old_value << 1` (upper bound, $\mu = 2$) and `old_value >> 1` (lower bound, $1/\mu$) and reverts on violation.

**Step 2 (Rate limiting).** `setTarget` is guarded by the `limited(Constant.MONTH, ...)` modifier, which restricts updates to once per $\Delta t_{\min} = $ `Constant.MONTH` $= $ `Constant.YEAR`/12 ≈ 30.4375 days (a compile-time constant, not a governable parameter). In interval $(t - t_0)$, at most $n = \lfloor(t - t_0)/\Delta t_{\min}\rfloor$ transitions occur.

**Step 3 (Composition).** After $n$ transitions: $\theta_n \leq \mu^n \theta_0$ and $\theta_n \geq \mu^{-n} \theta_0$.

**Step 4 (Transitions).** During transitions, the time-weighted mean stays between $\theta_{\text{old}}$ and $\theta_{\text{new}}$, preserving the bound. $\blacksquare$
:::

::: theorem
**Corollary 2.3** (Attack Detection Window). *To change a parameter by factor $F > \mu$: $T_{\text{attack}} \geq \lceil \log_\mu F \rceil \cdot \Delta t_{\min}$. With $\mu = 2$ and the compile-time constant $\Delta t_{\min} = $ `Constant.MONTH` $\approx$ 30.4375 days (not itself governable), a $10\times$ change requires 4 months.*
:::

## MEV Front-Running Resistance

::: theorem
**Theorem 2.4** (MEV Front-Running Cost). *A liquidation with profit $\pi$ cannot be profitably front-run if*

$$H_{\text{attacker}}/H_{\text{victim}} < t_{\text{cache}}/T_{\text{PoW}}(\pi)$$

*where $t_{\text{cache}}$ is the `PowLimited` cache window over which the PoW key is stable.*
:::

::: proof
**Proof.** The PoW hash includes `tx.origin`, preventing solution reuse across attacker EOAs. The `PowLimited` modifier caches the block hash anchoring the PoW key for `cacheTime` seconds, refreshing only once `cacheTime + _blockTime < block.timestamp`. Both `Pool` and `Oracle` instantiate `PowLimited(1 hours)`, so $t_{\text{cache}} = 1$ hour $= 3600$ s. With expected solve time $T_{\text{PoW}}(\pi) = 16^d / H$, the attacker must mine independently within $t_{\text{cache}}$ against its own `tx.origin`; front-running fails when $T_{\text{PoW}} > t_{\text{cache}}$, i.e. when difficulty $d$ is tuned so that $16^d / H_{\text{attacker}} > t_{\text{cache}} = 3600$ s. $\blacksquare$
:::
