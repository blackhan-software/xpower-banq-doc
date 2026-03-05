---
title: "Appendix B: Formal Proofs"
description: "Formal proofs for cascade attenuation, Sybil rate-limiting, governance rate bounds, and MEV front-running resistance."
---

# Appendix B: Formal Proofs

## Cascade Attenuation Proof

::: proof
**Proof** (Cascade Attenuation Theorem, Whitepaper Section 4.1). Let liquidation of position $P$ with lock fraction $\phi$ transfer supply tokens $S$ to liquidator $L$.

**Step 1:** By the Position Lock definition (Whitepaper, Section 4.1), locked supply tokens cannot be redeemed: $\text{redeem}(S_{\text{locked}}) \to \text{revert}$.

**Step 2:** Liquidator $L$ receives position tokens, not underlying assets. The underlying assets remain in the Vault.

**Step 3:** Only unlocked fraction $(1{-}\phi)$ can generate sell pressure. Price impact: $\Delta p = f((1{-}\phi) \cdot V_{\text{sold}})$.

**Step 4:** Lock property is preserved through transfer (the lock transfer formula, Whitepaper Section 4.1). Therefore the cascade amplification factor is bounded by $(1{-}\phi)$.
:::

## Sybil Rate-Limiting

::: definition
**Definition 6** (Sybil Resistance Scope). The cap system bounds accumulation *rate* via holder-count scaling. It does **not** guarantee that more accounts hurts an attacker's long-term equilibrium share—simulation shows less than 2% penalty over 60 weeks.
:::

::: theorem
**Theorem 2** (Sybil Attack Cost). *For an attacker to increase total cap gain by factor $F$, they must create $k > F^2 \cdot (n{+}2) - (n{+}2)$ accounts. This quadratic scaling makes large gains expensive.*
:::

::: proof
**Proof.** With 1 account: $C_1 = C_{\max} \cdot \beta(\lambda) / \sqrt{n{+}2}$. With $k$ equal accounts and small $\lambda/k\text{:}$ $C_k \approx 12\lambda C_{\max}/\sqrt{n{+}k{+}2}$. For $C_k > F \cdot C_1\text{:}$ $\sqrt{n{+}2}/\sqrt{n{+}k{+}2} > F/k$, yielding the stated bound.
:::

## Governance Rate Bound Proof

::: proof
**Proof** (Governance Rate Bound, Whitepaper Section 6).

**Step 1 (Single bound):** Each transition satisfies $\theta_0/\mu \leq \theta_1 \leq \mu \cdot \theta_0$, enforced by `Governed` modifier.

**Step 2 (Rate limiting):** `setTarget()` is limited to once per $\Delta t_{\min}$. In interval $(t{-}t_0)$, at most $n = \lfloor(t{-}t_0)/\Delta t_{\min}\rfloor$ transitions occur.

**Step 3 (Composition):** After $n$ transitions: $\theta_n \leq \mu^n \theta_0$ and $\theta_n \geq \mu^{-n} \theta_0$.

**Step 4 (Transitions):** During transitions, the time-weighted mean stays between $\theta_{\text{old}}$ and $\theta_{\text{new}}$, preserving the bound.
:::

::: theorem
**Corollary 3** (Attack Detection Window). *To change a parameter by factor $F > \mu\text{:}$ $T_{\text{attack}} \geq \lceil\log_\mu F\rceil \cdot \Delta t_{\min}$. With $\mu = 2$, $\Delta t_{\min} = 1$ month, a $10\times$ change requires 4 months.*
:::

## MEV Front-Running Resistance

::: theorem
**Theorem 4** (MEV Front-Running Cost). *A liquidation with profit $\pi$ cannot be profitably front-run if: $H_{\text{attacker}}/H_{\text{victim}} < \text{block time}/T_{\text{PoW}}(\pi)$*
:::

::: proof
**Proof.** The PoW hash includes `tx.origin`, preventing solution reuse. The attacker must solve independently within one block time (${\sim}2$ seconds on Avalanche). With expected solve time $T = 16^d/H$, front-running fails when $T > \text{block time}$.
:::
